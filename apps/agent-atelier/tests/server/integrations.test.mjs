import test from "node:test";
import assert from "node:assert/strict";
import { IntegrationsManager } from "../../server/integrations.mjs";

test("native inventory projects safe installed metadata and inspects only a current connector", async () => {
  const calls = [];
  const manager = new IntegrationsManager({
    dataDir: "/service",
    githubAvailable: async () => true,
    nativeRpc: async (method, args) => {
      calls.push([method, args]);
      if (method === "plugin/installed")
        return {
          marketplaceLoadErrors: [],
          marketplaces: [
            {
              path: "/private/marketplace",
              plugins: [
                {
                  id: "calendar@market",
                  installed: true,
                  enabled: true,
                  localVersion: "1.2.3",
                  interface: { displayName: "Calendar" },
                },
                { id: "not-installed@market", installed: false, enabled: true },
              ],
            },
          ],
        };
      if (method === "app/installed")
        return {
          apps: [
            {
              id: "connector_01",
              runtimeName: "Catalog",
              enabled: true,
              callable: true,
            },
            {
              id: "connector_02",
              runtimeName: "Disabled app",
              enabled: false,
              callable: false,
            },
          ],
        };
      assert.equal(method, "app/read");
      assert.deepEqual(args, { appIds: ["connector_01"], includeTools: true });
      return {
        apps: [
          {
            id: "connector_01",
            name: "Catalog",
            toolSummaries: [
              {
                name: "find",
                title: "Find",
                isEnabled: true,
                isReadOnly: true,
              },
              {
                name: "send",
                title: "Send",
                isEnabled: false,
                isReadOnly: false,
              },
            ],
          },
        ],
      };
    },
    readMcpInventory: async (cwd) => {
      assert.equal(cwd, "/service");
      return [
        {
          name: "user-server",
          enabled: true,
          transport: { url: "https://service.example/secret" },
          env: { SECRET: "private" },
        },
      ];
    },
    fetchImpl: async () =>
      assert.fail("Catalog inspection does not call the media provider"),
  });
  const catalog = await manager.list({ locale: "uk" });
  assert.deepEqual(
    catalog.entries.slice(0, 4).map(({ id, status }) => [id, status]),
    [
      ["calendar@market", "native_only"],
      ["connector_01", "native_only"],
      ["connector_02", "disabled"],
      ["user-server", "unverified"],
    ],
  );
  assert.match(catalog.entries[0].handoff.text, /^У цьому чаті Codex/);
  assert.doesNotMatch(
    JSON.stringify(catalog),
    /private|service\.example|not-installed/,
  );
  await assert.rejects(manager.inspect({ kind: "connector", id: "unlisted" }), {
    code: "NOT_FOUND",
  });
  assert.equal(
    calls.some(([method]) => method === "app/read"),
    false,
  );
  const inspected = await manager.inspect({
    kind: "connector",
    id: "connector_01",
  });
  assert.equal(inspected.source, "codex_connectors");
  assert.equal(inspected.status, "available");
  assert.deepEqual(
    inspected.tools.map(({ name, enabled, read_only }) => [
      name,
      enabled,
      read_only,
    ]),
    [
      ["find", true, true],
      ["send", false, false],
    ],
  );
  assert.deepEqual(inspected.entry.actions, []);
  const github = await manager.inspect({ kind: "connector", id: "github-cli" });
  assert.equal(github.source, "github_cli");
  assert.equal(github.entry.actions[0].id, "github.repository.read");
});

