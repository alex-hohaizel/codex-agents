import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createServer} from '../../server/index.mjs';
import {launchToken} from '../../server/session.mjs';

test('a real copied localhost cookie cannot retrieve a proof, private bytes or SSE without origin-scoped proof',async t=>{
 const root=await mkdtemp(join(tmpdir(),'atelier-private-reads-'));const artifact=join(root,'owned.png');await writeFile(artifact,Buffer.from('isolated-artifact-bytes'));const dist=join(root,'public');await mkdir(dist);await writeFile(join(dist,'index.html'),'<h1>Public shell</h1>');
 const app=new EventEmitter();Object.assign(app,{dataDir:join(root,'data'),instanceId:'instance_12345678-1234-1234-1234-123456789abc',
  store:{events:()=>[]},bootstrap:async csrf=>({csrf_token:csrf,private_canary:'test-only'}),doctor:async()=>({private_canary:'test-only'}),
  portfolio:{get:()=>({private_canary:'test-only'})},projects:{artifact:async()=>({file:artifact})},close:async()=>{}});
 const running=await createServer({application:app,port:0,dist});t.after(async()=>{await running.close();await rm(root,{recursive:true,force:true})});
 const claim=await fetch(running.origin+'/api/v1/session',{method:'POST',headers:{Origin:running.origin,'Content-Type':'application/json'},body:JSON.stringify({launch_token:launchToken(running.ownerSession.controlKey)})});
 const cookie=claim.headers.get('set-cookie').split(';')[0],proof=(await claim.json()).csrf_token;
 const copied=await fetch(running.origin+'/api/v1/session',{headers:{cookie}});assert.equal(copied.status,401);assert.equal((await copied.json()).csrf_token,undefined);
 for(const route of ['/bootstrap','/doctor','/portfolio','/events','/projects/p/artifact?path=owned.png']){
  const response=await fetch(running.origin+'/api/v1'+route,{headers:{cookie}});assert.equal(response.status,403,route);const text=await response.text();assert.ok(!text.includes('test-only')&&!text.includes('isolated-artifact-bytes'));
 }
 const query=await fetch(running.origin+'/api/v1/bootstrap?csrf='+proof,{headers:{cookie}});assert.equal(query.status,403);
 const bootstrap=await fetch(running.origin+'/api/v1/bootstrap',{headers:{cookie,'X-Atelier-CSRF':proof}});assert.equal(bootstrap.status,200);assert.equal((await bootstrap.json()).private_canary,'test-only');
 const refresh=await fetch(running.origin+'/api/v1/session',{headers:{cookie,'X-Atelier-CSRF':proof}});assert.equal(refresh.status,200);
 const trusted=await fetch(running.origin+'/api/v1/bootstrap',{headers:{'X-Atelier-Control':running.ownerSession.controlKey}});assert.equal(trusted.status,200);
 const bytes=await fetch(running.origin+'/api/v1/projects/p/artifact?path=owned.png',{headers:{cookie,'X-Atelier-CSRF':proof}});assert.equal(bytes.status,200);assert.equal(await bytes.text(),'isolated-artifact-bytes');
 const events=await fetch(running.origin+'/api/v1/events',{headers:{cookie,'X-Atelier-CSRF':proof}});assert.equal(events.status,200);await events.body.cancel();
});
