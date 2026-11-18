import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, copyFile, rm, chmod, realpath, readdir, lstat, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { request as rawRequest } from 'node:http';
import { createHash } from 'node:crypto';
import { start, runCli } from '../../setup/web.mjs';
import { securePrivatePath, assertPrivatePath } from '../../../apps/agent-atelier/server/platform.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const python = process.env.AGENT_SYSTEM_TEST_PYTHON || execFileSync(process.platform === 'win32' ? 'python' : 'python3', ['-c','import sys;print(sys.executable)'], { encoding:'utf8' }).trim();
const fakeEngine = String.raw`
import argparse,json,hashlib,sys,time,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',type=Path);p.add_argument('--home',type=Path);p.add_argument('--state',type=Path);p.add_argument('--locale');p.add_argument('--json',action='store_true');p.add_argument('--codex');p.add_argument('command');p.add_argument('--plan',type=Path);p.add_argument('--approve');p.add_argument('--journal',type=Path);p.add_argument('--resume',type=Path);p.add_argument('--entitlement',type=Path);a=p.parse_args();a.state.mkdir(parents=True,exist_ok=True)
def save(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(obj,sort_keys=True)+'\n').encode('utf8'))
def load(path):return json.loads(path.read_bytes())
rowfile=a.state/'fixture-operations.json';installed=a.state/'fixture-installed.json';source='a'*40
with (a.state/'fixture-calls.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps({'command':a.command,'argv':sys.argv[1:]})+'\n')
try:
 if a.command=='doctor':r={'status':'action-required','platform':{'os':sys.platform,'architecture':'fixture','supported_skills':True,'python':'fixture'},'components':{'profile_and_roles':{'included':True},'workbench':{'status':'included'}},'host':{'ready':False,'next':'Sign in with your own account.'},'next':'Offline files may be installed; sign in separately.'}
 elif a.command=='audit':
  op=a.state/'operations'/uuid.uuid4().hex;journal=op/'journal.json';plan={'ready':True,'mode':'fresh','optional':{'action':'install','target':str(a.home/'.agents/skills/atelier-orchestrator')}}
  if a.entitlement:plan['entitlement']={'sha256':hashlib.sha256(a.entitlement.read_bytes()).hexdigest()}
  save(a.plan,plan);h=hashlib.sha256(a.plan.read_bytes()).hexdigest();save(rowfile,[{'journal':str(journal),'plan':str(a.plan),'plan_sha256':h,'status':'planned','can_resume':True,'source_commit':source}]);r={'status':'ready','plan':str(a.plan),'plan_sha256':h,'mode':'fresh','destination':str(a.home/'.agents/skills'),'journal':str(journal),'blockers':[],'preview':{'components':[{'id':'skills','target':str(a.home/'.agents/skills'),'action':'install'}],'conflicts':[],'preserved_changes':[]}}
 elif a.command=='install':
  if hashlib.sha256(a.plan.read_bytes()).hexdigest()!=a.approve:raise ValueError('plan digest changed')
  rows=load(rowfile);row=rows[0];journal=Path(row['journal']);save(journal,{'status':'applying'});time.sleep(.35);f=a.home/'.agents/skills/fixture/SKILL.md';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'fixture-installed\n');row.update(status='complete',can_resume=False);save(journal,{'status':'complete'});save(rowfile,rows);save(installed,{'status':'complete','journal':str(journal),'source_commit':source});r={'status':'installed','journal':str(journal),'verification':{'status':'verified-files','skills':1}}
 elif a.command=='operations':r={'status':'ready','operations':load(rowfile) if rowfile.exists() else []}
 elif a.command=='status':r=load(installed) if installed.exists() else {'status':'not-installed-by-this-setup'}
 elif a.command=='verify':
  if not (a.home/'.agents/skills/fixture/SKILL.md').is_file():raise ValueError('owned fixture missing')
  r={'status':'verified-files','skills':1,'behavior_verified':False}
 elif a.command=='discover':r={'status':'native-discovery-verified','skills':1,'role_execution_verified':False}
 elif a.command in ('rollback','uninstall'):
  f=a.home/'.agents/skills/fixture/SKILL.md';f.unlink(missing_ok=True);rows=load(rowfile);rows[0]['status']='rolled-back' if a.command=='rollback' else 'uninstalled';save(rowfile,rows);r={'status':rows[0]['status']}
 elif a.command in ('first-task','prepare-first-task'):
  r={'status':'prepared','prompt':'$atelier-orchestrator\nCorrect only the heading.','execution_performed':False}
  if a.command=='first-task':
   r['prompt']='$atelier-orchestrator\nУкраїна: збережи нотатку.';raw=json.dumps(r,ensure_ascii=False).encode('utf8');split=raw.index('Україна'.encode('utf8'))+1;sys.stdout.buffer.write(raw[:split]);sys.stdout.buffer.flush();time.sleep(.1);sys.stdout.buffer.write(raw[split:]);sys.stdout.buffer.flush();sys.exit(0)
  if a.command=='prepare-first-task':
   project=a.state/'demo'/uuid.uuid4().hex;project.mkdir(parents=True);(project/'README.md').write_bytes(b'# Cheklist\n');(project/'notes.txt').write_bytes(b'Keep this note.\n');r['project']=str(project);launcher=project/'Open Codex.fixture';launcher.write_bytes(b'owned transport fixture launcher\n');r['launcher']=str(launcher)
 else:raise ValueError('unknown fixture command')
 print(json.dumps(r));sys.exit(2 if r['status']=='action-required' else 0)
except Exception as e:print(json.dumps({'status':'blocked','reason':str(e)}),file=sys.stderr);sys.exit(2)
`;

