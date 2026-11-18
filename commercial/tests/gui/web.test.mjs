import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, copyFile, rm, chmod, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { request as rawRequest } from 'node:http';
import { start, runCli } from '../../setup/web.mjs';
import { securePrivatePath } from '../../../apps/agent-atelier/server/platform.mjs';

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
  op=a.state/'operations'/uuid.uuid4().hex;journal=op/'journal.json';plan={'ready':True,'mode':'fresh','optional':{'action':'install','target':str(a.home/'.agents/skills/atelier-orchestrator')}};save(a.plan,plan);h=hashlib.sha256(a.plan.read_bytes()).hexdigest();save(rowfile,[{'journal':str(journal),'plan':str(a.plan),'plan_sha256':h,'status':'planned','can_resume':True,'source_commit':source}]);r={'status':'ready','plan':str(a.plan),'plan_sha256':h,'mode':'fresh','destination':str(a.home/'.agents/skills'),'journal':str(journal),'blockers':[],'preview':{'components':[{'id':'skills','target':str(a.home/'.agents/skills'),'action':'install'}],'conflicts':[],'preserved_changes':[]}}
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

async function fixture(t) {
 const dir = await realpath(await mkdtemp(join(tmpdir(),'agent-setup-web-')));
 await securePrivatePath(dir,{directory:true,pythonPath:python});
 const pkg = join(dir,'Отриманий Пакет'); const home = join(dir,'Покупець Home'); const state = join(home,'.local/share/codex-agent-system');
 await mkdir(join(pkg,'setup'),{recursive:true}); await mkdir(home,{recursive:true});
 await writeFile(join(pkg,'setup/setup.py'),fakeEngine);
 const server = join(pkg,'product/apps/agent-atelier/server'); await mkdir(server,{recursive:true});
 for(const file of ['session.mjs','utils.mjs','platform.mjs','platform_support.py','environment.mjs'])await copyFile(join(ROOT,'apps/agent-atelier/server',file),join(server,file));
 await writeFile(join(pkg,'product-manifest.json'),JSON.stringify({product_version:'test-only',source_commit:'a'.repeat(40),edition:'fixture'}));
 const ready = join(dir,'ready.json');
 // Test transport/privacy behavior with a real child process. This fixture is
 // not proof of the real kit's installation or native host discovery.
 const app = await start({packageRoot:pkg,pythonPath:python,home,state,readyPath:ready});
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
