import test from "node:test";
import assert from "node:assert/strict";
import { IntegrationsManager } from "../../server/integrations.mjs";
import { OPENAI_DOCS_SEARCH } from "../../server/native-actions.mjs";

const input = {
  operation: OPENAI_DOCS_SEARCH,
  arguments: { query: "Codex App Server" },
};
const descriptor = {
  name: "search_openai_docs",
  annotations: { readOnlyHint: true, destructiveHint: false },
  inputSchema: {
    type: "object",
    properties: { query: { type: "string" }, limit: { type: "integer" } },
  },
};

function mcpFixture({ tool = descriptor, hits = [] } = {}) {
  const calls = [];
  const manager = new IntegrationsManager({
    dataDir: "/service",
    nativeRpc: async () => ({}),
    readMcpInventory: async () => [],
    githubAvailable: async () => false,
    fetchImpl: async (url, options) => {
      const request = JSON.parse(options.body);
      calls.push(request.method);
      assert.equal(url, "https://developers.openai.com/mcp");
      assert.equal(options.method, "POST");
      assert.equal(options.redirect, "error");
      assert.equal(options.credentials, "omit");
      assert.equal(options.headers.Authorization, undefined);
      if (request.method === "initialize") {
        assert.equal(request.params.protocolVersion, "2025-06-18");
        return Response.json(
          {
            jsonrpc: "2.0",
            id: request.id,
            result: {
              protocolVersion: "2025-06-18",
              capabilities: { tools: {} },
            },
          },
          { headers: { "MCP-Session-Id": "fixture-session" } },
        );
      }
      assert.equal(options.headers["MCP-Session-Id"], "fixture-session");
      assert.equal(options.headers["MCP-Protocol-Version"], "2025-06-18");
      if (request.method === "notifications/initialized") {
        assert.equal(request.id, undefined);
        return new Response(null, { status: 202 });
      }
      if (request.method === "tools/list")
        return Response.json({
          jsonrpc: "2.0",
          id: request.id,
          result: { tools: [tool] },
        });
      assert.equal(request.method, "tools/call");
      assert.deepEqual(request.params, {
        name: "search_openai_docs",
        arguments: { query: "Codex App Server", limit: 5 },
      });
      const response = {
        jsonrpc: "2.0",
        id: request.id,
        result: { content: [{ type: "text", text: JSON.stringify({ hits }) }] },
      };
      const event = `data: ${JSON.stringify(response)}\r\n\r\n`;
      return new Response(
        new ReadableStream({
          start(controller) {
            const encoder = new TextEncoder();
            controller.enqueue(encoder.encode(": heartbeat\r\n\r\n"));
            controller.enqueue(encoder.encode(event.slice(0, 12)));
            controller.enqueue(encoder.encode(event.slice(12)));
          },
        }),
        { headers: { "Content-Type": "text/event-stream" } },
      );
    },
  });
  return { manager, calls };
}

test("public Docs MCP search returns only bounded official documentation links", async () => {
  const { manager, calls } = mcpFixture({
    hits: [
      {
        url: "https://learn.chatgpt.com/docs/app-server?token=private#protocol",
        hierarchy: { lvl1: "App Server" },
        content: "unprojected vendor text",
      },
      {
        url: "https://learn.chatgpt.com/docs/app-server#protocol",
        title: "Duplicate",
      },
      { url: "https://learn.chatgpt.com.example.org/docs/app-server" },
      { url: "https://user:password@developers.openai.com/api/docs" },
    ],
  });
  const inspection = await manager.inspect({ kind: "mcp", id: "openai-docs" });
  assert.equal(inspection.entry.actions[0].id, OPENAI_DOCS_SEARCH);
  assert.equal(inspection.source, "openai_docs_mcp");
  assert.deepEqual(calls, []);
  const result = await manager.run(input);
  assert.equal(result.kind, "documentation");
  assert.equal(result.status, "completed");
  assert.equal(result.count, 1);
  assert.deepEqual(result.content, [
    {
      title: "App Server",
      source_url: "https://learn.chatgpt.com/docs/app-server#protocol",
    },
  ]);
  assert.deepEqual(calls, [
    "initialize",
    "notifications/initialized",
    "tools/list",
    "tools/call",
  ]);
});

test("Docs search refuses an altered tool or extra input before sending a search", async () => {
  const { manager, calls } = mcpFixture({
    tool: {
      ...descriptor,
      annotations: { readOnlyHint: true, destructiveHint: true },
    },
  });
  await assert.rejects(
    manager.run({
      ...input,
      arguments: { ...input.arguments, endpoint: "https://invalid.example" },
    }),
    { code: "INVALID_INPUT" },
  );
  assert.deepEqual(calls, []);
  await assert.rejects(manager.run(input), {
    code: "INTEGRATION_RESPONSE_INVALID",
  });
  assert.deepEqual(calls, [
    "initialize",
    "notifications/initialized",
    "tools/list",
  ]);
});
