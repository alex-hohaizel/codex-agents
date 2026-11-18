import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, chmod, lstat, readFile, rm, realpath } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, win32 } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { platformStateRoot, securePrivatePath, assertPrivatePath, resolveNativeCommand, isPortableAbsolutePath, absolutePathPrefixes, logicalMode, portablePathIdentity, portablePathWithin, personalSkillRoots, installedPersonalSkillRoot } from "../../server/platform.mjs";
import { runtimeEnvironment } from "../../server/environment.mjs";
import { atomicWrite, isWithin } from "../../server/utils.mjs";
import { overridesToArgv } from "../../server/permissions.mjs";
const run = promisify(execFile);
async function fixture(t) { const root = await mkdtemp(join(tmpdir(), "atelier-platform-")); t.after(() => rm(root,{recursive:true,force:true})); return root; }

test("native platform storage preserves existing Mac identity and uses user-owned Windows/Linux roots", () => {
  assert.equal(platformStateRoot({platform:"darwin",home:"/Users/reader"}), "/Users/reader/Library/Application Support/Agent Atelier");
  assert.equal(platformStateRoot({platform:"win32",home:"C:\\Users\\Reader",env:{LOCALAPPDATA:"D:\\Private Data"}}), "D:\\Private Data\\Agent Atelier");
  assert.equal(platformStateRoot({platform:"linux",home:"/home/reader",env:{XDG_DATA_HOME:"/mnt/data"},product:true}), "/mnt/data/codex-agent-system/agent-atelier");
  assert.equal(platformStateRoot({platform:"linux",home:"/home/reader",env:{XDG_DATA_HOME:"relative"}}), "/home/reader/.local/share/agent-atelier");
});

test("personal Windows roots use CODEX_HOME compatibility while POSIX and existing legacy reads remain intact", async t => {
  assert.deepEqual(personalSkillRoots({platform:"win32",home:"D:\\Buyer Home"}),["D:\\Buyer Home\\.codex\\skills","D:\\Buyer Home\\.agents\\skills"]);
  assert.deepEqual(personalSkillRoots({platform:"darwin",home:"/Users/buyer"}),["/Users/buyer/.agents/skills","/Users/buyer/.codex/skills"]);
  assert.deepEqual(personalSkillRoots({platform:"linux",home:"/home/buyer"}),["/home/buyer/.agents/skills","/home/buyer/.codex/skills"]);
  const root=await fixture(t),canonical=join(root,"canonical"),legacy=join(root,"legacy"),name="owned-skill";
  await mkdir(join(legacy,name),{recursive:true});await writeFile(join(legacy,name,"SKILL.md"),"Preserve old installed bytes");
  assert.equal(installedPersonalSkillRoot(name,{roots:[canonical,legacy]}),legacy);
  await mkdir(join(canonical,name),{recursive:true});await writeFile(join(canonical,name,"SKILL.md"),"Current canonical bytes");
  assert.equal(installedPersonalSkillRoot(name,{roots:[canonical,legacy]}),canonical);
  await rm(join(canonical,name),{recursive:true});await writeFile(join(canonical,name),"Unrecognized canonical path");
  assert.equal(installedPersonalSkillRoot(name,{roots:[canonical,legacy]}),canonical);
  assert.equal(await readFile(join(legacy,name,"SKILL.md"),"utf8"),"Preserve old installed bytes");
});

test("Windows native runtime metadata is retained without passing ambient secrets or Python import overrides", () => {
  const result = runtimeEnvironment({USERPROFILE:"C:\\Users\\Reader",APPDATA:"A",LOCALAPPDATA:"B",AGENT_SYSTEM_PYTHON:"C:\\runtime\\python.exe",AGENT_SYSTEM_NODE:"C:\\runtime\\node.exe",PYTHONUTF8:"1",PYTHONIOENCODING:"utf-8",PYTHONDONTWRITEBYTECODE:"1",OPENAI_API_KEY:"never",PYTHONPATH:"poison"});
  assert.equal(result.USERPROFILE,"C:\\Users\\Reader"); assert.equal(result.AGENT_SYSTEM_PYTHON,"C:\\runtime\\python.exe");
  assert.equal(result.AGENT_SYSTEM_NODE,"C:\\runtime\\node.exe");
  assert.equal(result.PYTHONUTF8,"1"); assert.equal(result.PYTHONIOENCODING,"utf-8");
  assert.equal(result.OPENAI_API_KEY,undefined); assert.equal(result.PYTHONPATH,undefined);
});