async function fixture(t, options = {}) {
 const dir = await realpath(await mkdtemp(join(tmpdir(),'agent-setup-web-')));
 await securePrivatePath(dir,{directory:true,pythonPath:python});
 const pkg = join(dir,'Отриманий Пакет'); const home = join(dir,'Покупець Home'); const state = join(home,'.local/share/codex-agent-system');
 await mkdir(join(pkg,'setup'),{recursive:true}); await mkdir(home,{recursive:true});
 await writeFile(join(pkg,'setup/setup.py'),fakeEngine);
 const server = join(pkg,'product/apps/agent-atelier/server'); await mkdir(server,{recursive:true});
 for(const file of ['session.mjs','utils.mjs','platform.mjs','platform_support.py','environment.mjs'])await copyFile(join(ROOT,'apps/agent-atelier/server',file),join(server,file));
 await writeFile(join(pkg,'product-manifest.json'),JSON.stringify({product_id:'codex-agent-system',product_version:'1.8.0',source_commit:'a'.repeat(40),edition:options.edition || 'unassigned'}));
 const ready = join(dir,'ready.json');
 // Test transport/privacy behavior with a real child process. This fixture is
 // not proof of the real kit's installation or native host discovery.
 const app = await start({packageRoot:pkg,pythonPath:python,home,state,readyPath:ready,...(options.entitlementPath ? {entitlementPath:options.entitlementPath} : {})});
 t.after(async()=>{for(let i=0;i<100&&app.snapshot().active_job;i++)await new Promise(r=>setTimeout(r,30));await app.stop();await rm(dir,{recursive:true,force:true});});
 let cookie,csrf;
 const send = async(path,body,headers={})=>{
  const response=await fetch(app.origin+path,{method:body===undefined?'GET':'POST',headers:{...(body!==undefined?{'Content-Type':'application/json','Origin':app.origin}:{}),...(cookie?{Cookie:cookie}:{}),...(csrf?{'X-Setup-Csrf':csrf}:{}),...headers},body:body===undefined?undefined:JSON.stringify(body)});
  return {status:response.status,body:await response.json(),headers:response.headers};
 };
 const claim=async()=>{const token=new URLSearchParams(new URL(app.url).hash.slice(1)).get('launch');const r=await send('/api/session',{launch_token:token});assert.equal(r.status,200);cookie=r.headers.get('set-cookie').split(';')[0];csrf=r.body.csrf_token;return token;};
 const wait=async(id)=>{for(let i=0;i<200;i++){const r=await send('/api/state');const j=r.body.jobs.find(x=>x.id===id);if(j&&j.status!=='running')return j;await new Promise(r=>setTimeout(r,25));}throw Error('fixture job timed out');};
 const action=async(body)=>{const r=await send('/api/action',body);assert.equal(r.status,202,JSON.stringify(r.body));return wait(r.body.job_id);};
 return {dir,pkg,home,state,ready,app,send,claim,wait,action};
}

