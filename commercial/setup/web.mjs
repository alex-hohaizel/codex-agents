#!/usr/bin/env node
/** Local browser controls for the existing buyer setup transaction engine. */
import { createServer } from 'node:http';
import { randomUUID, createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { homedir, platform as hostPlatform } from 'node:os';
import { resolve, join, dirname, relative, sep, isAbsolute } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { readFile, mkdir, open, rename, lstat, realpath, unlink } from 'node:fs/promises';

const HERE = dirname(fileURLToPath(import.meta.url));
const HASH = /^[a-f0-9]{64}$/;
const PURCHASE_MAX = 256 * 1024;
const PURCHASE_BODY_MAX = 4 * Math.ceil(PURCHASE_MAX / 3) + 128;
const PRODUCT_VERSION = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[A-Za-z0-9.-]+)?$/;
const LOCALES = new Set(['en', 'uk']);
const LOCALE_SCHEMA = 'codex-agents.setup-locale/1';
const MUTATIONS = new Set(['install', 'resume', 'rollback', 'uninstall']);
const ACTIONS = new Set(['doctor', 'audit', 'install', 'verify', 'discover', 'resume', 'rollback', 'uninstall', 'first-task', 'practice', 'open-practice', 'open-codex', 'refresh', 'shutdown']);
const below = (root, path) => { const tail = relative(root, resolve(path)); return tail !== '' && tail !== '..' && !tail.startsWith('..' + sep) && !isAbsolute(tail); };
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const requireThat = (ok, code, message, status = 400) => { if (!ok) { const error = new Error(message); Object.assign(error, { code, status }); throw error; } };
const publicError = error => ({ status: 'blocked', code: error.code || 'SETUP_ERROR', reason: error.message || 'The setup operation could not be completed.' });

