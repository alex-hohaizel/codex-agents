import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, lstat, symlink } from 'node:fs/promises';
import { realpathSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Store } from '../../server/store.mjs';
import { RetentionManager } from '../../server/retention.mjs';

const AT = Date.parse('2026-11-09T12:00:00Z');
const OLD = '2025-01-01T00:00:00Z';
const RECENT = '2026-11-08T12:00:00Z';
const MIDDLE = '2026-09-20T12:00:00Z';
const categories = { 'native-controller': 'controller-backups', 'optional-update': 'optional-updates' };
async function fixture(t, policy = {}) {
  const home = await mkdtemp(join(realpathSync(tmpdir()), 'atelier-retention-controller-'));
  const dataDir = join(home, 'private-service'), native = join(home, 'native-product');
  await mkdir(dataDir); await mkdir(native);
  await writeFile(join(native, 'KEEP.json'), 'NATIVE-STATE-MUST-REMAIN');
  const store = new Store(join(dataDir, 'service.sqlite'));
  store.put('settings', 'owner', {});
  store.put('project', 'project_A', { id: 'project_A', root: native });
  const manager = new RetentionManager({ store, dataDir, clock: () => AT });
  manager.configure({ confirmed: true, policy: { event_days: 30, history_days: 90, input_cache_days: 30, backup_days: 90, automatic: false, ...policy } });
  t.after(async () => { store.close(); await rm(home, { recursive: true, force: true }); });
  return { home, dataDir, native, store, manager };
}
async function copy(f, kind, ident, options = {}) {
  const directory = join(f.dataDir, categories[kind], ident);
  await mkdir(directory, { recursive: true });
  const file = kind === 'native-controller' ? join(directory, 'state.json') : join(directory, 'before', 'SKILL.md');
  if (kind === 'optional-update') await mkdir(join(directory, 'before'));
  await writeFile(file, `PRIVATE-STATE-CANARY-${ident}`);
  const row = { id: ident, backup_id: ident, status: 'completed', completed_at: RECENT,
    root: f.native, ...(kind === 'native-controller' ? { project_id: 'project_A' } : { source_root: join(f.native, 'optional-source') }), ...options };
  f.store.put(kind, ident, row);
  return { row, directory, file };
}
const confirmed = p => ({ preview_id: p.preview_id, sha256: p.sha256, confirmed: true });
const absent = async path => assert.rejects(lstat(path), error => error.code === 'ENOENT');

test('explicit project forgetting removes both owned operation copy trees and associated receipts, preserving native state', async t => {
  const f = await fixture(t);
  const native = await copy(f, 'native-controller', 'native_one');
  const optional = await copy(f, 'optional-update', 'optional_one');
  const unrelated = await copy(f, 'optional-update', 'unrelated', { root: join(f.home, 'other'), source_root: join(f.home, 'other-source') });
  const before = f.store.export();
  const p = await f.manager.preview({ forget_project_ids: ['project_A'] });
  assert.equal(p.counts.operation_copies, 2);
  const result = await f.manager.apply(confirmed(p));
  assert.equal(result.native_projects_changed, false);
  await absent(native.directory); await absent(optional.directory);
  assert.equal(f.store.get('native-controller', native.row.id), null);
  assert.equal(f.store.get('optional-update', optional.row.id), null);
  assert.equal(await readFile(join(f.native, 'KEEP.json'), 'utf8'), 'NATIVE-STATE-MUST-REMAIN');
  assert.match(await readFile(unrelated.file, 'utf8'), /PRIVATE-STATE-CANARY/);
  f.store.restore(before, (kind, row) => f.manager.sanitizeRestored(kind, row));
  assert.equal(f.store.get('native-controller', native.row.id), null);
  assert.equal(f.store.get('optional-update', optional.row.id), null);
});