async function diagnosticPackage(f) {
 const names=['setup/web.mjs','setup/ui/index.html','setup/ui/app.mjs','setup/ui/style.css'];
 for(const name of names){await mkdir(dirname(join(f.pkg,name)),{recursive:true});await writeFile(join(f.pkg,name),'diagnostic-only fixture\n');}
 const manifest={product_id:'codex-agent-system',product_version:'diagnostic-fixture',source_commit:'a'.repeat(40),source_clean:false,files:{}};
 for(const name of [...names,'setup/setup.py']){const bytes=await readFile(join(f.pkg,name));manifest.files[name]={sha256:createHash('sha256').update(bytes).digest('hex'),size:bytes.length,mode:420};}
 await writeFile(join(f.pkg,'product-manifest.json'),JSON.stringify(manifest));
}

test('one-use launcher, owner-only ready receipt, exact Host/Origin and CSRF protect every action',async t=>{
 const f=await fixture(t);
 assert.equal((await f.send('/api/state')).status,401);
 const token=new URLSearchParams(new URL(f.app.url).hash.slice(1)).get('launch');
 assert.equal((await f.send('/api/session',{launch_token:token},{Origin:'https://example.invalid'})).status,403);
 await f.claim();
 assert.equal((await f.send('/api/session',{launch_token:token})).status,401);
 assert.equal((await f.send('/api/action',{action:'doctor'},{'X-Setup-Csrf':'wrong'})).status,403);
 assert.equal((await f.send('/api/action',{action:'doctor'},{Origin:'null'})).status,403);
 const hostStatus=await new Promise((resolveStatus,reject)=>{const req=rawRequest(f.app.origin+'/health',{headers:{Host:'attacker.invalid'}},r=>{r.resume();r.on('end',()=>resolveStatus(r.statusCode));});req.on('error',reject);req.end();});
 assert.equal(hostStatus,403);
 const ready=JSON.parse(await readFile(f.ready,'utf8'));assert.equal(ready.url,f.app.url);
 const html=await(await fetch(f.app.origin)).text();assert.ok(!html.includes(token));assert.ok(!html.includes(f.home));
 assert.match((await f.send('/api/session')).headers.get('content-security-policy'),/frame-ancestors 'none'/);
});

test('closed command contract rejects browser paths and arbitrary execution before spawning Python',async t=>{
 const f=await fixture(t);await f.claim();
 assert.equal((await f.send('/api/action',{action:'exec',command:'echo unsafe'})).status,400);
 assert.equal((await f.send('/api/action',{action:'audit',plan:'/tmp/arbitrary'})).status,400);
 assert.equal((await f.send('/api/action',{action:'install',plan_id:'unknown',approved:false})).status,400);
 const invalid=await f.action({action:'install',plan_id:'unknown',approved:true});assert.equal(invalid.result.code,'UNKNOWN_PLAN');
 await assert.rejects(readFile(join(f.state,'fixture-calls.jsonl')),{code:'ENOENT'});
});

test('a copied host cookie cannot disclose CSRF or private state without the origin-held header',async t=>{
 const f=await fixture(t);await f.claim();
 for(const path of ['/api/session','/api/state']){
  const denied=await f.send(path,undefined,{'X-Setup-Csrf':''});assert.equal(denied.status,403);assert.equal(denied.body.csrf_token,undefined);assert.equal(denied.body.home,undefined);
 }
 assert.equal((await f.send('/api/session')).status,200);assert.equal((await f.send('/api/state')).status,200);
});

