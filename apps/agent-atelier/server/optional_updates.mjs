import {
  readFile,
  readdir,
  lstat,
  mkdir,
  chmod,
  unlink,
  cp,
} from "node:fs/promises";
import { resolve, join, dirname, relative } from "node:path";
import { homedir } from "node:os";
import {
  atomicWrite,
  digest,
  exists,
  fail,
  id,
  now,
  parseStrictJson,
  sha,
  text,
} from "./utils.mjs";

const SOURCES = {
  "atelier-orchestrator": "optional-skills/atelier-orchestrator",
  "codex-agents-maintenance": "maintenance-skill",
};
const HASH = /^[a-f0-9]{64}$/;
async function safeParents(path) {
  for (let p = resolve(path); ; p = dirname(p)) {
    if (await exists(p))
      fail(
        !(await lstat(p)).isSymbolicLink(),
        "SOURCE_DRIFT",
        "Linked skill paths require separate review",
        409,
      );
    if (p === dirname(p)) break;
  }
}
async function tree(root) {
  await safeParents(root);
  if (!(await exists(root))) return {};
  fail(
    (await lstat(root)).isDirectory(),
    "SOURCE_DRIFT",
    "Skill source must be a directory",
    409,
  );
  const files = {};
  let size = 0;
  async function walk(path) {
    for (const entry of await readdir(path, { withFileTypes: true })) {
      if (entry.name === "__pycache__" || /\.py[co]$/.test(entry.name))
        continue;
      fail(
        ![".git", ".aws", ".ssh", "node_modules"].includes(entry.name) &&
          !/^(?:\.env(?:\..*)?|credentials(?:\..*)?|owner-credentials\.json|auth\.json|id_(?:rsa|ed25519)|.*\.(?:pem|key|p12|pfx))$/i.test(
            entry.name,
          ),
        "PRIVATE_PATH",
        "Private files are not optional skill source",
        409,
      );
      const full = join(path, entry.name),
        st = await lstat(full);
      fail(
        !st.isSymbolicLink(),
        "SOURCE_DRIFT",
        "Linked skill entries are not updated",
        409,
      );
      if (st.isDirectory()) await walk(full);
      else {
        fail(st.isFile(), "SOURCE_DRIFT", "Irregular skill entry", 409);
        size += st.size;
        fail(
          size <= 64 * 1024 * 1024 && Object.keys(files).length < 5000,
          "CAPACITY_LIMIT",
          "Optional skill exceeds its bounded source limit",
        );
        files[relative(root, full).split("\\").join("/")] = {
          sha256: sha(await readFile(full)),
          bytes: st.size,
          mode: st.mode & 0o777,
        };
      }
    }
  }
  await walk(root);
  return Object.fromEntries(
    Object.entries(files).sort(([a], [b]) => a.localeCompare(b)),
  );
}
const version = (raw) => /^#.*?(\d+\.\d+\.\d+)/m.exec(raw)?.[1] ?? "unknown";
function interfaceFields(raw) {
  return Object.fromEntries(
    ["icon_small", "icon_large", "brand_color"].map((key) => {
      const matches = [
        ...raw.matchAll(
          new RegExp(
            "^ {2}" + key + ":\\s*[\"']?([^\"'\\n]+?)[\"']?\\s*$",
            "gm",
          ),
        ),
      ];
      fail(
        matches.length <= 1,
        "POLICY_CONFLICT",
        "Ambiguous UI bindings require separate review",
        409,
      );
      return [key, matches[0]?.[1]?.trim() ?? null];
    }),
  );
}
// Preserve every non-presentation UI byte, including unknown host extensions.
// A duplicate policy/dependency section cannot hide behind a first-match parser.
const restrictions = (raw) =>
  raw
    .replace(
      /^ {2}(?:display_name|short_description|default_prompt|icon_small|icon_large|brand_color):[^\r\n]*(?:\r?\n|$)/gm,
      "",
    )
    .trim();
