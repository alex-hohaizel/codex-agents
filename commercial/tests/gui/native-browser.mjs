#!/usr/bin/env node
/** Real Chromium buttons against an already running, exact buyer package.
 * No fixture engine, model call, Playwright import, or test-only HTTP mutation.
 * Start setup/web.mjs with the package's bundled runtimes and an empty test HOME.
 */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, mkdtemp, lstat, realpath, rm } from 'node:fs/promises';
import { dirname, join, resolve, relative, sep, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { platform, arch } from 'node:os';
import { securePrivatePath, assertPrivatePath, resolveNativeCommand } from '../../../apps/agent-atelier/server/platform.mjs';

const args = Object.create(null);
for (let i = 2; i < process.argv.length; i++) {
  const flag = process.argv[i];
  assert.ok(['--ready-file','--browser','--output','--python','--timeout-seconds','--expect-codex-version'].includes(flag) && i + 1 < process.argv.length, 'Unknown or incomplete browser-proof argument.');
  assert.equal(args[flag], undefined, 'Duplicate browser-proof argument.');
  args[flag] = process.argv[++i];
}
assert.ok(args['--ready-file'] && args['--output'], 'Use --ready-file PRIVATE_READY.json --output PRIVATE_PROOF_FOLDER [--browser CHROMIUM_EXECUTABLE].');
const deadlineMs = Number(args['--timeout-seconds'] || 180) * 1000;
assert.ok(Number.isFinite(deadlineMs) && deadlineMs >= 1000 && deadlineMs <= 600000, 'Timeout must be between 1 and 600 seconds.');
const pythonPath = args['--python'] || process.env.AGENT_SYSTEM_PYTHON;
const pause = ms => new Promise(ok => setTimeout(ok, ms));
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const below = (root, path) => { const tail = relative(root, resolve(path)); return tail !== '' && tail !== '..' && !tail.startsWith('..' + sep) && !isAbsolute(tail); };
const report = { schema:'codex-agents.native-browser-proof/1', scope:'Actual Chromium pointer interactions, real bundled setup engine, real filesystem, and native Codex discovery. No model task is executed.', started_at:new Date().toISOString(), runner:{os:platform(),architecture:arch(),node:process.version}, steps:[], screenshots:[], model_execution:false };
let output, profile, browser, socket, nextId = 0, browserExit, launchSecret;
const pending = new Map();
const redact = value => String(value).replaceAll(launchSecret || '\0','[REDACTED_LAUNCH_TOKEN]');

async function boundedFile(path, maximum = 32 * 1024 * 1024) {
  const info = await lstat(path);
  assert.ok(info.isFile() && !info.isSymbolicLink() && info.nlink === 1 && info.size <= maximum, 'Expected a bounded ordinary proof input: ' + path);
  return readFile(path);
}
async function until(fn, label, timeout = deadlineMs) {
  const end = Date.now() + timeout; let lastError;
  while (Date.now() < end) {
    if (browserExit !== undefined) throw Error('Chromium exited before ' + label + ' (code ' + browserExit + ').');
    try { const value = await fn(); if (value) return value; } catch (error) { lastError = error; }
    await pause(150);
  }
  throw Error('Timed out waiting for ' + label + (lastError ? ': ' + redact(lastError.message) : '') + '.');
}
function call(method, params = {}) {
  const id = ++nextId;
  return new Promise((ok, fail) => {
    const timer = setTimeout(() => { pending.delete(id); fail(Error('Chromium protocol timed out: ' + method)); }, 30000);
    pending.set(id, { ok:value => { clearTimeout(timer); ok(value); }, fail:error => { clearTimeout(timer); fail(Error(redact(typeof error === 'object' ? JSON.stringify(error) : error))); } });
    try { socket.send(JSON.stringify({id,method,params})); } catch (error) { pending.get(id).fail(error.message); pending.delete(id); }
  });
}
async function evaluate(expression) {
  const reply = await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture:true});
  if (reply.exceptionDetails) throw Error('Browser evaluation failed: ' + redact(JSON.stringify(reply.exceptionDetails)));
  return reply.result.value;
}
async function snapshot() { return evaluate("fetch('/api/state',{cache:'no-store'}).then(async response=>{if(!response.ok)throw Error('State HTTP '+response.status);return response.json()})"); }
async function click(id) {
  const encoded = JSON.stringify(id);
  await until(() => evaluate(`Boolean(document.getElementById(${encoded}) && !document.getElementById(${encoded}).disabled && !document.getElementById(${encoded}).hidden)`), 'enabled visible ' + id);
  await evaluate(`document.getElementById(${encoded}).scrollIntoView({block:'center',behavior:'instant'})`);
  const point = await evaluate(`(()=>{const e=document.getElementById(${encoded}),r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;return {x,y,width:r.width,height:r.height,unobscured:e===document.elementFromPoint(x,y)||e.contains(document.elementFromPoint(x,y))}})()`);
  assert.ok(point.width > 0 && point.height > 0 && point.unobscured, 'Button is obscured or unrendered: ' + id);
  const coordinates = {x:point.x,y:point.y,button:'left',clickCount:1};
  await call('Input.dispatchMouseEvent',{type:'mousePressed',...coordinates});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',...coordinates});
}
async function buttonJob(id, action, expectedStatus) {
  await until(async () => !(await snapshot()).active_job, 'idle installer before ' + action);
  const before = new Set((await snapshot()).jobs.map(job => job.id)); const started = Date.now();
  await click(id);
  const completed = await until(async () => {
    const state = await snapshot();
    const job = state.jobs.find(row => row.action === action && !before.has(row.id));
    return job && job.status !== 'running' && !state.active_job ? {state,job} : false;
  }, 'actual ' + action + ' receipt');
  assert.equal(completed.job.status,'completed', action + ' was blocked: ' + JSON.stringify(completed.job.result));
  if (expectedStatus) assert.equal(completed.job.result.status,expectedStatus,action + ' returned: ' + JSON.stringify(completed.job.result));
  report.steps.push({action,interaction:'Chromium Input.dispatchMouseEvent on rendered button',duration_ms:Date.now()-started,receipt:completed.job.result});
  process.stdout.write('GUI '+action+': '+completed.job.result.status+' ('+(Date.now()-started)+' ms)\n');
  // The app polls independently; wait for its own actual result rendering.
  await until(() => evaluate('document.getElementById("job-banner").hidden && !document.getElementById("check-button").disabled'), 'UI receipt rendering for ' + action);
  return completed.job.result;
}
async function screenshot(name) {
  const reply = await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  const bytes = Buffer.from(reply.data,'base64'); await writeFile(join(output,name),bytes,{mode:0o600});
  report.screenshots.push({file:name,sha256:digest(bytes),bytes:bytes.length,viewport:await evaluate('({width:innerWidth,height:innerHeight,language:document.documentElement.lang})')});
}
async function browserExecutable() {
  const explicit = args['--browser'] || process.env.AGENT_SYSTEM_TEST_BROWSER;
  if (explicit) return realpath(resolve(explicit));
  const candidates = platform() === 'darwin' ? ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Chromium.app/Contents/MacOS/Chromium','/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'] : platform() === 'win32' ? [join(process.env.PROGRAMFILES || 'C:\\Program Files','Google/Chrome/Application/chrome.exe'),join(process.env.PROGRAMFILES || 'C:\\Program Files','Microsoft/Edge/Application/msedge.exe'),join(process.env.LOCALAPPDATA || 'C:\\Users\\Default\\AppData\\Local','Google/Chrome/Application/chrome.exe')] : ['chromium','chromium-browser','google-chrome','microsoft-edge'];
  for (const candidate of candidates) {
    try { const found = isAbsolute(candidate) ? candidate : (await resolveNativeCommand(candidate)).command; const info = await lstat(found); if (info.isFile() || info.isSymbolicLink()) return realpath(found); } catch {}
  }
  throw Error('A Chromium browser is unavailable. Install test-only Chromium and pass --browser with its executable path.');
}
async function installedBytes(pkg, state, discovery, install) {
  const home = state.home, managed = join(home,'.agents','skills');
  const core = JSON.parse((await boundedFile(join(pkg,'product/kit/manifest.json'),64*1024*1024)).toString('utf8'));
  assert.equal(core.skills.length,33,'Expected all 33 core skills.');
  const manifest = JSON.parse((await boundedFile(join(pkg,'product-manifest.json'))).toString('utf8'));
  const proof = {skills:[],roles:[],files_verified:0,bytes_verified:0,icons_verified:0};
  for (const skill of core.skills) {
    assert.match(skill.name,/^[a-z][a-z0-9-]+$/);
    for (const [name,record] of Object.entries(skill.files)) {
      const target = resolve(managed,skill.name,name); assert.ok(below(join(managed,skill.name),target));
      const bytes = await boundedFile(target,256*1024*1024);
      assert.equal(bytes.length,record.size,'Installed size differs: '+skill.name+'/'+name);
      assert.equal(digest(bytes),record.sha256,'Installed hash differs: '+skill.name+'/'+name);
      proof.files_verified++;proof.bytes_verified+=bytes.length;if (/(?:^|\/)(?:icon\.svg|.*icon.*\.png)$/.test(name))proof.icons_verified++;
    }
    const skillFile = join(managed,skill.name,'SKILL.md');
    assert.equal(resolve(discovery.observed_paths[skill.name]),skillFile,'Codex resolved another skill source.');
    proof.skills.push({name:skill.name,skill_sha256:skill.files['SKILL.md'].sha256,files:Object.keys(skill.files).length});
  }
  const prefix = 'product/optional-skills/atelier-orchestrator/';let optionalFiles=0;
  for (const [name,record] of Object.entries(manifest.files)) {
    if (!name.startsWith(prefix))continue;
    const target=resolve(managed,'atelier-orchestrator',name.slice(prefix.length));assert.ok(below(join(managed,'atelier-orchestrator'),target));
    const bytes=await boundedFile(target,256*1024*1024);assert.equal(bytes.length,record.size);assert.equal(digest(bytes),record.sha256,'Orchestrator hash differs: '+name);
    optionalFiles++;proof.files_verified++;proof.bytes_verified+=bytes.length;
  }
  assert.ok(optionalFiles>0,'Orchestrator was not verified.');
  assert.equal(resolve(discovery.observed_paths['atelier-orchestrator']),join(managed,'atelier-orchestrator/SKILL.md'));
  const roles=JSON.parse((await boundedFile(join(pkg,'product/agent-profiles/manifest.json'))).toString('utf8'));
  assert.equal(roles.roles.length,12);
  for(const role of roles.roles){assert.match(role.file,/^[a-z][a-z0-9-]+\.toml$/);const bytes=await boundedFile(join(home,'.codex','agents',role.file));assert.equal(digest(bytes),role.sha256,'Installed role differs: '+role.file);proof.roles.push({file:role.file,sha256:role.sha256});proof.files_verified++;proof.bytes_verified+=bytes.length;}
  assert.ok(below(state.state,install.journal),'Installation journal outside fixed state.');
  const rawJournal=await boundedFile(install.journal),journal=JSON.parse(rawJournal.toString('utf8'));
  assert.equal(journal.status,'complete');assert.ok(below(state.state,journal.plan));
  const rawPlan=await boundedFile(journal.plan);assert.equal(digest(rawPlan),journal.plan_sha256);
  const plan=JSON.parse(rawPlan.toString('utf8'));assert.equal(plan.source_commit,manifest.source_commit);assert.equal(plan.manifest_sha256,digest(await boundedFile(join(pkg,'product-manifest.json'))));
  assert.equal(journal.launcher,install.launcher);const launcher=await boundedFile(journal.launcher);assert.equal(digest(launcher),journal.launcher_sha256);
  return {...proof,orchestrator_files:optionalFiles,source_commit:plan.source_commit,journal_sha256:digest(rawJournal),plan_sha256:journal.plan_sha256,launcher_sha256:journal.launcher_sha256,model_execution:false};
}