test('audit binds exact plan bytes, explicit approval and single active job before changing fixture files',async t=>{
 const f=await fixture(t);await f.claim();
 const doctor=await f.action({action:'doctor'});assert.equal(doctor.result.status,'action-required');
 const audit=await f.action({action:'audit'});assert.equal(audit.result.status,'ready');assert.ok(audit.result.plan_id);assert.equal(audit.result.plan,undefined);
 await assert.rejects(readFile(join(f.home,'.agents/skills/fixture/SKILL.md')),{code:'ENOENT'});
 const start=await f.send('/api/action',{action:'install',plan_id:audit.result.plan_id,approved:true});assert.equal(start.status,202);
 assert.equal((await f.send('/api/action',{action:'shutdown'})).status,409);
 assert.equal((await f.send('/api/action',{action:'audit'})).status,409);
 const installed=await f.wait(start.body.job_id);assert.equal(installed.result.status,'installed');assert.equal((await readFile(join(f.home,'.agents/skills/fixture/SKILL.md'),'utf8')),'fixture-installed\n');
 const state=await f.send('/api/state');const op=state.body.operations[0];assert.ok(op.id);assert.equal(op.plan,undefined);
 const verified=await f.action({action:'verify',operation_id:op.id});assert.equal(verified.result.status,'verified-files');
 const practice=await f.action({action:'practice'});assert.equal(practice.result.execution_performed,false);assert.ok(practice.result.project.startsWith(f.state));assert.equal(await readFile(join(practice.result.project,'notes.txt'),'utf8'),'Keep this note.\n');
 const rollback=await f.action({action:'rollback',operation_id:op.id,approved:true});assert.equal(rollback.result.status,'rolled-back');
 const after=await f.send('/api/state');assert.equal(after.body.results.install,undefined);assert.equal(after.body.results.discover,undefined);assert.equal(after.body.results.audit,undefined);
});

test('changed saved audit is held; browser cannot replace its plan path or SHA',async t=>{
 const f=await fixture(t);await f.claim();const audit=await f.action({action:'audit'});
 const plan=join(f.state,'web-setup/plans',audit.result.plan_id+'.json');await writeFile(plan,'{}');
 const changed=await f.action({action:'install',plan_id:audit.result.plan_id,approved:true});assert.equal(changed.result.code,'PLAN_CHANGED');
 const calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);assert.equal(calls.filter(x=>x.command==='install').length,0);
});

test('new browser session refreshes checked engine operations and requires approval to resume',async t=>{
 const f=await fixture(t);await f.claim();const audited=await f.action({action:'audit'});
 const refreshed=await f.action({action:'refresh'});const op=refreshed.result.operations[0];assert.ok(op.can_resume);
 assert.equal((await f.send('/api/action',{action:'resume',operation_id:op.id})).status,400);
 const resumed=await f.action({action:'resume',operation_id:op.id,approved:true});assert.equal(resumed.result.status,'installed');
 assert.equal((await f.send('/api/action',{action:'verify',operation_id:op.id,journal:'/tmp/foreign'})).status,400);
});


test('ready receipt cannot overwrite an unrelated user file',async t=>{
 const f=await fixture(t);const victim=join(f.dir,'personal-note.json');await writeFile(victim,'Private original note.');
 await assert.rejects(start({packageRoot:f.pkg,pythonPath:python,home:f.home,state:f.state,readyPath:victim}));
 assert.equal(await readFile(victim,'utf8'),'Private original note.');
});

test('Codex opening binds a known practice launcher and preserves changed launcher bytes',async t=>{
 const f=await fixture(t);await f.claim();
 assert.equal((await f.send('/api/action',{action:'open-codex',practice_id:'unknown',launcher:'/tmp/arbitrary'})).status,400);
 const unknown=await f.action({action:'open-codex',practice_id:'unknown'});assert.equal(unknown.result.code,'LAUNCHER_REQUIRED');
 const practice=await f.action({action:'practice'});assert.ok(practice.result.launcher);
 await writeFile(practice.result.launcher,'Owner edited launcher.');
 const changed=await f.action({action:'open-codex',practice_id:practice.result.practice_id});assert.equal(changed.result.code,'LAUNCHER_CHANGED');
 assert.equal(await readFile(practice.result.launcher,'utf8'),'Owner edited launcher.');
 const calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);assert.equal(calls.length,1);assert.equal(calls[0].command,'prepare-first-task');
});

