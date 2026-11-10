import { isAbsolute, normalize, resolve } from "node:path";
import { readSource } from "./utils.mjs";

export const contextBindingsPath = ".atelier/context-bindings.json";
const schema = "atelier.context-bindings/1";
const hashPattern = /^[a-f0-9]{64}$/;
const ids = (value) =>
  Array.isArray(value) &&
  value.length <= 2000 &&
  value.every(
    (id) => typeof id === "string" && id.length > 0 && id.length <= 240,
  ) &&
  new Set(value).size === value.length;
const issue = (code, message, details = {}) => ({
  code,
  message,
  blocking: true,
  ...details,
});

// A binding is a source inventory, never an authority/approval or a second backlog.
// Only an explicit project source or the one project-owned conventional path is read.
export async function loadContextBindings({
  root,
  documents,
  sources,
  readFailures = [],
}) {
  const manifests = documents.filter((row) => row.data?.schema === schema);
  const result = { manifest: null, source_checks: [], loaded: [], issues: [] };
  const conventional = [...sources, ...readFailures].some(
    (row) => row.path === contextBindingsPath,
  );
  if (
    conventional &&
    !manifests.some((row) => row.path === contextBindingsPath)
  )
    result.issues.push(
      issue(
        "CONTEXT_INCOMPLETE",
        "The project context binding has an invalid schema or cannot be parsed",
        { path: contextBindingsPath },
      ),
    );
  if (!manifests.length) return result;
  if (manifests.length !== 1) {
    result.issues.push(
      issue(
        "CONTEXT_CONFLICT",
        "Choose one project context binding; multiple binding manifests are ambiguous",
      ),
    );
    return result;
  }
  const manifest = manifests[0];
  result.manifest = {
    path: manifest.path,
    sha256: sources.find((row) => row.path === manifest.path)?.sha256,
  };
  const data = manifest.data;
  if (
    typeof data.project_root !== "string" ||
    resolve(data.project_root) !== root ||
    data.project_root !== root
  )
    result.issues.push(
      issue(
        "SCOPE_MISMATCH",
        "Context bindings belong to a different canonical project root",
        { path: manifest.path },
      ),
    );
  for (const key of ["expected_requirement_ids", "expected_must_ids"]) {
    const value = data[key] ?? [];
    if (!ids(value))
      result.issues.push(
        issue(
          "CONTEXT_INCOMPLETE",
          `Context binding ${key} must contain unique requirement IDs`,
          { path: manifest.path },
        ),
      );
    else result[key] = value;
  }
  const links = data.requirement_links ?? [];
  if (
    !Array.isArray(links) ||
    links.length > 2000 ||
    links.some(
      (row) =>
        !row ||
        typeof row !== "object" ||
        typeof row.requirement_id !== "string" ||
        !row.requirement_id ||
        row.requirement_id.length > 240 ||
        typeof row.source_path !== "string" ||
        !row.source_path ||
        row.source_path.length > 4096 ||
        typeof row.source_excerpt !== "string" ||
        !row.source_excerpt ||
        row.source_excerpt.length > 20000,
    )
  )
    result.issues.push(
      issue(
        "CONTEXT_INCOMPLETE",
        "Declared requirement links need bounded IDs, pinned source paths and literal excerpts",
        { path: manifest.path },
      ),
    );
  else result.requirement_links = links;
  if (
    !Array.isArray(data.sources) ||
    data.sources.length < 1 ||
    data.sources.length > 40
  ) {
    result.issues.push(
      issue(
        "CONTEXT_INCOMPLETE",
        "Context bindings need between 1 and 40 explicit source pins",
        { path: manifest.path },
      ),
    );
    return result;
  }
  const seen = new Set();
  for (const row of data.sources) {
    if (
      !row ||
      typeof row !== "object" ||
      Array.isArray(row) ||
      typeof row.path !== "string" ||
      !row.path ||
      row.path.length > 4096 ||
      isAbsolute(row.path) ||
      normalize(row.path) !== row.path ||
      row.path.split(/[\\/]/).includes("..") ||
      typeof row.role !== "string" ||
      !row.role ||
      row.role.length > 120 ||
      !hashPattern.test(row.sha256) ||
      (row.required !== undefined && typeof row.required !== "boolean") ||
      (row.requirement_ids !== undefined && !ids(row.requirement_ids))
    ) {
      result.issues.push(
        issue(
          "CONTEXT_INCOMPLETE",
          "Every bound source needs a relative path, SHA-256, role and valid requirement IDs",
          { path: manifest.path },
        ),
      );
      continue;
    }
    if (seen.has(row.path) || row.path === manifest.path) {
      result.issues.push(
        issue(
          "CONTEXT_CONFLICT",
          "A bound source is duplicated or refers to its own manifest",
          { path: row.path },
        ),
      );
      continue;
    }
    seen.add(row.path);
    const check = {
      path: row.path,
      role: row.role,
      required: row.required !== false,
      expected_sha256: row.sha256,
      requirement_ids: row.requirement_ids ?? [],
    };
    try {
      const source = await readSource(root, row.path);
      check.observed_sha256 = source.sha256;
      check.status = source.sha256 === row.sha256 ? "verified" : "changed";
      result.loaded.push(source);
      if (check.status === "changed")
        result.issues.push(
          issue(
            "SOURCE_DRIFT",
            "A declared context source changed; review and rebind its current bytes",
            { path: row.path, blocking: check.required },
          ),
        );
    } catch (error) {
      check.status = error.code === "ENOENT" ? "missing" : "unreadable";
      result.issues.push(
        issue(
          "CONTEXT_INCOMPLETE",
          "A declared original source is unavailable inside this project",
          { path: row.path, blocking: check.required },
        ),
      );
    }
    result.source_checks.push(check);
  }
  return result;
}

