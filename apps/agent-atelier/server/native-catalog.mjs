import { isAbsolute } from "node:path";
import { fail, publicError, redact } from "./utils.mjs";

const PAGE_SIZE = 100;
const clip = (value, length) =>
  typeof value === "string" ? redact(value).slice(0, length) : "";

function newStream() {
  return {
    rows: new Map(),
    cursors: new Set(),
    cursor: undefined,
    pages: 0,
    exhausted: false,
    skipped: 0,
  };
}

export function nativeInventory(includeArchived, includeProjects) {
  return {
    includeArchived,
    active: newStream(),
    archived: includeArchived ? newStream() : null,
    projects: includeProjects ? newStream() : null,
  };
}

function projectRow(row) {
  if (typeof row?.id !== "string" || !row.id || !Array.isArray(row.roots))
    return null;
  if (
    row.roots.some(
      (root) => typeof root?.path !== "string" || !isAbsolute(root.path),
    )
  )
    return null;
  return {
    id: row.id,
    name: clip(row.name, 500),
    roots: row.roots.map((root) => root.path),
  };
}

function threadRow(row, archived, attachmentOwner) {
  if (
    typeof row?.id !== "string" ||
    !row.id ||
    typeof row.cwd !== "string" ||
    !isAbsolute(row.cwd)
  )
    return null;
  return {
    id: row.id,
    cwd: row.cwd,
    title: clip(row.name ?? row.preview, 500) || "Untitled",
    status:
      typeof row.status === "string"
        ? row.status
        : (row.status?.type ?? "unknown"),
    source:
      typeof row.source === "string"
        ? clip(row.source, 100)
        : row.source && typeof row.source === "object"
          ? redact(row.source)
          : "unknown",
    thread_source: clip(row.threadSource, 100) || null,
    updated_at: row.updatedAt,
    created_at: row.createdAt,
    parent_thread_id: clip(row.parentThreadId, 160) || null,
    native_project_id:
      typeof row.projectId === "string" && row.projectId ? row.projectId : null,
    archived,
    ...(attachmentOwner ? { attached_to_thread_id: attachmentOwner } : {}),
  };
}

async function advance(stream, read, normalize, maxPages) {
  for (let index = 0; index < maxPages && !stream.exhausted; index++) {
    const page = await read({ cursor: stream.cursor, limit: PAGE_SIZE });
    fail(
      Array.isArray(page?.data) && page.data.length <= PAGE_SIZE,
      "HOST_PROTOCOL_ERROR",
      "Native discovery did not return a bounded page",
      502,
    );
    const next = page.nextCursor ?? null;
    fail(
      next === null ||
        (typeof next === "string" &&
          next.length > 0 &&
          next.length <= 16384 &&
          !stream.cursors.has(next)),
      "HOST_PROTOCOL_ERROR",
      "Native discovery repeated or returned an invalid cursor",
      502,
    );
    for (const record of page.data) {
      const row = normalize(record);
      if (row) stream.rows.set(row.id, row);
      else stream.skipped++;
    }
    stream.pages++;
    stream.exhausted = next === null;
    if (next) stream.cursors.add(next);
    stream.cursor = next ?? undefined;
  }
}

export function streamCoverage(stream) {
  if (!stream) return null;
  return {
    count: stream.rows.size,
    pages: stream.pages,
    exhausted: stream.exhausted,
    complete: stream.exhausted && stream.skipped === 0 && !stream.unavailable,
    skipped: stream.skipped,
  };
}