test('shared launcher CLI never creates an unreachable no-open token session',async()=>{
 await assert.rejects(runCli(['--no-open']),{code:'READY_PATH_REQUIRED'});
 await assert.rejects(runCli(['--command','arbitrary']),{code:'INVALID_ARGUMENT'});
});

test('UTF-8 task text survives child process chunks split inside a Ukrainian character',async t=>{
 const f=await fixture(t);await f.claim();
 const task=await f.action({action:'first-task',locale:'uk'});
 assert.equal(task.result.prompt,'$atelier-orchestrator\nУкраїна: збережи нотатку.');
 assert.equal(task.result.prompt.includes('\ufffd'),false);
});

const purchase = (changes = {}) => ({schema:'codex-agents.purchase-entitlement/1',mode:'test-not-a-purchase',product_id:'codex-agent-system',
 order_id:'test-order-private',buyer_ref:'synthetic-private-buyer',edition:'solo',named_seats:1,purchased_product_major:1,purchased_version:'1.7.0',
 acquired_use:'perpetual-purchased-product-major',included_updates:'purchased-product-major',...changes});
const upload = bytes => ({document_base64:Buffer.from(bytes).toString('base64')});

test('purchase document selection requires same-origin owner CSRF and preserves the normal command body bound',async t=>{
 const f=await fixture(t);const body=upload(JSON.stringify(purchase()));
 assert.equal((await f.send('/api/purchase-document',body)).status,401);await f.claim();
 assert.equal((await f.send('/api/purchase-document',body,{'X-Setup-Csrf':'wrong'})).status,403);
 assert.equal((await f.send('/api/purchase-document',body,{Origin:'https://example.invalid'})).status,403);
 assert.equal((await f.send('/api/action',{action:'doctor',padding:'x'.repeat(33000)})).status,413);
 assert.equal((await f.send('/api/purchase-document',{...body,path:'/tmp/browser-selected-path'})).status,400);
 await assert.rejects(readFile(join(f.state,'fixture-calls.jsonl')),{code:'ENOENT'});
});

test('exact UTF-8 confirmation bytes are privately retained without PII in state and bind the next audit',async t=>{
 const f=await fixture(t);await f.claim();const old=await f.action({action:'audit'});
 const original=Buffer.from(JSON.stringify({schema:'codex-agents.purchase-confirmation/1',mode:'test-not-a-purchase',
  entitlement:purchase({buyer_ref:'synthetic-Приватний покупець'}),payment_processed:false},null,2)+'\n');
 const selected=await f.send('/api/purchase-document',upload(original));assert.equal(selected.status,200);
 const hash=createHash('sha256').update(original).digest('hex');assert.deepEqual(selected.body,{status:'document-ready',sha256:hash,edition:'solo',purchased_product_major:1});
 const directory=join(f.state,'web-setup/purchase-documents'),path=join(directory,(await readdir(directory))[0]);
 assert.deepEqual(await readFile(path),original);await assertPrivatePath(path,{pythonPath:python});await assertPrivatePath(directory,{directory:true,pythonPath:python});
 const before=await lstat(path);assert.equal((await f.send('/api/purchase-document',upload(original))).status,200);assert.equal((await lstat(path)).mtimeMs,before.mtimeMs);assert.deepEqual(await readFile(path),original);
 const selectedPath=join(directory,(await readdir(directory)).find(name=>name!==path.split(/[\\/]/).at(-1)));assert.notEqual(selectedPath,path);assert.deepEqual(await readFile(selectedPath),original);
 const state=await f.send('/api/state');assert.deepEqual(state.body.purchase_document,selected.body);assert.deepEqual(state.body.plans,[]);assert.equal(state.body.results.audit,undefined);
 assert.ok(!JSON.stringify(state.body).includes('synthetic-Приватний'));assert.ok(!JSON.stringify(selected.body).includes(path));
 const stale=await f.action({action:'install',plan_id:old.result.plan_id,approved:true});assert.equal(stale.result.code,'UNKNOWN_PLAN');
 const next=await f.action({action:'audit'});assert.equal(next.result.status,'ready');
 const calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse),audit=calls.filter(x=>x.command==='audit').at(-1);
 assert.equal(audit.argv[audit.argv.indexOf('--entitlement')+1],selectedPath);
 const plan=JSON.parse(await readFile(join(f.state,'web-setup/plans',next.result.plan_id+'.json'),'utf8'));assert.equal(plan.entitlement.sha256,hash);
 assert.equal((await f.action({action:'install',plan_id:next.result.plan_id,approved:true})).result.status,'installed');
});

