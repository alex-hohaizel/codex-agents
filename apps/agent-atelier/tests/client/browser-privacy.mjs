#!/usr/bin/env node
/** Real Chromium exercises the shipped workbench HTTP/session and client transport.
 * Only the application data adapter is an isolated fixture: no account, model,
 * installed suite, personal HOME, or existing workbench data is read or changed.
 */
import assert from 'node:assert/strict';
import http from 'node:http';
import {EventEmitter} from 'node:events';
import {spawn,execFile} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {browserEnvironment} from './browser-environment.mjs';

const flags={};
for(let i=2;i<process.argv.length;i++){
  const flag=process.argv[i];
  if(flag==='--allow-no-sandbox'){assert.equal(process.platform,'linux');flags[flag]=true;continue;}
  if(flag==='--allow-missing-h264'){assert.equal(process.platform,'linux');assert.equal(process.arch,'arm64');flags[flag]=true;continue;}
  assert.ok(['--package','--output','--browser','--python'].includes(flag)&&process.argv[i+1]&&!flags[flag], 'Unknown, duplicate, or incomplete browser privacy argument.');
  flags[flag]=process.argv[++i];
}
assert.ok(flags['--output']&&flags['--browser'],'Use --output PRIVATE_PROOF_DIR --browser CHROMIUM_EXECUTABLE [--package RECEIVED_PACKAGE] [--python BUNDLED_PYTHON].');
if(flags['--python'])process.env.AGENT_SYSTEM_PYTHON=flags['--python'];
const here=dirname(fileURLToPath(import.meta.url));
const product=flags['--package']?join(resolve(flags['--package']),'product'):resolve(here,'../../../..');
const appRoot=join(product,'apps','agent-atelier');
const {createServer}=await import(pathToFileURL(join(appRoot,'server/index.mjs')));
const {launchToken}=await import(pathToFileURL(join(appRoot,'server/session.mjs')));
const {securePrivatePath}=await import(pathToFileURL(join(appRoot,'server/platform.mjs')));
const output=resolve(flags['--output']);await mkdir(output,{recursive:true,mode:0o700});await securePrivatePath(output,{directory:true});
const root=await mkdtemp(join(tmpdir(),'atelier-browser-read-proof-'));await securePrivatePath(root,{directory:true});
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const pause=ms=>new Promise(ok=>setTimeout(ok,ms));
const report={schema:'codex-agents.workbench-browser-privacy/1',started_at:new Date().toISOString(),runner:{os:process.platform,architecture:process.arch,node:process.version},scope:'Actual Chromium, shipped server and client API transport; isolated application data adapter. Not full React visual or production account acceptance.',checks:[],model_execution:false};
let running,attacker,browser,socket,browserExit,browserClosed,profile,launchSecret,copiedCookie,browserDiagnostics='';
const pending=new Map();let sequence=0;
const redact=value=>String(value).replaceAll(launchSecret||'\0','[REDACTED]').replaceAll(copiedCookie||'\0','[REDACTED]');
function rejectPending(reason){for(const item of pending.values())item.fail(Error(reason));pending.clear();}
function call(method,params={},timeout=45000){
  return new Promise((ok,fail)=>{
    if(socket?.readyState!==WebSocket.OPEN){fail(Error('Chromium protocol is not connected'));return;}
    const id=++sequence,timer=setTimeout(()=>{pending.delete(id);fail(Error('Chromium command timed out: '+method));},timeout);
    pending.set(id,{ok:v=>{clearTimeout(timer);ok(v)},fail:e=>{clearTimeout(timer);fail(e)}});
    try{socket.send(JSON.stringify({id,method,params}));}catch(error){pending.get(id).fail(error);pending.delete(id);}
  });
}
async function cleanupBrowser(){
  const started=Date.now(),result={scope:'Only the captured spawned browser PID/tree and its private profile. No existing browser or other owner process is targeted.',browser_close:'not-connected',process_tree:'not-started'};
  if(socket?.readyState===WebSocket.OPEN){try{await call('Browser.close',{},1000);result.browser_close='requested'}catch{result.browser_close='bounded-request-failed'}}
  rejectPending('Chromium test is closing');socket?.close();
  if(browser?.pid){
    if(process.platform==='win32'){
      if(browserExit===undefined){
        result.process_tree=await new Promise(ok=>execFile(join(process.env.SYSTEMROOT||'C:\\Windows','System32','taskkill.exe'),['/PID',String(browser.pid),'/T','/F'],{timeout:5000,windowsHide:true,encoding:'utf8'},error=>ok(error?'taskkill-failed-or-already-exited':'taskkill-requested')));
      }else result.process_tree='browser-already-exited';
    }else{
      // detached:true creates a fresh group for this known test child. The
      // negative PID never refers to the invoking shell or an existing browser.
      const signal=kind=>{try{process.kill(-browser.pid,kind);return true}catch(error){if(error.code==='ESRCH')return false;throw error}};
      if(signal('SIGTERM')){await Promise.race([browserClosed,pause(1500)]);result.process_tree=signal('SIGKILL')?'owned-group-killed':'owned-group-exited';}
      else result.process_tree='owned-group-already-exited';
    }
    await Promise.race([browserClosed,pause(2000)]);
    result.parent_exit_observed=browserExit!==undefined;
    browser.stderr?.destroy();browser.stdout?.destroy();browser.stdin?.destroy();browser.unref();
  }
  result.duration_ms=Date.now()-started;return result;
}
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error('Browser evaluation failed: '+redact(r.exceptionDetails.exception?.description||r.exceptionDetails.text));return r.result.value;}
async function until(fn,label,ms=20000){const end=Date.now()+ms;while(Date.now()<end){if(browserExit!==undefined)throw Error('Chromium exited during '+label);if(await fn())return;await pause(80)}throw Error('Timed out: '+label);}
async function openPage(){
  const port=Number((await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0]);
  const pages=await fetch(`http://127.0.0.1:${port}/json/list`,{signal:AbortSignal.timeout(5000)}).then(r=>r.json());
  const page=pages.find(p=>p.type==='page');assert.ok(page);
  socket=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok,fail)=>{const timer=setTimeout(()=>{socket.close();fail(Error('Chromium protocol connection timed out'))},5000);socket.onopen=()=>{clearTimeout(timer);ok()};socket.onerror=()=>{clearTimeout(timer);fail(Error('Chromium protocol connection failed'))}});
  socket.onmessage=event=>{const message=JSON.parse(event.data);const item=pending.get(message.id);if(item){pending.delete(message.id);message.error?item.fail(Error(message.error.message)):item.ok(message.result)}};
  socket.onclose=()=>rejectPending('Chromium protocol disconnected');
  await call('Page.enable');await call('Runtime.enable');
}
function wave(){const samples=8000,body=Buffer.alloc(samples*2),header=Buffer.alloc(44);header.write('RIFF');header.writeUInt32LE(36+body.length,4);header.write('WAVEfmt ',8);header.writeUInt32LE(16,16);header.writeUInt16LE(1,20);header.writeUInt16LE(1,22);header.writeUInt32LE(8000,24);header.writeUInt32LE(16000,28);header.writeUInt16LE(2,32);header.writeUInt16LE(16,34);header.write('data',36);header.writeUInt32LE(body.length,40);return Buffer.concat([header,body]);}
try{
  const apiSource=await readFile(join(appRoot,'client/src/api.ts'),'utf8');
  report.source={api_sha256:digest(apiSource),server_sha256:digest(await readFile(join(appRoot,'server/index.mjs'))),driver_sha256:digest(await readFile(fileURLToPath(import.meta.url)))};
  if(flags['--package']){const manifest=JSON.parse(await readFile(join(flags['--package'],'product-manifest.json'),'utf8'));report.source.source_commit=manifest.source_commit||manifest.source?.commit||null;report.source.package_manifest_sha256=digest(await readFile(join(flags['--package'],'product-manifest.json')));}
  const dist=join(root,'public'),artifacts=join(root,'artifacts');await mkdir(dist);await mkdir(artifacts);
  await writeFile(join(dist,'client-api.js'),stripTypeScriptTypes(apiSource));
  await writeFile(join(dist,'index.html'),'<!doctype html><html><head><meta charset="utf-8"><title>Workbench private transport proof</title></head><body><h1>Workbench private transport proof</h1><p id="status">Opening isolated workbench session…</p><script type="module" src="/runner.js"></script></body></html>');
  await writeFile(join(dist,'runner.js'),`import {api} from './client-api.js'; window.api=api; window.receivedEvents=[]; window.bootstrapCount=0; api.bootstrap().then(value=>{window.privateReady=value.private_canary==='isolated-private-canary';window.bootstrapCount++;document.querySelector('#status').textContent=window.privateReady?'Authenticated workbench transport ready':'Unexpected fixture response'}).catch(error=>{window.privateError=error.code;document.querySelector('#status').textContent=error.message});`);
  const inputs={
    'preview.png':Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a0l8AAAAASUVORK5CYII=','base64'),
    'preview.wav':wave(),
    'preview.mp4':await readFile(join(product,'commercial/media/Buyer-Install-and-First-Result.mp4')),
    // Self-contained VP8 64x64, 2-frame blue fixture, generated once with:
    // ffmpeg -f lavfi -i color=c=blue:s=64x64:r=5:d=0.4 -an -c:v libvpx
    // -b:v 20k -fflags +bitexact -flags:v +bitexact -map_metadata -1 fixture.webm
    // Neither ffmpeg nor an additional runtime is needed by the native test.
    'preview.webm':Buffer.from('GkXfo59ChoEBQveBAULygQRC84EIQoKEd2VibUKHgQJChYECGFOAZwEAAAAAAAHyEU2bdLpNu4tTq4QVSalmU6yBoU27i1OrhBZUrmtTrIHGTbuMU6uEElTDZ1OsggEiTbuMU6uEHFO7a1OsggHc7AEAAAAAAABZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVSalmoCrXsYMPQkBNgIRMYXZmV0GETGF2ZkSJiEB5AAAAAAAAFlSua9euAQAAAAAAAE7XgQFzxYgAAAAAAAAAAZyBACK1nIN1bmSIgQCGhVZfVlA4g4EBI+ODhAvrwgDgkLCBQLqBQJqBAlWwhFW5gQFV7oEA7AEAAAAAAAACAAASVMNn0HNzzWPAi2PFiAAAAAAAAAABZ8iYRaOHRU5DT0RFUkSHi0xhdmMgbGlidnB4Z8ihRaOIRFVSQVRJT05Eh5MwMDowMDowMC40MDAwMDAwMDAAH0O2deDngQCjw4EAAICQAwCdASpAAEAAAEcIhYWIhYSIAgICdaoD+AIG6EFcMdITAFVYAP7/TRL//FhX8WFfxYV/8WFf/PzO7cX85gCjloEAyADRAQABEBAAGAAYWC/0AAiOgAAcU7trkbuPs4EAt4r3gQHxggF38IED','base64'),
    'preview.pdf':await readFile(join(product,'marketing/campaign/Showcase.pdf')),
    'unsafe.html':Buffer.from('<!doctype html><script>opener.window.unsafeArtifactExecuted=true</script>'),
    'unsafe.svg':Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"><script>opener.window.unsafeArtifactExecuted=true</script></svg>'),
  };
  for(const [name,bytes]of Object.entries(inputs))await writeFile(join(artifacts,name),bytes);
  const durableEvents=[{sequence:1,event:'fixture.first',data:{isolated:true}}],streams=[],requests=[];
  const app=new EventEmitter();Object.assign(app,{dataDir:join(root,'data'),instanceId:'instance_12345678-1234-1234-1234-123456789abc',store:{events:after=>durableEvents.filter(e=>e.sequence>after)},bootstrap:async csrf=>({csrf_token:csrf,private_canary:'isolated-private-canary'}),projects:{artifact:async(_id,name)=>{assert.ok(Object.hasOwn(inputs,name));return{file:join(artifacts,name)}}},close:async()=>{}});
  running=await createServer({application:app,port:0,dist});
  running.server.prependListener('request',(req,res)=>{if(req.url.startsWith('/api/'))requests.push({route:req.url,method:req.method,has_proof:typeof req.headers['x-atelier-csrf']==='string',has_cursor:req.headers['last-event-id']||null});if(req.url==='/api/v1/events'&&req.headers['x-atelier-csrf'])streams.push(res)});
  attacker=http.createServer((req,res)=>{copiedCookie=req.headers.cookie||'';res.end('<!doctype html><title>Isolated second-port listener</title>')});await new Promise(ok=>attacker.listen(0,'127.0.0.1',ok));
  profile=join(root,'browser-profile');await mkdir(profile,{mode:0o700});await securePrivatePath(profile,{directory:true});
  // Match Microsoft's Edge debugger policy on noninteractive Windows runners:
  // no shell token is available for optional de-elevation. Sandbox stays on.
  browser=spawn(resolve(flags['--browser']),['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--disable-dev-shm-usage','--password-store=basic','--use-mock-keychain','--disable-breakpad','--edge-skip-compat-layer-relaunch',...(process.platform==='win32'?['--do-not-de-elevate']:[]),'--autoplay-policy=no-user-gesture-required','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${profile}`,...(flags['--allow-no-sandbox']?['--no-sandbox']:[]),'about:blank'],{stdio:['ignore','ignore','pipe'],detached:process.platform!=='win32',windowsHide:true,shell:false,env:browserEnvironment()});
  browserClosed=new Promise(ok=>browser.once('close',ok));
  browser.stderr.setEncoding('utf8');browser.stderr.on('data',chunk=>{browserDiagnostics=(browserDiagnostics+chunk).slice(-8000)});
  browser.once('exit',code=>{browserExit=code??'signal'});browser.once('error',error=>{browserExit=error.code||'spawn-error'});
  await until(async()=>{try{return Boolean(await readFile(join(profile,'DevToolsActivePort'),'utf8'))}catch{return false}},'browser debugging endpoint',30000);await openPage();
  const version=await call('Browser.getVersion');report.browser={product:version.product,protocolVersion:version.protocolVersion};
  report.browser.media_capabilities=await evaluate(`(()=>{const v=document.createElement('video');return {h264_high_l32:v.canPlayType('video/mp4; codecs="avc1.640020"'),vp8:v.canPlayType('video/webm; codecs="vp8"'),wav:document.createElement('audio').canPlayType('audio/wav')}})()`);
  const downloads=join(root,'downloads');await mkdir(downloads);await call('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
  launchSecret=launchToken(running.ownerSession.controlKey);
  await call('Page.navigate',{url:running.origin+'/#atelier_launch='+launchSecret});await until(()=>evaluate('window.privateReady===true'),'first useful authenticated client read');
  assert.equal(await evaluate('location.hash'),'');assert.equal(requests.filter(r=>r.route==='/api/v1/session'&&r.method==='POST').length,1);report.checks.push({check:'One-use launcher claim and URL consumption',status:'passed'});
  // Same host cookies cross ports. A real second-port navigation captures the
  // HttpOnly cookie, then its backend replays it without browser Origin headers.
  await call('Page.navigate',{url:`http://127.0.0.1:${attacker.address().port}/capture`});await until(()=>Boolean(copiedCookie),'actual second-port cookie delivery');
  assert.ok(copiedCookie.includes('atelier_session_'));
  const replay=[];
  for(const path of ['/api/v1/session','/api/v1/bootstrap','/api/v1/events','/api/v1/projects/p/artifact?path=preview.png']){const response=await fetch(running.origin+path,{headers:{Cookie:copiedCookie},signal:AbortSignal.timeout(5000)});assert.equal(response.status,path.endsWith('/session')?401:403);const bytes=await response.text();assert.ok(!bytes.includes('isolated-private-canary')&&!bytes.includes(running.ownerSession.csrf));replay.push({route:path,status:response.status})}
  assert.equal(await evaluate("sessionStorage.getItem('atelier.session.csrf.v1')"),null);report.checks.push({check:'Real second-port cookie theft cannot read proof, bootstrap, SSE, or artifact; origin storage isolated',status:'passed',responses:replay});
  await call('Page.navigate',{url:running.origin+'/'});await until(()=>evaluate('window.privateReady===true'),'return without fragment using origin storage');
  await evaluate('window.privateReady=false');await call('Page.reload',{ignoreCache:true});await until(()=>evaluate('window.privateReady===true'),'browser refresh authenticated client');
  assert.equal(requests.filter(r=>r.route==='/api/v1/session'&&r.method==='POST').length,1);assert.ok(requests.filter(r=>r.route==='/api/v1/session'&&r.method==='GET'&&r.has_proof).length>=2);report.checks.push({check:'Navigate back and refresh retain origin-scoped proof without replaying launch token',status:'passed'});
  await evaluate("window.receivedEvents=[];window.eventStream=api.events(event=>window.receivedEvents.push(JSON.parse(event.data).sequence),{reconnectMs:250});true");await until(()=>evaluate('receivedEvents.includes(1)'),'authenticated live SSE event');
  durableEvents.push({sequence:2,event:'fixture.second',data:{isolated:true}});streams.at(-1).destroy();await until(()=>evaluate('receivedEvents.includes(2)'),'authenticated SSE reconnect and durable replay');
  assert.deepEqual(await evaluate('receivedEvents'),[1,2]);assert.ok(requests.some(r=>r.route==='/api/v1/events'&&r.has_cursor==='1'&&r.has_proof));await evaluate('eventStream.close();true');const connections=streams.length;await pause(450);assert.equal(streams.length,connections);report.checks.push({check:'Authenticated fetch SSE reconnects with Last-Event-ID and closes without secret URL',status:'passed',sequences:[1,2]});
  const media=await evaluate(`(async()=>{
    const result=[];
    const save=(url,name)=>{const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();return true};
    for(const name of ${JSON.stringify(Object.keys(inputs))}){
      const blob=await api.artifactBlob('p',name),bytes=new Uint8Array(await blob.arrayBuffer());
      const sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(b=>b.toString(16).padStart(2,'0')).join(''),url=URL.createObjectURL(blob);
      let decoded=null,download=null,environment_limit=null;
      if(name.endsWith('.png')){const image=new Image();image.src=url;document.body.append(image);await image.decode();decoded=image.naturalWidth===1}
      else if(/\.(wav|mp4|webm)$/.test(name)){
        const element=document.createElement(name.endsWith('.wav')?'audio':'video');element.muted=true;element.controls=true;element.src=url;document.body.append(element);
        try{
          await new Promise((ok,fail)=>{const timer=setTimeout(()=>fail(Error('Media metadata timed out: '+name)),15000);element.onloadedmetadata=()=>{clearTimeout(timer);ok()};element.onerror=()=>{clearTimeout(timer);const failure=Error('Media could not decode: '+name+' code '+element.error?.code);failure.media_code=element.error?.code;fail(failure)};element.load()});
          decoded=element.duration>0;await element.play();await new Promise(ok=>setTimeout(ok,100));element.pause();
        }catch(error){
          if(name!=='preview.mp4'||!${Boolean(flags['--allow-missing-h264'])}||element.canPlayType('video/mp4; codecs="avc1.640020"')!==''||error.media_code!==4)throw error;
          decoded=false;environment_limit={status:'environment-limit',reason:'This actual native Linux ARM test Chromium reports no H264 decoder and failed MEDIA_ERR_SRC_NOT_SUPPORTED. H264 playback was not accepted.',media_error_code:error.media_code};download=save(url,name);await new Promise(ok=>setTimeout(ok,150));
        }
      }else{const a=document.createElement('a');a.href=url;if(!name.endsWith('.pdf'))a.download=name;document.body.append(a);download=a.hasAttribute('download');if(download){a.click();await new Promise(ok=>setTimeout(ok,150))}}
      result.push({name,type:blob.type,bytes:blob.size,sha256,decoded,download,environment_limit});URL.revokeObjectURL(url);
    }
    return{artifacts:result,unsafe_executed:window.unsafeArtifactExecuted===true};
  })()`);
  assert.equal(media.unsafe_executed,false);
  report.limitations=[];
  for(const row of media.artifacts){
    assert.equal(row.sha256,digest(inputs[row.name]));
    if(/\.(png|wav|webm)$/.test(row.name))assert.equal(row.decoded,true);
    if(row.name==='preview.mp4'){if(row.environment_limit){assert.equal(flags['--allow-missing-h264'],true);report.limitations.push(row.environment_limit)}else assert.equal(row.decoded,true);report.checks.push({check:'Actual shipped H264 MP4 playback',status:row.environment_limit?'environment-limit':'passed',decoded:row.decoded,...(row.environment_limit||{})})}
    if(row.name.startsWith('unsafe.')){assert.ok(row.type.startsWith('text/plain'));assert.equal(row.download,true)}
    if(row.name.endsWith('.pdf')){assert.equal(row.type,'application/pdf');assert.equal(row.download,false)}
    if(row.download){await until(async()=>{try{return digest(await readFile(join(downloads,row.name)))===row.sha256}catch{return false}},'actual byte-exact download '+row.name);row.downloaded_bytes_verified=true}
  }
  report.checks.push({check:'Authenticated PNG decode, WAV/VP8 playback, exact MP4 delivery, PDF bytes/open link, and safe HTML/SVG downloads preserve server MIME',status:'passed',...media});
  assert.ok(requests.filter(r=>r.route.includes('/artifact?')).filter(r=>r.has_proof).length>=Object.keys(inputs).length);
  const picture=await call('Page.captureScreenshot',{format:'png'});const screenshot=Buffer.from(picture.data,'base64');await writeFile(join(output,'WORKBENCH-PRIVATE-TRANSPORT.png'),screenshot,{mode:0o600});report.screenshot={name:'WORKBENCH-PRIVATE-TRANSPORT.png',sha256:digest(screenshot)};
  report.status='passed';
}catch(error){report.status='failed';report.reason=redact(error.message);report.browser_failure={exit:browserExit??null,stderr:redact(browserDiagnostics)};process.exitCode=1;}finally{
  try{report.browser_cleanup=await cleanupBrowser();if(browser?.pid&&report.browser_cleanup.parent_exit_observed!==true){report.status='failed';report.reason||='Spawned test browser exit was not observed after bounded cleanup';process.exitCode=1}}catch(error){report.browser_cleanup={status:'failed',reason:redact(error.message)};report.status='failed';process.exitCode=1;browser?.stderr?.destroy();browser?.unref();rejectPending('Browser cleanup failed');socket?.close()}
  await running?.close();if(attacker){attacker.closeAllConnections();await new Promise(ok=>attacker.close(ok))}
  let privateRootRemoved=false;
  for(let i=0;i<10;i++){try{await rm(root,{recursive:true,force:true});privateRootRemoved=true;break}catch{await pause(250)}}
  report.browser_cleanup.private_root_removed=privateRootRemoved;
  if(!privateRootRemoved){report.status='failed';report.reason||='The private test profile and fixture cleanup could not be verified';process.exitCode=1}
  report.finished_at=new Date().toISOString();await writeFile(join(output,'WORKBENCH-BROWSER-PRIVACY.json'),JSON.stringify(report,null,2)+'\n',{mode:0o600});
  process.stdout.write('Workbench Chromium privacy '+report.status+(report.reason?': '+report.reason:'')+'\n');
}