try {
  const readyFile=await realpath(resolve(args['--ready-file']));await assertPrivatePath(readyFile,{pythonPath});
  const readyBytes=await boundedFile(readyFile,8192),ready=JSON.parse(readyBytes.toString('utf8'));
  assert.equal(ready.schema,'codex-agents.setup-web-ready/1');
  const url=new URL(ready.url);assert.equal(url.protocol,'http:');assert.equal(url.hostname,'127.0.0.1');assert.ok(Number(url.port)>0);assert.equal(url.pathname,'/');
  launchSecret=new URLSearchParams(url.hash.slice(1)).get('launch');assert.ok(launchSecret,'Ready receipt has no one-use launch token.');
  const pkg=await realpath(resolve(ready.package));
  output=resolve(args['--output']);assert.ok(!below(pkg,output)&&output!==pkg,'Keep proof files outside the audited buyer package.');
  await mkdir(output,{recursive:true,mode:0o700});output=await realpath(output);await securePrivatePath(output,{directory:true,pythonPath});
  profile=await mkdtemp(join(output,'.chromium-'));await securePrivatePath(profile,{directory:true,pythonPath});
  const manifestBytes=await boundedFile(join(pkg,'product-manifest.json')),manifest=JSON.parse(manifestBytes.toString('utf8'));
  assert.equal(manifest.product_id,'codex-agent-system');assert.match(manifest.source_commit,/^[a-f0-9]{40}$/);
  report.package={path:pkg,product_id:manifest.product_id,version:manifest.product_version,edition:manifest.edition,source_commit:manifest.source_commit,source_clean:manifest.source_clean,distribution:manifest.distribution,native_runtime:manifest.portable_runtimes?.[platform()+'-'+arch()],manifest_sha256:digest(manifestBytes),ready_receipt_sha256:digest(readyBytes),instance_id:ready.instance_id,setup_files:{}};
  for (const name of ['setup/web.mjs','setup/ui/index.html','setup/ui/app.mjs','setup/ui/style.css','setup/setup.py']) {
    const bytes=await boundedFile(join(pkg,name));assert.equal(digest(bytes),manifest.files[name]?.sha256,'GUI input differs from exact package inventory: '+name);report.package.setup_files[name]=digest(bytes);
  }
  report.driver_sha256=digest(await readFile(fileURLToPath(import.meta.url)));
  const executable=await browserExecutable();report.browser={executable};
  const flags=['--headless=new','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-default-apps','--disable-dev-shm-usage','--lang=en-US','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--user-data-dir='+profile];
  if (typeof process.getuid==='function'&&process.getuid()===0)flags.push('--no-sandbox');
  let browserErrors='';browser=spawn(executable,flags,{stdio:['ignore','ignore','pipe'],shell:false,windowsHide:true});
  browser.stderr.on('data',chunk=>{browserErrors=(browserErrors+chunk.toString('utf8')).slice(-16000)});
  browser.once('error',error=>{browserErrors+=error.message;browserExit='spawn-error'});browser.once('exit',code=>{browserExit=code??'signal'});
  const port=await until(async()=>Number((await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0]),'Chromium debug endpoint');
  const tab=await(await fetch('http://127.0.0.1:'+port+'/json/new?about:blank',{method:'PUT'})).json();
  socket=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((ok,fail)=>{socket.onopen=ok;socket.onerror=()=>fail(Error('Chromium protocol connection failed.'))});
  socket.onmessage=({data})=>{const row=JSON.parse(data),item=pending.get(row.id);if(item){pending.delete(row.id);row.error?item.fail(row.error):item.ok(row.result)}};
  socket.onclose=()=>{for(const item of pending.values())item.fail('Chromium protocol closed.');pending.clear()};
  report.browser.version=await call('Browser.getVersion');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1400,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:ready.url});
  await until(()=>evaluate('document.body.dataset.setupSession==="ready"'),'one-use owner session');
  await until(async()=>!(await snapshot()).active_job,'initial journal refresh');
  const initial=await snapshot();assert.equal(initial.instance_id,ready.instance_id);assert.equal(initial.product.source_commit,manifest.source_commit);assert.equal(initial.results.status.status,'not-installed-by-this-setup','Use a fresh isolated buyer HOME for this proof.');
  await evaluate('document.getElementById("locale").value="en";document.getElementById("locale").dispatchEvent(new Event("change"))');
  const doctor=await buttonJob('check-button','doctor');assert.equal(doctor.source_commit,manifest.source_commit);assert.equal(doctor.platform.supported_skills,true);assert.equal(doctor.host.version,args['--expect-codex-version']||'0.166.0','This proof requires the pinned real Codex host.');
  await evaluate('window.scrollTo(0,0)');await screenshot('GUI-DESKTOP-CHECK.png');
  const audit=await buttonJob('audit-button','audit','ready');assert.equal(audit.expected_skills,33);assert.equal(audit.roles,12);assert.equal(audit.preview.components.length,35);assert.equal(audit.preview.conflicts.length,0);
  await until(()=>evaluate('!document.getElementById("install-approval").disabled'),'explicit approval control');
  assert.equal(await evaluate('document.getElementById("install-approval").checked'),false);assert.equal(await evaluate('document.getElementById("install-button").disabled'),true);
  await click('install-approval');assert.equal(await evaluate('document.getElementById("install-approval").checked'),true);
  report.steps.push({action:'explicit-approval',interaction:'Chromium pointer click on unchecked approval checkbox',plan_sha256:audit.plan_sha256});
  await evaluate('document.getElementById("review").scrollIntoView({block:"start",behavior:"instant"})');await screenshot('GUI-DESKTOP-PLAN.png');
  const install=await buttonJob('install-button','install','installed');assert.equal(install.verification.skills,33);assert.equal(install.verification.orchestrator,true);assert.equal(install.verification.source_commit,manifest.source_commit);
  const verified=await buttonJob('verify-button','verify','verified-files');assert.equal(verified.skills,33);assert.equal(verified.behavior_verified,false);
  const discovery=await buttonJob('discover-button','discover','native-discovery-verified');assert.equal(discovery.skills,34);assert.equal(discovery.source_commit,manifest.source_commit);assert.equal(Object.keys(discovery.observed_paths).length,34);assert.equal(discovery.roles_explicitly_registered,12);assert.equal(discovery.role_execution_verified,false);assert.equal(discovery.behavior_verified,false);
  report.installed_bytes=await installedBytes(pkg,await snapshot(),discovery,install);
  const practice=await buttonJob('practice-button','practice','prepared');assert.equal(practice.execution_performed,false);assert.ok(practice.launcher);assert.ok(below((await snapshot()).state,practice.project));
  const fixture={};for(const [name,expected]of Object.entries(practice.fixture)){const bytes=await boundedFile(join(practice.project,name));assert.equal(bytes.toString('utf8'),expected);fixture[name]={sha256:digest(bytes),bytes:bytes.length};}
  assert.equal(await readFile(join(practice.project,'TASK.txt'),'utf8'),practice.prompt);assert.match(practice.prompt,/\$atelier-orchestrator/);assert.match(practice.prompt,/Cheklist/);assert.match(practice.prompt,/notes\.txt/);
  const launcher=await boundedFile(practice.launcher);assert.ok(below(practice.project,practice.launcher));
  if(platform()==='win32'){const match=/:AGENT_SYSTEM_LAUNCH_DATA\r?\n([A-Za-z0-9+/=]+)\r?\n$/.exec(launcher.toString('utf8'));assert.ok(match);const data=JSON.parse(Buffer.from(match[1],'base64').toString('utf8'));assert.ok(data.arguments.includes(practice.project));assert.ok(data.arguments.includes('-C'));assert.equal(data.environment.HOME,initial.home);}else{const quote=value=>/^[A-Za-z0-9_@%+=:,./-]+$/.test(value)?value:"'"+value.replaceAll("'","'\"'\"'")+"'";assert.ok(launcher.toString('utf8').includes('-C '+quote(practice.project)));}
  await until(()=>evaluate('!document.getElementById("open-codex-button").hidden && !document.getElementById("open-codex-button").disabled'),'verified project launcher button');
  const displayedPrompt=await evaluate('document.getElementById("practice-prompt").value');assert.ok(displayedPrompt.endsWith(practice.prompt));assert.ok(displayedPrompt.includes(practice.project));
  try{await call('Browser.grantPermissions',{origin:url.origin,permissions:['clipboardReadWrite','clipboardSanitizedWrite']})}catch{}
  await click('copy-prompt');await until(()=>evaluate('document.getElementById("copy-status").textContent'),'copy prompt result');
  const copyStatus=await evaluate('document.getElementById("copy-status").textContent');let clipboardVerified=false;
  if(copyStatus==='Prompt copied'){assert.equal(await evaluate('navigator.clipboard.readText()'),displayedPrompt);clipboardVerified=true;}else assert.equal(copyStatus,'Select and copy the prompt below.');
  report.practice={project:practice.project,fixture,task_sha256:digest(Buffer.from(practice.prompt)),launcher_sha256:digest(launcher),launcher_button_enabled:true,clipboard_verified:clipboardVerified,copy_status:copyStatus,model_execution:false};
  await evaluate('document.getElementById("begin").scrollIntoView({block:"start",behavior:"instant"})');await screenshot('GUI-DESKTOP-FIRST-TASK.png');
  await evaluate('document.getElementById("locale").value="uk";document.getElementById("locale").dispatchEvent(new Event("change"))');
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await evaluate('window.scrollTo(0,0)');
  const mobile=await evaluate('({lang:document.documentElement.lang,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,heading:document.querySelector("h1").textContent,hash:location.hash})');assert.equal(mobile.lang,'uk');assert.equal(mobile.width,390,'The mobile layout viewport expanded beyond the requested 390px.');assert.ok(mobile.scrollWidth<=391,'Horizontal overflow at 390px.');assert.equal(mobile.hash,'','One-use launch token was retained in URL.');assert.match(mobile.heading,/встановлення/);
  await screenshot('GUI-MOBILE-UK.png');report.mobile={...mobile,no_horizontal_overflow:true,token_removed:true};
  report.final_receipts=(await snapshot()).results;report.status='passed';report.finished_at=new Date().toISOString();
  await click('shutdown-button');await until(()=>evaluate('document.getElementById("result-banner").textContent.includes("Майстер") || document.getElementById("result-banner").textContent.includes("майстер")'),'explicit safe local shutdown');report.setup_shutdown_requested=true;
  await writeFile(join(output,'BROWSER-OBSERVATION.json'),JSON.stringify(report,null,2)+'\n',{mode:0o600});
  process.stdout.write('Native package browser flow PASS; source '+manifest.source_commit+'; proof '+output+'\n');
} catch(error) {
  report.status='failed';report.reason=redact(error.message);report.finished_at=new Date().toISOString();
  if(output){try{report.browser_state=await snapshot();report.rendered_text=await evaluate('document.body.innerText');await screenshot('GUI-FAILED.png')}catch(captureError){report.capture_error=redact(captureError.message)}await writeFile(join(output,'BROWSER-FAILURE.json'),JSON.stringify(report,null,2)+'\n',{mode:0o600});}
  process.stderr.write('Native package browser flow FAILED: '+redact(error.message).slice(0,2000)+'\n');process.exitCode=1;
} finally {
  if(socket?.readyState===WebSocket.OPEN){try{await call('Browser.close')}catch{}}
  socket?.close();
  if(browser&&browserExit===undefined){await Promise.race([new Promise(ok=>browser.once('exit',ok)),pause(5000)]);if(browserExit===undefined)browser.kill();}
  if(profile){for(let i=0;i<10;i++){try{await rm(profile,{recursive:true,force:true});break}catch{await pause(250)}}}
}
