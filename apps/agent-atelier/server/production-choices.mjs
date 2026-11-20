import { execFile } from "node:child_process";
import { lstat, realpath } from "node:fs/promises";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { runtimeEnvironment } from "./environment.mjs";
import { writablePaths } from "./permissions.mjs";
import { resolvePythonCommand } from "./platform.mjs";
import { fail, isWithin, readSource, safeFile } from "./utils.mjs";

const run = promisify(execFile);
const verifier = fileURLToPath(new URL("./production_choices.py", import.meta.url));
const record = "production-choices.json";
const phases = new Set(["explore", "implement", "scale", "accept"]);
const hash = /^[a-f0-9]{64}$/;
const experiment = "experiments/production-choices";

async function hasProjectRecord(root) {
  try {
    await lstat(join(root, record));
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    fail(false, "PRODUCTION_CHOICE_REQUIRED", "Cannot inspect the project production choice record", 409);
  }
}

async function verify(root, phase, expected) {
  const env = runtimeEnvironment(process.env);
  let stdout;
  try {
    const python = await resolvePythonCommand(env);
    ({ stdout } = await run(
      python.command,
      [...python.args, "-I", "-X", "utf8", "-B", verifier, "verify", root,
        "--phase", phase, ...(expected ? ["--expected-sha256", expected] : [])],
      { env, timeout: 15000, maxBuffer: 256 * 1024, windowsHide: true },
    ));
  } catch (error) {
    let reason;
    try { reason = JSON.parse(error.stdout).error; } catch {}
    fail(false, "PRODUCTION_CHOICE_REQUIRED",
      typeof reason === "string" ? reason.slice(0, 400)
        : "Production choice verification did not run. Check the project record and installed toolkit.",
      409);
  }
  let checked;
  try { checked = JSON.parse(stdout); } catch {}
  fail(checked?.ok === true && checked.phase === phase &&
    hash.test(checked.record_sha256) && (!expected || checked.record_sha256 === expected),
    "PRODUCTION_CHOICE_REQUIRED", "The project choice verifier did not return an exact admitted record", 409);
  return {
    path: record, phase, sha256: checked.record_sha256,
    decision_sha256: checked.decision_sha256 ?? null,
  };
}

export async function prepareProductionChoice(root, payload, { legacyProject = false } = {}) {
  const phase = payload.production_phase;
  fail(phase === undefined || phase === "repair" || phases.has(phase),
    "INVALID_INPUT", "Unsupported production phase");
  const exists = await hasProjectRecord(root);
  const writable = payload.scope === "workspace-write";
  if (!exists && phase === "repair" && legacyProject && writable)
    return { phase: "repair", legacy: true };
  if (!exists && phase === undefined && !writable) return null;
  const chosen = phase === "repair" ? "implement" : phase ?? (writable ? "implement" : "explore");
  if (chosen === "explore" && writable) {
    const paths = payload.allowed_paths;
    // Exploration may author a disposable slice, but cannot use its provisional
    // choice to write to the established product source.
    fail(Array.isArray(paths) && paths.length > 0 && paths.every(path =>
      typeof path === "string" && !path.includes("\\") &&
      path.split("/").every(segment => segment && segment !== ".." && segment !== ".") &&
      (path === experiment || path.startsWith(experiment + "/"))),
    "PRODUCTION_CHOICE_REQUIRED", "Writable exploration is limited to experiments/production-choices", 409);
  }
  return verify(root, chosen);
}

export function requirePreparedProductionChoice(scope, binding) {
  fail(binding || scope === "read-only", "PRODUCTION_CHOICE_REQUIRED",
    "This writable task has no bound production choice. Keep its history and prepare a new task with the current choice or an eligible bounded legacy repair.", 409);
}

async function verifyLegacyRepair(root, capsule) {
  const allowed = capsule?.allowed_paths;
  const scopeMessage = "A legacy repair needs explicit writable directories below the project root. Prepare again with the affected directories or use an approved production choice.";
  fail(capsule?.scope === "workspace-write" && Array.isArray(allowed) && allowed.length > 0,
    "PRODUCTION_CHOICE_REQUIRED", scopeMessage, 409);
  const paths = writablePaths(allowed);
  fail(!paths.includes("."), "PRODUCTION_CHOICE_REQUIRED", scopeMessage, 409);
  const directories = [];
  for (const path of paths) {
    try {
      const directory = await realpath(await safeFile(root, path, { directory: true }));
      fail(directory !== root && isWithin(root, directory),
        "PRODUCTION_CHOICE_REQUIRED", scopeMessage, 409);
      directories.push(directory);
    } catch (error) {
      if (error.code === "ENOENT" || error.code === "INVALID_PATH")
        fail(false, "SOURCE_DRIFT", `Legacy repair directory changed: ${path}. Review the writable scope and prepare again.`, 409);
      throw error;
    }
  }
  const outsideWriteScope = (path) => !directories.some((dir) => isWithin(dir, path));
  const instruction = capsule.instruction_manifest?.sources?.some((pin) =>
    pin.scope === "project" && pin.present && pin.nonempty && hash.test(pin.sha256) &&
    outsideWriteScope(pin.path));
  if (instruction) return;
  for (const pin of capsule.original_sources ?? []) {
    if (pin.kind === "task-source" || !pin.bytes || !hash.test(pin.sha256)) continue;
    const actual = await readSource(root, pin.path);
    if (!outsideWriteScope(await realpath(resolve(root, pin.path)))) continue;
    fail(actual.sha256 === pin.sha256, "SOURCE_DRIFT",
      "The governing source changed after preparation. Review it and prepare the legacy repair again.", 409);
    return;
  }
  fail(false, "PRODUCTION_CHOICE_REQUIRED",
    "A legacy repair needs a pinned governing project source outside its writable directories. Review project instructions or bind the current production choice before preparing again.", 409);
}

export async function verifyPreparedProductionChoice(root, binding, { legacyProject = false, capsule } = {}) {
  requirePreparedProductionChoice(capsule?.scope, binding);
  if (binding?.phase === "repair" && binding.legacy === true) {
    fail(legacyProject && !await hasProjectRecord(root), "SOURCE_DRIFT",
      "The legacy repair no longer applies. Prepare again using the current project choice.", 409);
    await verifyLegacyRepair(root, capsule);
    return;
  }
  if (!binding) {
    fail(!await hasProjectRecord(root), "SOURCE_DRIFT",
      "A production choice record appeared after preparation. Prepare again to bind it.", 409);
    return;
  }
  fail(binding.path === record && phases.has(binding.phase) && hash.test(binding.sha256),
    "TASK_NOT_READY", "Prepare a fresh task with the current production choice bindings", 409);
  const actual = await verify(root, binding.phase, binding.sha256);
  fail(actual.decision_sha256 === binding.decision_sha256, "SOURCE_DRIFT",
    "The approved production choice changed. Prepare and review the task again.", 409);
}
