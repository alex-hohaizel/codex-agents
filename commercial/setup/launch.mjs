import {existsSync,readFileSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync,spawn} from 'node:child_process';
import {runCli} from './web.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'..');
const key=process.platform+'-'+process.arch;
const manifest=JSON.parse(readFileSync(join(root,'product-manifest.json'),'utf8'));
const tools=manifest.portable_runtimes?.[key];
if(!tools)throw new Error('This package does not include '+key+'. Download the Universal installer or the matching platform asset.');
const python=join(root,tools.python_executable),node=join(root,tools.node_executable);
if(!existsSync(python)||!existsSync(node))throw new Error('Runtime files are missing. Extract a fresh verified release package.');
const env={...process.env,AGENT_SYSTEM_PYTHON:python,AGENT_SYSTEM_NODE:node,PYTHONUTF8:'1',PYTHONIOENCODING:'utf-8',PYTHONDONTWRITEBYTECODE:'1'};
delete env.PYTHONHOME;delete env.PYTHONPATH;delete env.NODE_OPTIONS;
Object.assign(process.env,env);
let args=process.argv.slice(2);
const workbench=args.indexOf('--workbench');
if(workbench>=0){
 args.splice(workbench,1);
 const result=spawnSync(node,[join(root,'control.mjs'),...(args.length?args:['start'])],{stdio:'inherit',env});
 process.exit(result.status??1);
}
const verbs=new Set(['doctor','audit','install','verify','discover','rollback','uninstall','status','operations','first-task','prepare-first-task']);
if(args.some(x=>verbs.has(x))||args.includes('--json')||args.includes('--help')){
 const result=spawnSync(python,['-B','-X','utf8',join(root,'setup/setup.py'),'--package',root,...args],{stdio:'inherit',env});
 process.exit(result.status??1);
}
const allowed=new Set(['--home','--state','--codex','--ready','--port','--entitlement']);
for(let i=0;i<args.length;i++){
 const flag=args[i];
 if(flag==='--no-open')continue;
 if(!allowed.has(flag)||!args[i+1])throw new Error('Unknown launcher argument: '+flag);
 i++;
}
await runCli(['--package',root,'--python',python,...args]);
