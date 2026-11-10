import { readFile, lstat, readdir } from "node:fs/promises";
import { realpathSync, lstatSync } from "node:fs";
import { basename, resolve, relative } from "node:path";
import { execFile } from "node:child_process";
import { runtimeEnvironment } from "./environment.mjs";
import { promisify } from "node:util";
import {
  contextBindingsPath,
  contextCoverage,
  loadContextBindings,
  reconcileDecisions,
} from "./context-bindings.mjs";
import {
  digest,
  exists,
  fail,
  id,
  listArtifacts,
  now,
  parseStrictJson,
  projectRoot,
  isWithin,
  readSource,
  redact,
  safeFile,
  sha,
  text,
  ServiceError,
} from "./utils.mjs";
const run = promisify(execFile);
// A recorded binding is an ownership boundary, not an invitation to resolve a
// replacement link. Explicit project previews canonicalize a user-selected root.
export function assertProjectRoot(root) {
  fail(
    resolve(root) === root,
    "SOURCE_DRIFT",
    "Recorded project root is not canonical",
    409,
  );
  for (let path = root; ; path = resolve(path, "..")) {
    fail(
      !lstatSync(path).isSymbolicLink(),
      "SOURCE_DRIFT",
      "A recorded project path was replaced by a link; review its identity again",
      409,
    );
    if (path === resolve(path, "..")) break;
  }
  fail(
    realpathSync(root) === root && lstatSync(root).isDirectory(),
    "SOURCE_DRIFT",
    "The recorded project root changed",
    409,
  );
  return root;
}
const stateRefs = [
  ".agent-foundry/state.json",
  ".agent-foundry/blueprint.json",
  ".appatelier/state.json",
  ".appatelier/profile.json",
  ".chatbotatelier/state.json",
  ".chatbot-atelier/state.json",
  ".gameatelier/orchestrator/state.json",
  ".gameatelier/state.json",
  ".atelier/state.json",
];
const instructionRefs = [
  contextBindingsPath,
  "AGENTS.md",
  "README.md",
  "releases/current.json",
  "governance/requirements.csv",
  "governance/QUALITY_MODEL.md",
  "standards/production-quality.md",
  "standards/context-capsule.md",
  "standards/production-profiles.json",
  "scripts/check_repository.py",
  "kit/verify_release.py",
  "docs/requirements.md",
  "docs/REQUIREMENTS.md",
  "docs/checkpoint.json",
  "docs/decisions.json",
  "docs/identity.json",
  "docs/project/CHECKPOINT_UA.md",
  "docs/project/CHECKPOINT.md",
  "docs/project/checkpoint.json",
];
const recordText = (row) =>
  typeof row === "string"
    ? row
    : row && typeof row === "object"
      ? ([
          row.text,
          row.title,
          row.objective,
          row.goal,
          row.mission,
          row.description,
        ].find((x) => typeof x === "string") ?? "")
      : "";
