import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,realpath,rm,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {SkillsManager,readInstalledSource} from '../../server/skills.mjs';
import {NativeControllers} from '../../server/controllers.mjs';

test('canonical and legacy native catalog sources are readable, pinned, and cannot escape approved roots',async t=>{
 const root=await mkdtemp(join(await realpath(tmpdir()),'atelier-personal-roots-'));t.after(()=>rm(root,{recursive:true,force:true}));
 const canonical=join(root,'home','.codex','skills'),legacy=join(root,'home','.agents','skills');
 const manager=new SkillsManager({repoRoot:join(root,'repo'),dataDir:join(root,'data'),personalRoots:[canonical,legacy]});
 const rows=[];
 for(const [parent,name]of [[canonical,'canonical-skill'],[legacy,'legacy-skill'],[legacy+'-outside','outside-skill']]){
  const folder=join(parent,name);await mkdir(folder,{recursive:true});const path=join(folder,'SKILL.md');await writeFile(path,'---\nname: '+name+'\ndescription: Bounded source fixture.\n---\n\n# Fixture 1.0.0\n');rows.push({name,path,scope:'user',enabled:true});
 }
 await manager.adoptHostCatalog(rows);
 const sources=[...manager.hostSources.values()];
 assert.equal(sources.find(s=>s.name==='canonical-skill').source_status,'host_discovered_source_read');
 assert.equal(sources.find(s=>s.name==='legacy-skill').source_status,'host_discovered_source_read');
 assert.equal(sources.find(s=>s.name==='outside-skill').source_status,'host_catalog_only');
 const before=await readFile(rows[1].path);
 const repoSkill=join(root,'repo','kit','skills','legacy-skill');await mkdir(repoSkill,{recursive:true});await writeFile(join(repoSkill,'SKILL.md'),before);
 const source=await manager.source('legacy-skill');assert.equal(source.primary_equal,true);assert.equal(source.installed.root,legacy);assert.equal(source.installed.root_kind,'legacy');
 assert.deepEqual(await readFile(rows[1].path),before);
 await writeFile(join(canonical,'legacy-skill'),'Unrecognized canonical entry');
 const blocked=await manager.source('legacy-skill');assert.equal(blocked.installed,null);assert.equal(blocked.installation_error,'ENOTDIR');
 const foundryFile=join(canonical,'agent-foundry');await writeFile(foundryFile,'Unrecognized controller source');
 const controllers=new NativeControllers({store:{list:()=>[]},repoRoot:join(root,'repo'),dataDir:join(root,'data'),projects:{},personalRoots:[canonical,legacy]});
 assert.equal(controllers.foundryRoot,foundryFile);
 // A linked source remains blocked; root-selection support grants no new link authority.
 const alias=join(root,'alias');await symlink(legacy,alias,process.platform==='win32'?'junction':'dir');
 await assert.rejects(readInstalledSource(alias,'legacy-skill'),error=>error.code==='SOURCE_DRIFT');
});
