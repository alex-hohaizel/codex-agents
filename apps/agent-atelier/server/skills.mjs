import {
  readFile,
  readdir,
  mkdir,
  realpath,
  lstat,
  writeFile,
  chmod,
} from "node:fs/promises";
import { resolve, join, dirname } from "node:path";
import { homedir, tmpdir } from "node:os";
import { assertPrivatePath, securePrivatePath, pythonExecutable } from "./platform.mjs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
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
  sha,
  text,
  ServiceError,
} from "./utils.mjs";
import { skillVersion } from "./skill_version.mjs";
const run = promisify(execFile);
const transportSchema = "atelier.execution-input-transport/1";
const taskIdentifier = (value) =>
  typeof value === "string" && /^[A-Za-z0-9_-]{1,180}$/.test(value);
const inputPath = (value) =>
  typeof value === "string" &&
  value.length <= 4096 &&
  !value.includes("\0") &&
  !value.includes("\\") &&
  !value.startsWith("/") &&
  value.split("/").every((part) => part && ![".", ".."].includes(part));

export function executionInputPaths(dataDir, taskId) {
  fail(
    taskIdentifier(taskId),
    "INVALID_INPUT",
    "Invalid execution-input task identity",
  );
  const canonicalDataDir = resolve(dataDir);
  const namespace = join(
    dirname(canonicalDataDir),
    "AgentAtelierExecutionInputs-" + sha(canonicalDataDir).slice(0, 24),
  );
  return { namespace, taskRoot: join(namespace, taskId) };
}

async function plainDirectory(path, owned = false) {
  const stat = await lstat(path);
  fail(
    stat.isDirectory() &&
      !stat.isSymbolicLink() &&
      (await realpath(path)) === path,
    "SOURCE_DRIFT",
    "Execution-input directory identity changed; prepare again",
    409,
  );
  if (owned) {
    try { await assertPrivatePath(path, { directory: true }); }
    catch { fail(false, "SOURCE_DRIFT", "Execution-input directory privacy changed; prepare again", 409); }
  }
}

async function ownedDirectories(base, relative) {
  await plainDirectory(base);
  let current = base;
  for (const part of relative.split("/").filter(Boolean)) {
    fail(
      ![".", ".."].includes(part),
      "SOURCE_DRIFT",
      "Invalid owned input directory",
      409,
    );
    current = join(current, part);
    let created = false;
    try {
      await mkdir(current, { mode: 0o700 });
      created = true;
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
    }
    if (created) await securePrivatePath(current, { directory: true });
    await plainDirectory(current, true);
  }
  return current;
}

export async function executionInputLocation(
  dataDir,
  taskId,
  nativeHome = process.env.CODEX_HOME ?? join(homedir(), ".codex"),
) {
  const { namespace, taskRoot } = executionInputPaths(dataDir, taskId);
  dataDir = resolve(dataDir);
  await plainDirectory(dataDir);
  await plainDirectory(dirname(namespace));
  fail(
    !/[?*\[\]{}\\\0]/.test(process.platform === "win32" ? namespace.replaceAll("\\", "/") : namespace),
    "CAPABILITY_UNVERIFIED",
    "Execution-input namespace cannot be represented by the supported native permission parser",
    409,
  );
  nativeHome = resolve(nativeHome);
  const denied = [
    dataDir,
    join(nativeHome, "memories"),
    join(nativeHome, "memories_v2"),
  ];
  for (const path of [...denied]) {
    try {
      denied.push(await realpath(path));
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
      try {
        await lstat(path);
      } catch (missing) {
        if (missing.code === "ENOENT") continue;
        throw missing;
      }
      throw new ServiceError(
        "CAPABILITY_UNVERIFIED",
        "A dangling native memory-store link prevents a safe execution-input namespace",
        409,
      );
    }
  }
  fail(
    denied.every(
      (path) => !isWithin(path, namespace) && !isWithin(namespace, path),
    ),
    "CAPABILITY_UNVERIFIED",
    "Execution inputs must be separate from service control and native memory stores",
    409,
  );
  return {
    namespace,
    taskRoot,
    namespaceOwner: {
      schema_version: transportSchema,
      data_dir_sha256: sha(dataDir),
    },
  };
}