test("Codex npm batch shim uses the declared JS entry and exact argv without a command shell", async t => {
  const root=await fixture(t),bin=join(root,"node_modules/@openai/codex/bin");await mkdir(bin,{recursive:true});
  await writeFile(join(root,"codex.cmd"),"@echo off\r\nexit /b 99\r\n");
  await writeFile(join(root,"node_modules/@openai/codex/package.json"),JSON.stringify({name:"@openai/codex",type:"module"}));
  const script=join(bin,"codex.js");await writeFile(script,"console.log(JSON.stringify(process.argv.slice(2)))\n");
  const args=["space and Україна","& echo forbidden","%SYSTEMROOT%","literal\"quote"];
  const cmd=await resolveNativeCommand(join(root,"codex.cmd"),args,{platform:"win32"});
  assert.equal(cmd.command,process.execPath);assert.equal(cmd.args[0],await realpath(script));
  assert.deepEqual(JSON.parse((await run(cmd.command,cmd.args)).stdout),args);
  await writeFile(join(root,"unreviewed.cmd"),"exit /b0");
  await assert.rejects(resolveNativeCommand(join(root,"unreviewed.cmd"),[],{platform:"win32"}),/Batch executables/);
  await writeFile(join(root,"node_modules/@openai/codex/package.json"),JSON.stringify({name:"another-package"}));
  await assert.rejects(resolveNativeCommand(join(root,"codex.cmd"),[],{platform:"win32"}),/resolve the installed Codex/);
});

test("private atomic Unicode data is exact and protected by the actual platform privacy boundary", async t => {
  const root=await fixture(t);await securePrivatePath(root,{directory:true});await assertPrivatePath(root,{directory:true});
  const path=join(root,"дані з пробілами.json"),bytes=Buffer.from('{"name":"Україна"}\n');await atomicWrite(path,bytes);
  await assertPrivatePath(path);assert.deepEqual(await readFile(path),bytes);
  if(process.platform!=="win32") { await chmod(path,0o644);await assert.rejects(assertPrivatePath(path),/owner-only/); }
  else { await run("icacls",[path,"/grant","*S-1-1-0:R"]);await assert.rejects(assertPrivatePath(path),/ACL/);await securePrivatePath(path); }
});

test("retention identities recognize drive and UNC roots without altering POSIX prefix hashes", () => {
  assert.equal(isPortableAbsolutePath("C:\\Users\\Reader\\project"),true);assert.equal(isPortableAbsolutePath("\\\\server\\share\\project"),true);
  assert.equal(isPortableAbsolutePath("relative/path"),false);
  assert.deepEqual(absolutePathPrefixes("/home/reader/project"),["/home","/home/reader","/home/reader/project"]);
  assert.deepEqual(absolutePathPrefixes("C:\\Users\\Reader\\project"),["C:\\Users","C:\\Users\\Reader","C:\\Users\\Reader\\project"]);
  assert.equal(portablePathIdentity("C:\\Users\\READER"),"c:\\users\\reader");
  assert.equal(portablePathWithin("C:\\Users\\Reader", "c:\\users\\READER\\project"),true);
  assert.equal(portablePathWithin("C:\\Users\\Reader", "D:\\Users\\Reader"),false);
  assert.equal(portablePathWithin("/home/reader", "/home/reader\\unrelated"),false);
});

test("MCP deny argv preserves a Windows-native inert command argument array", () => {
  assert.deepEqual(overridesToArgv({"mcp_servers.example.args":["-e","process.exit(1)"]}),['mcp_servers.example.args=["-e","process.exit(1)"]']);
});

test("Windows logical modes retain read-only enforcement and cross-drive scope stays outside", {skip:process.platform!=="win32"}, () => {
  assert.equal(logicalMode({mode:0o666},0o755),0o755);assert.equal(logicalMode({mode:0o666},0o444),0o666);
  const root=process.cwd();const other=win32.parse(root).root.toLowerCase()==="c:\\"?"D:\\other":"C:\\other";
  assert.equal(isWithin(root,other),false);
});