test("search uses the fixed read endpoint and returns attribution instead of media bytes", async () => {
  const manager = new IntegrationsManager({
    fetchImpl: async (url, options) => {
      assert.equal(url.origin, "https://api.openverse.org");
      assert.equal(url.pathname, "/v1/audio/");
      assert.equal(url.searchParams.get("q"), "station & ambience");
      assert.equal(url.searchParams.get("mature"), "false");
      assert.equal(url.searchParams.get("page_size"), "10");
      assert.equal(options.method, "GET");
      assert.equal(options.redirect, "error");
      assert.equal(options.credentials, "omit");
      return Response.json({
        results: [
          {
            id: "public-audio",
            title: "Rail station",
            creator: "Author",
            license: "by",
            license_version: "4.0",
            license_url: "https://creativecommons.org/licenses/by/4.0/",
            foreign_landing_url: "https://example.org/work",
            source: "example",
            url: "https://example.org/bytes.wav",
          },
          {
            id: "invalid-url",
            foreign_landing_url: "javascript:alert(1)",
            license_url: "https://example.org/?token=hidden",
          },
          { id: "sensitive", mature: true },
        ],
      });
    },
  });
  const result = await manager.run({
    operation: "openverse.audio.search",
    arguments: { query: "station & ambience" },
  });
  assert.equal(result.status, "completed");
  assert.equal(result.count, 2);
  assert.deepEqual(result.content[0], {
    id: "public-audio",
    title: "Rail station",
    creator: "Author",
    license: "by 4.0",
    medium: "audio",
    license_url: "https://creativecommons.org/licenses/by/4.0/",
    source_url: "https://example.org/work",
    source: "example",
  });
  assert.equal(result.content[1].source_url, null);
  assert.equal(result.content[1].license_url, null);
  assert.doesNotMatch(JSON.stringify(result), /bytes\.wav|hidden|sensitive/);
});

test("unsupported, oversharing and rate-limited operations never trigger a fallback", async () => {
  let requests = 0;
  const manager = new IntegrationsManager({
    fetchImpl: async () => {
      requests++;
      return new Response(null, { status: 429 });
    },
  });
  await assert.rejects(manager.run(null), { code: "INVALID_INPUT" });
  await assert.rejects(
    manager.run({
      operation: "openverse.images.search",
      arguments: { query: "image" },
      context: "private",
    }),
    { code: "INVALID_INPUT" },
  );
  await assert.rejects(
    manager.run({
      operation: "provider.generate",
      arguments: { query: "image" },
    }),
    { code: "INTEGRATION_OPERATION_UNAVAILABLE" },
  );
  await assert.rejects(
    manager.run({
      operation: "openverse.images.search",
      arguments: { query: "image", context: "private" },
    }),
    { code: "INVALID_INPUT" },
  );
  await assert.rejects(
    manager.run({
      operation: "openverse.images.search",
      arguments: { query: "Bearer source-secret-1234567890" },
    }),
    { code: "INVALID_INPUT" },
  );
  assert.equal(requests, 0);
  await assert.rejects(
    manager.run({
      operation: "openverse.images.search",
      arguments: { query: "image" },
    }),
    { code: "INTEGRATION_RATE_LIMITED" },
  );
  assert.equal(requests, 1);
});

test("GitHub read is bound to one repository and emits only projected metadata", async () => {
  const calls = [];
  const manager = new IntegrationsManager({
    readRepository: async (name) => {
      calls.push(name);
      return {
        full_name: "Workspace/Repository",
        default_branch: "main",
        visibility: "private",
        archived: false,
        owner: { email: "private@example.com" },
      };
    },
  });
  const read = (repository) =>
    manager.run({
      operation: "github.repository.read",
      arguments: { repository },
    });
  await assert.rejects(read("workspace/../repository"), {
    code: "INVALID_INPUT",
  });
  await assert.rejects(read("workspace/.."), { code: "INVALID_INPUT" });
  await assert.rejects(read("https://github.com/workspace/repository"), {
    code: "INVALID_INPUT",
  });
  assert.deepEqual(calls, []);
  await assert.rejects(read("workspace/redirect"), {
    code: "INTEGRATION_TARGET_MISMATCH",
  });
  const result = await read("workspace/repository");
  assert.equal(result.kind, "repository");
  assert.deepEqual(result.repository, {
    name: "Workspace/Repository",
    default_branch: "main",
    visibility: "private",
    archived: false,
    source_url: "https://github.com/Workspace/Repository",
  });
  assert.doesNotMatch(JSON.stringify(result), /private@example\.com/);
});