async function ownerFile(path, expected) {
  const stat = await lstat(path);
  fail(
    stat.isFile() &&
      !stat.isSymbolicLink() &&
      (await realpath(path)) === path &&
      (stat.mode & 0o222) === 0 &&
      stat.size <= 32 * 1024 * 1024,
    "SOURCE_DRIFT",
    "Execution-input ownership file changed",
    409,
  );
  const bytes = await readFile(path);
  const owner = parseStrictJson(bytes.toString(), 32 * 1024 * 1024);
  fail(
    owner &&
      typeof owner === "object" &&
      !Array.isArray(owner) &&
      digest(owner) === expected,
    "SOURCE_DRIFT",
    "Execution-input ownership binding changed",
    409,
  );
  return owner;
}

/** Only a deterministic namespace and the original task-binding hash can own cleanup. */
export async function verifyExecutionInputTask(dataDir, taskId, binding) {
  fail(
    typeof binding === "string" && /^[a-f0-9]{64}$/.test(binding),
    "SOURCE_DRIFT",
    "Execution-input task has no exact ownership binding",
    409,
  );
  const location = await executionInputLocation(dataDir, taskId);
  await plainDirectory(location.namespace, true);
  await ownerFile(
    join(location.namespace, "OWNERSHIP.json"),
    digest(location.namespaceOwner),
  );
  await plainDirectory(location.taskRoot, true);
  const owner = await ownerFile(join(location.taskRoot, "TASK.json"), binding);
  fail(
    owner.schema_version === transportSchema &&
      owner.task_id === taskId &&
      owner.data_dir_sha256 === sha(resolve(dataDir)) &&
      Array.isArray(owner.selections) &&
      owner.selections.length > 0 &&
      owner.selections.length <= 4 &&
      new Set(owner.selections.map((entry) => entry.directory_name)).size ===
        owner.selections.length &&
      owner.selections.every(
        (entry) =>
          /^[a-z0-9][a-z0-9-]{1,100}$/.test(entry.directory_name) &&
          typeof entry.source_locator === "string" &&
          /^[a-f0-9]{64}$/.test(entry.source_tree_sha256) &&
          Array.isArray(entry.manifest) &&
          entry.manifest.length <= 5000 &&
          entry.manifest.every(
            (row) =>
              inputPath(row.path) &&
              Number.isSafeInteger(row.bytes) &&
              row.bytes >= 0 &&
              /^[a-f0-9]{64}$/.test(row.sha256),
          ) &&
          digest(entry.manifest) === entry.source_tree_sha256,
      ),
    "SOURCE_DRIFT",
    "Invalid execution-input task ownership",
    409,
  );
  const members = owner.selections.flatMap((entry) =>
    entry.manifest.map((row) => ({
      ...row,
      path: "skills/" + entry.directory_name + "/" + row.path,
    })),
  );
  const taskBytes = await readFile(join(location.taskRoot, "TASK.json"));
  members.push({
    path: "TASK.json",
    bytes: taskBytes.length,
    sha256: sha(taskBytes),
  });
  await selectedInputTree(location.taskRoot, { exactManifest: members });
  return { ...location, owner };
}

export async function selectedInputTree(root, { exactManifest = null } = {}) {
  await plainDirectory(root, exactManifest !== null);
  const expected =
    exactManifest && new Map(exactManifest.map((row) => [row.path, row]));
  const expectedDirs = new Set();
  for (const row of exactManifest ?? []) {
    fail(
      inputPath(row.path),
      "SOURCE_DRIFT",
      "Invalid execution-input member path",
      409,
    );
    const parts = row.path.split("/");
    for (let index = 1; index < parts.length; index++)
      expectedDirs.add(parts.slice(0, index).join("/"));
  }
  const manifest = [];
  let total = 0;
  const visit = async (folder, prefix = "") => {
    for (const entry of (await readdir(folder, { withFileTypes: true })).sort(
      (a, b) => (a.name < b.name ? -1 : 1),
    )) {
      if (
        !expected &&
        ["__pycache__", ".DS_Store", ".git", "node_modules"].includes(
          entry.name,
        )
      )
        continue;
      fail(
        !entry.isSymbolicLink(),
        "SOURCE_DRIFT",
        "Linked skill input is unsupported",
        409,
      );
      const path = join(folder, entry.name),
        ref = prefix ? prefix + "/" + entry.name : entry.name;
      if (entry.isDirectory()) {
        fail(
          !expected || expectedDirs.has(ref),
          "SOURCE_DRIFT",
          "Unexpected execution-input directory",
          409,
        );
        await plainDirectory(path, exactManifest !== null);
        await visit(path, ref);
      } else {
        fail(
          entry.isFile(),
          "SOURCE_DRIFT",
          "Special skill input is unsupported",
          409,
        );
        const stat = await lstat(path);
        total += stat.size;
        fail(
          manifest.length < (expected ? 20_001 : 5000) &&
            total < (expected ? 288 : 64) * 1024 * 1024,
          "CAPACITY_LIMIT",
          "Selected skill input exceeds bounded snapshot size",
          409,
        );
        const bytes = await readFile(path);
        fail(
          bytes.length === stat.size,
          "SOURCE_DRIFT",
          "Skill input changed while reading",
          409,
        );
        const row = { path: ref, bytes: bytes.length, sha256: sha(bytes) };
        fail(
          !expected ||
            (expected.has(ref) &&
              digest(row) === digest(expected.get(ref)) &&
              (stat.mode & 0o222) === 0),
          "SOURCE_DRIFT",
          "Execution-input bytes, membership or read-only mode changed",
          409,
        );
        manifest.push(row);
      }
    }
  };
  await visit(root);
  fail(
    !expected || manifest.length === expected.size,
    "SOURCE_DRIFT",
    "Execution input is missing approved members; prepare again",
    409,
  );
  return { manifest, tree_sha256: digest(manifest), bytes: total };
}

