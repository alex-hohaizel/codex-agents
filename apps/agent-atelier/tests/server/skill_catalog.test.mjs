import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  readFile,
  realpath,
  rm,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";

import { SkillsManager } from "../../server/skills.mjs";
import { sha } from "../../server/utils.mjs";

const repoRoot = resolve(import.meta.dirname, "../../../..");

test("the catalog shows current skill metadata, legacy headings and host fallback labels", async (t) => {
  const project = await mkdtemp(
    join(await realpath(tmpdir()), "atelier-catalog-"),
  );
  t.after(() => rm(project, { recursive: true, force: true }));
  const manager = new SkillsManager({
    repoRoot,
    dataDir: join(project, "data"),
  });
  const release = JSON.parse(
    await readFile(join(repoRoot, "releases/current.json"), "utf8"),
  );
  const canonical = [
    ...release.stable_skill_names.map((name) => ({
      name,
      source: "kit/skills/" + name,
      version: release.suite_version,
    })),
    ...release.optional_skills,
  ];
  const readyName = "host-metadata";
  const ready = [
    "---",
    "name: " + readyName,
    "metadata:",
    '  version: "1.3.0-rc.2+verified"',
    "---",
    "",
    "# Previous heading 1.2.0",
    "",
  ].join("\n");
  const legacy = "# Legacy host skill 1.2.0\n";
  const noVersion = "# Host skill without a release version\n";
  const mergedName = "chatbot-atelier-qa";
  const merged = await readFile(
    join(repoRoot, "kit/skills", mergedName, "SKILL.md"),
  );
  const hostRows = [];
  for (const [name, bytes, withinProject, enabled] of [
    [readyName, ready, true, true],
    ["host-legacy", legacy, true, false],
    ["host-no-version", noVersion, true, true],
    ["host-unreadable", ready, false, true],
    [mergedName, merged, true, true],
  ]) {
    const root = withinProject ? join(project, ".agents/skills") : project;
    const path = join(root, name, "SKILL.md");
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, bytes);
    hostRows.push({ name, description: name, path, enabled, scope: "project" });
  }

  const registration = await manager.adoptHostCatalog(hostRows, [project]);
  assert.equal(registration.host_discovered, hostRows.length);
  const { entries } = await manager.list();
  for (const { name, source, version } of canonical) {
    const row = entries.find((entry) => entry.name === name);
    assert.equal(row.version, version, name);
    assert.equal(row.path, source + "/SKILL.md");
    assert.equal(
      row.source_sha256,
      sha(await readFile(join(repoRoot, row.path))),
    );
  }

  const discovered = entries.find((row) => row.name === readyName);
  assert.equal(discovered.version, "1.3.0-rc.2+verified");
  assert.equal(discovered.path, hostRows[0].path);
  assert.equal(discovered.source_sha256, sha(ready));
  assert.equal(discovered.execution_supported, true);
  assert.equal(discovered.update_supported, false);

  const disabled = entries.find((row) => row.name === "host-legacy");
  assert.equal(disabled.version, "1.2.0");
  assert.equal(disabled.discovery_status, "host_disabled");
  assert.equal(disabled.execution_supported, false);
  assert.equal(
    entries.find((row) => row.name === "host-no-version").version,
    "host-source",
  );

  const unreadable = entries.find((row) => row.name === "host-unreadable");
  assert.equal(unreadable.version, "unknown");
  assert.equal(unreadable.source_sha256, null);
  assert.equal(unreadable.execution_supported, false);

  const matching = entries.filter((row) => row.name === mergedName);
  assert.equal(matching.length, 1);
  assert.equal(matching[0].host_source_path, hostRows[4].path);
  assert.equal(matching[0].discovery_status, "host_discovered");
});
