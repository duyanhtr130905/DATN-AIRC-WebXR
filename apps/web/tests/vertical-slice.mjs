import { chromium } from "playwright";
import { spawn, spawnSync } from "node:child_process";
import { mkdir, writeFile, readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { platform } from "node:os";
import { PerspectiveCamera, Vector3 } from "three";
const root=resolve(fileURLToPath(new URL("../../..",import.meta.url)));
const out=resolve(root,".local/m1-c-browser");await mkdir(out,{recursive:true});
const report={status:"FAIL",executedAt:new Date().toISOString(),build:spawnSync("git",["rev-parse","HEAD"],{cwd:root,encoding:"utf8",windowsHide:true}).stdout.trim(),environment:{os:platform(),browser:null,renderer:"Chrome WebGL2 ANGLE software; not physical Galaxy/VR"},synthetic:true,scenarios:[]};
let browser,frontend;const errors=[];
async function scenario(name,run){const row={name,status:"FAIL"};report.scenarios.push(row);await run();row.status="PASS";}
try{
 const bin=process.env.CHROME_BIN||["C:/Program Files/Google/Chrome/Application/chrome.exe","/usr/bin/google-chrome","/usr/bin/chromium"].find(existsSync);assert.ok(bin,"CHROME_BIN required");
 frontend=spawn(process.execPath,[resolve(root,"apps/web/node_modules/vite/bin/vite.js"),"preview","--config",resolve(root,"apps/web/vite.config.ts"),"--host","127.0.0.1","--port","5173","--strictPort","--outDir",resolve(root,"apps/web/dist")],{cwd:root,windowsHide:true,env:{...process.env,API_PROXY_TARGET:`http://127.0.0.1:${process.env.API_PORT}`},stdio:"ignore"});
 frontend.on("error",error=>errors.push(error.message));
 let ready=false;for(let i=0;i<100;i++){try{if((await fetch("http://127.0.0.1:5173/")).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}assert.ok(ready,"Vite startup");
 browser=await chromium.launch({executablePath:bin,headless:true,args:["--use-angle=swiftshader","--enable-unsafe-swiftshader"]});report.environment.browser=browser.version();
 const context=await browser.newContext({viewport:{width:1440,height:1100}});const page=await context.newPage();page.on("pageerror",e=>errors.push(e.message));
 const origin="http://127.0.0.1:5173";const room=process.env.SYNTHETIC_ROOM_ID;
 const rows=(await (await fetch(`${origin}/api/v1/rooms/${room}/objects?limit=100`)).json()).data;
 assert.equal(rows.length,20);rows.sort((a,b)=>a.id.localeCompare(b.id));const target=rows.at(-1);
 await scenario("Real PostgreSQL Catalog UUIDs +41state atomic snapshot +Canvas",async()=>{
  await page.goto(origin);await page.getByLabel("Phòng synthetic").selectOption(room);
  await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor({timeout:15000});
  assert.equal(await page.locator("[data-object-id]").count(),20);await page.locator("canvas").waitFor();
  await page.waitForFunction(()=>document.querySelector("canvas")?.getBoundingClientRect().width>400);
  const states=await (await fetch(`${origin}/api/v1/rooms/${room}/states?limit=100`)).json();assert.equal(states.data.length,41);
 });
 await scenario("Actual mesh ray pick maps stable UUID into Information Panel",async()=>{
  const rect=await page.locator("canvas").boundingBox();const camera=new PerspectiveCamera(45,rect.width/rect.height,0.1,1000);camera.position.set(8,7,11);camera.lookAt(0,.5,0);camera.updateMatrixWorld();
  const point=new Vector3(3,.65,2.25).project(camera);
  await page.mouse.click(rect.x+(point.x+1)*rect.width/2,rect.y+(1-point.y)*rect.height/2);
  await page.locator(`[data-object-id="${target.id}"][aria-pressed="true"]`).waitFor();
  assert.ok((await page.getByTestId("object-panel").innerText()).includes(target.id));
 });
 let before;
 await scenario("Guarded CLI update -> PostgreSQL commit -> real WS -> Panel and Canvas pixels",async()=>{
  await page.locator('[data-state-type="equipment_status"][data-version="1"]').waitFor();
  before=await page.locator("canvas").screenshot({path:resolve(out,"canvas-available.png")});
  const value=resolve(root,".local/m1-c-value.json");await writeFile(value,JSON.stringify({status:"maintenance"}));
  const result=spawnSync(process.env.API_PYTHON||"python",["-m","app.modules.state.cli","--confirm-database",new URL(process.env.DATABASE_URL.replace("postgresql+psycopg:","postgresql:")).pathname.slice(1),"--room-id",room,"--target-kind","object","--target-id",target.id,"--state-type","equipment_status","--expected-version","1","--value-file",value],{cwd:resolve(root,"apps/api"),env:process.env,encoding:"utf8",windowsHide:true,timeout:10000});
  assert.equal(result.status,0,"Guarded CLI must commit");
  await page.locator('[data-state-type="equipment_status"][data-version="2"]').waitFor({timeout:10000});
  assert.match(await page.locator('[data-state-type="equipment_status"]').innerText(),/maintenance/);
  const after=await page.locator("canvas").screenshot({path:resolve(out,"canvas-maintenance.png")});assert.notDeepEqual(before,after,"Actual Canvas pixels change");
  await page.screenshot({path:resolve(out,"desktop.png"),fullPage:true});
 });
 await scenario("Room switch resets scope; return gets authoritative snapshot",async()=>{
  await page.getByLabel("Phòng synthetic").selectOption(process.env.SECOND_ROOM_ID);
  await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor();assert.equal(await page.locator("[data-object-id]").count(),1);assert.equal(await page.locator(`[data-object-id="${target.id}"]`).count(),0);
  await page.getByLabel("Phòng synthetic").selectOption(room);await page.locator('[data-testid="realtime"][data-status="connected"]').waitFor();
  await page.locator(`[data-object-id="${target.id}"]`).click();await page.locator('[data-state-type="equipment_status"][data-version="2"]').waitFor();
 });
 await scenario("390px viewport emulation: touch, keyboard/focus and no overflow",async()=>{
  const mobile=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});const p=await mobile.newPage();p.on("pageerror",e=>errors.push(e.message));await p.goto(origin);await p.getByLabel("Phòng synthetic").selectOption(room);await p.locator('[data-testid="realtime"][data-status="connected"]').waitFor();
  await p.locator(`[data-object-id="${target.id}"]`).tap();await p.locator('[data-state-type="equipment_status"][data-version="2"]').waitFor();assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await p.locator(`[data-object-id="${target.id}"]`).focus();assert.ok(await p.locator(`[data-object-id="${target.id}"]`).evaluate(el=>el===document.activeElement));await p.screenshot({path:resolve(out,"mobile-390.png"),fullPage:true});await mobile.close();
 });
 assert.deepEqual(errors,[]);report.status="PASS";await context.close();
}catch(error){report.error="Browser vertical slice assertion failed; inspect CI logs";console.error(error);process.exitCode=1;}
finally{await browser?.close();if(frontend&&frontend.exitCode===null){const exit=new Promise(r=>frontend.once("exit",r));frontend.kill();await Promise.race([exit,new Promise(r=>setTimeout(r,3000))]);if(frontend.exitCode===null)frontend.kill("SIGKILL");}await writeFile(resolve(out,"report.json"),JSON.stringify(report,null,2)+"\n");console.log(JSON.stringify(report,null,2));}
