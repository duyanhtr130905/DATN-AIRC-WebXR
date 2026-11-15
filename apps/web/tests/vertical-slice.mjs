import { chromium } from "playwright";
import { spawn, spawnSync } from "node:child_process";
import { mkdir, writeFile, readFile, readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { platform } from "node:os";
import { PerspectiveCamera, Vector3 } from "three";
const root=resolve(fileURLToPath(new URL("../../..",import.meta.url)));
const out=resolve(root,".local/m1-c-browser");await mkdir(out,{recursive:true});
const python=process.env.API_PYTHON||"python";
const database=new URL(process.env.DATABASE_URL.replace("postgresql+psycopg:","postgresql:")).pathname.slice(1);
assert.match(database,/^airc_test_catalog_[0-9a-f]{32}$/);
const report={status:"FAIL",executedAt:new Date().toISOString(),build:spawnSync("git",["rev-parse","HEAD"],{cwd:root,encoding:"utf8",windowsHide:true}).stdout.trim(),environment:{os:platform(),browser:null,renderer:"Chrome WebGL2 ANGLE software; not physical Galaxy/VR",apiProcesses:1},synthetic:true,scenarios:[],samples:[],network:{requests:0,webSockets:0,assets:[]}};
let browser,frontend;const children=[];const errors=[];let faulted=false;
const now=()=>Number(process.hrtime.bigint())/1e6;
async function scenario(name,run,faultInjection=false){const row={name,faultInjection,status:"FAIL"};report.scenarios.push(row);await run();row.status="PASS";}
async function waitFor(run,timeout=10000){const start=now();while(now()-start<timeout){if(await run())return;await new Promise(r=>setTimeout(r,20));}throw new Error("Bounded condition timed out");}
function command(module,args){const result=spawnSync(python,["-m",module,...args],{cwd:resolve(root,"apps/api"),env:process.env,encoding:"utf8",windowsHide:true,timeout:10000});assert.equal(result.status,0,"Guarded synthetic CLI failed");return result;}
function databaseFault(action){if(action==="block")faulted=true;const result=spawnSync(python,[resolve(root,"apps/api/tests/database_fault.py"),action,database],{cwd:root,env:process.env,encoding:"utf8",windowsHide:true,timeout:10000});assert.equal(result.status,0,"Disposable database fault operation failed");faulted=action==="block";}
async function update(room,target,version,status){
 const value=resolve(root,".local/m1-c-value.json");await writeFile(value,JSON.stringify({status}));
 const t0=now();const child=spawn(python,["-m","app.modules.state.cli","--confirm-database",database,"--room-id",room,"--target-kind","object","--target-id",target,"--state-type","equipment_status","--expected-version",String(version),"--value-file",value,"--diagnostics"],{cwd:resolve(root,"apps/api"),env:process.env,windowsHide:true,stdio:["ignore","pipe","pipe"]});children.push(child);
 let stdout="";let ack=null;child.stdout.on("data",data=>{stdout+=data;if(ack===null&&stdout.includes("\n"))ack=now();});child.stderr.resume();
 const finished=new Promise((res,rej)=>{child.on("error",rej);child.on("exit",code=>code===0?res():rej(new Error("Guarded CLI exited nonzero")));});
 let timer;try{await Promise.race([finished,new Promise((_,reject)=>{timer=setTimeout(()=>{child.kill();reject(new Error("CLI deadline"));},10000);})]);}finally{clearTimeout(timer);}
 return {t0,t1_ack:ack??now(),result:JSON.parse(stdout)};
}
async function calibrate(page){
 const exchanges=[];for(let i=0;i<12;i++){const before=now();const browser=await page.evaluate(()=>performance.now());const after=now();exchanges.push({before,browser,after,lower:before-browser,upper:after-browser});}
 exchanges.sort((a,b)=>(a.upper-a.lower)-(b.upper-b.lower));return {...exchanges[0],exchanges};
}
function summary(values){const sorted=[...values].sort((a,b)=>a-b);return {n:sorted.length,p50:sorted[Math.ceil(sorted.length*.5)-1],p95:sorted[Math.ceil(sorted.length*.95)-1],max:sorted.at(-1)};}
try{
 const bin=process.env.CHROME_BIN||["C:/Program Files/Google/Chrome/Application/chrome.exe","/usr/bin/google-chrome","/usr/bin/chromium"].find(existsSync);assert.ok(bin,"CHROME_BIN required");
 frontend=spawn(process.execPath,[resolve(root,"apps/web/node_modules/vite/bin/vite.js"),"preview","--config",resolve(root,"apps/web/vite.config.ts"),"--host","127.0.0.1","--port","5173","--strictPort","--outDir",resolve(root,"apps/web/dist")],{cwd:root,windowsHide:true,env:{...process.env,API_PROXY_TARGET:`http://127.0.0.1:${process.env.API_PORT}`},stdio:"ignore"});frontend.on("error",e=>errors.push(e.message));
 await waitFor(async()=>{try{return(await fetch("http://127.0.0.1:5173/")).ok;}catch{return false;}});
 browser=await chromium.launch({executablePath:bin,headless:true,args:["--use-angle=swiftshader","--enable-unsafe-swiftshader"]});report.environment.browser=browser.version();
 const context=await browser.newContext({viewport:{width:1440,height:1100}});const page=await context.newPage();page.on("pageerror",e=>errors.push(e.message));
 page.on("request",request=>{report.network.requests++;const path=new URL(request.url()).pathname;if(path.startsWith("/assets/")&&report.network.assets.length<100&&!report.network.assets.includes(path))report.network.assets.push(path);});page.on("websocket",()=>report.network.webSockets++);
 const origin="http://127.0.0.1:5173";const room=process.env.SYNTHETIC_ROOM_ID;
 await scenario("Empty PostgreSQL startup: no rooms, no hidden hardcoded fallback",async()=>{
  const rooms=await(await fetch(`${origin}/api/v1/rooms`)).json();assert.deepEqual(rooms.data,[]);
  await page.goto(origin);await page.getByTestId("catalog-status").filter({hasText:/Chưa có phòng/}).waitFor();assert.equal(await page.locator("canvas").count(),0);
 });
 await scenario("Explicit guarded CLI seed creates synthetic Catalog/state, idempotent",async()=>{
  command("app.modules.catalog.vertical_seed",["--confirm-database",database]);command("app.modules.catalog.vertical_seed",["--confirm-database",database]);
  await page.getByRole("button",{name:/Tải lại Catalog/}).click();await page.getByLabel("Phòng synthetic").selectOption(room);
 });
 const rows=(await(await fetch(`${origin}/api/v1/rooms/${room}/objects?limit=100`)).json()).data;
 assert.equal(rows.length,20);rows.sort((a,b)=>a.id.localeCompare(b.id));const target=rows.at(-1);
 await scenario("Real PostgreSQL UUID Catalog +41state atomic snapshot +Canvas",async()=>{
  await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor({timeout:15000});assert.equal(await page.locator("[data-object-id]").count(),20);
  await page.waitForFunction(()=>document.querySelector("canvas")?.getBoundingClientRect().width>400);
  const states=await(await fetch(`${origin}/api/v1/rooms/${room}/states?limit=100`)).json();assert.equal(states.data.length,41);assert.ok(await page.evaluate(()=>Boolean(window.__AIRC_TEST__)),"Build with VITE_TEST_DIAGNOSTICS=1");
 });
 await scenario("Actual mesh ray pick maps stable UUID into Information Panel",async()=>{
  const rect=await page.locator("canvas").boundingBox();const camera=new PerspectiveCamera(45,rect.width/rect.height,.1,1000);camera.position.set(8,7,11);camera.lookAt(0,.5,0);camera.updateMatrixWorld();const point=new Vector3(3,.65,2.25).project(camera);
  await page.mouse.click(rect.x+(point.x+1)*rect.width/2,rect.y+(1-point.y)*rect.height/2);
  await page.locator(`[data-object-id="${target.id}"][aria-pressed="true"]`).waitFor();assert.ok((await page.getByTestId("object-panel").innerText()).includes(target.id));
 });
 await scenario("Guarded CLI -> real WS -> Panel + afterRender material + actual Canvas pixels",async()=>{
  await page.locator('[data-state-type="equipment_status"][data-version="1"]').waitFor();const before=await page.locator("canvas").screenshot({path:resolve(out,"canvas-available.png")});
  const changed=await update(room,target.id,1,"maintenance");assert.equal(changed.result.state.version,2);
  await page.locator('[data-state-type="equipment_status"][data-version="2"]').waitFor();
  await page.waitForFunction(({target})=>window.__AIRC_TEST__.events.some(e=>e.kind==="scene.afterRender"&&e.objectId===target&&e.version===2&&e.materialColor==="c14336"),{target:target.id});
  const after=await page.locator("canvas").screenshot({path:resolve(out,"canvas-maintenance.png")});assert.notDeepEqual(before,after);await page.screenshot({path:resolve(out,"desktop.png"),fullPage:true});
 });
 await scenario("20 measured updates with browser clock calibration and render observation",async()=>{
  report.calibrationBefore=await calibrate(page);const offset=(report.calibrationBefore.lower+report.calibrationBefore.upper)/2;
  for(let i=0;i<20;i++){
    const status=i%2===0?"available":"maintenance";const version=i+3;const color=status==="maintenance"?"c14336":"c46b37";
    const changed=await update(room,target.id,version-1,status);
    await page.waitForFunction(({target,version,color})=>window.__AIRC_TEST__.events.some(e=>e.kind==="scene.afterRender"&&e.objectId===target&&e.version===version&&e.materialColor===color),{target:target.id,version,color});
    await page.locator(`[data-state-type="equipment_status"][data-version="${version}"]`).waitFor();
    const events=await page.evaluate(()=>window.__AIRC_TEST__.events);const sequence=changed.result.sequence;
    const received=events.find(e=>e.kind==="received"&&e.type==="state.updated"&&e.sequence===sequence);
    const react=events.find(e=>e.kind==="react.applied"&&e.sequence===sequence);
    const render=events.find(e=>e.kind==="scene.afterRender"&&e.objectId===target.id&&e.version===version&&e.materialColor===color);
    assert.ok(received&&react&&render);assert.ok(render.at>=received.at);assert.ok(react.at>=received.at);
    const pyStart=Number(changed.result.test_diagnostics.started_ns)/1e6;const pyCommit=Number(changed.result.test_diagnostics.committed_ns)/1e6;
    const pyOffsetLower=changed.t0-pyStart,pyOffsetUpper=changed.t1_ack-pyCommit;
    assert.ok(pyOffsetLower<=pyOffsetUpper);
    report.samples.push({version,sequence,status,t0_node_ms:changed.t0,t1_commit_node_bounds:[pyCommit+pyOffsetLower,pyCommit+pyOffsetUpper],t1_ack_node_ms:changed.t1_ack,t2_browser_ms:received.at,t3_browser_ms:react.at,t4_afterRender_browser_ms:render.at,materialColor:render.materialColor,drawCalls:render.drawCalls,transaction_ms:changed.result.test_diagnostics.transaction_ms,update_to_render_ms:render.at+offset-changed.t0,commit_to_render_bounds_ms:[render.at+report.calibrationBefore.lower-(pyCommit+pyOffsetUpper),render.at+report.calibrationBefore.upper-(pyCommit+pyOffsetLower)],receive_to_react_ms:react.at-received.at,receive_to_render_ms:render.at-received.at});
  }
  report.calibrationAfter=await calibrate(page);
  const beforeMid=(report.calibrationBefore.lower+report.calibrationBefore.upper)/2,afterMid=(report.calibrationAfter.lower+report.calibrationAfter.upper)/2;
  const drift=Math.abs(afterMid-beforeMid);assert.ok(drift<=10,"Clock endpoint drift exceeds10ms measurement budget");
  report.clockWindow={lower:Math.min(report.calibrationBefore.lower,report.calibrationAfter.lower)-1,upper:Math.max(report.calibrationBefore.upper,report.calibrationAfter.upper)+1,endpointDriftMs:drift,quantizationAllowanceMs:1,driftBudgetMs:10};
  const midpoint=(report.clockWindow.lower+report.clockWindow.upper)/2;
  for(const sample of report.samples){sample.update_to_render_ms=sample.t4_afterRender_browser_ms+midpoint-sample.t0_node_ms;sample.commit_to_render_bounds_ms=[sample.t4_afterRender_browser_ms+report.clockWindow.lower-sample.t1_commit_node_bounds[1],sample.t4_afterRender_browser_ms+report.clockWindow.upper-sample.t1_commit_node_bounds[0]];}
  report.latency=summary(report.samples.map(s=>s.update_to_render_ms));report.transaction=summary(report.samples.map(s=>s.transaction_ms));report.receiveToRender=summary(report.samples.map(s=>s.receive_to_render_ms));report.errors=0;report.timeouts=0;
  report.clockPolicy="Node hrtime orchestrates t0/spawn and commit ack. Browser performance.now mapped by12request/reply offset bounds; use hull of shortest-RTT calibration before/after plus1ms allowance; endpoint drift must be<=10ms. Estimated intervals assume stable clock rate inside the window. Python perf_counter commit is mapped only to a conservative Node spawn-to-ack interval; no subtraction of independent origins. t4 is Three onAfterRender draw submission plus pixel screenshot, not hardware scanout. t0 includes guarded CLI process startup.";
 });
 await scenario("Duplicate/old deltas ignored; injected sequence gap forces reconnect snapshot",async()=>{
  const sequence=report.samples.at(-1).sequence;
  await page.evaluate(()=>{const p=window.__AIRC_TEST__;p.inject(p.lastDelta);p.inject({...p.lastDelta,sequence:p.lastDelta.sequence-1});});
  assert.match(await page.getByTestId("realtime").innerText(),new RegExp(`sequence ${sequence}`));
  await page.evaluate(()=>{const p=window.__AIRC_TEST__;p.inject({...p.lastDelta,sequence:p.lastDelta.sequence+2});});
  await page.waitForFunction(()=>window.__AIRC_TEST__.events.some(e=>e.kind==="connection"&&e.status==="resync_required"));
  await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor({timeout:15000});await page.locator('[data-state-type="equipment_status"][data-version="22"]').waitFor();
 },true);
 await scenario("Actual socket disconnect marks stale; reconnect authoritative snapshot",async()=>{
  const start=now();const marker=await page.evaluate(()=>{const p=window.__AIRC_TEST__;const marker=performance.now();p.disconnect();return marker;});
  await page.waitForFunction(marker=>window.__AIRC_TEST__.events.some(e=>e.at>=marker&&e.status==="stale"),marker);
  await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor({timeout:15000});report.reconnect_ms=now()-start;
 },true);
 await scenario("Room switch clears scope, keyboard selection and no leaked old-room state",async()=>{
  await page.getByLabel("Phòng synthetic").selectOption(process.env.SECOND_ROOM_ID);await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor();assert.equal(await page.locator("[data-object-id]").count(),1);assert.equal(await page.locator(`[data-object-id="${target.id}"]`).count(),0);
  await page.getByLabel("Phòng synthetic").selectOption(room);await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor();const button=page.locator(`[data-object-id="${target.id}"]`);await button.focus();await page.keyboard.press("Enter");await page.locator('[data-state-type="equipment_status"][data-version="22"]').waitFor();
 });
 await scenario("390px viewport emulation: touch/focus and no overflow",async()=>{
  const mobile=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});const p=await mobile.newPage();p.on("pageerror",e=>errors.push(e.message));await p.goto(origin);await p.getByLabel("Phòng synthetic").selectOption(room);await p.locator('[data-testid="realtime"][data-status="connected"]').waitFor();await p.locator(`[data-object-id="${target.id}"]`).tap();await p.locator('[data-state-type="equipment_status"][data-version="22"]').waitFor();assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:resolve(out,"mobile-390.png"),fullPage:true});await mobile.close();
 });
 await scenario("WebGL unavailable fault: live DOM Catalog/Panel remains usable",async()=>{
  const unsupported=await browser.newContext();await unsupported.addInitScript(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type==="webgl2"?null:original.call(this,type,...args);};});const p=await unsupported.newPage();await p.goto(origin);await p.getByLabel("Phòng synthetic").selectOption(room);await p.getByRole("alert").filter({hasText:/WebGL2/}).waitFor();await p.locator(`[data-object-id="${target.id}"]`).click();await p.locator('[data-state-type="equipment_status"][data-version="22"]').waitFor();assert.equal(await p.locator("canvas").count(),0);await p.screenshot({path:resolve(out,"unsupported-live.png"),fullPage:true});await unsupported.close();
 },true);
 await scenario("Public read contract filters private metadata; no write endpoints",async()=>{
  const object=await(await fetch(`${origin}/api/v1/objects/${target.id}`)).json();assert.deepEqual(Object.keys(object.data.metadata).sort(),["description","label"]);for(const key of ["evidence_ref","external_reference","transform"])assert.equal(key in object.data,false);
  for(const method of ["POST","PATCH","DELETE"]){const response=await fetch(`${origin}/api/v1/objects/${target.id}`,{method});assert.equal(response.status,405);}
 });
 await scenario("Real disposable PostgreSQL disconnect ->503/stale -> recovery snapshot",async()=>{
  const marker=await page.evaluate(()=>performance.now());databaseFault("block");
  try{
    await waitFor(async()=>{const response=await fetch(`${origin}/api/ready`);return response.status===503;});assert.equal((await fetch(`${origin}/api/health`)).status,200);
    await page.waitForFunction(marker=>window.__AIRC_TEST__.events.some(e=>e.at>=marker&&e.status==="stale"),marker,{timeout:15000});
    assert.equal((await fetch(`${origin}/api/v1/rooms`)).status,503);
  }finally{databaseFault("restore");}
  await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor({timeout:20000});await page.locator('[data-state-type="equipment_status"][data-version="22"]').waitFor();
 },true);
 await scenario("Software-rendered browser frame timing and bounded network requests",async()=>{
  report.frameIntervalsMs=await page.evaluate(()=>new Promise(resolve=>{const times=[];let previous;function frame(at){if(previous!==undefined)times.push(at-previous);previous=at;if(times.length<90)requestAnimationFrame(frame);else resolve(times);}requestAnimationFrame(frame);}));report.frameTiming=summary(report.frameIntervalsMs);assert.ok(report.network.requests<150,"No request polling storm");assert.ok(!report.network.assets.some(path=>/emulate-|office_|meeting_room-|living_room-|music_room-/.test(path)),"Unused XR emulator/example chunks are not fetched");
  const assetDir=resolve(root,"apps/web/dist/assets");report.bundle=[];for(const file of await readdir(assetDir)){const size=(await stat(resolve(assetDir,file))).size;report.bundle.push({file,bytes:size});}
 });
 await scenario("Actual backend process shutdown -> visible unavailable; no live fallback",async()=>{
  await writeFile(resolve(root,".local/m1-c-stop-api.request"),"stop owned test server only");
  await waitFor(async()=>{try{return !(await fetch(`${origin}/api/health`)).ok;}catch{return true;}},12000);
  await page.getByRole("button",{name:/Tải lại Catalog/}).click();await page.getByRole("alert").filter({hasText:/Backend không khả dụng/}).waitFor();assert.equal(await page.locator("[data-object-id]").count(),0);assert.equal(await page.locator("canvas").count(),0);
 },true);
 assert.deepEqual(errors,[]);report.status="PASS";await context.close();
}catch(error){report.error="C3 assertion failed; inspect CI logs; no private paths persisted in report";console.error(error);process.exitCode=1;}
finally{
 if(faulted){try{databaseFault("restore");}catch{process.exitCode=1;}}
 await browser?.close();for(const child of [...children,frontend].filter(Boolean)){if(child.exitCode===null){const exit=new Promise(r=>child.once("exit",r));child.kill();await Promise.race([exit,new Promise(r=>setTimeout(r,3000))]);if(child.exitCode===null)child.kill("SIGKILL");}}
 await writeFile(resolve(out,"report.json"),JSON.stringify(report,null,2)+"\n");console.log(JSON.stringify({status:report.status,scenarios:report.scenarios,latency:report.latency},null,2));
}