test('purchase document validation blocks wrong product, SKU, major, shape, encoding and oversize bytes',async t=>{
 const f=await fixture(t,{edition:'solo'});await f.claim();
 const invalid=[purchase({product_id:'another-product'}),purchase({edition:'team',named_seats:5}),purchase({purchased_product_major:2,purchased_version:'2.0.0'}),
  purchase({purchased_version:'2.0.0'}),purchase({named_seats:5}),purchase({schema:'unknown/1'}),purchase({acquired_use:'subscription'}),
  {schema:'codex-agents.purchase-confirmation/1',mode:'purchased',entitlement:purchase()}];
 for(const item of invalid)assert.equal((await f.send('/api/purchase-document',upload(JSON.stringify(item)))).status,400);
 for(const document_base64 of ['!not-base64','YQ','YWJj====','Y Q=='])assert.equal((await f.send('/api/purchase-document',{document_base64})).status,400);
 assert.equal((await f.send('/api/purchase-document',upload(Buffer.from([0xff,0xfe,0x7b])))).status,400);
 const duplicate=Buffer.from('{"schema":"unknown","schema":"customer-private-key"}');const rejected=await f.send('/api/purchase-document',upload(duplicate));assert.equal(rejected.status,400);assert.ok(!JSON.stringify(rejected.body).includes('customer-private-key'));
 const tooLarge=upload(JSON.stringify(purchase({padding:'x'.repeat(256*1024)})));assert.equal((await f.send('/api/purchase-document',tooLarge)).status,413);
 assert.equal((await f.send('/api/state')).body.purchase_document,null);
 await assert.rejects(readdir(join(f.state,'web-setup/purchase-documents')),{code:'ENOENT'});
});

test('a Team document above the command body limit is accepted only by its bounded receipt route',async t=>{
 const f=await fixture(t,{edition:'team'});await f.claim();
 const bytes=Buffer.from(JSON.stringify(purchase({edition:'team',named_seats:5,padding:'x'.repeat(64*1024)})));
 const selected=await f.send('/api/purchase-document',upload(bytes));assert.equal(selected.status,200);assert.equal(selected.body.edition,'team');
 const directory=join(f.state,'web-setup/purchase-documents');assert.deepEqual(await readFile(join(directory,(await readdir(directory))[0])),bytes);
 assert.equal((await f.action({action:'audit'})).result.status,'ready');
});

test('selection observes the same single-job boundary as install and cannot invalidate an active plan',async t=>{
 const f=await fixture(t);await f.claim();const audited=await f.action({action:'audit'});
 const started=await f.send('/api/action',{action:'install',plan_id:audited.result.plan_id,approved:true});assert.equal(started.status,202);
 const blocked=await f.send('/api/purchase-document',upload(JSON.stringify(purchase())));assert.equal(blocked.status,409);assert.equal(blocked.body.code,'OPERATION_RUNNING');
 assert.equal((await f.wait(started.body.job_id)).result.status,'installed');assert.equal((await f.send('/api/state')).body.purchase_document,null);
});