export function reconcileDecisions(decisions) {
  const indexed = new Map(),
    superseded = new Set(),
    corrections = [],
    issues = [];
  for (const row of decisions) {
    if (typeof row.id !== "string") continue;
    const group = indexed.get(row.id) ?? [];
    group.push(row);
    indexed.set(row.id, group);
  }
  for (const [id, group] of indexed)
    if (group.length > 1)
      issues.push(
        issue("CONTEXT_CONFLICT", "Native decisions have an ambiguous duplicate identity", {
          decision_id: id,
          paths: group.map((row) => row.source_ref),
        }),
      );
  const edges = new Map();
  for (const row of decisions) {
    if (row.supersedes === undefined) continue;
    if (typeof row.id !== "string" || !ids(row.supersedes)) {
      issues.push(
        issue(
          "CONTEXT_CONFLICT",
          "A decision correction needs a stable ID and an explicit supersedes ID list",
          { path: row.source_ref },
        ),
      );
      continue;
    }
    if (
      indexed.get(row.id)?.length !== 1 ||
      row.supersedes.some((id) => indexed.get(id)?.length !== 1)
    ) {
      issues.push(
        issue(
          "CONTEXT_CONFLICT",
          "A decision correction refers to a missing or ambiguous native decision",
          { path: row.source_ref },
        ),
      );
      continue;
    }
    edges.set(row.id, row.supersedes);
    for (const id of row.supersedes) superseded.add(id);
    corrections.push({
      id: row.id,
      supersedes: row.supersedes,
      source_ref: row.source_ref,
      source_sha256: row.source_sha256,
    });
  }
  const visiting = new Set(),
    visited = new Set();
  const visit = (id) => {
    if (visiting.has(id)) return false;
    if (visited.has(id)) return true;
    visiting.add(id);
    for (const prior of edges.get(id) ?? []) if (!visit(prior)) return false;
    visiting.delete(id);
    visited.add(id);
    return true;
  };
  if ([...edges.keys()].some((id) => !visit(id)))
    issues.push(
      issue("CONTEXT_CONFLICT", "Native decision corrections form a cycle"),
    );
  // On a conflicting graph retain every decision; never silently choose a winner.
  return {
    current_decisions: issues.length
      ? decisions
      : decisions.filter((row) => !superseded.has(row.id)),
    corrections,
    issues,
  };
}