test('backup expiry prunes raw copies without prematurely deleting retained history and invalidates old restored backup claims', async t => {
  const f = await fixture(t, { history_days: null, backup_days: 1 });
  const c = await copy(f, 'native-controller', 'native_backup_old', { completed_at: OLD, result: { note: 'History is retained' } });
  const original = f.store.get('native-controller', c.row.id);
  const p = await f.manager.preview();
  assert.equal(p.counts.operation_copies, 1);
  await f.manager.apply(confirmed(p));
  await absent(c.directory);
  assert.equal(f.store.get('native-controller', c.row.id).result.note, 'History is retained');
  assert.equal(f.store.get('native-controller', c.row.id).backup_pruned, true);
  assert.equal(f.manager.sanitizeRestored('native-controller', original).backup_pruned, true);
});

test('history expiry retains only minimal association metadata for longer-lived copies; later expiry still cleans them after restore', async t => {
  const f = await fixture(t, { history_days: 30, backup_days: 90 });
  const c = await copy(f, 'optional-update', 'optional_history_old', { completed_at: MIDDLE, private_result: 'PRIVATE-HISTORY-CONTENT' });
  const before = f.store.export();
  const p = await f.manager.preview();
  assert.equal(p.counts.operation_copies, 0);
  assert.equal(p.counts.retained_operation_copy_indexes, 1);
  await f.manager.apply(confirmed(p));
  assert.equal(f.store.get('optional-update', c.row.id), null);
  const marker = f.store.get('operation-copy', `optional-update:${c.row.id}`);
  assert.ok(marker);
  assert.ok(!JSON.stringify(marker).includes('PRIVATE-HISTORY-CONTENT'));
  assert.ok(!JSON.stringify(marker).includes(f.native));
  assert.match(await readFile(c.file, 'utf8'), /PRIVATE-STATE-CANARY/);
  f.store.restore(before, (kind, row) => f.manager.sanitizeRestored(kind, row));
  assert.equal(f.store.get('optional-update', c.row.id), null);
  assert.ok(f.store.get('operation-copy', marker.id));
  f.manager.clock = () => Date.parse('2027-03-01T12:00:00Z');
  const later = await f.manager.preview();
  assert.equal(later.counts.operation_copies, 1);
  await f.manager.apply(confirmed(later));
  await absent(c.directory);
  assert.equal(f.store.get('operation-copy', marker.id), null);
});

test('project forgetting discovers retained operation copies by source-root hashes after their original receipts expired', async t => {
  const f = await fixture(t, { history_days: 30, backup_days: null });
  const c = await copy(f, 'optional-update', 'optional_retained', { completed_at: MIDDLE });
  const first = await f.manager.preview(); await f.manager.apply(confirmed(first));
  assert.equal(f.store.get('optional-update', c.row.id), null);
  assert.ok(f.store.get('operation-copy', `optional-update:${c.row.id}`));
  const p = await f.manager.preview({ forget_project_ids: ['project_A'] });
  assert.equal(p.counts.operation_copies, 1);
  await f.manager.apply(confirmed(p));
  await absent(c.directory);
  assert.equal(f.store.get('operation-copy', `optional-update:${c.row.id}`), null);
});

test('pending and unknown native/optional operations prevent cleanup; uncorrelated directories are never eligible', async t => {
  const f = await fixture(t);
  for (const kind of Object.keys(categories)) for (const status of ['pending', 'outcome_unknown']) {
    const c = await copy(f, kind, `${kind.replaceAll('-', '_')}_${status}`, { status });
    await assert.rejects(f.manager.preview({ forget_project_ids: ['project_A'] }), error => error.code === 'WRITER_CONFLICT');
    assert.match(await readFile(c.file, 'utf8'), /PRIVATE-STATE-CANARY/);
    f.store.db.prepare('DELETE FROM records WHERE kind=? AND id=?').run(kind, c.row.id);
  }
  await assert.rejects(f.manager.file('controller-backups/unowned'), error => error.code === 'OUTSIDE_ROOT');
  const c = await copy(f, 'native-controller', 'native_owned');
  await assert.rejects(f.manager.file(`controller-backups/${c.row.id}/state.json`), error => error.code === 'OUTSIDE_ROOT');
  await assert.rejects(f.manager.file(`controller-backups/${c.row.id}`, null, { kind: 'optional-update', record_id: c.row.id, backup_id: c.row.id, relative: `controller-backups/${c.row.id}` }), error => error.code === 'OUTSIDE_ROOT');
});

