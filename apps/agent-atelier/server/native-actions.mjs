import { SERVICE_VERSION } from "../shared/contracts.mjs";
import { fail, now, parseStrictJson, redact, ServiceError } from "./utils.mjs";

export const OPENAI_DOCS_SEARCH = "openai_docs.search";
const endpoint = "https://developers.openai.com/mcp";
const protocolVersion = "2025-06-18";
const searchTool = "search_openai_docs";
const responseLimit = 1024 * 1024;
const resultLimit = 5;
const docsHosts = new Set([
  "developers.openai.com",
  "platform.openai.com",
  "learn.chatgpt.com",
]);

function invalidResponse() {
  return new ServiceError(
    "INTEGRATION_RESPONSE_INVALID",
    "OpenAI Docs MCP returned an invalid or unsupported response",
    502,
  );
}

async function readMessage(response, id) {
  const contentType = response.headers.get("content-type") ?? "";
  const json = /^application\/json(?:\s*;|$)/i.test(contentType);
  const events = /^text\/event-stream(?:\s*;|$)/i.test(contentType);
  if (!response.body || (!json && !events)) {
    await response.body?.cancel().catch(() => {});
    throw invalidResponse();
  }
  const decoder = new TextDecoder("utf-8", { fatal: true });
  let buffer = "";
  let bytes = 0;
  try {
    for await (const chunk of response.body) {
      bytes += chunk.byteLength;
      if (bytes > responseLimit) throw invalidResponse();
      buffer += decoder.decode(chunk, { stream: true });
      if (events) {
        let delimiter;
        while ((delimiter = /\r?\n\r?\n/.exec(buffer))) {
          const data = buffer
            .slice(0, delimiter.index)
            .split(/\r?\n/)
            .filter((line) => line.startsWith("data:"))
            .map((line) => line.slice(5).replace(/^ /, ""))
            .join("\n");
          buffer = buffer.slice(delimiter.index + delimiter[0].length);
          if (!data) continue;
          const message = parseStrictJson(data, responseLimit);
          if (message?.id === id) return message;
        }
      }
    }
    if (json) return parseStrictJson(buffer + decoder.decode(), responseLimit);
  } catch (error) {
    if (error?.name === "TimeoutError" || error?.name === "AbortError")
      throw error;
    throw invalidResponse();
  }
  throw invalidResponse();
}

function source(hit) {
  if (typeof hit?.url !== "string" || hit.url.length > 2048) return null;
  let url;
  try {
    url = new URL(hit.url);
  } catch {
    return null;
  }
  if (
    url.protocol !== "https:" ||
    !docsHosts.has(url.hostname) ||
    url.username ||
    url.password ||
    url.port
  )
    return null;
  url.search = "";
  const heading = [hit.hierarchy?.lvl1, hit.hierarchy?.lvl0, hit.title].find(
    (value) => typeof value === "string" && value.trim(),
  );
  return {
    title: heading
      ? redact(heading)
          .replace(/[\u0000-\u001f\u007f]/g, " ")
          .trim()
          .slice(0, 240)
      : url.pathname,
    source_url: url.href,
  };
}

export async function searchOpenAIDocs(query, fetchImpl = fetch) {
  const headers = {
    Accept: "application/json, text/event-stream",
    "Content-Type": "application/json",
  };
  const signal = AbortSignal.timeout(20_000);
  async function rpc(method, params, id) {
    const response = await fetchImpl(endpoint, {
      method: "POST",
      headers: { ...headers },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method,
        params,
        ...(id !== undefined ? { id } : {}),
      }),
      credentials: "omit",
      redirect: "error",
      cache: "no-store",
      signal,
    });
    if (!response.ok || id === undefined) {
      await response.body?.cancel().catch(() => {});
      if (response.status === 429)
        throw new ServiceError(
          "INTEGRATION_RATE_LIMITED",
          "OpenAI Docs MCP rate limit reached",
          429,
        );
      fail(
        response.ok,
        "INTEGRATION_UNAVAILABLE",
        "OpenAI Docs MCP is unavailable",
        503,
      );
      return;
    }
    const session = response.headers.get("mcp-session-id");
    if (session !== null) {
      if (
        !/^[\x21-\x7e]{1,256}$/.test(session) ||
        (headers["MCP-Session-Id"] && headers["MCP-Session-Id"] !== session)
      ) {
        await response.body?.cancel().catch(() => {});
        throw invalidResponse();
      }
      headers["MCP-Session-Id"] = session;
    }
    const message = await readMessage(response, id);
    if (
      message?.id !== id ||
      message.jsonrpc !== "2.0" ||
      !Object.hasOwn(message, "result") ||
      message.error
    )
      throw invalidResponse();
    return message.result;
  }

  try {
    const initialization = await rpc(
      "initialize",
      {
        protocolVersion,
        capabilities: {},
        clientInfo: { name: "agent-atelier", version: SERVICE_VERSION },
      },
      1,
    );
    if (
      initialization?.protocolVersion !== protocolVersion ||
      !initialization?.capabilities?.tools
    )
      throw invalidResponse();
    headers["MCP-Protocol-Version"] = protocolVersion;
    await rpc("notifications/initialized", {});
    const catalog = await rpc("tools/list", {}, 2);
    const matchingTools = Array.isArray(catalog?.tools)
      ? catalog.tools.filter((candidate) => candidate?.name === searchTool)
      : [];
    const tool = matchingTools[0];
    const schema = tool?.inputSchema;
    if (
      matchingTools.length !== 1 ||
      tool.annotations?.readOnlyHint !== true ||
      tool.annotations?.destructiveHint === true ||
      schema?.type !== "object" ||
      schema.properties?.query?.type !== "string" ||
      !["integer", "number"].includes(schema.properties?.limit?.type)
    )
      throw invalidResponse();
    const result = await rpc(
      "tools/call",
      {
        name: searchTool,
        arguments: { query, limit: resultLimit },
      },
      3,
    );
    if (!result || result.isError === true) throw invalidResponse();
    const payload =
      result.structuredContent ??
      parseStrictJson(
        result.content?.find(({ type }) => type === "text")?.text,
        responseLimit,
      );
    if (!Array.isArray(payload?.hits)) throw invalidResponse();
    const sources = new Map();
    for (const hit of payload.hits.slice(0, resultLimit)) {
      const link = source(hit);
      if (link && !sources.has(link.source_url))
        sources.set(link.source_url, link);
    }
    if (payload.hits.length && !sources.size) throw invalidResponse();
    return {
      kind: "documentation",
      operation: OPENAI_DOCS_SEARCH,
      checked_at: now(),
      provider: "OpenAI Docs MCP",
      tool: searchTool,
      status: "completed",
      content: [...sources.values()],
      count: sources.size,
    };
  } catch (error) {
    if (error instanceof ServiceError && error.code !== "INVALID_JSON")
      throw error;
    if (error instanceof ServiceError) throw invalidResponse();
    throw new ServiceError(
      "INTEGRATION_UNAVAILABLE",
      "OpenAI Docs MCP could not be reached",
      503,
    );
  }
}