export function contextCoverage(binding, requirements, decisionIssues = []) {
  const expected = binding.expected_requirement_ids ?? [];
  const expectedMust = binding.expected_must_ids ?? [];
  const indexed = new Map(
    requirements.map((row) => [
      String(row.id ?? row.requirement_id ?? row.key),
      row,
    ]),
  );
  const missing = expected.filter((id) => !indexed.has(id));
  const missingMust = expectedMust.filter((id) => {
    const row = indexed.get(id);
    const nativePriority = String(
      row?.priority ?? row?.severity ?? "must",
    ).toLowerCase();
    const priority = ["must", "should", "could"].includes(nativePriority)
      ? nativePriority
      : "must";
    return !row || row.applicable === false || priority !== "must";
  });
  const issues = [
    ...binding.issues,
    ...decisionIssues.map((row) =>
      binding.manifest ? row : { ...row, blocking: false },
    ),
  ];
  if (missing.length || missingMust.length)
    issues.push(
      issue(
        "CONTEXT_INCOMPLETE",
        "The native requirement register omits or weakens declared required obligations",
        { requirement_ids: [...new Set([...missing, ...missingMust])] },
      ),
    );
  for (const check of binding.source_checks) {
    const omitted = check.requirement_ids.filter(
      (id) =>
        !requirements.some(
          (row) =>
            String(row.id ?? row.requirement_id ?? row.key) === id &&
            row.source_ref === check.path,
        ),
    );
    if (omitted.length)
      issues.push(
        issue(
          "CONTEXT_INCOMPLETE",
          "A source-to-requirement binding is not present in the parsed native register",
          {
            path: check.path,
            requirement_ids: omitted,
            blocking: check.required,
          },
        ),
      );
  }
  const requirement_checks = [];
  for (const link of binding.requirement_links ?? []) {
    const sourceCheck = binding.source_checks.find(
      (row) => row.path === link.source_path,
    );
    const original = binding.loaded.find(
      (row) => row.path === link.source_path,
    );
    const row = indexed.get(link.requirement_id);
    const verbatim =
      row?.verbatim ??
      row?.source_text ??
      row?.source_text_uk ??
      row?.text ??
      row?.description ??
      row?.requirement;
    const status = !sourceCheck
      ? "source-not-bound"
      : sourceCheck.status !== "verified"
        ? "original-unverified"
        : !row
          ? "missing-requirement"
          : !original?.text.includes(link.source_excerpt)
            ? "quote-not-in-source"
            : typeof verbatim !== "string" ||
                !verbatim.includes(link.source_excerpt)
              ? "quote-not-in-requirement"
              : "verified-excerpt";
    requirement_checks.push({
      ...link,
      source_sha256: sourceCheck?.observed_sha256,
      status,
    });
    if (status !== "verified-excerpt")
      issues.push(
        issue(
          "CONTEXT_INCOMPLETE",
          "A declared original excerpt is not preserved in its native requirement",
          {
            path: link.source_path,
            requirement_ids: [link.requirement_id],
            blocking: sourceCheck?.required !== false,
          },
        ),
      );
  }
  return {
    schema_version: "atelier.context-coverage/1",
    status: issues.some(
      (row) => row.code === "CONTEXT_CONFLICT" || row.code === "SCOPE_MISMATCH",
    )
      ? "conflict"
      : issues.length
        ? "incomplete"
        : binding.manifest
          ? "verified-declared-bindings"
          : "unverified",
    manifest_ref: binding.manifest,
    source_checks: binding.source_checks,
    requirement_checks,
    expected_requirement_ids: expected,
    expected_must_ids: expectedMust,
    missing_requirement_ids: missing,
    missing_must_ids: missingMust,
    issues,
    source_completeness_authenticated: false,
    notice:
      "Only declared source pins, requirement identities and explicit decision corrections are checked. A missing undeclared original or omitted meaning needs independent source reconciliation; no approval or completeness is inferred.",
  };
}