export async function advanceInventory(previous, history, maxPages) {
  const next = structuredClone(previous);
  const warnings = [];
  for (const key of ["active", "archived"]) {
    const stream = next[key];
    if (!stream) continue;
    const archived = key === "archived";
    await advance(
      stream,
      (page) => history.list({ ...page, archived }),
      (row) => threadRow(row, archived),
      maxPages,
    );
    if (stream.skipped)
      warnings.push({
        code: "NATIVE_THREAD_RECORD_INVALID",
        message:
          "Some native thread records had no usable identity or absolute project path",
        stream: key,
        count: stream.skipped,
      });
  }
  let projectError = next.projects?.unavailable ?? null;
  if (next.projects && !projectError) {
    try {
      await advance(
        next.projects,
        (page) => history.projectCatalog(page),
        projectRow,
        maxPages,
      );
      if (next.projects.skipped)
        warnings.push({
          code: "NATIVE_PROJECT_RECORD_INVALID",
          message:
            "Some native projects had no usable identity or root descriptor",
          count: next.projects.skipped,
        });
    } catch (error) {
      projectError = publicError(error);
      if (
        error.code === "CODEX_RPC_ERROR" &&
        [-32601, -32602].includes(error.details?.rpc_code)
      ) {
        next.projects.exhausted = true;
        next.projects.unavailable = projectError;
      }
    }
  }
  if (projectError)
    warnings.push({
      code: "NATIVE_PROJECT_CATALOG_UNAVAILABLE",
      message: "The native project catalog could not be read completely",
      details: { reason: projectError.code },
    });
  const threads = new Map(next.archived?.rows);
  // A thread can move between streams during a multi-page scan. Keep one row
  // and record the overlap rather than treating two observations as two chats.
  const overlaps = [];
  for (const [id, row] of next.active.rows) {
    if (threads.has(id)) overlaps.push(id);
    threads.set(id, row);
  }
  if (overlaps.length)
    warnings.push({
      code: "NATIVE_ARCHIVE_CHANGED_DURING_DISCOVERY",
      message:
        "Some threads appeared in both lists while discovery was running; refresh their archive state",
      count: overlaps.length,
    });
  return {
    inventory: next,
    threads,
    warnings,
    projectError,
    overlapCount: overlaps.length,
  };
}

export function newAttachmentInventory(threads, includeArchived) {
  const inventory = {
    includeArchived,
    queue: [],
    owners: new Set(),
    rows: new Map(),
    pages: 0,
    warnings: [],
  };
  for (const thread of threads) enqueueAttachmentOwner(inventory, thread);
  return inventory;
}

function enqueueAttachmentOwner(inventory, owner) {
  if (inventory.owners.has(owner.id)) return;
  inventory.owners.add(owner.id);
  for (const archived of inventory.includeArchived ? [false, true] : [false]) {
    inventory.queue.push({ owner, archived, stream: newStream() });
  }
}

export async function advanceAttachments(
  previous,
  read,
  accept,
  maxPages = 256,
) {
  const next = structuredClone(previous);
  for (let consumed = 0; next.queue.length && consumed < maxPages;) {
    const batch = next.queue.splice(0, Math.min(8, maxPages - consumed));
    consumed += batch.length;
    const results = await Promise.allSettled(
      batch.map(({ owner, archived, stream }) =>
        advance(
          stream,
          (page) => read(owner, { ...page, archived }),
          (row) => threadRow(row, archived, owner.id),
          1,
        ),
      ),
    );
    for (const [index, result] of results.entries()) {
      const { owner, archived, stream } = batch[index];
      if (result.status === "rejected") {
        const error = publicError(result.reason);
        const unsupported =
          error.code === "CODEX_RPC_ERROR" &&
          [-32601, -32602].includes(error.details?.rpc_code);
        next.warnings.push({
          code: unsupported
            ? "NATIVE_ATTACHMENT_LIST_UNAVAILABLE"
            : "NATIVE_ATTACHMENT_PAGE_FAILED",
          message: unsupported
            ? "This Codex version cannot list attached native chats"
            : "A page of attached native chats could not be read",
          thread_id: owner.id,
          details: { reason: error.code },
        });
        if (unsupported) {
          next.queue = [];
          return next;
        }
        // Other pages in this batch remain usable. Refresh can retry the failed scope.
        continue;
      }
      next.pages++;
      if (stream.skipped)
        next.warnings.push({
          code: "NATIVE_ATTACHMENT_RECORD_INVALID",
          message:
            "An attached native chat had no usable identity or absolute path",
          thread_id: owner.id,
        });
      for (const row of stream.rows.values()) {
        if (row.id === owner.id) {
          next.warnings.push({
            code: "NATIVE_ATTACHMENT_FILTER_UNVERIFIED",
            message:
              "The native host returned the parent chat as its own attachment",
            thread_id: owner.id,
          });
          continue;
        }
        if (!accept(row)) {
          next.warnings.push({
            code: "NATIVE_ATTACHMENT_OUTSIDE_PROJECT",
            message:
              "An attached chat belongs to another project or has an unavailable folder",
            thread_id: owner.id,
          });
          continue;
        }
        if (!next.owners.has(row.id)) next.rows.set(row.id, row);
        enqueueAttachmentOwner(next, row);
      }
      if (!stream.exhausted) {
        stream.rows.clear();
        stream.skipped = 0;
        next.queue.push({ owner, archived, stream });
      }
    }
  }
  return next;
}