const section = (raw, pattern, { excludeCompleted = false } = {}) => {
  const lines = raw.split(/\r?\n/);
  const start = lines.findIndex(
    (line) => /^#{1,5}\s/.test(line) && pattern.test(line),
  );
  if (start < 0) return [];
  const result = [];
  for (const line of lines.slice(start + 1)) {
    if (/^#{1,5}\s/.test(line)) break;
    if (
      excludeCompleted &&
      /^\s*(?:(?:[-*+]|\d+[.)])\s+)?\[[xX]\](?:\s|$)/.test(line)
    )
      continue;
    const clean = line.replace(/^\s*(?:[-*]|\d+[.)])\s+/, "").trim();
    if (clean) result.push(clean);
    if (result.length >= 6) break;
  }
  return result;
};
export function projectSignals(documents, sources) {
  const goals = [],
    next_actions = [],
    work_records = [],
    agents = [];
  const sourceMap = new Map(sources.map((x) => [x.path, x.sha256]));
  for (const document of documents) {
    const data = document.data,
      source_ref = document.path,
      source_sha256 = sourceMap.get(source_ref);
    if (!data || typeof data !== "object") continue;
    if (typeof data.markdown === "string") {
      const goalLines = section(
        data.markdown,
        /(?:мета|місія|mission|objective|goal)/i,
      );
      if (goalLines.length)
        goals.push({
          text: goalLines.join(" ").slice(0, 1400),
          status: "declared",
          source_ref,
          source_sha256,
          basis: "source-document; approval not inferred",
        });
      for (const line of section(
        data.markdown,
        /(?:наступн|next\s+(?:step|action)|продовжен)/i,
        { excludeCompleted: true },
      ))
        next_actions.push({
          text: line.slice(0, 700),
          status: "declared",
          source_ref,
          source_sha256,
        });
      for (const match of data.markdown.matchAll(
        /^\s*[-*]\s+\[([xX])\]\s+(.+)$/gm,
      ))
        work_records.push({
          id: `record-${sha(source_ref + match[0]).slice(0, 16)}`,
          objective: match[2].slice(0, 800),
          status: "recorded",
          native_status: "checked",
          source: "native-project",
          source_ref,
          source_sha256,
          evidence_refs: [{ path: source_ref, sha256: source_sha256 }],
          skills: [],
        });
      continue;
    }
    const blueprint = data.blueprint?.data;
    const approval = data.approval;
    const authority = approval?.canonical_authority;
    const authorityDocument =
      authority && documents.find((row) => row.path === authority.path);
    const authorityItems =
      authorityDocument?.data?.items?.filter(
        (row) => row.id === authority.record_id,
      ) ?? [];
    const authorityCurrent = !!(
      authority &&
      sourceMap.get(authority.path) === authority.sha256 &&
      authorityDocument?.data?.schema_version === "foundry-authority/1" &&
      authorityItems.length === 1 &&
      authorityItems[0].actor === "user" &&
      authorityItems[0].decision === "approve" &&
      authorityItems[0].scope === approval.scope &&
      authorityItems[0].subject_sha256 === data.blueprint?.sha256
    );
    const approvedBlueprint = !!(
      blueprint &&
      data.blueprint.sha256 &&
      digest(blueprint) === data.blueprint.sha256 &&
      approval?.actor === "user" &&
      approval?.status === "confirmed" &&
      approval.decision === "approve" &&
      approval.revoked !== true &&
      approval.blueprint_sha256 === data.blueprint.sha256 &&
      approval.blueprint_revision === blueprint.revision &&
      approval.design_revision === data.design_revision &&
      authorityCurrent
    );
    const goal = [
      blueprint?.goal,
      data.goal,
      data.objective,
      data.mission,
      data.profile?.goal,
      data.project?.objective,
    ]
      .map(recordText)
      .find(Boolean);
    if (goal)
      goals.push({
        text: goal.slice(0, 3000),
        status: approvedBlueprint ? "accepted" : "declared",
        source_ref,
        source_sha256,
        basis: approvedBlueprint
          ? "current-native-approval-record"
          : "native-source; acceptance not inferred",
        ...(approvedBlueprint
          ? {
              approval_ref: source_ref + "#/approval",
              subject_sha256: data.blueprint.sha256,
            }
          : {}),
      });
    const actions = data.next_actions ?? data.next_action ?? data.next_steps;
    for (const row of typeof actions === "string"
      ? [{ text: actions }]
      : rows(actions)) {
      const value = recordText(row) || recordText(row.value);
      if (value)
        next_actions.push({
          text: value.slice(0, 700),
          status: "declared",
          source_ref,
          source_sha256,
        });
    }
    for (const key of ["tasks", "task", "jobs", "job", "milestones"]) {
      for (const row of rows(data[key]).slice(0, 500)) {
        const objective = recordText(row);
        if (objective)
          work_records.push({
            id: `record-${sha(source_ref + key + row.id + objective).slice(0, 16)}`,
            native_id: row.id,
            objective: objective.slice(0, 1000),
            outcome: recordText(row.result ?? row.output).slice(0, 1600),
            status: "recorded",
            native_status:
              typeof row.status === "string" ? row.status : "unknown",
            source: "native-project",
            source_ref,
            source_sha256,
            evidence_refs: [{ path: source_ref, sha256: source_sha256 }],
            skills: [],
          });
      }
    }
    const entry =
      data.project_agent ??
      data.entry_skill ??
      blueprint?.entry_skill ??
      blueprint?.agent_name;
    const name = typeof entry === "string" ? entry : entry?.name;
    if (typeof name === "string" && /^[a-z0-9][a-z0-9-]{1,100}$/.test(name))
      agents.push({
        name,
        status: "declared",
        availability: "planned",
        discovery_status: "unverified",
        source_ref,
        source_sha256,
      });
  }
  const goal = goals.find((x) => x.status === "accepted") ??
    goals.find((x) => x.basis.startsWith("native")) ??
    goals[0] ?? {
      text: "",
      status: "unknown",
      source_ref: null,
      source_sha256: null,
      basis: "No current goal source found",
    };
  return { goal, goals, next_actions, work_records, agents };
}
function csvRecords(raw) {
  const records = [];
  let rows = [],
    row = [],
    cell = "",
    quoted = false;
  for (let i = 0; i < raw.length; i++) {
    const c = raw[i];
    if (c === '"') {
      if (quoted && raw[i + 1] === '"') {
        cell += '"';
        i++;
      } else quoted = !quoted;
    } else if (c === "," && !quoted) {
      row.push(cell);
      cell = "";
    } else if (c === "\n" && !quoted) {
      row.push(cell.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      cell = "";
    } else cell += c;
  }
  if (cell || row.length) {
    row.push(cell);
    rows.push(row);
  }
  const header = rows.shift() ?? [];
  return rows
    .filter((x) => x.some(Boolean))
    .map((values) =>
      Object.fromEntries(
        header.map((key, index) => [key, values[index] ?? ""]),
      ),
    );
}
const schemaOf = (value) =>
  value?.schema_version ?? value?.schema ?? value?.version ?? "unknown";
const rows = (value) =>
  Array.isArray(value)
    ? value
    : value && typeof value === "object"
      ? Object.entries(value).map(([key, v]) =>
          v && typeof v === "object"
            ? {
                id: key,
                ...v,
              }
            : {
                id: key,
                value: v,
              },
        )
      : [];
const projectKind = (sources) =>
  sources.some((x) => x.path.startsWith(".gameatelier"))
    ? "game"
    : sources.some((x) => x.path.startsWith(".appatelier"))
      ? "app"
      : sources.some((x) => x.path.startsWith(".chatbot"))
        ? "bot"
        : sources.some((x) => x.path.startsWith(".agent-foundry"))
          ? "agent"
          : "generic";
function currentCheckpoint(root, binding, documents, sources) {
  const checkpoints = binding.source_checks.filter(
    (row) => row.role === "checkpoint",
  );
  const gap = (code, message) => ({
    current_checkpoint: null,
    current_checkpoint_gap: {
      code,
      message,
      blocking: false,
      source_refs: checkpoints.map((row) => row.path),
    },
  });
  const manifest = documents.find((row) => row.path === binding.manifest?.path);
  if (!manifest || manifest.data?.project_root !== root)
    return gap(
      "CHECKPOINT_NOT_DECLARED",
      "A current checkpoint needs one explicit context binding for this project",
    );
  if (checkpoints.length !== 1)
    return gap(
      checkpoints.length ? "CHECKPOINT_AMBIGUOUS" : "CHECKPOINT_NOT_DECLARED",
      "Declare exactly one checkpoint source; a current phase is not guessed from other files",
    );
  const check = checkpoints[0];
  const source = sources.find((row) => row.path === check.path);
  const loaded = binding.loaded.find((row) => row.path === check.path);
  if (
    !check.required ||
    check.status !== "verified" ||
    !source ||
    !loaded ||
    source.sha256 !== check.expected_sha256 ||
    loaded.sha256 !== source.sha256 ||
    check.observed_sha256 !== source.sha256
  )
    return gap(
      "CHECKPOINT_SOURCE_UNVERIFIED",
      "The required checkpoint source must match its declared current bytes",
    );
  const data = documents.find((row) => row.path === check.path)?.data;
  const boundedText = (value, maximum) =>
    typeof value === "string" &&
    value.trim().length > 0 &&
    value.length <= maximum;
  const boundedRows = (value) =>
    Array.isArray(value) &&
    value.length <= 100 &&
    value.every((row) => boundedText(row, 4000));
  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data) ||
    !boundedText(data.phase, 2000) ||
    !boundedRows(data.completed) ||
    !boundedRows(data.in_progress) ||
    !boundedText(data.next, 4000)
  )
    return gap(
      "CHECKPOINT_SHAPE_UNSUPPORTED",
      "Checkpoint phase/next must be bounded text and completed/in_progress must be bounded text arrays",
    );
  return {
    current_checkpoint: redact({
      phase: data.phase,
      completed: data.completed,
      in_progress: data.in_progress,
      next: data.next,
      source_ref: check.path,
      source_sha256: source.sha256,
      status: "declared",
    }),
    current_checkpoint_gap: null,
  };
}
export async function inspectProject(rootValue, { sourceRefs = [] } = {}) {
  const root = await projectRoot(rootValue);
  fail(
    Array.isArray(sourceRefs) &&
      sourceRefs.length <= 40 &&
      sourceRefs.every((x) => typeof x === "string" && x.length <= 4096),
    "INVALID_INPUT",
    "Use at most40 explicit relative native source locators",
  );
  for (const ref of sourceRefs) await safeFile(root, ref);
  const sources = [];
  const documents = [];
  const warnings = [];
  const ingest = (source) => {
    const ref = source.path;
    // A bound source may already have been discovered as a known native record.
    // Keep its parsed bytes and source pin from the same read, without duplicates.
    const oldSource = sources.findIndex((row) => row.path === ref);
    const oldDocument = documents.findIndex((row) => row.path === ref);
    const pin = {
      path: ref,
      sha256: source.sha256,
      bytes: source.bytes,
      kind:
        ref === contextBindingsPath
          ? "context-binding"
          : ref.endsWith(".json")
            ? "native-state"
            : "instruction",
    };
    if (oldSource >= 0) sources[oldSource] = pin;
    else sources.push(pin);
    let parsed;
    if (ref.endsWith(".csv"))
      parsed = { path: ref, data: { requirements: csvRecords(source.text) } };
    if (ref.endsWith(".json")) {
      try {
        parsed = { path: ref, data: parseStrictJson(source.text) };
      } catch (error) {
        warnings.push({
          path: ref,
          code: error.code ?? "INVALID_JSON",
          message: error.message,
        });
      }
    }
    if (/\.md$/i.test(ref))
      parsed = { path: ref, data: { markdown: source.text } };
    if (parsed && oldDocument >= 0) documents[oldDocument] = parsed;
    else if (parsed) documents.push(parsed);
    else if (oldDocument >= 0) documents.splice(oldDocument, 1);
  };
  const additionalRefs = [];
  for (const folder of ["docs/project", "docs/agent", "docs/requirements"]) {
    try {
      const entries = await readdir(
        await safeFile(root, folder, { directory: true }),
        { withFileTypes: true },
      );
      for (const entry of entries
        .sort((a, b) => a.name.localeCompare(b.name))
        .slice(0, 50)) {
        if (
          entry.isFile() &&
          /\.(?:md|json)$/i.test(entry.name) &&
          /checkpoint|passport|pasport|requirements|decision|identity|roadmap|prd|implementation.scenario|plan/i.test(
            entry.name,
          )
        )
          additionalRefs.push(folder + "/" + entry.name);
      }
    } catch {}
  }
  for (const ref of [
    ...new Set([
      ...stateRefs,
      ...instructionRefs,
      ...additionalRefs,
      ...sourceRefs,
    ]),
  ])
    if (await exists(resolve(root, ref))) {
      try {
        const source = await readSource(root, ref);
        ingest(source);
      } catch (error) {
        warnings.push({
          path: ref,
          code: error.code ?? "READ_FAILED",
          message: error.message,
        });
      }
    }
  const binding = await loadContextBindings({
    root,
    documents,
    sources,
    readFailures: warnings,
  });
  for (const source of binding.loaded) ingest(source);
  const artifacts = await listArtifacts(root);
  for (const document of [...documents]) {
    const binding = document.data?.approval?.canonical_authority;
    if (
      typeof binding?.path !== "string" ||
      documents.some((x) => x.path === binding.path)
    )
      continue;
    try {
      const source = await readSource(root, binding.path);
      const data = parseStrictJson(source.text);
      documents.push({ path: binding.path, data });
      sources.push({
        path: binding.path,
        sha256: source.sha256,
        bytes: source.bytes,
        kind: "native-authority",
      });
    } catch (error) {
      warnings.push({
        path: binding.path,
        code: error.code ?? "READ_FAILED",
        message:
          "Native approval source is unavailable; accepted goal not inferred",
      });
    }
  }
  let repository = { present: false };
  if (await exists(resolve(root, ".git"))) {
    try {
      const { stdout } = await run("git", ["-C", root, "rev-parse", "HEAD"], {
        timeout: 4e3,
        maxBuffer: 4096,
      });
      repository = {
        present: true,
        commit: stdout.trim(),
      };
      const branch = await run(
        "git",
        ["-C", root, "branch", "--show-current"],
        {
          timeout: 4e3,
          maxBuffer: 4096,
        },
      );
      repository.branch = branch.stdout.trim();
    } catch {
      repository = {
        present: true,
        status: "unverified",
      };
    }
  }
  const native = documents.filter(
    (x) =>
      x.path.startsWith(".") && x.data?.schema !== "atelier.context-bindings/1",
  );
  const primary = native[0]?.data;
  const kind = projectKind(sources);
  const requirements = [],
    decisions = [],
    identity = [],
    readiness = [],
    deferred_work = [];
  const append = (target, values, source) => {
    for (const row of rows(values))
      target.push({
        ...(typeof row === "string" ? { text: redact(row) } : redact(row)),
        source_ref: source,
        source_sha256: sources.find((item) => item.path === source)?.sha256,
      });
  };
  for (const document of documents) {
    const data = document.data;
    if (!data || typeof data !== "object") continue;
    append(
      requirements,
      data.requirements ?? data.requirement_registry ?? data.requirement,
      document.path,
    );
    append(decisions, data.decisions ?? data.decision, document.path);
    if (data.identity) append(identity, data.identity, document.path);
    if (data.readiness) append(readiness, data.readiness, document.path);
    append(deferred_work, data.deferred_work ?? data.deferred, document.path);
  }
  for (const check of binding.source_checks) {
    if (
      !["requirements", "decisions"].includes(check.role) ||
      check.status !== "verified"
    )
      continue;
    const data = documents.find((row) => row.path === check.path)?.data;
    const nativeRows =
      check.role === "requirements"
        ? (data?.requirements ??
          data?.requirement_registry ??
          data?.requirement)
        : (data?.decisions ?? data?.decision);
    check.projection_status =
      nativeRows && typeof nativeRows === "object"
        ? "native-records-read"
        : "unsupported";
    if (check.projection_status === "unsupported")
      binding.issues.push({
        code: "CONTEXT_INCOMPLETE",
        message:
          "The declared structured source has no supported native record group; keep it as a source and provide an explicit native projection",
        path: check.path,
        blocking: check.required,
      });
  }
  const decisionContext = reconcileDecisions(decisions);
  const context_coverage = contextCoverage(
    binding,
    requirements,
    decisionContext.issues,
  );
  warnings.push(...context_coverage.issues);
  const schemas = native.map((x) => ({
    path: x.path,
    schema: schemaOf(x.data),
  }));
  const signals = projectSignals(documents, sources);
  try {
    for (const entry of (
      await readdir(
        await safeFile(root, ".agents/skills", { directory: true }),
        { withFileTypes: true },
      )
    )
      .filter((x) => x.isDirectory())
      .sort((a, b) => a.name.localeCompare(b.name))
      .slice(0, 50)) {
      try {
        const ref = `.agents/skills/${entry.name}/SKILL.md`;
        const source = await readSource(root, ref);
        const frontmatter =
          /^---[ \t]*\r?\n([\s\S]*?)\r?\n---(?:[ \t]*\r?\n|[ \t]*$)/.exec(
            source.text,
          )?.[1];
        const name =
          frontmatter &&
          /^name:[ \t]*["']?([a-z0-9-]+)["']?[ \t]*$/m.exec(frontmatter)?.[1];
        if (name) {
          sources.push({
            path: ref,
            sha256: source.sha256,
            bytes: source.bytes,
            kind: "project-agent",
          });
          signals.agents.push({
            name,
            status: "observed",
            availability: "installed",
            source_ref: ref,
            source_sha256: source.sha256,
            discovery_status: "unverified",
          });
        }
      } catch {}
    }
  } catch {}
  const revision = digest({ sources, repository });
  return {
    root,
    name: basename(root),
    kind,
    revision,
    phase:
      typeof (primary?.phase ?? primary?.current_phase ?? primary?.stage) ===
      "string"
        ? (primary?.phase ?? primary?.current_phase ?? primary?.stage)
        : "not_recorded",
    status: warnings.length ? "attention" : "observed",
    summary:
      typeof (primary?.mission ?? primary?.objective ?? primary?.goal) ===
      "string"
        ? (primary?.mission ?? primary?.objective ?? primary?.goal)
        : "",
    native_schema: schemas,
    capabilities: {
      read: true,
      prepare: true,
      dispatch: true,
      native_mutation: false,
      decision_write: false,
      evidence_write: false,
    },
    sources,
    requirements,
    decisions,
    current_decisions: decisionContext.current_decisions,
    corrections: decisionContext.corrections,
    deferred_work,
    context_coverage,
    identity,
    readiness,
    artifacts,
    repository,
    warnings,
    ...redact(signals),
    native_state_present: native.length > 0,
    projection_notice:
      "Read-only projection. Product state is authoritative; binding does not migrate or adopt a project.",
    ...currentCheckpoint(root, binding, documents, sources),
  };
}
export class ProjectAdapter {
  constructor(store, privateDataRoot) {
    this.store = store;
    this.privateDataRoot = privateDataRoot
      ? realpathSync(privateDataRoot)
      : null;
    this.previews = new Map();
  }
  async preview(payload) {
    const root = await projectRoot(text(payload.root, "root", 1, 4096));
    fail(
      !this.privateDataRoot ||
        (!isWithin(this.privateDataRoot, root) &&
          !isWithin(root, this.privateDataRoot)),
      "PRIVATE_PATH",
      "Select a product root disjoint from the service's private data directory",
      403,
    );
    const view = await inspectProject(root, {
      sourceRefs: payload.source_refs ?? [],
    });
    const preview_id = id("preview");
    this.previews.set(preview_id, {
      view,
      source_refs: payload.source_refs ?? [],
      expires: Date.now() + 10 * 60 * 1e3,
    });
    return {
      preview_id,
      ...view,
    };
  }
  async bind(payload) {
    const preview = this.previews.get(text(payload.preview_id, "preview_id"));
    fail(
      preview && preview.expires > Date.now(),
      "PREVIEW_EXPIRED",
      "Preview expired; inspect the project again",
      409,
    );
    const view = await inspectProject(preview.view.root, {
      sourceRefs: preview.source_refs,
    });
    fail(
      view.revision === preview.view.revision,
      "SOURCE_DRIFT",
      "Project sources changed after preview",
      409,
    );
    const existing = this.store
      .list("project")
      .find((x) => x.root === view.root);
    if (
      existing &&
      JSON.stringify(existing.source_refs ?? []) !==
        JSON.stringify(preview.source_refs)
    ) {
      existing.source_refs = preview.source_refs;
      existing.revision = view.revision;
    }
    if (
      existing &&
      [
        "app",
        "bot",
        "game",
        "agent",
        "research",
        "document",
        "mixed",
        "generic",
      ].includes(payload.view_profile)
    )
      existing.view_profile = payload.view_profile;
    if (existing)
      this.store.put(
        "project",
        existing.id,
        existing,
        existing.record_revision,
      );
    if (existing)
      return {
        project: existing,
        existing: true,
      };
    const stamp = now();
    const project = {
      id: id("project"),
      name:
        typeof payload.name === "string"
          ? text(payload.name, "name", 1, 160)
          : view.name,
      root: view.root,
      kind: view.kind,
      view_profile: [
        "app",
        "bot",
        "game",
        "agent",
        "research",
        "document",
        "mixed",
        "generic",
      ].includes(payload.view_profile)
        ? payload.view_profile
        : view.kind,
      revision: view.revision,
      phase: view.phase,
      status: view.status,
      summary: view.summary,
      repository: view.repository,
      native_schema: view.native_schema,
      source_refs: preview.source_refs,
      capabilities: view.capabilities,
      created_at: stamp,
      updated_at: stamp,
    };
    const result = this.store.put("project", project.id, project);
    this.previews.delete(payload.preview_id);
    return { project: result };
  }
  async workspace(projectId) {
    const project = this.get(projectId);
    const current = await inspectProject(project.root, {
      sourceRefs: project.source_refs ?? [],
    });
    return {
      ...current,
      project: {
        ...project,
        revision: current.revision,
        phase: current.phase,
        status: current.status,
        native_schema: current.native_schema,
        repository: current.repository,
      },
      jobs: this.store.list("job").filter((x) => x.project_id === projectId),
      tasks: this.store.list("task").filter((x) => x.project_id === projectId),
      context: {
        source_revision: current.revision,
        sources: current.sources,
        authority: "native-project",
        notice: current.projection_notice,
        coverage: current.context_coverage,
        current_decisions: current.current_decisions,
        corrections: current.corrections,
        deferred_work: current.deferred_work,
      },
      service_decisions: this.store
        .list("decision")
        .filter((x) => x.project_id === projectId),
      service_evidence: this.store
        .list("evidence")
        .filter((x) => x.project_id === projectId),
    };
  }
  get(projectId) {
    const project = this.store.get("project", projectId);
    fail(project, "PROJECT_NOT_FOUND", "Project binding not found", 404);
    assertProjectRoot(project.root);
    fail(
      !this.privateDataRoot ||
        (!isWithin(this.privateDataRoot, project.root) &&
          !isWithin(project.root, this.privateDataRoot)),
      "PRIVATE_PATH",
      "The binding overlaps the service private data directory; select disjoint roots",
      403,
    );
    return project;
  }
  async refresh(projectId, expected) {
    const project = this.get(projectId);
    if (expected)
      fail(
        project.revision === expected,
        "REVISION_CONFLICT",
        "Binding revision changed; refresh",
        409,
      );
    const view = await inspectProject(project.root, {
      sourceRefs: project.source_refs ?? [],
    });
    return {
      project: this.store.put(
        "project",
        projectId,
        {
          ...project,
          revision: view.revision,
          phase: view.phase,
          status: view.status,
          native_schema: view.native_schema,
          repository: view.repository,
        },
        project.record_revision,
      ),
      warnings: view.warnings,
    };
  }
  async diff(projectId, ref) {
    const project = this.get(projectId);
    if (ref) await safeFile(project.root, ref);
    fail(
      await exists(resolve(project.root, ".git")),
      "UNSUPPORTED_CAPABILITY",
      "This project has no verified Git working tree",
      409,
    );
    const args = [
      "--no-pager",
      "-C",
      project.root,
      "diff",
      "--no-ext-diff",
      "--no-textconv",
      "--ignore-submodules=all",
      "--no-color",
    ];
    if (ref) args.push("--", ref);
    try {
      const result = await run("git", args, {
        cwd: project.root,
        env: runtimeEnvironment(),
        timeout: 5000,
        maxBuffer: 1024 * 1024,
      });
      return {
        diff: redact(result.stdout),
        truncated: false,
        source: "git working tree",
        path: ref ?? null,
      };
    } catch (error) {
      if (error.code === "ERR_CHILD_PROCESS_STDIO_MAXBUFFER")
        return {
          diff: redact(error.stdout ?? ""),
          truncated: true,
          source: "git working tree",
          path: ref ?? null,
        };
      throw new ServiceError(
        "DIFF_UNAVAILABLE",
        "Git working-tree comparison could not be read",
        409,
      );
    }
  }
  async content(projectId, ref) {
    const project = this.get(projectId);
    const file = await safeFile(project.root, ref, {
      maxBytes: 4 * 1024 * 1024,
    });
    const bytes = await readFile(file);
    return {
      path: ref,
      sha256: sha(bytes),
      bytes: bytes.length,
      content: redact(bytes.toString("utf8")),
    };
  }
  async artifact(projectId, ref) {
    const project = this.get(projectId);
    const file = await safeFile(project.root, ref, {
      maxBytes: 24 * 1024 * 1024,
    });
    return {
      file,
      project,
    };
  }
}
