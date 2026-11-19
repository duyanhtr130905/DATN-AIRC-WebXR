/** Responsive rendering emulation only; does not certify physical mobile or touch locomotion. */
import {spawn,execFileSync} from 'node:child_process';import {createRequire} from 'node:module';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),web=path.join(root,'apps/web'),out=path.join(root,'.local/p507-e0-e1');
const {chromium}=createRequire(path.join(web,'package.json'))('playwright');
const vite=spawn(process.execPath,[path.join(web,'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','5187','--strictPort'],{cwd:web,windowsHide:true,stdio:'ignore'});
let browser;const report={head:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),dirty:!!execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim(),result:'FAIL',scope:'Viewport/touch emulation; physical phone NOT TESTED, mobile touch navigation NOT IMPLEMENTED',cases:[]};
try{
 for(let i=0;i<100;i++){try{if((await fetch('http://127.0.0.1:5187/p507-webxr-e1.html')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/google-chrome'),args:process.env.P507_GPU==='default'?['--enable-webgl']:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});report.browser=browser.version();
 for(const viewport of [{width:390,height:844},{width:768,height:1024}]){
  const ctx=await browser.newContext({viewport,isMobile:true,hasTouch:true,deviceScaleFactor:1}),p=await ctx.newPage();
  await p.goto('http://127.0.0.1:5187/p507-webxr-e1.html',{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>window.__P507_E1__,null,{polling:100,timeout:180000});
  const actual=await p.evaluate(()=>{const api=window.__P507_E1__;let selected=null;for(let x=-.8;x<=.8&&!selected;x+=.2)for(let y=-.7;y<=.7&&!selected;y+=.2)selected=api.select(x,y);const rect=id=>{const r=document.querySelector(id).getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};};return {e0:api.snapshot().e0,selected,panel:document.querySelector('#selection').textContent,aside:rect('aside'),selection:rect('#selection'),viewport:[innerWidth,innerHeight],canvas:api.snapshot().renderResolution};});
  assert.equal(actual.e0,'E0_PASS');assert(actual.selected);assert(actual.panel.includes('PROVISIONAL / USER_REPORTED'));
  await p.screenshot({path:path.join(out,`responsive-${viewport.width}.png`)});
  const fits=[actual.aside,actual.selection].every(r=>r.left>=0&&r.right<=viewport.width+.5&&r.top>=0&&r.bottom<=viewport.height+.5);
  report.cases.push({viewport,actual,result:fits?'PASS':'PARTIAL_PANEL_OVERFLOW'});await ctx.close();
 }
 report.result=report.cases.every(c=>c.result==='PASS')?'PASS':'PARTIAL';
}finally{await fs.writeFile(path.join(out,'responsive-report.json'),JSON.stringify(report,null,2)+'\n');if(browser)await browser.close();vite.kill();}
console.log(JSON.stringify(report,null,2));if(report.result!=='PASS')process.exitCode=1;
