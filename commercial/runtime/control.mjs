import { createHash, randomUUID } from 'node:crypto';
import { createReadStream, existsSync } from 'node:fs';
import { readFile, lstat, readdir, realpath, mkdir, mkdtemp, copyFile, chmod, writeFile, rename, rm } from 'node:fs/promises';
import { spawn, execFileSync } from 'node:child_process';
import { resolve, dirname, relative, join, isAbsolute, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { tmpdir, release } from 'node:os';
import { DatabaseSync } from 'node:sqlite';
const root = dirname(fileURLToPath(import.meta.url));
const productPrefix = existsSync(join(root,'product-manifest.json')) ? 'product/' : '';
const { platformStateRoot, securePrivatePath, assertPrivatePath, logicalMode } = await import(pathToFileURL(join(root,productPrefix+'apps/agent-atelier/server/platform.mjs')).href);
const args = process.argv.slice(2);
const verb = args[0] ?? 'start';
const at = name => { const i = args.indexOf(name); return i < 0 ? undefined : args[i+1]; };
const fail = (check, message) => { if (!check) throw new Error(message); };
const within=(base,target)=>{const name=relative(resolve(base),resolve(target));return name===''||(!isAbsolute(name)&&name!=='..'&&!name.startsWith('..'+sep));};
const member=rel=>{fail(!isAbsolute(rel)&&!rel.includes('\\')&&rel.split('/').every(x=>x&&x!=='.'&&x!=='..'),'Invalid snapshot path');if(process.platform==='win32')fail(rel.split('/').every(x=>!x.includes(':')&&!/[. ]$/.test(x)&&!/^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(x)),'Windows snapshot alias/device path rejected');};
const hash = async path => { const digest = createHash('sha256'); for await (const part of createReadStream(path)) digest.update(part); return digest.digest('hex'); };
const output = data => console.log(JSON.stringify(data, null, 2));
async function regular(path) {
  const info = await lstat(path);
  fail(info.isFile() && !info.isSymbolicLink() && info.nlink === 1, 'Expected one regular owned file: ' + path);
  return info;
}
async function safePath(path) {
  path = resolve(path);
  let here = path;
  while (true) {
    try { fail(!(await lstat(here)).isSymbolicLink(), 'Linked state path rejected: ' + here); }
    catch (e) { if (e.code !== 'ENOENT') throw e; }
    const parent = dirname(here); if (parent === here) break; here = parent;
  }
  return path;
}
async function inventory(folder, skip = new Set(), maxFiles = 20000) {
  const files = {}, pending = [''];
  let count = 0;
  while (pending.length) {
    const prefix = pending.pop();
    for (const name of await readdir(join(folder, prefix))) {
      const rel = prefix ? prefix + '/' + name : name;
      if (skip.has(rel)) continue;
      const path = join(folder,rel), info = await lstat(path);
      fail(!info.isSymbolicLink(), 'Linked runtime/state member rejected: ' + rel);
      if (info.isDirectory()) pending.push(rel);
      else {
        fail(info.isFile() && info.nlink === 1 && info.size <= 512*1024*1024, 'Unexpected file in runtime/state: '+rel);
        fail(++count <= maxFiles, 'State or runtime inventory exceeds bounded capacity');
        files[rel] = {sha256:await hash(path), size:info.size, mode:info.mode & 0o777};
      }
    }
  }
  return Object.fromEntries(Object.entries(files).sort(([a],[b])=>a.localeCompare(b,'en')));
}
function sameFiles(actual, expected) {
  fail(Object.keys(actual).length === Object.keys(expected).length,'Runtime/state file inventory changed');
  for (const [path, pin] of Object.entries(expected)) {
    const item = actual[path];
    fail(item && item.sha256===pin.sha256 && item.size===pin.size && logicalMode({mode:item.mode},pin.mode)===pin.mode,'Runtime/state content or mode changed: '+path);
  }
}
async function verify() {
  let manifest;
  if(productPrefix) {
    await regular(join(root,'product-manifest.json'));
    const product=JSON.parse(await readFile(join(root,'product-manifest.json'),'utf8'));
    fail(product.schema==='codex-agents.commercial-package/1'&&product.product_id==='codex-agent-system','Unknown product descriptor');
    const key=process.platform+'-'+process.arch, tools=product.portable_runtimes?.[key];
    fail(tools,'Choose a ready package matching this operating system and architecture');
    for(const name of ['node_executable','python_executable']) { member(tools[name]); fail(product.files[tools[name]],'Runtime executable is outside the product inventory'); }
    const runtimePath='runtimes/'+key+'/runtime.json';
    fail(product.files[runtimePath],'Runtime provenance is outside the product inventory');
    const runtime=JSON.parse(await readFile(join(root,runtimePath),'utf8'));
    fail(runtime.schema==='codex-agents.portable-runtime/1'&&runtime.target===key,'Runtime provenance target differs');
    sameFiles(await inventory(root,new Set(['product-manifest.json','SHA256SUMS']),65000),product.files);
    fail(await realpath(process.execPath)===await realpath(join(root,tools.node_executable)),'Launch this product with its included Node runtime');
    const python=await realpath(join(root,tools.python_executable)),node=await realpath(join(root,tools.node_executable));
    process.env.AGENT_SYSTEM_PYTHON=python;process.env.AGENT_SYSTEM_NODE=node;
    process.env.PYTHONUTF8='1';process.env.PYTHONIOENCODING='utf-8';process.env.PYTHONDONTWRITEBYTECODE='1';
    delete process.env.PYTHONHOME;delete process.env.PYTHONPATH;delete process.env.NODE_OPTIONS;delete process.env.NODE_PATH;
    process.env.PATH=(process.env.PATH||'')+(process.platform==='win32'?';':':')+dirname(python)+(process.platform==='win32'?';':':')+dirname(node);
    const component=product.components?.workbench;
    manifest={...product,platform:{os:process.platform,arch:process.arch},node_version:runtime.node.version,
      node_provenance:{verification:runtime.node_signature??'Pinned vendor inputs; see included runtime provenance'},
      service_version:typeof component==='string'?component:component?.version,sqlite_schema_max:1,
      notarization:product.notarization??'No platform signing/notarization claim; see included product guide'};
  } else {
    await regular(join(root,'runtime-manifest.json'));
    manifest = JSON.parse(await readFile(join(root,'runtime-manifest.json'),'utf8'));
    fail(manifest.schema === 'codex-agents.workbench-runtime/1', 'Unknown runtime descriptor');
    sameFiles(await inventory(root,new Set(['runtime-manifest.json'])),manifest.files);
  }
  fail(['darwin','linux','win32'].includes(manifest.platform.os) && ['arm64','x64'].includes(manifest.platform.arch),'Unknown runtime platform');
  fail(process.platform===manifest.platform.os && process.arch===manifest.platform.arch, 'Choose the runtime archive matching this operating system and architecture.');
  if(process.platform==='darwin') {
    const version=execFileSync('/usr/bin/sw_vers',['-productVersion'],{encoding:'utf8'}).trim().split('.').map(Number);
    fail(version[0]>13 || (version[0]===13 && version[1]>=5),'This runtime requires macOS13.5 or newer.');
  } else if(process.platform==='win32') {
    fail(Number(release().split('.')[0])>=10,'This runtime requires a supported Windows10/11 release.');
  }
  fail(process.versions.node===manifest.node_version, 'Bundled Node runtime version mismatch');
  return manifest;
}
async function stateFolder(requireExisting=true) {
  const path = await safePath(at('--data-dir') ?? process.env.ATELIER_DATA_DIR ?? platformStateRoot({product:true}));
  if (requireExisting) { fail((await lstat(path)).isDirectory(),'State directory is missing'); if(process.platform==='win32') await assertPrivatePath(path,{directory:true}); }
  fail(!within(root,path),'Keep state outside the runtime bundle');
  return path;
}
async function schema(dataDir, max) {
  const database = join(dataDir,'atelier.sqlite');
  try { await regular(database); }
  catch (e) { if (e.code==='ENOENT') return null; throw e; }
  // SQLite may update shared-memory coordination even on a read-only open.
  // Inspect a stable private copy so preflight never changes source bytes.
  const scratch=await mkdtemp(join(tmpdir(),'atelier-schema-'));
  if(process.platform==='win32') await securePrivatePath(scratch,{directory:true});
  const copies=[];
  let db;
  try {
    for(const suffix of ['', '-wal']) {
      const from=database+suffix;
      try { await regular(from); } catch(e) { if(e.code==='ENOENT'&&suffix)continue;throw e; }
      const before=await hash(from);
      await copyFile(from,join(scratch,'atelier.sqlite'+suffix),1);
      fail(await hash(from)===before,'State changed while checking schema; stop and reconcile the owner');
      copies.push([from,before]);
    }
    db=new DatabaseSync(join(scratch,'atelier.sqlite'),{readOnly:true});
    const value = db.prepare('PRAGMA user_version').get().user_version;
    fail(Number.isSafeInteger(value) && value <= max,'Database is newer than this runtime. Use its matching version; do not downgrade the store.');
    for(const [from,before] of copies) fail(await hash(from)===before,'State changed during schema preflight');
    return value;
  } finally { db?.close(); await rm(scratch,{recursive:true,force:true}); }
}
async function clone(from,to,files) {
  for (const [rel,pin] of Object.entries(files)) {
    member(rel);
    const target=join(to,rel); await mkdir(dirname(target),{recursive:true,mode:0o700});
    await copyFile(join(from,rel),target,1); if(process.platform==='win32') await securePrivatePath(target); await chmod(target,pin.mode);
  }
}
async function snapshot(manifest) {
  const dataDir=await stateFolder();
  fail(at('--output'),'Choose an empty snapshot destination with --output');
  const dest=await safePath(at('--output'));
  fail(!within(dataDir,dest) && !within(dest,dataDir),'Snapshot must be outside current state');
  fail(!within(root,dest) && !within(dest,root),'Snapshot output must stay outside the runtime bundle');
  await mkdir(dest,{mode:0o700});
  if(process.platform==='win32') await securePrivatePath(dest,{directory:true});
  const {acquireInstance}=await import(pathToFileURL(join(root,productPrefix+'apps/agent-atelier/server/instance.mjs')).href);
  let release;
  try {
    release=await acquireInstance(dataDir);
    const stateSchema=await schema(dataDir,manifest.sqlite_schema_max);
    const files=await inventory(dataDir,new Set(['instance.lock','runtime.json']));
    fail(Object.keys(files).length>0,'Empty state cannot be snapshotted');
    await mkdir(join(dest,'data'),{mode:0o700});
    if(process.platform==='win32') await securePrivatePath(join(dest,'data'),{directory:true});
    await clone(dataDir,join(dest,'data'),files);
    sameFiles(await inventory(dataDir,new Set(['instance.lock','runtime.json'])),files);
    sameFiles(await inventory(join(dest,'data')),files);
    const receipt={schema:'codex-agents.workbench-offline-snapshot/1',source_runtime:manifest.source_commit,
      service_version:manifest.service_version,sqlite_user_version:stateSchema,files};
    await writeFile(join(dest,'snapshot-manifest.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx',mode:0o600});
    output({status:'snapshot-verified',snapshot:dest,sha256:await hash(join(dest,'snapshot-manifest.json')),sqlite_user_version:stateSchema,
      next:'Keep this private snapshot with the exact runtime. Restore into a NEW directory before switching runtimes.'});
  } catch(error) {
    // Preserve partial output for review. Never unlink an unknown completed snapshot.
    throw error;
  } finally { await release?.(); }
}
async function restore(manifest) {
  fail(at('--snapshot') && at('--output') && /^[a-f0-9]{64}$/.test(at('--sha256')??''),'restore requires --snapshot PATH --sha256 HASH --output NEW_PATH');
  const from=await safePath(at('--snapshot')), dest=await safePath(at('--output'));
  fail(!within(from,dest) && !within(dest,from),'Restore output must be separate');
  fail(!within(root,dest) && !within(dest,root),'Restored state must stay outside the runtime bundle');
  await regular(join(from,'snapshot-manifest.json'));
  fail(await hash(join(from,'snapshot-manifest.json'))===at('--sha256'),'Snapshot receipt digest differs');
  const receipt=JSON.parse(await readFile(join(from,'snapshot-manifest.json'),'utf8'));
  fail(receipt.schema==='codex-agents.workbench-offline-snapshot/1' && receipt.sqlite_user_version<=manifest.sqlite_schema_max,
       'This runtime cannot read the snapshot schema');
  sameFiles(await inventory(join(from,'data')),receipt.files);
  await mkdir(dest,{mode:0o700});
  if(process.platform==='win32') await securePrivatePath(dest,{directory:true});
  const {acquireInstance}=await import(pathToFileURL(join(root,productPrefix+'apps/agent-atelier/server/instance.mjs')).href);
  const release=await acquireInstance(dest);
  try {
    await clone(join(from,'data'),dest,receipt.files);
    sameFiles(await inventory(dest,new Set(['instance.lock'])),receipt.files);
    await schema(dest,manifest.sqlite_schema_max);
  } finally { await release(); }
  output({status:'restored-new-directory',data_dir:dest,snapshot_sha256:at('--sha256'),source_preserved:true,
    next:'Run status, then start this exact runtime with --data-dir set to the restored directory. Existing data is untouched.'});
}
try {
  fail(new Set(['start','stop','status','doctor','verify','inspect','snapshot','restore']).has(verb),'Use start, stop, status, doctor, verify, inspect, snapshot or restore.');
  const allowed = new Set(['--data-dir','--port','--no-open','--output','--snapshot','--sha256']);
  for(let i=1;i<args.length;i++){
    fail(allowed.has(args[i]),'Unsupported runtime option: '+args[i]);
    if(args[i]!=='--no-open') { fail(i+1<args.length && !args[i+1].startsWith('--'),'Missing runtime option value'); i++; }
  }
  const manifest=await verify();
  if(verb==='verify' || verb==='inspect') {
    output({status:'verified',source_commit:manifest.source_commit,service_version:manifest.service_version,
      platform:manifest.platform,node_version:manifest.node_version,node_provenance:manifest.node_provenance.verification,
      notarization:manifest.notarization,state:'outside-runtime',mode_policy:process.platform==='win32'?'Windows read-only attribute; private state verified by DACL':'POSIX mode bits',first_run:process.platform==='win32'?'Launch.cmd':process.platform==='darwin'?'Launch.command':'Launch.sh'});
  } else if (verb==='snapshot') await snapshot(manifest);
  else if (verb==='restore') await restore(manifest);
  else {
    const dataDir=await stateFolder(false);
    if(verb==='start') { try { await schema(dataDir,manifest.sqlite_schema_max); } catch(e) { if(e.code!=='ENOENT')throw e; } }
    const child=spawn(process.execPath,[join(root,productPrefix+'apps/agent-atelier/launcher/atelier.mjs'),verb,'--data-dir',dataDir,...args.slice(1).filter((v,i,a)=> v!=='--data-dir' && a[i-1]!=='--data-dir')],
      {cwd:root,env:{...process.env,ATELIER_DATA_DIR:dataDir},stdio:'inherit'});
    child.on('error',error=>{ console.error(JSON.stringify({status:'error',message:error.message}));process.exitCode=1; });
    child.on('exit',code=>{process.exitCode=code??1;});
  }
} catch(error) {
  console.error(JSON.stringify({status:'blocked',message:error.message,next:'Keep the current installation. Check the runtime archive, target architecture, state ownership and documented recovery procedure.'},null,2));
  process.exitCode=1;
}
