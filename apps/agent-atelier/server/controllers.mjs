import { execFile } from "node:child_process";
import {
  readFile,
  readdir,
  lstat,
  mkdir,
  realpath,
  chmod,
} from "node:fs/promises";
import { homedir } from "node:os";
import { resolve, join, relative, isAbsolute } from "node:path";
import { pythonExecutable } from "./platform.mjs";
import { runtimeEnvironment } from "./environment.mjs";
import {
  atomicWrite,
  digest,
  exists,
  fail,
  id,
  isWithin,
  now,
  parseStrictJson,
  readSource,
  redact,
  safeFile,
  sha,
  text,
  ServiceError,
  containsObviousCredential,
} from "./utils.mjs";

const RECORD = new Set([
  "blueprint",
  "approve",
  "lesson",
  "artifact",
  "test",
  "evidence",
  "execution",
  "requirement",
  "decision",
  "task",
  "intake",
  "pause",
  "capability",
  "grant",
  "action",
  "receipt",
]);
const ID = new Set([
  "readiness",
  "start",
  "complete",
  "phase-check",
  "dispatch",
  "receipt",
]);
const ALLOWED = new Set([
  "init",
  "blueprint",
  "check",
  "approve",
  "build-gate",
  "context",
  "lesson",
  "artifact",
  "test",
  "evidence",
  "execution",
  "requirement",
  "decision",
  "task",
  "readiness",
  "start",
  "complete",
  "phase-check",
  "bundle-check",
  "intake",
  "pause",
  "resume",
  "capability",
  "grant",
  "action",
  "dispatch",
  "receipt",
  "refresh",
  "suite-update-plan",
]);
const SECRET =
  /^(?:\.env(?:\..*)?|credentials(?:\..*)?|owner-credentials\.json|auth\.json|id_(?:rsa|ed25519)|.*\.(?:pem|key|p12|pfx))$/i;
const PRIVATE = new Set([".git", ".aws", ".ssh", ".config", "node_modules"]);
const HASH = /^[a-f0-9]{64}$/;
const PARAMS = {
  init: ["project_id", "purpose"],
  blueprint: ["change_authority_path"],
  approve: ["sha256", "revision", "scope"],
  context: ["query"],
  readiness: ["id"],
  start: ["id"],
  complete: ["id", "evidence"],
  "phase-check": ["id", "scope", "execution_id"],
  "bundle-check": ["directory"],
  intake: ["source"],
  dispatch: ["id", "revision"],
  receipt: ["id", "outcome"],
  refresh: ["accept_suite_update"],
};
async function boundProject(projects, projectId) {
  const project = projects.get(projectId);
  for (let path = resolve(project.root); ; path = resolve(path, "..")) {
    fail(
      !(await lstat(path)).isSymbolicLink(),
      "SOURCE_DRIFT",
      "The bound project path was replaced by a link; review its identity again",
      409,
    );
    if (path === resolve(path, "..")) break;
  }
  fail(
    (await realpath(project.root)) === project.root &&
      (await lstat(project.root)).isDirectory(),
    "SOURCE_DRIFT",
    "The bound project root changed",
    409,
  );
  return project;
}

function ref(value, field, allowDot = false) {
  const input = text(value, field, 1, 4096);
  fail(
    !isAbsolute(input) &&
      !input.includes("\\") &&
      !input.includes("\0") &&
      !input.includes(":"),
    "OUTSIDE_ROOT",
    "A project-relative path is required",
  );
  const parts = input.split("/");
  fail(
    (allowDot && input === ".") ||
      parts.every(
        (p) =>
          p && p !== "." && p !== ".." && !PRIVATE.has(p) && !SECRET.test(p),
      ),
    "PRIVATE_PATH",
    "Private or noncanonical controller path",
  );
  return input;
}

async function bundle(root) {
  for (let path = root; ; path = resolve(path, "..")) {
    fail(
      !(await lstat(path)).isSymbolicLink(),
      "SOURCE_DRIFT",
      "Linked controller source root is not supported",
      409,
    );
    if (path === resolve(path, "..")) break;
  }
  const files = {};
  let bytes = 0;
  async function walk(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      if (
        ["tests", "__pycache__"].includes(entry.name) ||
        entry.name.startsWith("test_") ||
        /\.py[co]$/.test(entry.name)
      )
        continue;
      const path = join(directory, entry.name),
        st = await lstat(path);
      fail(
        !st.isSymbolicLink(),
        "SOURCE_DRIFT",
        "Linked controller source is not supported",
        409,
      );
      if (st.isDirectory()) await walk(path);
      else {
        fail(st.isFile(), "SOURCE_DRIFT", "Irregular controller source", 409);
        bytes += st.size;
        fail(
          bytes <= 64 * 1024 * 1024 && Object.keys(files).length < 5000,
          "SOURCE_DRIFT",
          "Controller source closure exceeds its limit",
          409,
        );
        files[relative(root, path).split("\\").join("/")] = sha(
          await readFile(path),
        );
      }
    }
  }
  await walk(root);
  fail(
    files["scripts/foundry.py"],
    "CAPABILITY_UNVERIFIED",
    "Foundry controller is not installed",
    409,
  );
  return { files, sha256: digest(files) };
}