async function preservation(beforeRoot, sourceRoot, before, after) {
  if (!Object.keys(before).length)
    return {
      existing: false,
      icons_preserved: true,
      restrictions_preserved: true,
    };
  const a = await readFile(
      join(beforeRoot, "agents/openai.yaml"),
      "utf8",
    ).catch(() => ""),
    b = await readFile(join(sourceRoot, "agents/openai.yaml"), "utf8").catch(
      () => "",
    );
  const fieldsA = interfaceFields(a),
    fieldsB = interfaceFields(b);
  fail(
    digest(fieldsA) === digest(fieldsB),
    "IDENTITY_CONFLICT",
    "Keep existing icon bindings and brand color; reconcile the proposed visual change first",
    409,
  );
  for (const key of ["icon_small", "icon_large"])
    if (fieldsA[key]) {
      const path = fieldsA[key].replace(/^\.\//, "");
      fail(
        before[path]?.sha256 && before[path].sha256 === after[path]?.sha256,
        "IDENTITY_CONFLICT",
        "Existing icon bytes differ; preserve the actual local identity before updating",
        409,
      );
    }
  fail(
    restrictions(a) === restrictions(b),
    "POLICY_CONFLICT",
    "Invocation policy or dependencies changed; review them separately",
    409,
  );
  return {
    existing: true,
    icons_preserved: true,
    restrictions_preserved: true,
  };
}

export class OptionalUpdates {
  constructor({
    store,
    repoRoot,
    dataDir,
    installedRoot = resolve(homedir(), ".agents/skills"),
  }) {
    this.store = store;
    this.repoRoot = repoRoot;
    this.dataDir = dataDir;
    this.installedRoot = installedRoot;
    this.previews = new Map();
    this.busy = false;
    for (const row of store.list("optional-update"))
      if (row.status === "pending")
        store.put("optional-update", row.id, {
          ...row,
          status: "outcome_unknown",
          reason:
            "Service restarted before optional-source verification; inspect current source before replay",
        });
  }
  clear() {
    this.previews.clear();
  }
  async preview(payload) {
    const name = text(payload.name, "name");
    fail(
      SOURCES[name],
      "UNSUPPORTED_OPERATION",
      "Only declared optional reusable skills are managed here",
    );
    const source = resolve(this.repoRoot, SOURCES[name]),
      target = resolve(this.installedRoot, name);
    const before = await tree(target),
      after = await tree(source);
    fail(
      after["SKILL.md"],
      "SOURCE_DRIFT",
      "Optional source entry is missing",
      409,
    );
    const content = await readFile(join(source, "SKILL.md"), "utf8");
    fail(
      new RegExp("^---\\s*\\nname: " + name + "\\s*\\n").test(content),
      "SOURCE_DRIFT",
      "Stable optional skill name changed",
      409,
    );
    if (
      !Object.keys(before).length &&
      this.installedRoot === resolve(homedir(), ".agents/skills")
    )
      fail(
        !(await exists(resolve(homedir(), ".codex/skills", name))),
        "SOURCE_DRIFT",
        "A legacy installed source exists; resolve it before creating a duplicate",
        409,
      );
    const baselines = parseStrictJson(
      await readFile(
        resolve(this.repoRoot, "optional-skills/UPDATE_BASELINES.json"),
        "utf8",
      ),
    );
    const known = Object.values(baselines.skills?.[name] ?? {}).some(
      (b) => digest(b.files) === digest(before),
    );
    const noop = digest(before) === digest(after),
      fresh = !Object.keys(before).length;
    const preserved = await preservation(target, source, before, after);
    const conflicts =
      !fresh && !noop && !known
        ? [
            "Installed source has unknown local changes; preserve them and prepare an exact compatible source merge first",
          ]
        : [];
    const changes = [
      ...new Set([...Object.keys(before), ...Object.keys(after)]),
    ]
      .filter((n) => digest(before[n] ?? null) !== digest(after[n] ?? null))
      .map((path) => ({
        path,
        change: !before[path] ? "added" : !after[path] ? "removed" : "changed",
        before: before[path] ?? null,
        after: after[path] ?? null,
      }));
    const preview = {
      preview_id: id("optional-preview"),
      name,
      source_root: source,
      target_root: target,
      installed_version: fresh
        ? null
        : version(await readFile(join(target, "SKILL.md"), "utf8")),
      candidate_version: version(content),
      before_sha256: digest(before),
      source_sha256: digest(after),
      changes,
      preservation: preserved,
      conflicts,
      ready: !conflicts.length,
      noop,
      expires_at: Date.now() + 600000,
      authority_epoch: this.store.get("settings", "owner").authority_epoch,
      scope:
        "Only this declared optional source; no core/product/account changes",
      backup_before_write: true,
    };
    preview.sha256 = digest(preview);
    for (const [k, p] of this.previews)
      if (p.public.expires_at < Date.now()) this.previews.delete(k);
    fail(
      this.previews.size < 50,
      "CAPACITY_LIMIT",
      "Finish existing optional update previews first",
    );
    this.previews.set(preview.preview_id, {
      public: preview,
      before,
      after,
      source,
      target,
    });
    return preview;
  }
  async apply(payload) {
    fail(
      !this.busy,
      "WRITER_CONFLICT",
      "Optional source maintenance is active",
      409,
    );
    const entry = this.previews.get(payload.preview_id),
      p = entry?.public;
    fail(
      entry &&
        p.ready &&
        p.expires_at > Date.now() &&
        payload.sha256 === p.sha256 &&
        payload.confirmed === true,
      "PREVIEW_REQUIRED",
      "Review and confirm the exact ready optional-source preview",
      409,
    );
    fail(
      p.authority_epoch === this.store.get("settings", "owner").authority_epoch,
      "SOURCE_DRIFT",
      "Owner authority changed; prepare a new preview",
      409,
    );
    fail(
      !this.store
        .list("optional-update")
        .some((r) => ["pending", "outcome_unknown"].includes(r.status)),
      "OUTCOME_UNKNOWN",
      "Verify or reconcile unfinished optional maintenance first",
      409,
    );
    fail(
      digest(await tree(entry.target)) === p.before_sha256 &&
        digest(await tree(entry.source)) === p.source_sha256,
      "SOURCE_DRIFT",
      "Optional source changed after preview",
      409,
    );
    if (p.noop) {
      this.previews.delete(p.preview_id);
      return {
        status: "noop",
        name: p.name,
        installed_source_verified: true,
        source_sha256: p.source_sha256,
        host_discovery_verified: false,
      };
    }
    this.busy = true;
    try {
      const ident = id("optional-update"),
        directory = join(this.dataDir, "optional-updates", ident),
        beforePath = join(directory, "before"),
        afterPath = join(directory, "after");
      const journal = {
        id: ident,
        backup_id: ident,
        name: p.name,
        root: entry.target,
        source_root: entry.source,
        status: "pending",
        phase: "staging",
        before: entry.before,
        after: entry.after,
        before_sha256: p.before_sha256,
        after_sha256: p.source_sha256,
        preservation: p.preservation,
        preview_sha256: p.sha256,
        started_at: now(),
        written: [],
        removed: [],
        owner_confirmed: true,
      };
      // Own every private copy before creating it. A failed staging attempt is
      // terminal and eligible for retention without implying a target mutation.
      this.store.put("optional-update", ident, journal);
      this.previews.delete(p.preview_id);
      try {
        await mkdir(directory, { recursive: true, mode: 0o700 });
        if (Object.keys(entry.before).length)
          await cp(entry.target, beforePath, { recursive: true });
        else await mkdir(beforePath, { mode: 0o700 });
        await cp(entry.source, afterPath, { recursive: true });
        fail(
          digest(await tree(beforePath)) === p.before_sha256 &&
            digest(await tree(afterPath)) === p.source_sha256,
          "SOURCE_DRIFT",
          "Source changed while staging the reviewed update",
          409,
        );
        journal.phase = "writing";
        this.store.put("optional-update", ident, journal);
        await mkdir(entry.target, { recursive: true });
        for (const [name, pin] of Object.entries(entry.after)) {
          const expected = { ...entry.before };
          for (const written of journal.written)
            expected[written] = entry.after[written];
          fail(
            digest(await tree(entry.target)) === digest(expected),
            "SOURCE_DRIFT",
            "Installed source changed during maintenance; preserve the current bytes and reconcile",
            409,
          );
          const bytes = await readFile(join(afterPath, name));
          fail(
            sha(bytes) === pin.sha256,
            "SOURCE_DRIFT",
            "Staged candidate changed",
            409,
          );
          await atomicWrite(join(entry.target, name), bytes);
          await chmod(join(entry.target, name), pin.mode);
          journal.written.push(name);
          this.store.put("optional-update", ident, journal);
        }
        for (const name of Object.keys(entry.before).filter(
          (n) => !entry.after[n],
        )) {
          fail(
            (await tree(entry.target))[name]?.sha256 ===
              entry.before[name].sha256,
            "SOURCE_DRIFT",
            "Removed source changed unexpectedly",
            409,
          );
          await unlink(join(entry.target, name));
          journal.removed.push(name);
          this.store.put("optional-update", ident, journal);
        }
        fail(
          digest(await tree(entry.target)) === p.source_sha256,
          "SOURCE_DRIFT",
          "Optional source verification failed",
          409,
        );
        const done = {
          ...journal,
          status: "completed",
          completed_at: now(),
          installed_source_verified: true,
          host_discovery_verified: false,
          next_action:
            "Refresh the actual host skill catalog; installed bytes do not certify execution",
        };
        this.store.put("optional-update", ident, done);
        return done;
      } catch (error) {
        this.store.put(
          "optional-update",
          ident,
          journal.phase === "staging"
            ? {
                ...journal,
                status: "failed",
                completed_at: now(),
                stage_error: String(error.message),
                next_action:
                  "Staging failed before installed-source mutation; retain or clean the owned private copies and prepare a fresh preview",
              }
            : {
                ...journal,
                status: "outcome_unknown",
                error: String(error.message),
                next_action: "Verify current source before any replay",
              },
        );
        throw error;
      }
    } finally {
      this.busy = false;
    }
  }
  async verify(payload) {
    fail(
      !this.busy,
      "WRITER_CONFLICT",
      "Wait for source maintenance to finish",
      409,
    );
    const journal = this.store.get(
      "optional-update",
      text(payload.journal_id, "journal_id"),
    );
    fail(journal, "NOT_FOUND", "Optional update journal not found", 404);
    fail(
      journal.root === resolve(this.installedRoot, journal.name) &&
        SOURCES[journal.name],
      "SOURCE_DRIFT",
      "Installed target identity does not match the managed optional skill",
      409,
    );
    const current = await tree(journal.root),
      hash = digest(current),
      after = hash === journal.after_sha256,
      before = hash === journal.before_sha256;
    const status = after
      ? "completed"
      : before
        ? journal.status === "rolled_back"
          ? "rolled_back"
          : "failed"
        : "outcome_unknown";
    const observed = {
      ...journal,
      status,
      verified_at: now(),
      ...(status !== "outcome_unknown"
        ? { completed_at: journal.completed_at ?? now() }
        : {}),
      current_sha256: hash,
      installed_source_verified: after,
      reconciled_by: "actual full-tree observation; no replay",
    };
    this.store.put("optional-update", journal.id, observed);
    return observed;
  }
  async rollback(payload) {
    fail(
      !this.busy && payload.confirmed === true,
      "PREVIEW_REQUIRED",
      "Review the current optional source and explicitly confirm rollback",
      409,
    );
    const journal = this.store.get(
      "optional-update",
      text(payload.journal_id, "journal_id"),
    );
    fail(journal, "NOT_FOUND", "Optional update journal not found", 404);
    fail(
      !journal.backup_pruned,
      "SOURCE_DRIFT",
      "The reviewed before-copy was pruned; rollback is unavailable",
      409,
    );
    fail(
      journal.root === resolve(this.installedRoot, journal.name) &&
        SOURCES[journal.name],
      "SOURCE_DRIFT",
      "Unexpected optional target identity",
      409,
    );
    fail(
      !this.store
        .list("optional-update")
        .some(
          (r) =>
            r.id !== journal.id &&
            ["pending", "outcome_unknown"].includes(r.status),
        ),
      "OUTCOME_UNKNOWN",
      "Reconcile other optional operations first",
      409,
    );
    const current = await tree(journal.root);
    fail(
      HASH.test(payload.current_sha256 ?? "") &&
        digest(current) === payload.current_sha256,
      "REVISION_CONFLICT",
      "Current source changed since rollback review",
      409,
    );
    for (const [name, pin] of Object.entries(current))
      fail(
        digest(pin) === digest(journal.before[name] ?? null) ||
          digest(pin) === digest(journal.after[name] ?? null),
        "SOURCE_DRIFT",
        "Later unknown edits must be preserved",
        409,
      );
    // Atomic replacement never removes a file shared by both versions. Its
    // later deletion is an unknown owner edit, not an interrupted update.
    for (const name of Object.keys(journal.before).filter(
      (name) => journal.after[name],
    ))
      fail(
        current[name],
        "SOURCE_DRIFT",
        "A later deletion must be preserved; do not resurrect it through rollback",
        409,
      );
    const backup = join(this.dataDir, "optional-updates", journal.id, "before");
    fail(
      (await exists(backup)) &&
        digest(await tree(backup)) === journal.before_sha256,
      "SOURCE_DRIFT",
      "Before-copy is missing or changed",
      409,
    );
    this.busy = true;
    try {
      this.store.put("optional-update", journal.id, {
        ...journal,
        status: "pending",
        rollback_started_at: now(),
      });
      for (const [name, pin] of Object.entries(journal.before)) {
        await atomicWrite(
          join(journal.root, name),
          await readFile(join(backup, name)),
        );
        await chmod(join(journal.root, name), pin.mode);
      }
      for (const name of Object.keys(current).filter((n) => !journal.before[n]))
        await unlink(join(journal.root, name));
      fail(
        digest(await tree(journal.root)) === journal.before_sha256,
        "SOURCE_DRIFT",
        "Rollback verification failed",
        409,
      );
      const done = {
        ...journal,
        status: "rolled_back",
        completed_at: now(),
        current_sha256: journal.before_sha256,
        automatic_external_rollback: false,
      };
      this.store.put("optional-update", journal.id, done);
      return done;
    } catch (error) {
      this.store.put("optional-update", journal.id, {
        ...journal,
        status: "outcome_unknown",
        error: String(error.message),
      });
      throw error;
    } finally {
      this.busy = false;
    }
  }
}