async function copyApprovedInput(sourceRoot, targetRoot, manifest) {
  await mkdir(targetRoot, { mode: 0o700 });
  await securePrivatePath(targetRoot, { directory: true });
  await plainDirectory(targetRoot);
  for (const row of manifest) {
    fail(
      inputPath(row.path),
      "SOURCE_DRIFT",
      "Invalid approved skill member",
      409,
    );
    const source = join(sourceRoot, row.path);
    const stat = await lstat(source);
    fail(
      stat.isFile() &&
        !stat.isSymbolicLink() &&
        (await realpath(source)) === source,
      "SOURCE_DRIFT",
      "Approved skill member identity changed",
      409,
    );
    const bytes = await readFile(source);
    fail(
      bytes.length === row.bytes && sha(bytes) === row.sha256,
      "SOURCE_DRIFT",
      "Approved skill member changed while copying",
      409,
    );
    const destination = join(targetRoot, row.path);
    const parent = row.path.split("/").slice(0, -1).join("/");
    await ownedDirectories(targetRoot, parent);
    await writeFile(destination, bytes, { flag: "wx", mode: 0o400 });
    await chmod(destination, 0o400);
  }
  await selectedInputTree(targetRoot, { exactManifest: manifest });
}
export async function readInstalledSource(root, name) {
  fail(
    /^[a-z0-9][a-z0-9-]{1,100}$/.test(name),
    "INVALID_INPUT",
    "Invalid stable skill name",
  );
  if (!(await exists(root)) || !(await exists(join(root, name, "SKILL.md"))))
    return null;
  fail(
    (await realpath(root)) === root,
    "SOURCE_DRIFT",
    "Linked installed root requires explicit identity review",
    409,
  );
  return readSource(root, name + "/SKILL.md");
}
export class SkillsManager {
  constructor({ store, repoRoot, dataDir }) {
    this.store = store;
    this.repoRoot = repoRoot;
    this.dataDir = dataDir;
    this.busy = false;
    this.hostSources = new Map();
  }
  async list(query = "") {
    const names = [];
    const root = resolve(this.repoRoot, "kit/skills");
    for (const entry of await readdir(root, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      try {
        const source = await readSource(root, `${entry.name}/SKILL.md`);
        const description =
          /^description:\s*(.+)$/m
            .exec(source.text)?.[1]
            ?.replace(/^"|"$/g, "") ?? "";
        let installedSource = null,
          installationError = null;
        try {
          installedSource = await readInstalledSource(
            resolve(homedir(), ".agents/skills"),
            entry.name,
          );
        } catch (error) {
          installationError = error.code ?? "READ_FAILED";
        }
        const installedBytes = installedSource?.text ?? null;
        names.push({
          name: entry.name,
          description,
          version: skillVersion(source.text),
          source_sha256: source.sha256,
          installed_sha256: installedBytes ? sha(installedBytes) : null,
          source_status: "canonical_source_read",
          managed_by: "core-suite",
          update_supported: true,
          execution_supported: true,
          source_id: entry.name,
          installation_status: installationError
            ? "blocked_source"
            : installedBytes
              ? sha(installedBytes) === source.sha256
                ? "primary_matches"
                : "primary_differs"
              : "not_found",
          installation_error: installationError,
          discovery_status: "unverified",
          path: `kit/skills/${entry.name}/SKILL.md`,
        });
      } catch (error) {
        names.push({
          name: entry.name,
          source_status: "unavailable",
          error: error.code ?? "READ_FAILED",
        });
      }
    }
    for (const [name, folder] of [
      ["atelier-orchestrator", "optional-skills/atelier-orchestrator"],
      ["codex-agents-maintenance", "maintenance-skill"],
    ]) {
      try {
        const source = await readSource(this.repoRoot, folder + "/SKILL.md");
        names.push({
          name,
          source_id: name,
          description: /^description:\s*(.+)$/m.exec(source.text)?.[1] ?? "",
          version: skillVersion(source.text),
          source_sha256: source.sha256,
          source_status: "canonical_source_read",
          installation_status: "unverified",
          discovery_status: "unverified",
          managed_by: "optional",
          update_supported: false,
          execution_supported: true,
          path: folder + "/SKILL.md",
        });
      } catch {}
    }
    for (const entry of this.hostSources.values()) {
      const matching = names.find(
        (row) =>
          row.name === entry.name && row.source_sha256 === entry.source_sha256,
      );
      if (matching) {
        matching.discovery_status = entry.discovery_status;
        matching.host_source_id = entry.source_id;
        matching.host_source_path = entry.path;
        matching.host_enabled = entry.enabled;
        continue;
      }
      names.push(entry);
    }
    const roles = [
      "architecture",
      "backend",
      "conversation",
      "cost",
      "integrations",
      "judge",
      "platform",
      "privacy",
      "product",
      "qa",
      "reliability",
      "skeptic",
    ];
    for (const role of roles) {
      const name = "foundry-" + role;
      try {
        const source = await readSource(
          resolve(homedir(), ".codex/agents"),
          name + ".toml",
        );
        names.push({
          name,
          source_id: "role:" + name,
          description:
            /^description\s*=\s*"([^"]+)"/m.exec(source.text)?.[1] ?? "",
          version: "host-config",
          source_sha256: source.sha256,
          source_status: "host_profile_source_present",
          installation_status: "source_present",
          discovery_status: "runtime_unverified",
          managed_by: "role-profile",
          update_supported: false,
          execution_supported: false,
          scope: "Source config presence is not an actual role invocation",
        });
      } catch {}
    }
    const search = text(String(query || " "), "query", 0, 200).toLowerCase();
    return {
      entries: names.filter(
        (x) =>
          !search ||
          `${x.name} ${x.description}`.toLowerCase().includes(search),
      ),
      summary: {
        canonical: names.filter((row) => row.managed_by === "core-suite")
          .length,
        optional: names.filter((row) => row.managed_by === "optional").length,
        host_discovered: names.filter((row) => row.managed_by === "host-source")
          .length,
        role_profiles: names.filter((row) => row.managed_by === "role-profile")
          .length,
        primary_matches: names.filter(
          (x) => x.installation_status === "primary_matches",
        ).length,
        primary_differs: names.filter(
          (x) => x.installation_status === "primary_differs",
        ).length,
        not_found: names.filter((x) => x.installation_status === "not_found")
          .length,
      },
      scope:
        "Primary SKILL source comparison; full-tree installation and live discovery are separate checks",
      work_status: "deferred_to_separate_task",
    };
  }
  async adoptHostCatalog(rows, projectRoots = []) {
    const allowed = [
      resolve(homedir(), ".agents/skills"),
      resolve(homedir(), ".codex/skills"),
      resolve(homedir(), ".codex/plugins/cache"),
      ...projectRoots.map((root) => resolve(root, ".agents/skills")),
    ];
    const discovered = new Map();
    for (const row of rows) {
      if (typeof row.path !== "string" || typeof row.name !== "string")
        continue;
      const path = resolve(row.path);
      const approvedRoot = allowed.find((root) => path.startsWith(root + "/"));
      const source_id = "host:" + sha(path).slice(0, 16);
      let source = null;
      if (approvedRoot && path.endsWith("/SKILL.md"))
        try {
          fail(
            (await realpath(approvedRoot)) === approvedRoot,
            "SOURCE_DRIFT",
            "Linked host source root requires explicit identity review",
            409,
          );
          source = await readSource(
            approvedRoot,
            path.slice(approvedRoot.length + 1),
          );
        } catch {}
      const externalDependency =
        path.startsWith(resolve(homedir(), ".codex/plugins/cache") + "/") ||
        /mcp__|plugin:\/\/|skills\.read|image_gen|imagegen\.imagegen|cua\.get/.test(
          source?.text ?? "",
        );
      const executionReason =
        row.enabled === false
          ? "The supported host reports this source disabled"
          : !source
            ? "The source is outside approved roots or cannot be read safely"
            : externalDependency
              ? "This source requires external plugin/media/tool capabilities that have not been verified on the restricted local executor; continue in a capable reviewed Codex host"
              : null;
      discovered.set(source_id, {
        name: row.name,
        source_id,
        description: row.description ?? "",
        version: source ? skillVersion(source.text, "host-source") : "unknown",
        source_sha256: source?.sha256 ?? null,
        source_status: source
          ? "host_discovered_source_read"
          : "host_catalog_only",
        discovery_status:
          row.enabled === false ? "host_disabled" : "host_discovered",
        installation_status: "host_source_present",
        managed_by: "host-source",
        update_supported: false,
        execution_supported:
          !!source && row.enabled !== false && !externalDependency,
        execution_reason: executionReason,
        required_capability_route: externalDependency
          ? "capable_reviewed_codex_host"
          : "local_cli_self_contained",
        path: row.path,
        source_path: source ? path : null,
        scope: row.scope,
        enabled: row.enabled,
      });
    }
    this.hostSources = discovered;
    return {
      host_discovered: discovered.size,
      scope: "Actual skills/list rows only, not all cache versions",
    };
  }
  skillRoot(name, { execution = false } = {}) {
    if (this.hostSources.has(name)) {
      const source = this.hostSources.get(name);
      fail(
        source.source_path && (!execution || source.execution_supported),
        "CAPABILITY_UNVERIFIED",
        source.execution_reason ??
          "Selected host source cannot be read through an approved root",
        409,
      );
      return dirname(source.source_path);
    }
    fail(
      /^[a-z0-9][a-z0-9-]{1,100}$/.test(name),
      "INVALID_INPUT",
      "Invalid stable skill name",
    );
    if (name === "atelier-orchestrator")
      return resolve(this.repoRoot, "optional-skills/atelier-orchestrator");
    if (name === "codex-agents-maintenance")
      return resolve(this.repoRoot, "maintenance-skill");
    return resolve(this.repoRoot, "kit/skills", name);
  }
  async tree(root) {
    return selectedInputTree(root);
  }
  async selections(names, taskId) {
    fail(
      Array.isArray(names) &&
        names.length <= 4 &&
        new Set(names).size === names.length,
      "INVALID_INPUT",
      "Select at most four distinct competencies",
    );
    fail(
      taskIdentifier(taskId),
      "INVALID_INPUT",
      "Invalid selected-input task identity",
    );
    if (!names.length) return [];
    const plans = [];
    for (const name of names) {
      const sourceRoot = this.skillRoot(name, { execution: true });
      fail(
        await exists(join(sourceRoot, "SKILL.md")),
        "CAPABILITY_UNVERIFIED",
        "Selected skill source is unavailable",
        409,
      );
      const before = await this.tree(sourceRoot);
      plans.push({
        selection_id: name,
        name: this.hostSources.get(name)?.name ?? name,
        directory_name: this.hostSources.has(name)
          ? "host-" + sha(name).slice(0, 16)
          : name,
        source_locator: sourceRoot,
        source_tree_sha256: before.tree_sha256,
        manifest: before.manifest,
      });
    }
    const location = await executionInputLocation(this.dataDir, taskId);
    let createdNamespace = false;
    try {
      await mkdir(location.namespace, { mode: 0o700 });
      createdNamespace = true;
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
    }
    if (createdNamespace) await securePrivatePath(location.namespace, { directory: true });
    await plainDirectory(location.namespace, true);
    const namespaceFile = join(location.namespace, "OWNERSHIP.json");
    if (createdNamespace) {
      await writeFile(namespaceFile, JSON.stringify(location.namespaceOwner), { flag: "wx", mode: 0o400 });
      await chmod(namespaceFile, 0o400);
    }
    await ownerFile(namespaceFile, digest(location.namespaceOwner));
    // Never adopt or overwrite a partial/replaced task namespace.
    await mkdir(location.taskRoot, { mode: 0o700 });
    await securePrivatePath(location.taskRoot, { directory: true });
    await mkdir(join(location.taskRoot, "skills"), { mode: 0o700 });
    await securePrivatePath(join(location.taskRoot, "skills"), { directory: true });
    const owner = {
      schema_version: transportSchema,
      data_dir_sha256: sha(resolve(this.dataDir)),
      task_id: taskId,
      selections: plans,
    };
    const binding = digest(owner);
    await writeFile(
      join(location.taskRoot, "TASK.json"),
      JSON.stringify(owner),
      { flag: "wx", mode: 0o400 },
    );
    await chmod(join(location.taskRoot, "TASK.json"), 0o400);
    const result = [];
    for (const plan of plans) {
      const archiveRoot = join(
        this.dataDir,
        "task-inputs",
        taskId,
        "skills",
        plan.directory_name,
      );
      await ownedDirectories(
        resolve(this.dataDir),
        "task-inputs/" + taskId + "/skills",
      );
      const snapshotRoot = join(
        location.taskRoot,
        "skills",
        plan.directory_name,
      );
      await copyApprovedInput(plan.source_locator, archiveRoot, plan.manifest);
      await copyApprovedInput(plan.source_locator, snapshotRoot, plan.manifest);
      fail(
        (await this.tree(plan.source_locator)).tree_sha256 ===
          plan.source_tree_sha256,
        "SOURCE_DRIFT",
        "Skill source changed during snapshot; prepare again",
        409,
      );
      result.push({
        name: plan.name,
        selection_id: plan.selection_id,
        source_locator: plan.source_locator,
        source_tree_sha256: plan.source_tree_sha256,
        archive_root: archiveRoot,
        snapshot_root: snapshotRoot,
        path: join(snapshotRoot, "SKILL.md"),
        sha256: plan.manifest.find((row) => row.path === "SKILL.md").sha256,
        manifest: plan.manifest,
        execution_transport: {
          schema_version: transportSchema,
          task_id: taskId,
          data_dir_sha256: sha(resolve(this.dataDir)),
          task_binding_sha256: binding,
          namespace_owner_sha256: digest(location.namespaceOwner),
          directory_name: plan.directory_name,
        },
        delivery_fact:
          "Pinned execution-only input copy; private control archive retained separately, not a personal-skill installation or file-backup receipt",
      });
    }
    await this.verifySelections(result, taskId);
    return result;
  }
  async verifySelections(selections, expectedTaskId = undefined) {
    const supplied = selections ?? [];
    fail(
      Array.isArray(supplied),
      "INVALID_INPUT",
      "Selected inputs must be an array",
    );
    if (expectedTaskId !== undefined) {
      fail(
        taskIdentifier(expectedTaskId),
        "INVALID_INPUT",
        "Invalid execution-input task identity",
      );
      const ownerPath = join(
        executionInputPaths(this.dataDir, expectedTaskId).taskRoot,
        "TASK.json",
      );
      let hasTaskBinding = false;
      try {
        await lstat(ownerPath);
        hasTaskBinding = true;
      } catch (error) {
        if (error.code !== "ENOENT") throw error;
      }
      // Once a task owns the new transport, an empty or stripped supplied set
      // cannot silently opt that task back into the historical verifier.
      fail(
        !hasTaskBinding ||
          (supplied.length > 0 &&
            supplied.every(
              (entry) =>
                entry?.execution_transport?.schema_version ===
                  transportSchema &&
                entry.execution_transport.task_id === expectedTaskId,
            )),
        "SOURCE_DRIFT",
        "The existing task binding requires its complete execution-input set; prepare again",
        409,
      );
    }
    const verified = new Map();
    for (const selected of supplied) {
      if (!selected.execution_transport) {
        // Existing capsules retain their original snapshot contract and paths.
        fail(
          selected.execution_transport === undefined &&
            selected.archive_root === undefined &&
            !isWithin(
              executionInputPaths(this.dataDir, "legacy").namespace,
              resolve(selected.snapshot_root),
            ),
          "SOURCE_DRIFT",
          "A derived execution input cannot be downgraded to a legacy snapshot",
          409,
        );
        const canonical = await this.tree(selected.source_locator),
          snapshot = await this.tree(selected.snapshot_root);
        fail(
          canonical.tree_sha256 === selected.source_tree_sha256 &&
            snapshot.tree_sha256 === selected.source_tree_sha256,
          "SOURCE_DRIFT",
          "Selected competence or immutable snapshot changed; prepare again",
          409,
        );
        continue;
      }
      const transport = selected.execution_transport;
      fail(
        transport.schema_version === transportSchema &&
          transport.data_dir_sha256 === sha(resolve(this.dataDir)) &&
          (expectedTaskId === undefined ||
            transport.task_id === expectedTaskId),
        "SOURCE_DRIFT",
        "Execution-input transport belongs to another service",
        409,
      );
      let location = verified.get(transport.task_id);
      try {
        if (!location) {
          location = await verifyExecutionInputTask(
            this.dataDir,
            transport.task_id,
            transport.task_binding_sha256,
          );
          verified.set(transport.task_id, location);
        }
        const plan = location.owner.selections.find(
          (entry) => entry.directory_name === transport.directory_name,
        );
        const archive = join(
          this.dataDir,
          "task-inputs",
          transport.task_id,
          "skills",
          transport.directory_name,
        );
        const execution = join(
          location.taskRoot,
          "skills",
          transport.directory_name,
        );
        fail(
          plan &&
            transport.task_binding_sha256 === digest(location.owner) &&
            transport.namespace_owner_sha256 ===
              digest(location.namespaceOwner) &&
            selected.archive_root === archive &&
            selected.snapshot_root === execution &&
            selected.path === join(execution, "SKILL.md") &&
            selected.name === plan.name &&
            selected.selection_id === plan.selection_id &&
            selected.source_locator === plan.source_locator &&
            selected.source_tree_sha256 === plan.source_tree_sha256 &&
            digest(selected.manifest) === digest(plan.manifest) &&
            selected.sha256 ===
              plan.manifest.find((row) => row.path === "SKILL.md")?.sha256,
          "SOURCE_DRIFT",
          "Execution-input task/source binding changed; prepare again",
          409,
        );
        const canonical = await this.tree(selected.source_locator);
        fail(
          canonical.tree_sha256 === selected.source_tree_sha256,
          "SOURCE_DRIFT",
          "Selected canonical skill changed; prepare again",
          409,
        );
        await selectedInputTree(archive, { exactManifest: selected.manifest });
        await selectedInputTree(execution, {
          exactManifest: selected.manifest,
        });
      } catch (error) {
        if (error.code === "ENOENT")
          throw new ServiceError(
            "SOURCE_DRIFT",
            "An execution input or its control archive is missing; prepare the task again",
            409,
          );
        throw error;
      }
    }
    for (const [taskId, location] of verified) {
      const actual = (selections ?? []).filter(
        (entry) => entry.execution_transport?.task_id === taskId,
      );
      fail(
        actual.length === location.owner.selections.length &&
          new Set(
            actual.map((entry) => entry.execution_transport.directory_name),
          ).size === actual.length,
        "SOURCE_DRIFT",
        "Approved execution-input selection membership changed; prepare again",
        409,
      );
    }
  }
  async source(name) {
    const root = this.skillRoot(name);
    fail(
      (await realpath(root)) === root,
      "SOURCE_DRIFT",
      "Linked source root requires explicit identity review",
      409,
    );
    const source = await readSource(root, "SKILL.md");
    let installed = null,
      installation_error = null;
    try {
      const primary = this.hostSources.has(name)
        ? source
        : await readInstalledSource(resolve(homedir(), ".agents/skills"), name);
      if (primary)
        installed = { sha256: primary.sha256, content: redact(primary.text) };
    } catch (error) {
      installation_error = error.code ?? "READ_FAILED";
    }
    return {
      name,
      canonical: {
        path: join(root, "SKILL.md"),
        sha256: source.sha256,
        content: redact(source.text),
      },
      installed,
      installation_error,
      primary_equal: installed?.sha256 === source.sha256,
      scope: "Primary source only; no runtime or full-tree installation claim",
    };
  }
  async #native(args, timeout = 12e4) {
    const script = resolve(this.repoRoot, "kit/portable/update_skill_suite.py");
    fail(
      await exists(script),
      "CAPABILITY_UNVERIFIED",
      "Native suite updater is unavailable",
      409,
    );
    try {
      const result = await run(pythonExecutable(), ["-B", script, ...args], {
        cwd: this.repoRoot,
        timeout,
        maxBuffer: 8 * 1024 * 1024,
        env: {
          ...process.env,
          PYTHONDONTWRITEBYTECODE: "1",
          TMPDIR: tmpdir(),
        },
      });
      return parseStrictJson(result.stdout, 8 * 1024 * 1024);
    } catch (error) {
      if (error.stdout?.trim())
        try {
          return parseStrictJson(error.stdout, 8 * 1024 * 1024);
        } catch {}
      let details;
      try {
        details = parseStrictJson(error.stderr ?? "");
      } catch {}
      throw new ServiceError(
        "UPDATER_FAILED",
        details?.error ??
          "Native updater could not complete; inspect the conflict report",
        409,
        redact(details ?? { exit_code: error.code }),
      );
    }
  }
  async audit(payload = {}) {
    const destination = resolve(
      payload.installed_root ?? join(homedir(), ".agents/skills"),
    );
    fail(
      [
        join(homedir(), ".agents/skills"),
        join(homedir(), ".codex/skills"),
      ].includes(destination),
      "SCOPE_MISMATCH",
      "Choose one supported personal skill root",
    );
    const planId = id("plan");
    const folder = join(this.dataDir, "skill-plans");
    await mkdir(folder, {
      recursive: true,
      mode: 448,
    });
    const path = join(folder, `${planId}.json`);
    const result = await this.#native([
      "audit",
      "--kit",
      join(this.repoRoot, "kit"),
      "--destination",
      destination,
      "--plan",
      path,
    ]);
    const bytes = await readFile(path);
    const plan = this.store.put("skill-plan", planId, {
      id: planId,
      path,
      sha256: sha(bytes),
      created_at: now(),
      destination,
      ready: result.ready === true,
      summary: redact(result),
    });
    return {
      plan_id: planId,
      plan_sha256: plan.sha256,
      ready: plan.ready,
      plan: redact(result),
    };
  }
  async diff(payload) {
    const plan = this.store.get("skill-plan", text(payload.plan_id, "plan_id"));
    fail(plan, "PLAN_NOT_FOUND", "Update plan not found", 404);
    const bytes = await readFile(plan.path);
    fail(
      sha(bytes) === plan.sha256,
      "SOURCE_DRIFT",
      "The reviewed update plan changed",
      409,
    );
    return {
      plan_id: plan.id,
      plan_sha256: plan.sha256,
      plan: parseStrictJson(bytes.toString("utf8")),
      notice:
        "Native source-to-target plan; apply requires exact digest and confirmation",
    };
  }
  async apply(payload) {
    fail(
      !this.busy,
      "WRITER_CONFLICT",
      "Another global skill operation is active",
      409,
    );
    const plan = this.store.get("skill-plan", text(payload.plan_id, "plan_id"));
    fail(
      plan?.ready,
      "PLAN_NOT_READY",
      "Only an exact ready plan may be applied",
      409,
    );
    fail(
      payload.confirmed === true && payload.plan_sha256 === plan.sha256,
      "SCOPE_MISMATCH",
      "Confirm the exact reviewed plan digest",
      409,
    );
    this.busy = true;
    try {
      const bytes = await readFile(plan.path);
      fail(
        sha(bytes) === plan.sha256,
        "SOURCE_DRIFT",
        "The update plan changed",
        409,
      );
      const result = await this.#native(["apply", "--plan", plan.path]);
      const journalPath = result.journal ?? result.journal_path;
      const record = {
        id: id("journal"),
        plan_id: plan.id,
        created_at: now(),
        result: redact(result),
        path: journalPath ?? null,
      };
      this.store.put("skill-journal", record.id, record);
      return {
        journal_id: record.id,
        ...redact(result),
        discovery_status: "unverified",
        product_adoption: "not_performed",
      };
    } finally {
      this.busy = false;
    }
  }
  async verify(payload) {
    const args = ["verify", "--kit", join(this.repoRoot, "kit")];
    let journal;
    if (payload.journal_id) {
      journal = this.store.get(
        "skill-journal",
        text(payload.journal_id, "journal_id"),
      );
      fail(
        journal?.path,
        "JOURNAL_NOT_FOUND",
        "Exact native journal is unavailable",
        404,
      );
      args.push("--journal", journal.path);
      const plan = this.store.get("skill-plan", journal.plan_id);
      if (plan) args.push("--destination", plan.destination);
    }
    return this.#native(args);
  }
  async rollback(payload) {
    fail(
      !this.busy,
      "WRITER_CONFLICT",
      "Another global skill operation is active",
      409,
    );
    fail(
      payload.confirmed === true,
      "SCOPE_MISMATCH",
      "Confirm rollback of the exact native journal",
      409,
    );
    const journal = this.store.get(
      "skill-journal",
      text(payload.journal_id, "journal_id"),
    );
    fail(
      journal?.path,
      "JOURNAL_NOT_FOUND",
      "Exact native journal is unavailable",
      404,
    );
    this.busy = true;
    try {
      return await this.#native(["rollback", "--journal", journal.path]);
    } finally {
      this.busy = false;
    }
  }
}