test('changed retained purchase bytes block a fresh audit and a previously approved install without overwriting them',async t=>{
 const f=await fixture(t);await f.claim();const bytes=Buffer.from(JSON.stringify(purchase()));
 const selected=await f.send('/api/purchase-document',upload(bytes)),directory=join(f.state,'web-setup/purchase-documents'),path=join(directory,(await readdir(directory))[0]);
 await writeFile(path,'changed-private-document');
 const audit=await f.action({action:'audit'});assert.equal(audit.result.code,'PURCHASE_DOCUMENT_CHANGED');assert.ok(!JSON.stringify(audit.result).includes(path));
 const repeated=await f.send('/api/purchase-document',upload(bytes));assert.equal(repeated.status,200);assert.equal(await readFile(path,'utf8'),'changed-private-document');
 const selectedPath=join(directory,(await readdir(directory)).find(name=>name!==path.split(/[\\/]/).at(-1)));assert.deepEqual(await readFile(selectedPath),bytes);
 const approved=await f.action({action:'audit'});assert.equal(approved.result.status,'ready');await writeFile(selectedPath,'changed-after-audit');
 const install=await f.action({action:'install',plan_id:approved.result.plan_id,approved:true});assert.equal(install.result.code,'PURCHASE_DOCUMENT_CHANGED');
 const calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);assert.equal(calls.filter(x=>x.command==='install').length,0);
});

test('explicit original selection recovers after an interrupted partial cache write without changing orphan data',async t=>{
 const f=await fixture(t);await f.claim();const bytes=Buffer.from(JSON.stringify(purchase())),hash=createHash('sha256').update(bytes).digest('hex');
 const directory=join(f.state,'web-setup/purchase-documents');await mkdir(directory,{mode:0o700});
 const orphan=join(directory,hash+'-00000000-0000-4000-8000-000000000000.json');await writeFile(orphan,Buffer.from('partial-private-document'),{mode:0o600});
 const selected=await f.send('/api/purchase-document',upload(bytes));assert.equal(selected.status,200);assert.equal(selected.body.sha256,hash);
 assert.equal(await readFile(orphan,'utf8'),'partial-private-document');assert.equal((await readdir(directory)).length,2);
 const audited=await f.action({action:'audit'});assert.equal(audited.result.status,'ready');
 const calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse),actual=calls.at(-1).argv;
 const selectedPath=actual[actual.indexOf('--entitlement')+1];assert.notEqual(selectedPath,orphan);assert.deepEqual(await readFile(selectedPath),bytes);
});

test('an explicit legacy CLI document is still passed unchanged until a valid GUI selection replaces it',async t=>{
 const legacyDir=await mkdtemp(join(tmpdir(),'legacy-purchase-'));t.after(()=>rm(legacyDir,{recursive:true,force:true}));
 const legacy=join(legacyDir,'legacy-receipt.json');await writeFile(legacy,'Legacy opaque receipt retained by the existing CLI.');
 const f=await fixture(t,{entitlementPath:legacy});await f.claim();await f.action({action:'audit'});
 let calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);assert.equal(calls.at(-1).argv[calls.at(-1).argv.indexOf('--entitlement')+1],legacy);
 await f.send('/api/purchase-document',upload(JSON.stringify(purchase())));await f.action({action:'audit'});
 calls=(await readFile(join(f.state,'fixture-calls.jsonl'),'utf8')).trim().split('\n').map(JSON.parse);assert.notEqual(calls.at(-1).argv[calls.at(-1).argv.indexOf('--entitlement')+1],legacy);assert.equal(await readFile(legacy,'utf8'),'Legacy opaque receipt retained by the existing CLI.');
});

test('a linked receipt storage directory cannot redirect document writes', {skip:process.platform==='win32'},async t=>{
 const f=await fixture(t);await f.claim();const outside=join(f.dir,'unrelated-private');await mkdir(outside);await symlink(outside,join(f.state,'web-setup/purchase-documents'));
 assert.equal((await f.send('/api/purchase-document',upload(JSON.stringify(purchase())))).status,400);assert.deepEqual(await readdir(outside),[]);
});

