/** E0-only Three.js manual vertex vs Box3 check; no E1 renderer or controls. */
import {spawn} from 'node:child_process';
import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),web=path.join(root,'apps/web');
const out=path.resolve(process.env.P507_TV_DIAGNOSTIC_DIR||path.join(root,'.local/p507-tv-diagnostic'));
await fs.mkdir(out,{recursive:true});
const {chromium}=createRequire(path.join(web,'package.json'))('playwright');
const vite=spawn(process.execPath,[path.join(web,'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','5186','--strictPort'],{cwd:web,windowsHide:true,stdio:'ignore'});
let browser;
try{
  for(let i=0;i<80;i++){try{if((await fetch('http://127.0.0.1:5186/p507-webxr-e1.html')).ok)break;}catch{}if(vite.exitCode!==null)throw Error('Diagnostic Vite exited');await new Promise(r=>setTimeout(r,100));}
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/google-chrome'),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader']});
  const page=await browser.newPage();await page.goto('http://127.0.0.1:5186/p507-webxr-e1.html');
  const result=await page.evaluate(async()=>{
    const {GLTFLoader}=await import('/node_modules/three/examples/jsm/loaders/GLTFLoader.js');
    const {Vector3,Box3,REVISION}=await import('/node_modules/three/build/three.module.js');
    const response=await fetch('/p507-e1-assets/P507_G1_G2_PROVISIONAL.glb');if(!response.ok)throw Error('Missing pinned asset');
    const bytes=await response.arrayBuffer();
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
    if(hash!=='8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49')throw Error('Not frozen R4');
    const g=await new GLTFLoader().parseAsync(bytes,'/p507-e1-assets/');g.scene.updateMatrixWorld(true);
    const parts=[];const union=new Box3();
    g.scene.traverse(node=>{if(!node.isMesh)return;let at=node;while(at&&!at.userData.survey_instance_id)at=at.parent;if(at?.userData.survey_instance_id!=='P507-TV-LARGE')return;
      const manual=new Box3(),position=node.geometry.attributes.position;for(let i=0;i<position.count;i++)manual.expandByPoint(new Vector3().fromBufferAttribute(position,i).applyMatrix4(node.matrixWorld));
      const box=new Box3().setFromObject(node,true),bounds=[...manual.min.toArray(),...manual.max.toArray()],boxBounds=[...box.min.toArray(),...box.max.toArray()];union.union(manual);
      const association=g.parser.associations.get(node)||{};
      parts.push({name:node.name,id:at.userData.survey_instance_id,parent:node.parent?.name||null,positionCount:position.count,indexCount:node.geometry.index?.count??null,association,matrixWorldColumnMajor:node.matrixWorld.toArray(),manual_bounds_gltf:bounds,box3_precise_bounds_gltf:boxBounds,max_delta_m:Math.max(...bounds.map((v,i)=>Math.abs(v-boxBounds[i])))});
    });
    if(parts.length!==5)throw Error('Unexpected TV primitive grouping');
    return {label:'E0_ONLY_READ_ONLY_DIAGNOSTIC',asset_sha256:hash,three_version:REVISION,components:parts,union_bounds_gltf:[...union.min.toArray(),...union.max.toArray()],box3_vs_manual_max_delta_m:Math.max(...parts.map(p=>p.max_delta_m)),e0:'E0_FAIL_UNCHANGED',e1:'NOT_RUN'};
  });
  result.browser=browser.version();
  await fs.writeFile(path.join(out,'three-tv-report.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({three:result.three_version,browser:result.browser,components:result.components.length,box3_vs_manual_max_delta_m:result.box3_vs_manual_max_delta_m,union:result.union_bounds_gltf},null,2));
}finally{if(browser)await browser.close();vite.kill();}
