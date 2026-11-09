import {
  readFile,
  readdir,
  mkdir,
  realpath,
  lstat,
  cp,
  chmod,
} from "node:fs/promises";
import { resolve, join, dirname } from "node:path";
import { homedir } from "node:os";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import {
  atomicWrite,
  digest,
  exists,
  fail,
  id,
  now,
  parseStrictJson,
  readSource,
  redact,
  sha,
  text,
  ServiceError,
} from "./utils.mjs";
const run = promisify(execFile);
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
        const version =
          /^#.*?(\d+\.\d+\.\d+)/m.exec(source.text)?.[1] ?? "unknown";
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
          version,
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
          version: /^#.*?(\d+\.\d+\.\d+)/m.exec(source.text)?.[1] ?? "unknown",
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
        version: source
          ? (/^#.*?(\d+\.\d+\.\d+)/m.exec(source.text)?.[1] ?? "host-source")
          : "unknown",
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
    fail(
      (await realpath(root)) === root,
      "SOURCE_DRIFT",
      "Linked skill source root requires explicit identity review",
      409,
    );
    const manifest = [];
    let total = 0;
    const visit = async (folder, prefix = "") => {
      for (const entry of (await readdir(folder, { withFileTypes: true })).sort(
        (a, b) => (a.name < b.name ? -1 : 1),
      )) {
        if (
          ["__pycache__", ".DS_Store", ".git", "node_modules"].includes(
            entry.name,
          )
        )
          continue;
        fail(
          !entry.isSymbolicLink(),
          "SOURCE_DRIFT",
          "Linked skill source cannot be snapshotted",
          409,
        );
        const path = join(folder, entry.name),
          ref = prefix ? prefix + "/" + entry.name : entry.name;
        if (entry.isDirectory()) await visit(path, ref);
        else if (entry.isFile()) {
          const stat = await lstat(path);
          total += stat.size;
          fail(
            manifest.length < 5000 && total < 64 * 1024 * 1024,
            "CAPACITY_LIMIT",
            "Selected skill source exceeds bounded snapshot size",
            409,
          );
          const bytes = await readFile(path);
          manifest.push({ path: ref, bytes: bytes.length, sha256: sha(bytes) });
        }
      }
    };
    await visit(root);
    return { manifest, tree_sha256: digest(manifest), bytes: total };
  }
  async selections(names, taskId) {
    fail(
      Array.isArray(names) &&
        names.length <= 4 &&
        new Set(names).size === names.length,
      "INVALID_INPUT",
      "Select at most four distinct competencies",
    );
    const result = [];
    for (const name of names) {
      const sourceRoot = this.skillRoot(name, { execution: true });
      const entryName = this.hostSources.get(name)?.name ?? name;
      const directoryName = this.hostSources.has(name)
        ? "host-" + sha(name).slice(0, 16)
        : name;
      fail(
        await exists(join(sourceRoot, "SKILL.md")),
        "CAPABILITY_UNVERIFIED",
        "Selected skill source is unavailable",
        409,
      );
      const before = await this.tree(sourceRoot);
      const snapshotRoot = join(
        this.dataDir,
        "task-inputs",
        taskId,
        "skills",
        directoryName,
      );
      await mkdir(dirname(snapshotRoot), { recursive: true, mode: 0o700 });
      await cp(sourceRoot, snapshotRoot, {
        recursive: true,
        errorOnExist: true,
        force: false,
        filter: (source) =>
          !source
            .split(/[\\/]/)
            .some((part) =>
              ["__pycache__", ".DS_Store", ".git", "node_modules"].includes(
                part,
              ),
            ),
      });
      const snapshot = await this.tree(snapshotRoot),
        after = await this.tree(sourceRoot);
      fail(
        before.tree_sha256 === snapshot.tree_sha256 &&
          before.tree_sha256 === after.tree_sha256,
        "SOURCE_DRIFT",
        "Skill source changed during snapshot; prepare again",
        409,
      );
      for (const row of snapshot.manifest)
        await chmod(join(snapshotRoot, row.path), 0o400);
      result.push({
        name: entryName,
        selection_id: name,
        source_locator: sourceRoot,
        source_tree_sha256: before.tree_sha256,
        snapshot_root: snapshotRoot,
        path: join(snapshotRoot, "SKILL.md"),
        sha256: snapshot.manifest.find((row) => row.path === "SKILL.md").sha256,
        manifest: snapshot.manifest,
        delivery_fact:
          "Pinned canonical execution input snapshot, not a personal-skill installation",
      });
    }
    return result;
  }
  async verifySelections(selections) {
    for (const selected of selections ?? []) {
      const canonical = await this.tree(selected.source_locator),
        snapshot = await this.tree(selected.snapshot_root);
      fail(
        canonical.tree_sha256 === selected.source_tree_sha256 &&
          snapshot.tree_sha256 === selected.source_tree_sha256,
        "SOURCE_DRIFT",
        "Selected competence or immutable snapshot changed; prepare again",
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
      const result = await run("python3", ["-B", script, ...args], {
        cwd: this.repoRoot,
        timeout,
        maxBuffer: 8 * 1024 * 1024,
        env: {
          ...process.env,
          PYTHONDONTWRITEBYTECODE: "1",
          TMPDIR: "/private/tmp",
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