test('operation copy symlinks and post-preview replacements are rejected without following or deleting their targets', async t => {
  const f = await fixture(t);
  const c = await copy(f, 'native-controller', 'native_symlink');
  await symlink(join(f.native, 'KEEP.json'), join(c.directory, 'linked.json'));
  await assert.rejects(f.manager.preview({ forget_project_ids: ['project_A'] }), error => error.code === 'OUTSIDE_ROOT');
  await rm(join(c.directory, 'linked.json'));
  const p = await f.manager.preview({ forget_project_ids: ['project_A'] });
  await writeFile(c.file, 'NEW-UNREVIEWED-BYTES');
  await assert.rejects(f.manager.apply(confirmed(p)), error => error.code === 'REVISION_CONFLICT');
  assert.equal(await readFile(c.file, 'utf8'), 'NEW-UNREVIEWED-BYTES');
  assert.equal(await readFile(join(f.native, 'KEEP.json'), 'utf8'), 'NATIVE-STATE-MUST-REMAIN');
});

test('pending cleanup retains exact operation ownership after receipt tombstones and restore; restart can finish only unchanged bytes', async t => {
  const f = await fixture(t);
  const c = await copy(f, 'native-controller', 'native_interrupted');
  const before = f.store.export();
  const p = await f.manager.preview({ forget_project_ids: ['project_A'] });
  f.manager.finishFiles = async () => { throw new Error('Synthetic interruption after tombstones'); };
  await assert.rejects(f.manager.apply(confirmed(p)), /Synthetic interruption/);
  assert.equal(f.store.get('native-controller', c.row.id), null);
  const pending = f.store.get('privacy-cleanup', p.preview_id);
  assert.equal(pending.files[0].owned_operation.record_id, c.row.id);
  f.store.restore(before, (kind, row) => f.manager.sanitizeRestored(kind, row));
  assert.equal(f.store.get('native-controller', c.row.id), null);
  const resumed = new RetentionManager({ store: f.store, dataDir: f.dataDir, clock: () => AT });
  await resumed.finishFiles(p.preview_id);
  await absent(c.directory);
  assert.equal(f.store.get('privacy-cleanup', p.preview_id).status, 'completed');
  assert.equal(await readFile(join(f.native, 'KEEP.json'), 'utf8'), 'NATIVE-STATE-MUST-REMAIN');
});

test('restarted operation-copy cleanup refuses replacement bytes even after the original owner receipt was forgotten', async t => {
  const f = await fixture(t);
  const c = await copy(f, 'optional-update', 'optional_interrupted');
  const p = await f.manager.preview({ forget_project_ids: ['project_A'] });
  f.manager.finishFiles = async () => { throw new Error('Synthetic file-cleanup interruption'); };
  await assert.rejects(f.manager.apply(confirmed(p)), /Synthetic file-cleanup interruption/);
  assert.equal(f.store.get('optional-update', c.row.id), null);
  await writeFile(c.file, 'REPLACEMENT-IS-NOT-AUTHORIZED');
  const resumed = new RetentionManager({ store: f.store, dataDir: f.dataDir, clock: () => AT });
  await assert.rejects(resumed.finishFiles(p.preview_id), error => error.code === 'REVISION_CONFLICT');
  assert.equal(await readFile(c.file, 'utf8'), 'REPLACEMENT-IS-NOT-AUTHORIZED');
  assert.equal(await readFile(join(f.native, 'KEEP.json'), 'utf8'), 'NATIVE-STATE-MUST-REMAIN');
});