test('failed browser startup retains its real signal and bounded redacted stderr', {skip:process.platform==='win32'},async t=>{
 const f=await fixture(t);
 // Diagnostic transport only: deliberately exit before CDP or any installer
 // action. This cannot produce a passed native package/browser receipt.
 await diagnosticPackage(f);
 const token=new URLSearchParams(new URL(f.app.url).hash.slice(1)).get('launch');
 assert.match(token,/^[A-Za-z0-9_.-]+$/);
 const executable=join(f.dir,'failing-browser');await writeFile(executable,'#!/bin/sh\nprintf "%s\\n" "Diagnostic startup failure '+token+'" >&2\nkill -TERM $$\n',{mode:493});
 const proof=join(f.dir,'browser-proof');const argv=[join(ROOT,'commercial/tests/gui/native-browser.mjs'),'--ready-file',f.ready,'--output',proof,'--browser',executable];
 if(process.platform==='linux')argv.push('--allow-no-sandbox');
 let failed;try{execFileSync(process.execPath,argv,{encoding:'utf8',timeout:20000,stdio:'pipe'});}catch(error){failed=error;}
 assert.equal(failed?.status,1);
 const report=JSON.parse(await readFile(join(proof,'BROWSER-FAILURE.json'),'utf8'));
 assert.equal(report.status,'failed');assert.equal(report.browser_failure.signal,'SIGTERM');assert.equal(report.browser_failure.exit_code,null);
 assert.ok(report.browser_failure.stderr.includes('Diagnostic startup failure'));assert.ok(report.browser_failure.stderr.includes('[REDACTED_LAUNCH_TOKEN]'));assert.ok(!JSON.stringify(report).includes(token));
 if(process.platform==='linux')assert.match(report.browser.sandbox,/explicit --allow-no-sandbox/);
 await f.claim();await assert.rejects(readFile(join(f.state,'fixture-calls.jsonl')),{code:'ENOENT'});
});

test('a hung test browser and its child group cannot keep the failed driver alive', {skip:process.platform==='win32'},async t=>{
 const f=await fixture(t);await diagnosticPackage(f);
 const executable=join(f.dir,'hung-browser'),pids=join(f.dir,'browser-pids.txt');
 await writeFile(executable,'#!/bin/sh\ntrap "" TERM\nsleep 60 &\nprintf "%s %s\\n" "$$" "$!" > "$BROWSER_FIXTURE_PIDS"\nwhile :; do sleep 1; done\n',{mode:493});
 const proof=join(f.dir,'hung-browser-proof');const argv=[join(ROOT,'commercial/tests/gui/native-browser.mjs'),'--ready-file',f.ready,'--output',proof,'--browser',executable,'--timeout-seconds','1'];
 if(process.platform==='linux')argv.push('--allow-no-sandbox');
 let failed;const began=Date.now();try{execFileSync(process.execPath,argv,{encoding:'utf8',timeout:15000,stdio:'pipe',env:{...process.env,BROWSER_FIXTURE_PIDS:pids}});}catch(error){failed=error;}
 assert.equal(failed?.status,1);assert.ok(Date.now()-began<12000,'Failed browser cleanup exceeded its bound');
 const report=JSON.parse(await readFile(join(proof,'BROWSER-FAILURE.json'),'utf8'));assert.equal(report.status,'failed');assert.equal(report.browser_failure.phase,'debug-endpoint');assert.equal(report.browser_cleanup.forced,true);assert.equal(report.browser_cleanup.signal,'SIGKILL');assert.equal(report.browser_cleanup.root_exit_observed,true);assert.equal(report.browser_cleanup.profile_removed,true);
 const [rootPid]= (await readFile(pids,'utf8')).trim().split(' ').map(Number);assert.throws(()=>process.kill(rootPid,0),{code:'ESRCH'});
 await assert.rejects(readFile(join(f.state,'fixture-calls.jsonl')),{code:'ENOENT'});
});