async function regularFile(path, max = 2 * 1024 * 1024) {
  const info = await lstat(path);
  requireThat(info.isFile() && !info.isSymbolicLink() && info.nlink === 1 && info.size <= max, 'INVALID_FILE', 'Expected a bounded regular setup file.');
  return readFile(path);
}
async function safeDirectory(path) {
  const absolute = resolve(path);
  let cursor = absolute;
  while (true) {
    try { const info = await lstat(cursor); requireThat(info.isDirectory() && !info.isSymbolicLink(), 'LINKED_PATH', 'The installer needs an ordinary local directory.'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = dirname(cursor); if (parent === cursor) break; cursor = parent;
  }
  return absolute;
}

async function dependencies(packageRoot) {
  const base = join(packageRoot, 'product', 'apps', 'agent-atelier', 'server');
  await regularFile(join(base, 'session.mjs'));
  const { OwnerSession, launchToken } = await import(pathToFileURL(join(base, 'session.mjs')).href);
  const { parseStrictJson } = await import(pathToFileURL(join(base, 'utils.mjs')).href);
  const platformTools = await import(pathToFileURL(join(base, 'platform.mjs')).href);
  return { OwnerSession, launchToken, parseStrictJson, platformTools };
}

async function jsonBody(req, parseStrictJson, max = 32 * 1024) {
  requireThat((req.headers['content-type'] || '').split(';')[0].trim().toLowerCase() === 'application/json', 'JSON_REQUIRED', 'Send a JSON command.', 415);
  requireThat(!req.headers['content-length'] || Number(req.headers['content-length']) <= max, 'BODY_TOO_LARGE', 'The command is too large.', 413);
  let length = 0; const chunks = [];
  for await (const chunk of req) { length += chunk.length; requireThat(length <= max, 'BODY_TOO_LARGE', 'The command is too large.', 413); chunks.push(chunk); }
  const body = parseStrictJson(Buffer.concat(chunks).toString('utf8'), max);
  requireThat(body && typeof body === 'object' && !Array.isArray(body), 'INVALID_COMMAND', 'Expected one command object.');
  return body;
}

export async function start(options = {}) {
  const packageRoot = await realpath(resolve(options.packageRoot || resolve(HERE, '..')));
  const home = await safeDirectory(options.home || homedir());
  const state = await safeDirectory(options.state || join(home, '.local', 'share', 'codex-agent-system'));
  const requestedPython = options.pythonPath || process.env.AGENT_SYSTEM_PYTHON;
  requireThat(typeof requestedPython === 'string' && requestedPython.length > 0 && isAbsolute(requestedPython), 'PYTHON_REQUIRED', 'Start through the packaged launcher so the bundled Python can be selected.');
  const pythonPath = await realpath(requestedPython);
  await regularFile(pythonPath, 512 * 1024 * 1024);
  const setupScript = join(packageRoot, 'setup', 'setup.py');
  await regularFile(setupScript);
  const { OwnerSession, launchToken, parseStrictJson, platformTools } = await dependencies(packageRoot);
  const secure = (path, directory = false) => platformTools.securePrivatePath(path, { directory, pythonPath });
  const uiState = join(state, 'web-setup');
  await mkdir(uiState, { recursive: true, mode: 0o700 }); await secure(uiState, true);
  const localePath = join(uiState, 'locale.json');
  async function readLocale() {
    try {
      const bytes = await regularFile(localePath, 1024);
      await platformTools.assertPrivatePath(localePath, { pythonPath });
      const record = parseStrictJson(bytes.toString('utf8'), 1024);
      requireThat(record?.schema === LOCALE_SCHEMA && LOCALES.has(record.locale) && Object.keys(record).length === 2,
        'UNKNOWN_LOCALE_RECORD', 'The saved language record is not recognized. Preserve it before repairing the preference.', 409);
      return record.locale;
    } catch (error) {
      if (error.code === 'ENOENT') return null;
      throw error;
    }
  }
  let preferredLocale = await readLocale().catch(() => null);
  async function saveLocale(locale) {
    if (await readLocale() !== locale) {
      const temporary = localePath + '.' + randomUUID() + '.tmp';
      const file = await open(temporary, 'wx', 0o600);
      try {
        try {
          await secure(temporary);
          await file.writeFile(JSON.stringify({ schema: LOCALE_SCHEMA, locale }) + '\n');
          await file.sync();
        } finally { await file.close(); }
        await rename(temporary, localePath);
        await platformTools.syncDirectory(uiState);
      } finally { await unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error; }); }
    }
    preferredLocale = locale;
    return { preferred_locale: preferredLocale };
  }
  const plansDirectory = join(uiState, 'plans');
  await mkdir(plansDirectory, { recursive: true, mode: 0o700 }); await secure(plansDirectory, true);
  const session = new OwnerSession();
  const plans = new Map(), operations = new Map(), practices = new Map();
  const operationKeys = new Map();
  const jobs = new Map(); const results = Object.create(null);
  let activeJob = null, stopping = false, origin, cookieName;
  let purchaseDocument = null;
  const instanceId = randomUUID();
  let product;
  try {
    const manifest = parseStrictJson((await regularFile(join(packageRoot, 'product-manifest.json'), 16 * 1024 * 1024)).toString('utf8'), 16 * 1024 * 1024);
    product = { name: 'Codex Agent System', product_id: manifest.product_id, version: manifest.product_version, source_commit: manifest.source_commit, edition: manifest.edition, received_manifest: true };
  } catch (error) { product = { name: 'Codex Agent System', received_manifest: false }; }
  const commandArgs = (command, extra = [], locale = 'en') => [
    '-I', '-X', 'utf8', '-B', setupScript, '--package', packageRoot, '--home', home, '--state', state,
    '--locale', locale, '--json', ...(options.codexPath ? ['--codex', options.codexPath] : []), command, ...extra,
  ];

  function purchaseSummary(bytes) {
    let document;
    try { document = parseStrictJson(new TextDecoder('utf-8', { fatal: true }).decode(bytes), PURCHASE_MAX); }
    catch { requireThat(false, 'INVALID_PURCHASE_DOCUMENT', 'Choose an original UTF-8 JSON purchase document from your trusted delivery.'); }
    const object = value => value && typeof value === 'object' && !Array.isArray(value);
    requireThat(object(document), 'INVALID_PURCHASE_DOCUMENT', 'Expected an original purchase document object.');
    let entitlement = document;
    if (document.schema === 'codex-agents.purchase-confirmation/1') {
      entitlement = document.entitlement;
      requireThat(object(entitlement) && document.mode === entitlement.mode, 'INVALID_PURCHASE_DOCUMENT', 'The confirmation and its purchase document do not agree.');
    }
    requireThat(object(entitlement) && entitlement.schema === 'codex-agents.purchase-entitlement/1' &&
      ['test-not-a-purchase', 'purchased'].includes(entitlement.mode), 'INVALID_PURCHASE_DOCUMENT', 'This purchase document format is not supported.');
    requireThat(entitlement.product_id === 'codex-agent-system' && product.product_id === entitlement.product_id,
      'WRONG_PURCHASE_PRODUCT', 'The purchase document belongs to another product.');
    requireThat(['solo', 'team'].includes(entitlement.edition) && entitlement.named_seats === ({ solo: 1, team: 5 })[entitlement.edition] &&
      (product.edition === 'unassigned' || product.edition === entitlement.edition), 'WRONG_PURCHASE_EDITION', 'Choose the purchase document for this package edition.');
    const purchased = typeof entitlement.purchased_version === 'string' && PRODUCT_VERSION.exec(entitlement.purchased_version);
    const current = typeof product.version === 'string' && PRODUCT_VERSION.exec(product.version);
    requireThat(Number.isSafeInteger(entitlement.purchased_product_major) && entitlement.purchased_product_major >= 0 && purchased && current &&
      Number(purchased[1]) === entitlement.purchased_product_major && Number(current[1]) === entitlement.purchased_product_major,
      'WRONG_PURCHASE_MAJOR', 'This document does not cover the package product major. Keep your original document and use the purchased version.');
    requireThat(typeof entitlement.order_id === 'string' && /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(entitlement.order_id) &&
      entitlement.acquired_use === 'perpetual-purchased-product-major' && entitlement.included_updates === 'purchased-product-major',
      'INVALID_PURCHASE_DOCUMENT', 'The recorded purchase rights are not supported.');
    return { status: 'document-ready', sha256: sha(bytes), edition: entitlement.edition, purchased_product_major: entitlement.purchased_product_major };
  }
  async function checkedPurchaseDocument() {
    if (!purchaseDocument) return options.entitlementPath ? resolve(options.entitlementPath) : null;
    try {
      await safeDirectory(dirname(purchaseDocument.path));
      await platformTools.assertPrivatePath(dirname(purchaseDocument.path), { directory: true, pythonPath });
      await platformTools.assertPrivatePath(purchaseDocument.path, { pythonPath });
      requireThat(sha(await regularFile(purchaseDocument.path, PURCHASE_MAX)) === purchaseDocument.summary.sha256,
        'PURCHASE_DOCUMENT_CHANGED', 'The selected purchase document changed. Preserve it and select the original document again.', 409);
    } catch { requireThat(false, 'PURCHASE_DOCUMENT_CHANGED', 'The selected purchase document changed or is unavailable. Preserve it and select the original document again.', 409); }
    return purchaseDocument.path;
  }
  async function keepPurchaseDocument(body) {
    requireThat(Object.keys(body).length === 1 && typeof body.document_base64 === 'string', 'INVALID_PURCHASE_DOCUMENT', 'Send only the selected purchase document bytes.');
    const encoded = body.document_base64;
    requireThat(encoded.length > 0 && encoded.length <= 4 * Math.ceil(PURCHASE_MAX / 3) &&
      /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(encoded),
      'INVALID_PURCHASE_DOCUMENT', 'The selected document encoding is invalid or too large.');
    const bytes = Buffer.from(encoded, 'base64');
    requireThat(bytes.length > 0 && bytes.length <= PURCHASE_MAX && bytes.toString('base64') === encoded,
      'INVALID_PURCHASE_DOCUMENT', 'The selected document encoding is invalid or too large.');
    const summary = purchaseSummary(bytes);
    const directory = join(uiState, 'purchase-documents');
    requireThat(![packageRoot, join(home, '.agents', 'skills'), join(home, '.codex', 'skills')].some(root => directory === root || below(root, directory)),
      'INVALID_PURCHASE_STORAGE', 'Purchase documents must stay outside the package and skill discovery folders.');
    await safeDirectory(directory); await mkdir(directory, { recursive: true, mode: 0o700 }); await secure(directory, true);
    // Each explicit selection gets its own record. A kill during this write
    // can leave an inactive partial record; selecting the original again can
    // recover without overwriting or reusing that unknown file.
    const path = join(directory, summary.sha256 + '-' + randomUUID() + '.json');
    const file = await open(path, 'wx', 0o600);
    try { await secure(path); await file.writeFile(bytes); await file.sync(); } finally { await file.close(); }
    await platformTools.syncDirectory(directory);
    await platformTools.assertPrivatePath(path, { pythonPath });
    requireThat((await regularFile(path, PURCHASE_MAX)).equals(bytes), 'PURCHASE_DOCUMENT_CHANGED', 'An existing purchase document changed. Preserve it and reconcile the original record.', 409);
    purchaseDocument = { path, summary };
    return summary;
  }

  function run(command, extra, job, locale) {
    return new Promise(resolveJob => {
      const child = spawn(pythonPath, commandArgs(command, extra, locale), {
        cwd: packageRoot, shell: false, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONDONTWRITEBYTECODE: '1' },
      });
      child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
      let output = '', errorOutput = '', truncated = false, settled = false;
      const capture = (chunk, stderr = false) => {
        const text = typeof chunk === 'string' ? chunk : chunk.toString('utf8');
        if (stderr) errorOutput = (errorOutput + text).slice(-256 * 1024);
        else if (Buffer.byteLength(output) + Buffer.byteLength(text) <= 2 * 1024 * 1024) output += text;
        else truncated = true;
      };
      child.stdout.on('data', chunk => capture(chunk)); child.stderr.on('data', chunk => capture(chunk, true));
      const attention = setTimeout(() => { if (!settled) job.attention = 'The operation is taking longer than expected. Keep this window open; do not start another installer.'; }, 180_000);
      const done = (code, spawnError) => {
        if (settled) return; settled = true; clearTimeout(attention);
        let receipt;
        if (!spawnError && !truncated) {
          for (const content of [output, errorOutput]) {
            try { receipt = parseStrictJson(content.trim(), 2 * 1024 * 1024); if (receipt && typeof receipt === 'object' && !Array.isArray(receipt)) break; receipt = undefined; } catch {}
          }
        }
        if (!receipt) receipt = { status: 'blocked', reason: spawnError?.message || (truncated ? 'Setup output exceeded its safety bound.' : 'The setup engine did not return a readable result.'), diagnostic: errorOutput.slice(-2500), outcome: MUTATIONS.has(job.action) ? 'unverified-read-journal-before-retry' : 'not-observed' };
        resolveJob({ ...receipt, exit_code: code ?? null });
      };
      child.once('error', error => done(null, error)); child.once('close', code => done(code));
    });
  }
  async function refreshOperations(job, locale) {
    const receipt = await run('operations', [], job, locale);
    if (receipt.status === 'ready' && Array.isArray(receipt.operations)) {
      operations.clear();
      for (const row of receipt.operations.slice(0, 200)) {
        if (!row || typeof row.journal !== 'string' || !below(state, row.journal)) continue;
        const id = operationKeys.get(row.journal) || randomUUID(); operationKeys.set(row.journal, id);
        operations.set(id, { ...row, id });
      }
    }
    results.operations = { ...receipt, operations: [...operations.values()].map(({ plan, journal, ...row }) => ({ ...row, journal_display: journal })) };
    const current = await run('status', [], job, locale); results.status = current;
    if (typeof current.journal === 'string' && below(state, current.journal) && ![...operations.values()].some(row => row.journal === current.journal)) {
      const id = operationKeys.get(current.journal) || randomUUID(); operationKeys.set(current.journal, id);
      operations.set(id, { id, journal: current.journal, status: current.status, can_resume: false });
    }
    return { status: 'ready', installed: current, operations: [...operations.values()].map(({ plan, journal, ...row }) => ({ ...row, journal_display: journal })) };
  }
  async function perform(body, job) {
    const locale = body.locale ?? preferredLocale ?? 'en';
    if (body.action === 'audit') {
      requireThat(plans.size < 64, 'PLAN_LIMIT', 'Reopen setup before creating more audit plans.', 429);
      const id = randomUUID(), plan = join(plansDirectory, id + '.json');
      const entitlement = await checkedPurchaseDocument();
      const extra = ['--plan', plan, ...(entitlement ? ['--entitlement', entitlement] : [])];
      const receipt = await run('audit', extra, job, locale);
      if (receipt.plan_sha256) {
        requireThat(HASH.test(receipt.plan_sha256) && resolve(receipt.plan) === plan, 'INVALID_PLAN', 'The setup engine returned an unexpected audit identity.');
        const bytes = await regularFile(plan, 16 * 1024 * 1024);
        requireThat(sha(bytes) === receipt.plan_sha256, 'PLAN_CHANGED', 'The audited plan changed. Run a new audit.', 409);
        const document = parseStrictJson(bytes.toString('utf8'), 16 * 1024 * 1024);
        if (purchaseDocument) {
          await checkedPurchaseDocument();
          requireThat(document.entitlement?.sha256 === purchaseDocument.summary.sha256,
            'PURCHASE_DOCUMENT_CHANGED', 'The audited purchase document differs from the selected original. Prepare a new plan.', 409);
        }
        plans.set(id, { path: plan, sha256: receipt.plan_sha256, ready: document.ready === true, journal: receipt.journal, purchase_sha256: purchaseDocument?.summary.sha256 ?? null });
        const preview = receipt.preview || { components: [
          { id: 'skills', target: receipt.destination, action: document.mode },
          { id: 'orchestrator', target: document.optional?.destination || document.optional?.target, action: document.optional?.action },
          { id: 'profile-and-roles', target: join(home, '.codex'), action: 'reviewed-profile-merge' },
        ], conflicts: receipt.blockers || [], preserved_changes: [] };
        const result = { ...receipt, plan_id: id, preview }; delete result.plan;
        results.audit = result; return result;
      }
      results.audit = receipt; return receipt;
    }
    if (body.action === 'install') {
      for (const key of ['install','resume','verify','discover']) delete results[key];
      const plan = plans.get(body.plan_id); requireThat(plan && plan.ready, 'UNKNOWN_PLAN', 'Run and review a ready audit in this window before installing.', 409);
      requireThat(plan.purchase_sha256 === (purchaseDocument?.summary.sha256 ?? null), 'PURCHASE_DOCUMENT_CHANGED', 'Prepare a new plan after selecting a purchase document.', 409);
      await checkedPurchaseDocument();
      requireThat(sha(await regularFile(plan.path, 16 * 1024 * 1024)) === plan.sha256, 'PLAN_CHANGED', 'The audited plan changed. Run a new audit.', 409);
      const receipt = await run('install', ['--plan', plan.path, '--approve', plan.sha256], job, locale);
      results.install = receipt; await refreshOperations(job, locale); return receipt;
    }
    if (['verify', 'discover', 'resume', 'rollback', 'uninstall'].includes(body.action)) {
      if (MUTATIONS.has(body.action)) for (const key of ['install','resume','verify','discover']) delete results[key];
      if (['rollback','uninstall'].includes(body.action)) { plans.clear(); delete results.audit; }
      const operation = operations.get(body.operation_id); requireThat(operation, 'UNKNOWN_OPERATION', 'Refresh the installation history and select a known operation.', 409);
      let command = body.action, extra = ['--journal', operation.journal];
      if (body.action === 'resume') {
        requireThat((operation.can_resume || operation.resumable) && typeof operation.plan === 'string' && HASH.test(operation.plan_sha256), 'NOT_RESUMABLE', 'This operation does not have a checked resumable plan.', 409);
        requireThat(below(state, operation.plan), 'INVALID_OPERATION', 'The recovery plan is outside this installation state.');
        command = 'install'; extra = ['--plan', operation.plan, '--approve', operation.plan_sha256, '--resume', operation.journal];
      }
      const receipt = await run(command, extra, job, locale); results[body.action] = receipt;
      if (body.action !== 'discover') await refreshOperations(job, locale);
      return receipt;
    }
    if (body.action === 'refresh') return refreshOperations(job, locale);
    if (body.action === 'practice') {
      requireThat(practices.size < 20, 'PRACTICE_LIMIT', 'Reuse one of the prepared practice projects.', 429);
      const prepared = await run('prepare-first-task', [], job, locale);
      if (typeof prepared.project !== 'string') { results.practice = prepared; return prepared; }
      requireThat(below(state, prepared.project), 'INVALID_PROJECT', 'The prepared project is outside the fixed setup state.');
      const id = randomUUID();
      const launcher = prepared.launcher; let launcher_sha256;
      if (launcher) { requireThat(below(prepared.project, launcher), 'INVALID_LAUNCHER', 'The practice launcher is outside its owned project.'); launcher_sha256 = sha(await regularFile(launcher, 256 * 1024)); }
      practices.set(id, { project: prepared.project, launcher, launcher_sha256 });
      const result = { ...prepared, practice_id: id, execution_performed: false };
      results.practice = result; return result;
    }
    if (body.action === 'open-practice') {
      const practice = practices.get(body.practice_id); requireThat(practice, 'UNKNOWN_PROJECT', 'Create a practice project in this window first.', 409);
      const project = practice.project;
      const command = hostPlatform() === 'darwin' ? '/usr/bin/open' : hostPlatform() === 'win32' ? 'explorer.exe' : 'xdg-open';
      await new Promise((ok, fail) => {
        const child = spawn(command, [project], { stdio: 'ignore', shell: false, windowsHide: true });
        child.once('error', fail); child.once('spawn', () => { child.unref(); ok(); });
      });
      return { status: 'folder-open-requested', project, execution_performed: false };
    }
    if (body.action === 'open-codex') {
      const practice = practices.get(body.practice_id); requireThat(practice?.launcher, 'LAUNCHER_REQUIRED', 'Install and verify the toolkit, then prepare a new practice project.', 409);
      const bytes = await regularFile(practice.launcher, 256 * 1024);
      requireThat(sha(bytes) === practice.launcher_sha256, 'LAUNCHER_CHANGED', 'The prepared launcher changed. Preserve the edit and create a new practice project.', 409);
      await refreshOperations(job, locale);
      const current = [...operations.values()].find(row => row.journal === results.status?.journal);
      requireThat(current, 'INSTALLATION_REQUIRED', 'Refresh and verify the installed toolkit before opening Codex.', 409);
      const verification = await run('verify', ['--journal', current.journal], job, locale);
      requireThat(verification.status === 'verified-files', 'VERIFICATION_REQUIRED', verification.reason || 'The installed files could not be verified.', 409);
      const launch = async (command, args, environment = {}) => new Promise((ok, fail) => {
        const child = spawn(command, args, { shell: false, stdio: 'ignore', windowsHide: true, env: { ...process.env, ...environment } });
        const deadline = setTimeout(() => { child.unref(); ok(); }, 5000);
        child.once('error', error => { clearTimeout(deadline); fail(error); });
        child.once('exit', code => { clearTimeout(deadline); code === 0 ? ok() : fail(new Error('The desktop launcher did not accept the request. Open the generated launcher manually.')); });
      });
      if (hostPlatform() === 'darwin') await launch('/usr/bin/open', [practice.launcher]);
      else if (hostPlatform() === 'win32') {
        const match = /^@echo off\r?\nsetlocal DisableDelayedExpansion\r?\nset "AGENT_SYSTEM_LAUNCH_FILE=%~f0"\r?\npowershell\.exe -NoLogo -NoProfile -EncodedCommand ([A-Za-z0-9+/]+={0,2})\r?\nexit \/b %ERRORLEVEL%\r?\n:AGENT_SYSTEM_LAUNCH_DATA\r?\n[A-Za-z0-9+/]+={0,2}\r?\n$/.exec(bytes.toString('utf8'));
        requireThat(match, 'INVALID_LAUNCHER', 'The prepared Windows launcher does not match the owned launcher format.');
        const wrapper = `Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoLogo -NoProfile -NoExit -EncodedCommand ${match[1]}'`;
        await launch('powershell.exe', ['-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',Buffer.from(wrapper,'utf16le').toString('base64')], { AGENT_SYSTEM_LAUNCH_FILE: practice.launcher });
      } else {
        let accepted = false;
        for (const [terminal, flag] of [['x-terminal-emulator','-e'],['gnome-terminal','--'],['konsole','-e'],['xfce4-terminal','--execute'],['xterm','-e']]) {
          let command;
          try { command = await platformTools.resolveNativeCommand(terminal, [flag, practice.launcher]); } catch { continue; }
          await launch(command.command, command.args); accepted = true; break;
        }
        requireThat(accepted, 'TERMINAL_REQUIRED', 'A desktop terminal is unavailable. Open the generated project launcher from the displayed folder.');
      }
      return { status: 'launcher-open-requested', project: practice.project, launcher: practice.launcher, execution_performed: false, next: 'Paste the supplied task in your own Codex session; setup has not executed the task.' };
    }
    const receipt = await run(body.action, [], job, locale); results[body.action] = receipt; return receipt;
  }
  const view = () => ({ status: activeJob ? 'running' : 'ready', instance_id: instanceId, product, home, state, results, preferred_locale: preferredLocale, purchase_document: purchaseDocument?.summary ?? null,
    plans: [...plans].map(([id, row]) => ({ id, ready: row.ready, sha256: row.sha256 })),
    operations: [...operations.values()].map(({ plan, journal, ...row }) => ({ ...row, journal_display: journal })),
    active_job: activeJob ? jobs.get(activeJob) : null, jobs: [...jobs.values()].slice(-20),
  });
  const headers = res => {
    res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Content-Type-Options', 'nosniff'); res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
  };
  const json = (res, status, value) => { res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(value)); };
  const authenticated = req => (req.headers.cookie || '').split(';').some(pair => { const [key, ...parts] = pair.trim().split('='); return key === cookieName && session.authenticated(parts.join('=')); });
  const server = createServer(async (req, res) => {
    headers(res);
    try {
      requireThat(req.headers.host === new URL(origin).host, 'INVALID_HOST', 'Unexpected local installer host.', 403);
      requireThat(!req.headers.origin || req.headers.origin === origin, 'CROSS_ORIGIN_DENIED', 'Cross-origin requests are not accepted.', 403);
      const url = new URL(req.url, origin);
      if (req.method === 'GET' && ['/', '/assets/app.mjs', '/assets/style.css'].includes(url.pathname)) {
        const name = url.pathname === '/' ? 'index.html' : url.pathname.slice('/assets/'.length);
        const bytes = await regularFile(join(HERE, 'ui', name), 512 * 1024);
        res.writeHead(200, { 'Content-Type': name.endsWith('.html') ? 'text/html; charset=utf-8' : name.endsWith('.css') ? 'text/css; charset=utf-8' : 'text/javascript; charset=utf-8' }); return res.end(bytes);
      }
      if (req.method === 'GET' && url.pathname === '/health') return json(res, 200, { status: 'ok', product: 'codex-agent-system-setup', instance_id: instanceId });
      if (url.pathname === '/api/session' && req.method === 'POST') {
        requireThat(req.headers.origin === origin, 'CROSS_ORIGIN_DENIED', 'A same-origin launcher claim is required.', 403);
        const body = await jsonBody(req, parseStrictJson);
        requireThat(Object.keys(body).length === 1 && typeof body.launch_token === 'string', 'INVALID_COMMAND', 'Expected the launcher token only.');
        const result = session.claim(body.launch_token);
        res.setHeader('Set-Cookie', `${cookieName}=${result.session}; HttpOnly; SameSite=Strict; Path=/`);
        return json(res, 200, { status: 'ready', csrf_token: result.csrf_token });
      }
      requireThat(authenticated(req), 'SESSION_REQUIRED', 'Open this window through the local installer launcher.', 401);
      if (req.method === 'GET') requireThat(session.csrfAuthorized(req.headers['x-setup-csrf']), 'CSRF_REQUIRED', 'Reopen or refresh this authorized installer window.', 403);
      if (url.pathname === '/api/session' && req.method === 'GET') return json(res, 200, { status: 'ready', csrf_token: session.csrf });
      if (url.pathname === '/api/state' && req.method === 'GET') return json(res, 200, view());
      if (url.pathname === '/api/locale-preference' && req.method === 'POST') {
        requireThat(req.headers.origin === origin && session.csrfAuthorized(req.headers['x-setup-csrf']), 'CSRF_REQUIRED', 'Refresh this local installer before changing the language.', 403);
        const body = await jsonBody(req, parseStrictJson, 1024);
        requireThat(Object.keys(body).length === 1 && LOCALES.has(body.locale), 'INVALID_LOCALE', 'Choose English or Ukrainian.');
        return json(res, 200, await saveLocale(body.locale));
      }
      if (url.pathname === '/api/purchase-document' && req.method === 'POST') {
        requireThat(req.headers.origin === origin && session.csrfAuthorized(req.headers['x-setup-csrf']), 'CSRF_REQUIRED', 'Refresh this local installer before selecting a document.', 403);
        requireThat(!activeJob, 'OPERATION_RUNNING', 'Wait for the current operation to finish before selecting a document.', 409);
        const id = randomUUID(), job = { id, action: 'purchase-document', status: 'running', started_at: new Date().toISOString(), phase: 'purchase-document' };
        jobs.set(id, job); while (jobs.size > 40) jobs.delete(jobs.keys().next().value); activeJob = id;
        plans.clear(); delete results.audit;
        try {
          const body = await jsonBody(req, parseStrictJson, PURCHASE_BODY_MAX);
          const result = await keepPurchaseDocument(body); job.result = result; job.status = 'completed'; return json(res, 200, result);
        } catch (error) {
          const safeError = Object.assign(new Error(error.code === 'BODY_TOO_LARGE' ? 'The selected document is too large.' :
            ['INVALID_PURCHASE_DOCUMENT','WRONG_PURCHASE_PRODUCT','WRONG_PURCHASE_EDITION','WRONG_PURCHASE_MAJOR','PURCHASE_DOCUMENT_CHANGED','INVALID_PURCHASE_STORAGE'].includes(error.code) ? error.message : 'The purchase document could not be retained. Preserve the original and try a new audit.'),
          { code: error.code === 'BODY_TOO_LARGE' ? error.code : ['INVALID_PURCHASE_DOCUMENT','WRONG_PURCHASE_PRODUCT','WRONG_PURCHASE_EDITION','WRONG_PURCHASE_MAJOR','PURCHASE_DOCUMENT_CHANGED','INVALID_PURCHASE_STORAGE'].includes(error.code) ? error.code : 'INVALID_PURCHASE_DOCUMENT', status: error.status || 400 });
          job.result = publicError(safeError); job.status = 'blocked'; throw safeError;
        } finally { job.finished_at = new Date().toISOString(); activeJob = null; }
      }
      requireThat(url.pathname === '/api/action' && req.method === 'POST', 'NOT_FOUND', 'Unknown installer route.', 404);
      requireThat(req.headers.origin === origin && session.csrfAuthorized(req.headers['x-setup-csrf']), 'CSRF_REQUIRED', 'Refresh this local installer before sending a command.', 403);
      const body = await jsonBody(req, parseStrictJson);
      requireThat(ACTIONS.has(body.action), 'UNKNOWN_ACTION', 'Unknown installer command.');
      const allowed = new Set(['action', 'locale', ...(['install'].includes(body.action) ? ['plan_id', 'approved'] : []), ...(['verify', 'discover', 'resume', 'rollback', 'uninstall'].includes(body.action) ? ['operation_id', 'approved'] : []), ...(['open-practice','open-codex'].includes(body.action) ? ['practice_id'] : [])]);
      requireThat(Object.keys(body).every(key => allowed.has(key)), 'INVALID_COMMAND', 'The browser cannot supply paths, commands or unknown options.');
      requireThat(body.locale === undefined || LOCALES.has(body.locale), 'INVALID_LOCALE', 'Choose English or Ukrainian.');
      requireThat(!MUTATIONS.has(body.action) || body.approved === true, 'APPROVAL_REQUIRED', 'Review the displayed action and explicitly confirm it.');
      requireThat(!activeJob, 'OPERATION_RUNNING', 'Wait for the current operation to finish. Its journal will remain available.', 409);
      if (body.action === 'shutdown') {
        stopping = true; json(res, 200, { status: 'stopped' }); setTimeout(() => server.close(), 40).unref(); return;
      }
      const id = randomUUID(); const job = { id, action: body.action, status: 'running', started_at: new Date().toISOString(), phase: body.action };
      jobs.set(id, job); while (jobs.size > 40) jobs.delete(jobs.keys().next().value); activeJob = id;
      json(res, 202, { status: 'running', job_id: id });
      Promise.resolve().then(() => perform(body, job)).then(result => { job.result = result; job.status = 'completed'; })
        .catch(error => { job.result = publicError(error); job.status = 'blocked'; })
        .finally(() => { job.finished_at = new Date().toISOString(); activeJob = null; });
    } catch (error) { if (!res.headersSent) json(res, error.status || 400, publicError(error)); else res.destroy(); }
  });
  await new Promise((ok, fail) => { server.once('error', fail); server.listen(options.port ?? 0, '127.0.0.1', ok); });
  origin = `http://127.0.0.1:${server.address().port}`; cookieName = `agent_system_setup_${server.address().port}`;
  const url = origin + '/#launch=' + encodeURIComponent(launchToken(session.controlKey));
  const stop = async () => { requireThat(!activeJob, 'OPERATION_RUNNING', 'The current operation must finish before shutting down.', 409); stopping = true; await new Promise((ok, fail) => server.close(error => error ? fail(error) : ok())); };
  try { if (options.readyPath) {
    const ready = resolve(options.readyPath); await safeDirectory(dirname(ready));
    try { await lstat(dirname(ready)); await platformTools.assertPrivatePath(dirname(ready), { directory: true, pythonPath }); }
    catch (error) { if (error.code !== 'ENOENT') throw error; await mkdir(dirname(ready), { recursive: true, mode: 0o700 }); await secure(dirname(ready), true); }
    try { const previous = parseStrictJson((await regularFile(ready, 8192)).toString('utf8'), 8192); requireThat(previous.schema === 'codex-agents.setup-web-ready/1', 'UNKNOWN_READY_FILE', 'The ready path already contains an unrelated file. Choose a new private ready path.'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const temporary = ready + '.' + randomUUID() + '.tmp'; const fd = await open(temporary, 'wx', 0o600);
    try { await fd.writeFile(JSON.stringify({ schema: 'codex-agents.setup-web-ready/1', url, pid: process.pid, instance_id: instanceId, package: packageRoot }) + '\n'); await fd.sync(); } finally { await fd.close(); }
    await secure(temporary); await rename(temporary, ready);
  } } catch (error) { await new Promise(ok => server.close(ok)); throw error; }
  return { server, url, origin, instanceId, stop, snapshot: view, get stopping() { return stopping; } };
}

export async function runCli(args = process.argv.slice(2)) {
  const values = Object.create(null);
  for (let i = 0; i < args.length; i++) {
    const key = args[i]; if (key === '--no-open') { values.noOpen = true; continue; }
    requireThat(['--package', '--python', '--home', '--state', '--codex', '--port', '--ready', '--entitlement'].includes(key) && i + 1 < args.length, 'INVALID_ARGUMENT', 'Unknown or incomplete installer argument.');
    values[key.slice(2)] = args[++i];
  }
  requireThat(!values.noOpen || values.ready, 'READY_PATH_REQUIRED', 'Use --ready with --no-open; launcher tokens are not printed to logs.');
  const app = await start({ packageRoot: values.package, pythonPath: values.python, home: values.home, state: values.state, codexPath: values.codex, port: values.port ? Number(values.port) : 0, readyPath: values.ready, entitlementPath: values.entitlement });
  if (!values.noOpen) {
    const command = hostPlatform() === 'darwin' ? '/usr/bin/open' : hostPlatform() === 'win32' ? 'rundll32.exe' : 'xdg-open';
    const argv = hostPlatform() === 'win32' ? ['url.dll,FileProtocolHandler', app.url] : [app.url];
    const child = spawn(command, argv, { stdio: 'ignore', shell: false, windowsHide: true }); child.on('error', () => process.stderr.write('The browser could not be opened. Reopen the installer launcher or use its private ready receipt.\n')); child.unref();
  }
  process.stdout.write(`Codex Agent System setup is running locally at ${app.origin}. Keep this window open during installation.\n`);
  const onSignal = () => { app.stop().catch(() => process.stderr.write('An operation is active. Wait for its journal before closing setup.\n')); };
  process.on('SIGINT', onSignal); process.on('SIGTERM', onSignal);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) runCli().catch(error => { process.stderr.write((error.message || String(error)) + '\n'); process.exitCode = 2; });
