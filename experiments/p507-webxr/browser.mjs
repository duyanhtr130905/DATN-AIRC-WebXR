/** Actual Chrome/GLTFLoader evidence, headless SwiftShader smoke only. */
import {spawn,execFileSync} from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import os from 'node:os';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),web=path.join(root,'apps/web'),out=path.join(root,'.local/p507-e0-e1');
const require=createRequire(path.join(web,'package.json')),{chromium}=require('playwright');
const url='http://127.0.0.1:5183/p507-webxr-e1.html';
let browser;const errors=[],requests=[];
const vite=spawn(process.execPath,[path.join(web,'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','5183','--strictPort'],{cwd:web,windowsHide:true,stdio:'pipe'});
let logs='';vite.stdout.on('data',x=>logs+=x);vite.stderr.on('data',x=>logs+=x);
const report={result:'FAIL',environment:'Headless Chrome ANGLE SwiftShader; software WebGL only',head:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),dirty:!!execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim(),timestamp:new Date().toISOString(),os:os.platform()+' '+os.release(),cpu:os.cpus()[0]?.model,physicalGPU:'NOT RUN',vr72:'NOT TESTED',scenarios:[],runs:[]};
async function scenario(name,fn){await fn();report.scenarios.push({name,result:'PASS'});}
async function ready(page){await page.goto(url);await page.waitForFunction(()=>window.__P507_E1__||document.querySelector('#status').textContent.startsWith('ERROR'),null,{timeout:180000});assert((await page.locator('#status').innerText()).startsWith('LOADED'),await page.locator('#status').innerText());}
try{
 for(let i=0;i<80;i++){try{if((await fetch(url)).ok)break;}catch{}if(vite.exitCode!==null)throw Error(logs);await new Promise(r=>setTimeout(r,200));}
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/google-chrome'),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
 report.browser=browser.version();
 const context=await browser.newContext({viewport:{width:1280,height:720},deviceScaleFactor:1});
 await context.addInitScript(()=>{window.__forbiddenCalls=[];if(navigator.xr)navigator.xr.requestSession=()=>{window.__forbiddenCalls.push('XR');throw Error('XR forbidden');};if(navigator.mediaDevices)navigator.mediaDevices.getUserMedia=()=>{window.__forbiddenCalls.push('media');throw Error('media forbidden');};});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push({method:r.method(),url:r.url()}));
 await scenario('actual R4 load, scene contract and spawn',async()=>{await ready(page);const s=await page.evaluate(()=>window.__P507_E1__.snapshot());assert.equal(s.e0,'E0_PASS');assert.equal(s.geometry.placedIDs,121);assert.equal(s.geometry.worldBoundsMatched,121);assert.deepEqual(s.position,[1.25,-7.415]);assert.equal(s.inputActive,false);report.coldLoad=s;});
 await scenario('actual raycast child/group to logical record',async()=>{const ids=await page.evaluate(()=>{const ids=[];for(let x=-.9;x<=.9;x+=.15)for(let y=-.8;y<=.8;y+=.15){const id=window.__P507_E1__.select(x,y);if(id)ids.push(id);}return [...new Set(ids)];});assert(ids.includes('P507-DESK-A01')||ids.some(id=>id.startsWith('P507-DESK-A')));assert(!ids.includes('P507-CHAIR-C-09'));report.selectionIDs=ids;});
 await scenario('WASD gated until pointer lock',async()=>{await page.keyboard.down('w');await page.waitForTimeout(500);await page.keyboard.up('w');assert.deepEqual(await page.evaluate(()=>window.__P507_E1__.snapshot().position),[1.25,-7.415]);});
 await scenario('user gesture lock, WASD, mouse look, ESC and reset',async()=>{
   await page.locator('#enter').click();await page.waitForFunction(()=>window.__P507_E1__.snapshot().inputActive);
   await page.keyboard.down('s');await page.waitForTimeout(700);await page.keyboard.up('s');
   const s=await page.evaluate(()=>window.__P507_E1__.snapshot());assert(s.position[0]<1.25 && s.position[0]>.35);
   await page.mouse.move(650,380);const yaw=await page.evaluate(()=>window.__P507_E1__.snapshot().yaw);assert.notEqual(yaw,-Math.PI/2);
   await page.keyboard.press('Escape');await page.waitForFunction(()=>!window.__P507_E1__.snapshot().inputActive);
   const p=await page.evaluate(()=>window.__P507_E1__.snapshot().position);await page.keyboard.down('w');await page.waitForTimeout(300);await page.keyboard.up('w');assert.deepEqual(await page.evaluate(()=>window.__P507_E1__.snapshot().position),p);
   await page.locator('#reset').click();assert.deepEqual(await page.evaluate(()=>window.__P507_E1__.snapshot().position),[1.25,-7.415]);
 });
 await scenario('blur clears held movement',async()=>{await page.locator('#enter').click();await page.waitForFunction(()=>window.__P507_E1__.snapshot().inputActive);await page.keyboard.down('w');await page.evaluate(()=>window.dispatchEvent(new Event('blur')));const s=await page.evaluate(()=>window.__P507_E1__.snapshot());assert(!s.inputActive&&s.keys.length===0);await page.keyboard.up('w');await page.evaluate(()=>window.__P507_E1__.reset());});
 const navigation=JSON.parse(await fs.readFile(path.join(out,'navigation-report.json'),'utf8'));
 await scenario('actual browser route segments and blocked continuation',async()=>{await page.evaluate(route=>{const api=window.__P507_E1__;api.reset();for(let i=1;i<route.length;i++){const a=api.snapshot().position,b=route[i],r=api.move([b[0]-a[0],b[1]-a[1]]);if(r.reason)throw Error(r.reason);}},navigation.route);const r=await page.evaluate(()=>window.__P507_E1__.move([0,1.3]));assert(r.reason);report.route=navigation;await page.screenshot({path:path.join(out,'west-route-desktop.png')});await page.evaluate(()=>window.__P507_E1__.reset());});
 // Short CI protocol, explicitly different from 30s+3x120s real GPU protocol.
 const warmup=Number(process.env.P507_WARMUP_MS||2000),duration=Number(process.env.P507_SAMPLE_MS||10000);
 report.protocol={warmupMs:warmup,runs:3,targetDurationMs:duration,method:'rAF intervals; FPS=1000*n/sum(ms), nearest-rank percentiles. All slow frames retained. Scripted west route loops through validated Navigation.move at 1.2m/s; camera yaw fixed -PI/2. Clamp .05s matches runtime.',deviation:'Short software CI smoke, not approved physical-device KPI protocol'};
 await page.waitForTimeout(warmup);
 for(let run=0;run<3;run++){
   await page.evaluate(route=>{const api=window.__P507_E1__;api.reset();api.measure();window.__routeTimer={route,index:1,direction:1,last:performance.now(),stopped:false};function step(now){const r=window.__routeTimer;if(r.stopped)return;const dt=Math.min((now-r.last)/1000,.05);r.last=now;const p=api.snapshot().position,t=r.route[r.index],dx=t[0]-p[0],dz=t[1]-p[1],dist=Math.hypot(dx,dz),d=Math.min(dist,1.2*dt);const result=api.move(dist?[dx/dist*d,dz/dist*d]:[0,0]);if(result.reason)throw Error('Measured route blocked '+result.reason);if(dist<.02){if(r.index===r.route.length-1)r.direction=-1;else if(r.index===0)r.direction=1;r.index+=r.direction;}requestAnimationFrame(step);}requestAnimationFrame(step);},navigation.route);
   await page.waitForTimeout(duration);const snapshot=await page.evaluate(()=>{window.__routeTimer.stopped=true;window.__P507_E1__.pause();return window.__P507_E1__.snapshot();});assert(snapshot.frameTimeMs.sampleCount>=10);report.runs.push(snapshot);
 }
 await page.evaluate(()=>{window.__P507_E1__.reset();window.__P507_E1__.measure();});await page.waitForTimeout(500);await page.evaluate(()=>window.__P507_E1__.pause());await page.screenshot({path:path.join(out,'spawn-desktop.png')});
 // Lighting comparison: same scene, same camera, identical settings, original preview unchanged.
 const preview=await context.newPage();await preview.route('**/p507-local-preview/P507_G1_G2_PROVISIONAL.glb',route=>route.fulfill({path:path.join(out,'artifact/P507_G1_G2_PROVISIONAL.glb'),contentType:'model/gltf-binary'}));await preview.goto('http://127.0.0.1:5183/p507-g1-g2-preview.html');await preview.waitForFunction(()=>window.__P507_REVIEW__,null,{timeout:180000});await preview.evaluate(()=>window.__P507_REVIEW__.aim('hero'));await preview.waitForTimeout(1500);await preview.evaluate(()=>window.__P507_REVIEW__.pause());await preview.screenshot({path:path.join(out,'frozen-preview-hero.png')});await preview.close();
 // Negative loading scenarios use intercepted HTTP fixtures, never GPU performance claims.
 for(const kind of ['missing','hash','schema','corrupt']){
   await scenario('error state: '+kind,async()=>{const p=await context.newPage();await p.route('**/p507-e1-assets/**',async route=>{
     const name=new URL(route.request().url()).pathname.split('/').at(-1);
     if(kind==='missing'&&name==='asset-manifest.json')return route.fulfill({status:404,body:'missing'});
     if(kind==='hash'&&name==='P507_G1_G2_PROVISIONAL.glb')return route.fulfill({body:Buffer.from('corrupt')});
     if(kind==='schema'||kind==='corrupt'){
       const m=JSON.parse(await fs.readFile(path.join(out,'served/asset-manifest.json'),'utf8')),lock=JSON.parse(await fs.readFile(path.join(out,'served/asset-lock.json'),'utf8'));
       const {createHash}=await import('node:crypto');
       if(kind==='schema')m.schema_version=999;
       else {const bad=Buffer.from('invalid glb structure');const hash=createHash('sha256').update(bad).digest('hex');m.model_sha256=hash;m.model_bytes=bad.length;lock.files['P507_G1_G2_PROVISIONAL.glb']={sha256:hash,bytes:bad.length};if(name==='P507_G1_G2_PROVISIONAL.glb')return route.fulfill({body:bad});}
       const content=JSON.stringify(m);lock.files['asset-manifest.json'].sha256=createHash('sha256').update(content).digest('hex');
       if(name==='asset-lock.json')return route.fulfill({json:lock});if(name==='asset-manifest.json')return route.fulfill({body:content,contentType:'application/json'});
     }return route.continue();});await p.goto(url);await p.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('ERROR'),null,{timeout:30000});assert(!await p.evaluate(()=>!!window.__P507_E1__));await p.close();});
 }
 await scenario('unsupported WebGL state',async()=>{const p=await context.newPage();await p.addInitScript(()=>Object.defineProperty(window,'WebGL2RenderingContext',{value:undefined}));await p.goto(url);await p.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('UNSUPPORTED'));await p.close();});
 assert.deepEqual(await page.evaluate(()=>window.__forbiddenCalls),[]);assert(!requests.some(r=>r.method!=='GET'||/\/api\/|\/ws/.test(r.url)));assert.deepEqual(errors,[]);
 report.errors=errors;report.forbiddenMediaXRCalls=[];report.result='PASS';
}catch(error){report.error=String(error);report.e0='E0_FAIL';report.e1='BLOCKED_BY_E0';if(browser){const pages=browser.contexts().flatMap(c=>c.pages());if(pages[0]){report.statusText=await pages[0].locator('#status').innerText().catch(()=>null);report.diagnostic=await pages[0].locator('#status').getAttribute('data-diagnostic').catch(()=>null);await pages[0].screenshot({path:path.join(out,'e0-error-desktop.png')}).catch(()=>{});}}throw error;}finally{report.viteLog=logs;await fs.writeFile(path.join(out,'browser-report-e1.json'),JSON.stringify(report,null,2)+'\n');if(browser)await browser.close();vite.kill();}
console.log(JSON.stringify({result:report.result,scenarios:report.scenarios,runs:report.runs.map(r=>({...r.frameTimeMs,raw:undefined}))},null,2));
