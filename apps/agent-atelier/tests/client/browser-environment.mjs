/** Test browser only: real Windows known folders, never a copied user profile.
 * The engine/server/driver retain their synthetic buyer environment. Browser
 * profile isolation is supplied separately by --user-data-dir at each spawn.
 */
import assert from 'node:assert/strict';

export function browserEnvironment(input=process.env,platform=process.platform){
  const result={...input},key='AGENT_SYSTEM_TEST_BROWSER_SYSTEM_ENV',raw=result[key];
  delete result[key];
  if(raw===undefined)return result;
  assert.equal(platform,'win32','System browser folder override is Windows-test-only.');
  const folders=JSON.parse(raw);
  assert.ok(folders&&typeof folders==='object'&&!Array.isArray(folders));
  assert.deepEqual(Object.keys(folders).sort(),['APPDATA','HOME','LOCALAPPDATA','USERPROFILE']);
  for(const [name,value]of Object.entries(folders)){
    assert.ok(typeof value==='string'&&/^(?:[A-Za-z]:[\\/]|\\\\)/.test(value)&&!value.includes('\0'),'Invalid Windows browser known folder: '+name);
    result[name]=value;
  }
  return result;
}
