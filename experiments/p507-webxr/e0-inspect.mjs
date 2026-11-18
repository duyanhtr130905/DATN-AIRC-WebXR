/** Reproducible E0-only inspection. Never enables E1 or modifies frozen inputs. */
import {spawn,execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),web=path.join(root,'apps/web'),out=path.join(root,'.local/p507-e0-e1');
const {chromium}=createRequire(path.join(web,'package.json'))('playwright');
const vite=spawn(process.execPath,[path.join(web,'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port','5185','--strictPort'],{cwd:web,windowsHide:true,stdio:'ignore'});
let browser;
try{
  for(let i=0;i<80;i++){try{if((await fetch('http://127.0.0.1:5185/p507-webxr-e1.html')).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/google-chrome'),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1280,height:720}});await page.route('**/src/p507-webxr-e1.ts',r=>r.fulfill({contentType:'application/javascript',body:'// E0-only audit: E1 entry intentionally not executed.'}));await page.goto('http://127.0.0.1:5185/p507-webxr-e1.html');
  const report=await page.evaluate(async()=>{
    const {GLTFLoader}=await import('/node_modules/three/examples/jsm/loaders/GLTFLoader.js'),{Vector3,Raycaster,PerspectiveCamera,Vector2}=await import('/node_modules/three/build/three.module.js');
    const {validateScene,reference}=await import('/src/p507-e1/scene-contract.ts'),{logicalId}=await import('/src/p507-e1/core.ts');
    const m=await(await fetch('/p507-e1-assets/asset-manifest.json')).json(),bytes=await(await fetch('/p507-e1-assets/P507_G1_G2_PROVISIONAL.glb')).arrayBuffer(),g=await new GLTFLoader().parseAsync(bytes,'/p507-e1-assets/');g.scene.updateMatrixWorld(true);
    const known=new Set(m.instances.filter(i=>i.status!=='UNPLACED').map(i=>i.id)),violations=[],meshIds=new Set();let meshCount=0,childMappings=0;
    g.scene.traverse(node=>{if(!node.isMesh)return;meshCount++;const id=logicalId(node,known);if(id){meshIds.add(id);if(!node.userData.survey_instance_id)childMappings++;}const proxy=m.collision_proxies.find(p=>p.id===id);if(!proxy)return;const pos=node.geometry.attributes.position;let maxOut=0;
      for(let i=0;i<pos.count;i++){const v=new Vector3().fromBufferAttribute(pos,i).applyMatrix4(node.matrixWorld),x=v.x,y=-v.z,z=v.y,dist=proxy.polygon.map((a,j)=>{const b=proxy.polygon[(j+1)%proxy.polygon.length];return ((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))/Math.hypot(b[0]-a[0],b[1]-a[1]);});const outside=Math.min(Math.max(0,-Math.min(...dist)),Math.max(0,Math.max(...dist)));maxOut=Math.max(maxOut,outside,proxy.bottom_z-z,z-proxy.top_z);}if(maxOut>.001)violations.push({id,node:node.name,maxOutsideM:maxOut});
    });
    let contractError=null,geometry=null;try{geometry=validateScene(g.scene,m);}catch(e){contractError=String(e);}
    const negatives=[];for(const mode of ['double-scale','double-rotate']){g.scene.scale.setScalar(mode==='double-scale'?1.15:1);g.scene.rotation.x=mode==='double-rotate'?Math.PI/2:0;try{validateScene(g.scene,m);negatives.push({mode,result:'FAIL_NOT_DETECTED'});}catch(e){negatives.push({mode,result:String(e).includes('identity transform')?'PASS':'UNEXPECTED_ERROR',error:String(e)});}}g.scene.scale.setScalar(1);g.scene.rotation.set(0,0,0);g.scene.updateMatrixWorld(true);
    const reject=(mode,fn,pattern)=>{try{fn();throw Error('NOT_DETECTED');}catch(e){const error=String(e);if(!pattern.test(error))throw Error(mode+': unexpected '+error);negatives.push({mode,result:'PASS',error});}};
    const badRef=structuredClone(reference);badRef.records[0].bounds[0]+=.1;
    reject('reference bounds wrong',()=>validateScene(g.scene,m,badRef),/E0_EXPORT_BOUNDS/);
    for(const mode of ['missing','duplicate']){const r=structuredClone(reference);if(mode==='missing')r.records.pop();else r.records[0]=r.records[1];reject('reference '+mode,()=>validateScene(g.scene,m,r),/E0_REFERENCE_RECORDS/);}
    const wrongHash=structuredClone(reference);wrongHash.model_sha256='0'.repeat(64);reject('reference asset hash',()=>validateScene(g.scene,m,wrongHash),/E0_REFERENCE_ASSET/);
    for(const mode of ['missing','duplicate']){const n=structuredClone(m);if(mode==='missing')n.instances.pop();else n.instances[0].id=n.instances[1].id;reject('manifest '+mode,()=>validateScene(g.scene,n),/IDs/);}
    let target;g.scene.traverse(n=>{if(!target&&n.isMesh&&logicalId(n,known)==='P507-DESK-A01')target=n;});
    const own=target.userData.survey_instance_id;target.userData.survey_instance_id='INVALID-ID';reject('wrong logical ID',()=>validateScene(g.scene,m),/Unknown\/unplaced GLB ID INVALID-ID/);if(own===undefined)delete target.userData.survey_instance_id;else target.userData.survey_instance_id=own;
    const px=target.position.x;target.position.x+=.1;reject('wrong child transform',()=>validateScene(g.scene,m),/E0_PROXY_CONTAINMENT|E0_EXPORT_BOUNDS/);target.position.x=px;
    const pos=target.geometry.attributes.position,original=pos.getX(0);pos.setX(0,original+10);reject('vertex outside proxy',()=>validateScene(g.scene,m),/E0_PROXY_CONTAINMENT: P507-DESK-A01/);pos.setX(0,original);g.scene.updateMatrixWorld(true);

    const camera=new PerspectiveCamera(78,1280/720,.04,60);camera.position.set(1.25,1.65,-7.415);camera.rotation.order='YXZ';camera.rotation.y=-Math.PI/2;camera.updateMatrixWorld();const ray=new Raycaster(),selected=new Set();
    for(let x=-.9;x<.91;x+=.15)for(let y=-.8;y<.81;y+=.15){ray.setFromCamera(new Vector2(x,y),camera);const hit=ray.intersectObject(g.scene,true)[0];if(hit){const id=logicalId(hit.object,known);if(id)selected.add(id);}}
    return {e0:contractError?'E0_FAIL':'E0_PASS',e1:'NOT_RUN_E0_ONLY_AUDIT',contractError,geometry,meshCount,logicalMeshIDs:meshIds.size,childMeshesResolvedThroughAncestor:childMappings,orientedProxyViolations:violations,proxyVertexToleranceM:.001,negativeTransformTests:negatives,actualRaycastIDs:[...selected],notice:'Static Python-derived reference versus independent Chrome GLTFLoader. No expected bounds generated by runtime; E1 measured separately.'};
  });
  report.head=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();report.dirty=!!execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim();report.timestamp=new Date().toISOString();report.browser=browser.version();report.environment='Headless Chrome SwiftShader';
  await fs.writeFile(path.join(out,'e0-scene-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
  if(report.e0!=='E0_PASS')process.exitCode=1;
}finally{if(browser)await browser.close();vite.kill();}
