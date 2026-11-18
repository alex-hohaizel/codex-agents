import assert from 'node:assert/strict';
import test from 'node:test';
import {browserEnvironment} from './browser-environment.mjs';

const folders={HOME:'C:\\Users\\runner',USERPROFILE:'C:\\Users\\runner',APPDATA:'C:\\Users\\runner\\AppData\\Roaming',LOCALAPPDATA:'C:\\Users\\runner\\AppData\\Local'};
const input={HOME:'D:\\isolated buyer',CODEX_HOME:'D:\\isolated buyer\\.codex',AGENT_SYSTEM_TEST_BROWSER_SYSTEM_ENV:JSON.stringify(folders)};
test('Only browser child receives system folders; engine environment and Codex home stay isolated',()=>{
  const result=browserEnvironment(input,'win32');
  assert.equal(result.HOME,folders.HOME);assert.equal(result.CODEX_HOME,input.CODEX_HOME);
  assert.equal(input.HOME,'D:\\isolated buyer');assert.equal(result.AGENT_SYSTEM_TEST_BROWSER_SYSTEM_ENV,undefined);
});
test('Reject browser override carrying arbitrary variables or incomplete known folders',()=>{
  for(const bad of [{...folders,API_KEY:'private'}, {...folders,CODEX_HOME:'C:\\personal'}, {HOME:folders.HOME},[],null]){
    assert.throws(()=>browserEnvironment({...input,AGENT_SYSTEM_TEST_BROWSER_SYSTEM_ENV:JSON.stringify(bad)},'win32'));
  }
});
test('Reject malformed folder metadata and use outside native Windows tests',()=>{
  for(const bad of ['relative','C:\\bad\0path',7])assert.throws(()=>browserEnvironment({...input,AGENT_SYSTEM_TEST_BROWSER_SYSTEM_ENV:JSON.stringify({...folders,APPDATA:bad})},'win32'));
  assert.throws(()=>browserEnvironment(input,'darwin'));
  assert.deepEqual(browserEnvironment({HOME:'/isolated'},'linux'),{HOME:'/isolated'});
});
