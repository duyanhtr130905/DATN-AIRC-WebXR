/** App JWT preflight only in reviewed main workflows. No key/JWT/token written to disk. */
import {createPrivateKey,sign} from 'node:crypto';
import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
export function checkContext(e){
 if(e.GITHUB_ACTIONS!=='true'||e.GITHUB_REPOSITORY!=='duyanhtr130905/DATN-AIRC-WebXR'||e.GITHUB_REPOSITORY_ID!=='1457386122'||!['push','workflow_dispatch'].includes(e.GITHUB_EVENT_NAME)||e.GITHUB_REF!=='refs/heads/main'||e.GITHUB_SHA!==e.GITHUB_WORKFLOW_SHA||!/^[a-f0-9]{40}$/.test(e.GITHUB_SHA||''))throw Error('UNTRUSTED_CONTEXT');
 if(!['p507-e0-e1.yml','p507-tv-diagnostic.yml'].some(n=>e.GITHUB_WORKFLOW_REF===`duyanhtr130905/DATN-AIRC-WebXR/.github/workflows/${n}@refs/heads/main`))throw Error('UNTRUSTED_WORKFLOW');
}
export function verify(app,installation,e){
 const minimal=p=>JSON.stringify(Object.entries(p||{}).sort())===JSON.stringify([['contents','read'],['metadata','read']]);
 if(String(app.id)!==e.P507_APP_ID||app.client_id!==e.P507_APP_CLIENT_ID||app.owner?.login!=='duyanhtr130905'||String(installation.id)!==e.P507_VAULT_INSTALLATION_ID||installation.app_id!==app.id||installation.account?.login!=='duyanhtr130905'||installation.repository_selection!=='selected'||installation.suspended_at||!minimal(app.permissions)||!minimal(installation.permissions))throw Error('APP_IDENTITY_MISMATCH');
 return {result:'APP_IDENTITY_PASS',app_id:app.id,client_id:app.client_id,installation_id:installation.id,owner:installation.account.login,permissions:installation.permissions,repository_selection:'selected',head:e.GITHUB_SHA,verified_at:new Date().toISOString()};
}
async function main(){
 try{
  checkContext(process.env);
  for(const k of ['P507_APP_ID','P507_APP_CLIENT_ID','P507_VAULT_INSTALLATION_ID','P507_APP_PRIVATE_KEY'])if(!process.env[k])throw Error('SECURITY_APPROVAL_REQUIRED');
  const now=Math.floor(Date.now()/1000),enc=o=>Buffer.from(JSON.stringify(o)).toString('base64url');
  const unsigned=enc({alg:'RS256',typ:'JWT'})+'.'+enc({iat:now-60,exp:now+300,iss:process.env.P507_APP_CLIENT_ID});
  const jwt=unsigned+'.'+sign('RSA-SHA256',Buffer.from(unsigned),createPrivateKey(process.env.P507_APP_PRIVATE_KEY)).toString('base64url');
  async function get(path){const r=await fetch('https://api.github.com'+path,{redirect:'error',signal:AbortSignal.timeout(30000),headers:{Authorization:'Bearer '+jwt,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2026-03-10'}});if(!r.ok)throw Error('APP_API_REJECTED');return r.json();}
  const report=verify(await get('/app'),await get('/app/installations/'+encodeURIComponent(process.env.P507_VAULT_INSTALLATION_ID)),process.env);
  await fs.mkdir('.local/p507-ci',{recursive:true});await fs.writeFile('.local/p507-ci/app-identity.json',JSON.stringify(report,null,2)+'\n');console.log('APP_IDENTITY_PASS');
 }catch{console.error('SECURITY_APPROVAL_REQUIRED: App identity preflight failed; no credential details logged');process.exitCode=1;}
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)await main();