async function statePin(session) {
  const path = join(session, ".agent-foundry/state.json");
  if (!(await exists(path)))
    return { sha256: "missing", revision: null, state: null };
  const source = await readSource(session, ".agent-foundry/state.json");
  const state = parseStrictJson(source.text);
  return { sha256: source.sha256, revision: state.revision, state };
}

function runNative(python, args, input, cwd, timeout) {
  return new Promise((resolveResult) => {
    const child = execFile(
      python,
      args,
      { cwd, env: runtimeEnvironment(), timeout, maxBuffer: 4 * 1024 * 1024, windowsHide: true },
      (error, stdout, stderr) => resolveResult({ error, stdout, stderr }),
    );
    child.stdin.on("error", () => {});
    child.stdin.end(input ?? "");
  });
}

export class NativeControllers {
  constructor({
    store,
    repoRoot,
    dataDir,
    projects,
    foundryRoot,
    python = pythonExecutable(),
    run = runNative,
    timeoutMs = 30000,
  }) {
    this.store = store;
    this.repoRoot = repoRoot;
    this.dataDir = dataDir;
    this.projects = projects;
    this.foundryRoot =
      foundryRoot ?? resolve(homedir(), ".agents/skills/agent-foundry");
    this.python = python;
    this.run = run;
    this.timeoutMs = timeoutMs;
    this.previews = new Map();
    for (const row of store.list("native-controller"))
      if (row.status === "pending")
        store.put("native-controller", row.id, {
          ...row,
          status: "outcome_unknown",
          reason:
            "Service restarted before a native controller receipt; reconcile before replay",
        });
  }
  clear() {
    this.previews.clear();
  }
  async preview(projectId, payload) {
    const project = await boundProject(this.projects, projectId);
    fail(
      (payload.controller ?? "foundry") === "foundry",
      "CAPABILITY_UNVERIFIED",
      "Only the source-bound Foundry controller adapter is available",
      409,
    );
    const operation = text(payload.operation, "operation");
    fail(
      ALLOWED.has(operation),
      "UNSUPPORTED_OPERATION",
      "Unsupported native controller operation",
    );
    const sessionRef = ref(payload.session_path ?? ".", "session_path", true);
    const session =
      sessionRef === "."
        ? project.root
        : await safeFile(project.root, sessionRef, {
            directory: true,
            allowMissing: operation === "init",
          });
    fail(
      isWithin(project.root, session),
      "OUTSIDE_ROOT",
      "Controller session must stay in the bound project",
    );
    const pin = await statePin(session);
    fail(
      operation === "init"
        ? pin.sha256 === "missing"
        : pin.sha256 !== "missing",
      "NATIVE_STATE_CONFLICT",
      operation === "init"
        ? "An existing session cannot be initialized again"
        : "Initialize or select a real Foundry session first",
      409,
    );
    const incomingParams = payload.params ?? {};
    fail(
      incomingParams &&
        typeof incomingParams === "object" &&
        !Array.isArray(incomingParams),
      "INVALID_INPUT",
      "params must be an object",
    );
    const params = { ...incomingParams };
    fail(
      Object.keys(params).every((k) => (PARAMS[operation] ?? []).includes(k)),
      "INVALID_INPUT",
      "Unknown parameter for this native operation",
    );
    const args = [operation, session];
    const add = (flag, value) => args.push(flag, text(value, flag, 1, 10000));
    const number = (flag, value) => {
      fail(
        Number.isSafeInteger(value) && value > 0,
        "INVALID_INPUT",
        `${flag} must be a positive integer`,
      );
      args.push(flag, String(value));
    };
    let record = null,
      recordSource = null;
    const nativeBlueprint = pin.state?.blueprint;
    const inlineOwnerApproval =
      operation === "approve" &&
      typeof payload.owner_approval_text === "string";
    if (inlineOwnerApproval) {
      fail(
        nativeBlueprint?.data && HASH.test(nativeBlueprint.sha256 ?? ""),
        "NATIVE_STATE_CONFLICT",
        "A registered native blueprint is required before approval",
        409,
      );
      fail(
        !pin.state.approval?.canonical_authority,
        "SCOPE_MISMATCH",
        "This project uses a bound canonical authority file; preserve and update that source through a reviewed record_path",
        409,
      );
      params.sha256 ??= nativeBlueprint.sha256;
      params.revision ??= nativeBlueprint.data.revision;
      params.scope ??= nativeBlueprint.data.scope;
      fail(
        params.sha256 === nativeBlueprint.sha256 &&
          params.revision === nativeBlueprint.data.revision &&
          params.scope === nativeBlueprint.data.scope,
        "REVISION_CONFLICT",
        "Approval must match the current native blueprint",
        409,
      );
      record = {
        actor: "user",
        source: "Agent Atelier authenticated owner review",
        verbatim: text(
          payload.owner_approval_text,
          "owner_approval_text",
          1,
          10000,
        ),
        scope: params.scope,
        decision: "approve",
      };
      const raw = JSON.stringify(record);
      fail(
        !containsObviousCredential(raw),
        "PRIVATE_PATH",
        "Do not place credentials in owner statements",
      );
      recordSource = {
        path: null,
        sha256: sha(raw),
        bytes: Buffer.byteLength(raw),
        text: raw,
      };
    }
    if (
      RECORD.has(operation) ||
      (operation === "refresh" && params.accept_suite_update === true)
    ) {
      fail(
        !Object.hasOwn(payload, "record"),
        "INVALID_INPUT",
        "Use a reviewable project record_path, not an anonymous inline record",
      );
      if (!inlineOwnerApproval) {
        const recordRef = ref(payload.record_path, "record_path");
        recordSource = await readSource(session, recordRef);
      }
      fail(
        recordSource.bytes <= 512 * 1024,
        "CAPACITY_LIMIT",
        "Controller record exceeds its review limit",
        409,
      );
      record = parseStrictJson(recordSource.text);
      fail(
        record && typeof record === "object" && !Array.isArray(record),
        "INVALID_INPUT",
        "Controller record must be an object",
      );
      fail(
        !containsObviousCredential(recordSource.text),
        "PRIVATE_PATH",
        "Do not place credentials in controller records",
      );
      // Native helpers also validate paths. Reject private path fields before
      // the trusted process can read them, including not-yet-created artifacts.
      const inspect = async (value, key = "") => {
        if (
          typeof value === "string" &&
          /(?:^path$|_path$|^directory$)/.test(key)
        ) {
          ref(value, key);
          await safeFile(session, value, {
            allowMissing: true,
            directory: key === "directory",
          });
        } else if (Array.isArray(value))
          for (const child of value) await inspect(child, key);
        else if (value && typeof value === "object")
          for (const [name, child] of Object.entries(value))
            await inspect(child, name);
      };
      await inspect(record);
      args.push("--record", "-");
    }
    if (operation === "init") {
      fail(
        /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(params.project_id ?? ""),
        "INVALID_INPUT",
        "Portable project_id required",
      );
      add("--project-id", params.project_id);
      fail(
        ["factory", "project"].includes(params.purpose ?? "factory"),
        "INVALID_INPUT",
        "Invalid Foundry purpose",
      );
      add("--purpose", params.purpose ?? "factory");
    }
    if (ID.has(operation)) add("--id", params.id);
    if (operation === "approve") {
      fail(
        HASH.test(params.sha256 ?? ""),
        "INVALID_INPUT",
        "Exact blueprint SHA256 required",
      );
      add("--sha256", params.sha256);
      number("--revision", params.revision);
      add("--scope", params.scope);
      fail(
        record.actor === "user" &&
          typeof record.verbatim === "string" &&
          record.verbatim.trim() &&
          record.scope === params.scope,
        "INVALID_INPUT",
        "Exact owner authority record is required for approval",
      );
    }
    if (operation === "blueprint" && params.change_authority_path) {
      const path = ref(params.change_authority_path, "change_authority_path");
      await readSource(session, path);
      add("--change-authority", resolve(session, path));
    }
    if (operation === "context" && params.query) add("--query", params.query);
    if (operation === "complete" && params.evidence) {
      fail(
        Array.isArray(params.evidence) && params.evidence.length <= 100,
        "INVALID_INPUT",
        "Bounded evidence ID array required",
      );
      for (const evidence of params.evidence) add("--evidence", evidence);
    }
    if (operation === "phase-check") {
      add("--scope", params.scope);
      add("--execution-id", params.execution_id);
    }
    if (operation === "dispatch") number("--revision", params.revision);
    if (operation === "receipt") {
      fail(
        ["succeeded", "failed", "unknown"].includes(params.outcome),
        "INVALID_INPUT",
        "Actual receipt outcome required",
      );
      add("--outcome", params.outcome);
    }
    if (operation === "bundle-check") {
      const path = ref(params.directory, "directory");
      await safeFile(session, path, { directory: true });
      add("--directory", resolve(session, path));
    }
    if (operation === "intake") {
      const path = ref(params.source, "source");
      await readSource(session, path);
      add("--source", resolve(session, path));
    }
    if (operation === "refresh" && params.accept_suite_update === true)
      args.push("--accept-suite-update");
    const closure = await bundle(this.foundryRoot);
    const wrapper = resolve(
      this.repoRoot,
      "apps/agent-atelier/server/foundry_cas.py",
    );
    const wrapperSha = sha(await readFile(wrapper));
    const platformSupport = resolve(this.repoRoot, "apps/agent-atelier/server/platform_support.py");
    const platformSupportSha = sha(await readFile(platformSupport));
    const preview = {
      preview_id: id("controller-preview"),
      project_id: projectId,
      root: project.root,
      controller: "foundry",
      operation,
      session_path: sessionRef,
      native_state_sha256: pin.sha256,
      native_revision: pin.revision,
      controller_source_sha256: closure.sha256,
      wrapper_sha256: wrapperSha,
      platform_support_sha256: platformSupportSha,
      record_path: recordSource?.path ?? null,
      record_sha256: recordSource?.sha256 ?? null,
      params,
      record: record ? redact(record) : null,
      argv: args,
      expires_at: Date.now() + 10 * 60 * 1000,
      subject: nativeBlueprint?.data
        ? {
            id: nativeBlueprint.data.id,
            goal: nativeBlueprint.data.goal,
            scope: nativeBlueprint.data.scope,
            revision: nativeBlueprint.data.revision,
            sha256: nativeBlueprint.sha256,
            entry_skill: nativeBlueprint.data.entry_skill,
            skills: nativeBlueprint.data.skills,
            components: nativeBlueprint.data.components,
          }
        : null,
      authority_epoch: this.store.get("settings", "owner").authority_epoch,
      effects: [
        "Source-pinned native Foundry state transition only; no model, provider, deployment or product runtime is executed",
      ],
      actual_native_guards_retained: true,
      child_filesystem_permission_expansion: false,
    };
    preview.sha256 = digest(preview);
    for (const [key, value] of this.previews)
      if (value.public.expires_at < Date.now()) this.previews.delete(key);
    fail(
      this.previews.size < 50,
      "CAPACITY_LIMIT",
      "Finish or let existing controller previews expire",
    );
    this.previews.set(preview.preview_id, {
      public: preview,
      session,
      args,
      input: recordSource?.text ?? "",
      closure,
      wrapper,
      platformSupport,
    });
    return preview;
  }
  async apply(projectId, payload) {
    const found = this.previews.get(payload.preview_id),
      p = found?.public;
    fail(
      found &&
        p.project_id === projectId &&
        p.expires_at > Date.now() &&
        payload.sha256 === p.sha256 &&
        payload.confirmed === true,
      "PREVIEW_REQUIRED",
      "Review the current exact controller preview before applying",
      409,
    );
    fail(
      p.authority_epoch === this.store.get("settings", "owner").authority_epoch,
      "SOURCE_DRIFT",
      "Service authority changed; prepare a fresh controller preview",
      409,
    );
    fail(
      (await boundProject(this.projects, projectId)).root === p.root,
      "SOURCE_DRIFT",
      "Project binding changed",
      409,
    );
    fail(
      !this.store
        .list("native-controller")
        .some(
          (r) =>
            ["pending", "outcome_unknown"].includes(r.status) &&
            (isWithin(r.root, p.root) || isWithin(p.root, r.root)),
        ),
      "OUTCOME_UNKNOWN",
      "Review and reconcile the unknown native operation before another mutation",
      409,
    );
    fail(
      (await statePin(found.session)).sha256 === p.native_state_sha256,
      "REVISION_CONFLICT",
      "Native state changed since preview",
      409,
    );
    fail(
      (await bundle(this.foundryRoot)).sha256 === p.controller_source_sha256 &&
        sha(await readFile(found.wrapper)) === p.wrapper_sha256,
      "SOURCE_DRIFT",
      "Controller source changed since preview",
      409,
    );
    if (p.record_path)
      fail(
        (await readSource(found.session, p.record_path)).sha256 ===
          p.record_sha256,
        "SOURCE_DRIFT",
        "Controller input record changed since preview",
        409,
      );
    const recordId = id("native-controller"),
      backupDir = join(this.dataDir, "controller-backups", recordId);
    const receipt = {
      id: recordId,
      project_id: projectId,
      root: p.root,
      session_path: p.session_path,
      operation: p.operation,
      status: "pending",
      preview_sha256: p.sha256,
      before_sha256: p.native_state_sha256,
      source_sha256: p.controller_source_sha256,
      wrapper_sha256: p.wrapper_sha256,
      platform_support_sha256: p.platform_support_sha256,
      phase: "staging",
      operation_guard: 1,
      backup_id: recordId,
      started_at: now(),
      owner_confirmed: true,
      executes_model_or_external_effect: false,
    };
    // Ownership precedes every retained copy, including interrupted staging.
    this.store.put("native-controller", recordId, receipt);
    this.previews.delete(payload.preview_id);
    const sourceRoot = join(backupDir, "source"),
      wrapper = join(backupDir, "foundry_cas.py");
    try {
      await mkdir(backupDir, { recursive: true, mode: 0o700 });
      if (p.native_state_sha256 !== "missing") {
        const before = await readFile(
          join(found.session, ".agent-foundry/state.json"),
        );
        fail(
          sha(before) === p.native_state_sha256,
          "REVISION_CONFLICT",
          "Native state changed before backup",
          409,
        );
        await atomicWrite(join(backupDir, "state.json"), before);
      }
      // Execute the entire reviewed closure, never a script next to mutable
      // normative references. Each copy is checked before and after staging.
      for (const [name, expected] of Object.entries(found.closure.files)) {
        const bytes = await readFile(join(this.foundryRoot, name));
        fail(
          sha(bytes) === expected,
          "SOURCE_DRIFT",
          "Controller source changed during staging",
          409,
        );
        await atomicWrite(join(sourceRoot, name), bytes);
        await chmod(join(sourceRoot, name), 0o400);
      }
      fail(
        (await bundle(sourceRoot)).sha256 === p.controller_source_sha256,
        "SOURCE_DRIFT",
        "Staged controller closure changed",
        409,
      );
      const wrapperBytes = await readFile(found.wrapper);
      fail(
        sha(wrapperBytes) === p.wrapper_sha256,
        "SOURCE_DRIFT",
        "Controller adapter changed during staging",
        409,
      );
      await atomicWrite(wrapper, wrapperBytes);
      const platformSupportBytes = await readFile(found.platformSupport);
      fail(sha(platformSupportBytes) === p.platform_support_sha256, "SOURCE_DRIFT", "Reviewed platform adapter changed during staging", 409);
      await atomicWrite(join(backupDir, "platform_support.py"), platformSupportBytes);
      await chmod(join(backupDir, "platform_support.py"), 0o400);
      await atomicWrite(
        join(backupDir, "closure.json"),
        JSON.stringify(found.closure.files),
      );
      await atomicWrite(join(backupDir, "operation.lock"), "");
      receipt.phase = "native_pending";
      this.store.put("native-controller", recordId, receipt);
    } catch (error) {
      this.store.put("native-controller", recordId, {
        ...receipt,
        status: "rejected",
        phase: "staging_failed",
        completed_at: now(),
        error: String(error.message),
        native_state_changed: false,
      });
      throw error;
    }
    const script = join(sourceRoot, "scripts/foundry.py");
    const args = [
      "-B",
      wrapper,
      "--operation-dir",
      backupDir,
      "--platform-support-sha256",
      p.platform_support_sha256,
      "--closure-sha256",
      p.controller_source_sha256,
      "--script",
      script,
      "--script-sha256",
      found.closure.files["scripts/foundry.py"],
      "--expected-state",
      p.native_state_sha256,
      "--",
      ...found.args,
    ];
    let result;
    try {
      result = await this.run(
        this.python,
        args,
        found.input,
        p.root,
        this.timeoutMs,
      );
    } catch (error) {
      result = { error, stdout: "", stderr: "" };
    }
    let after;
    try {
      after = await statePin(found.session);
    } catch {
      after = { sha256: "unreadable", revision: null };
    }
    let output = null;
    try {
      output = parseStrictJson(
        result.stdout || result.stderr || "{}",
        4 * 1024 * 1024,
      );
    } catch {
      output = {
        message: String(
          result.stderr || result.stdout || result.error?.message || "",
        ).slice(0, 10000),
      };
    }
    const unknown =
      after.sha256 === "unreadable" ||
      Boolean(
        result.error &&
        (result.error.killed ||
          result.error.signal ||
          typeof result.error.code !== "number"),
      );
    if (Buffer.byteLength(JSON.stringify(output)) > 512 * 1024) {
      const raw = JSON.stringify(redact(output));
      await atomicWrite(join(backupDir, "result.json"), raw);
      output = {
        truncated: true,
        sha256: sha(raw),
        bytes: Buffer.byteLength(raw),
        local_receipt: join("controller-backups", recordId, "result.json"),
      };
    }
    const final = {
      ...receipt,
      phase: "observed",
      status: unknown
        ? "outcome_unknown"
        : result.error
          ? "rejected"
          : "completed",
      after_sha256: after.sha256,
      native_revision: after.revision,
      completed_at: now(),
      result: redact(output),
      native_state_changed: after.sha256 !== p.native_state_sha256,
      next_action: unknown
        ? "Read current native state and reconcile; do not repeat the operation"
        : "Refresh native source and verify the specific gate; this receipt is not model execution or product acceptance",
    };
    this.store.put("native-controller", recordId, final);
    return final;
  }
  async reconcile(projectId, payload) {
    const receipt = this.store.get(
      "native-controller",
      text(payload.receipt_id, "receipt_id"),
    );
    fail(
      receipt?.project_id === projectId && receipt.status === "outcome_unknown",
      "INVALID_INPUT",
      "Unknown native controller receipt required",
    );
    const root = (await boundProject(this.projects, projectId)).root;
    fail(root === receipt.root, "SOURCE_DRIFT", "Project binding changed", 409);
    fail(
      receipt.operation_guard === 1,
      "OUTCOME_UNKNOWN",
      "Legacy operation has no lifecycle guard; independently establish that its writer stopped before resolving it",
      409,
    );
    // Durable staging precedes every subprocess launch. A restart here has
    // no orphan native writer and may not yet have an adapter or lease file.
    if (receipt.phase !== "staging") {
      const directory = join(this.dataDir, "controller-backups", receipt.id),
        wrapper = join(directory, "foundry_cas.py");
      fail(
        sha(await readFile(wrapper)) === receipt.wrapper_sha256,
        "SOURCE_DRIFT",
        "The recorded lifecycle adapter changed",
        409,
      );
      if (receipt.platform_support_sha256) fail(sha(await readFile(join(directory, "platform_support.py"))) === receipt.platform_support_sha256, "SOURCE_DRIFT", "Recorded platform adapter changed", 409);
      // A current-state observation alone cannot exclude an orphaned child still
      // waiting on the native lock. Revoke under the same operation flock that
      // the child holds throughout its entire native invocation.
      const guard = await runNative(
        this.python,
        [
          "-B",
          wrapper,
          "--operation-dir",
          directory,
          ...(receipt.platform_support_sha256 ? ["--platform-support-sha256", receipt.platform_support_sha256] : []),
          payload.confirmed === true ? "--revoke" : "--inspect",
        ],
        "",
        root,
        this.timeoutMs,
      );
      fail(
        !guard.error,
        "WRITER_CONFLICT",
        "The previous native writer is still active or its lifecycle cannot be established; wait and reconcile again",
        409,
      );
    }
    const session =
      receipt.session_path === "."
        ? root
        : await safeFile(root, receipt.session_path, {
            directory: true,
            allowMissing: receipt.operation === "init",
          });
    const pin = await statePin(session);
    const view = {
      receipt_id: receipt.id,
      current_sha256: pin.sha256,
      current_revision: pin.revision,
      result:
        "Current native state observed; original outcome is not automatically certified",
      operation: receipt.operation,
    };
    view.sha256 = digest(view);
    if (payload.confirmed !== true) return view;
    fail(
      payload.sha256 === view.sha256,
      "REVISION_CONFLICT",
      "Review the current native state before resolving the unknown operation",
      409,
    );
    const final = {
      ...receipt,
      status: "reconciled_unclassified",
      reconciled_at: now(),
      reconciliation: view,
      automatic_replay: false,
    };
    this.store.put("native-controller", receipt.id, final);
    return final;
  }
}
