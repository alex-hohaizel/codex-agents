import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,realpath,rm,symlink} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {packagedPythonTerminfoRoots} from '../../server/codex.mjs';
import {sha} from '../../server/utils.mjs';

async function fixture(t) {
 const root=await realpath(await mkdtemp(join(tmpdir(),'python-term-roots-')));t.after(()=>rm(root,{recursive:true,force:true}));
 const python=join(root,'python/bin/python3.13');await mkdir(join(root,'python/bin'),{recursive:true});await writeFile(python,'argument-contract fixture; never executed');
 const directories=['python/share/terminfo','python/share/terminfo-extra'];
 const files={'python/bin/python3.13':{sha256:sha(await readFile(python))}};
 for(const directory of directories){await mkdir(join(root,directory,'x'),{recursive:true});await writeFile(join(root,directory,'x/xterm'),'database fixture');files[directory+'/x/xterm']={sha256:sha('database fixture')};}
 const descriptor={schema:'codex-agents.portable-runtime/1',target:process.platform+'-'+process.arch,python:{executable:'python/bin/python3.13'},files,terminfo_dirs:directories};
 const save=()=>writeFile(join(root,'runtime.json'),JSON.stringify(descriptor));await save();return{root,python,directories,descriptor,save};
}
test('terminal sandbox dependencies come only from the exact selected Python provenance',async t=>{
 const f=await fixture(t),previous=process.env.TERMINFO_DIRS;process.env.TERMINFO_DIRS='/private/unrelated-owner-data';
 try{assert.deepEqual(await packagedPythonTerminfoRoots(f.python),await Promise.all(f.directories.map(name=>realpath(join(f.root,name)))));}finally{if(previous===undefined)delete process.env.TERMINFO_DIRS;else process.env.TERMINFO_DIRS=previous;}
 f.descriptor.terminfo_dirs=['../unrelated-owner-data'];await f.save();
 await assert.rejects(packagedPythonTerminfoRoots(f.python),error=>error.code==='CAPABILITY_UNVERIFIED');
});
test('changed selected Python bytes and linked database directories cannot expand read authority',async t=>{
 const f=await fixture(t);await writeFile(f.python,'changed selected executable');
 await assert.rejects(packagedPythonTerminfoRoots(f.python),error=>error.code==='CAPABILITY_UNVERIFIED');
 f.descriptor.files['python/bin/python3.13'].sha256=sha(await readFile(f.python));await f.save();
 const outside=join(f.root,'outside');await mkdir(outside);const database=join(f.root,f.directories[0]);await rm(database,{recursive:true});await symlink(outside,database,process.platform==='win32'?'junction':'dir');
 await assert.rejects(packagedPythonTerminfoRoots(f.python),error=>error.code==='CAPABILITY_UNVERIFIED');
});
