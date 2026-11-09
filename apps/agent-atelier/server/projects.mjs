import { readFile, lstat, readdir } from "node:fs/promises";
import { realpathSync } from "node:fs";
import { basename, resolve, relative } from "node:path";
import { execFile } from "node:child_process";
import { runtimeEnvironment } from "./environment.mjs";
import { promisify } from "node:util";
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
];
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
export async function inspectProject(rootValue) {
  const root = await projectRoot(rootValue);
  const sources = [];
  const documents = [];
  const warnings = [];
  for (const ref of [...stateRefs, ...instructionRefs])
    if (await exists(resolve(root, ref))) {
      try {
        const source = await readSource(root, ref);
        sources.push({
          path: ref,
          sha256: source.sha256,
          bytes: source.bytes,
          kind: ref.endsWith(".json") ? "native-state" : "instruction",
        });
        if (ref.endsWith(".csv"))
          documents.push({
            path: ref,
            data: { requirements: csvRecords(source.text) },
          });
        if (ref.endsWith(".json")) {
          try {
            documents.push({
              path: ref,
              data: parseStrictJson(source.text),
            });
          } catch (error) {
            warnings.push({
              path: ref,
              code: error.code ?? "INVALID_JSON",
              message: error.message,
            });
          }
        }
      } catch (error) {
        warnings.push({
          path: ref,
          code: error.code ?? "READ_FAILED",
          message: error.message,
        });
      }
    }
  const artifacts = await listArtifacts(root);
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
  const native = documents.filter((x) => x.path.startsWith("."));
  const primary = native[0]?.data;
  const kind = projectKind(sources);
  const requirements = [],
    decisions = [],
    identity = [],
    readiness = [];
  const append = (target, values, source) => {
    for (const row of rows(values))
      target.push({
        ...redact(row),
        source_ref: source,
      });
  };
  for (const document of documents) {
    const data = document.data;
    append(
      requirements,
      data.requirements ?? data.requirement_registry,
      document.path,
    );
    append(decisions, data.decisions, document.path);
    if (data.identity) append(identity, data.identity, document.path);
    if (data.readiness) append(readiness, data.readiness, document.path);
  }
  const schemas = native.map((x) => ({
    path: x.path,
    schema: schemaOf(x.data),
  }));
  const revision = digest({
    sources,
    repository,
  });
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
    identity,
    readiness,
    artifacts,
    repository,
    warnings,
    native_state_present: native.length > 0,
    projection_notice:
      "Read-only projection. Product state is authoritative; binding does not migrate or adopt a project.",
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
    const view = await inspectProject(root);
    const preview_id = id("preview");
    this.previews.set(preview_id, {
      view,
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
    const view = await inspectProject(preview.view.root);
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
    const current = await inspectProject(project.root);
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
    const view = await inspectProject(project.root);
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
