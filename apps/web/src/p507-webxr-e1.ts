/** Isolated DEV-only E0/E1 experiment. No backend, telemetry, XR or media access. */
import {ACESFilmicToneMapping,AmbientLight,Color,DirectionalLight,HemisphereLight,Mesh,MeshStandardMaterial,PCFSoftShadowMap,PerspectiveCamera,PMREMGenerator,Raycaster,RectAreaLight,Scene,SRGBColorSpace,Vector2,WebGLRenderer} from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {RectAreaLightUniformsLib} from 'three/examples/jsm/lights/RectAreaLightUniformsLib.js';
import {check,displacement,InputState,logicalId,Navigation,PLAYER,SPAWN,summarize,validateManifest,type Manifest,type Point} from './p507-e1/core.ts';
import {validateScene} from './p507-e1/scene-contract.ts';
const el=(id:string)=>document.getElementById(id)!;
const show=(s:string)=>{el('status').textContent=s;};
const input=new InputState();
const canvas=el('view') as HTMLCanvasElement;
declare global {interface Window {__P507_E1__?: {snapshot:()=>Record<string,any>; reset:()=>void; measure:()=>void; move:(delta:Point)=>unknown; select:(x:number,y:number)=>string|null; pause:()=>void}}}
if(!import.meta.env.DEV) show('Development-only: khÃ´ng há»— trá»£ deployment.');
else if(!window.WebGL2RenderingContext) show('UNSUPPORTED: WebGL2 khÃ´ng kháº£ dá»¥ng.');
else run().catch(error=>{input.clear();show('ERROR: '+String(error));});
async function run(){
  const directory='/p507-e1-assets/';
  const get=async(name:string)=>{const r=await fetch(directory+name);check(r.ok,'Thiáº¿u asset '+name+' (HTTP '+r.status+'). Cháº¡y validator --prepare.');return r;};
  const loadStart=performance.now();
  const lock=await (await get('asset-lock.json')).json();
  const manifestBytes=await (await get('asset-manifest.json')).arrayBuffer();
  const sha=async(b:ArrayBuffer)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),v=>v.toString(16).padStart(2,'0')).join('');
  check(await sha(manifestBytes)===lock.files['asset-manifest.json'].sha256,'Manifest SHA-256 mismatch');
  const m=validateManifest(JSON.parse(new TextDecoder().decode(manifestBytes)) as Manifest);
  const bytes=await (await get('P507_G1_G2_PROVISIONAL.glb')).arrayBuffer(),hash=await sha(bytes);
  check(hash===m.model_sha256 && hash===lock.files['P507_G1_G2_PROVISIONAL.glb'].sha256 && bytes.byteLength===m.model_bytes,'GLB SHA-256/bytes mismatch');
  const gltf=await new GLTFLoader().parseAsync(bytes,directory),parsedMs=performance.now()-loadStart;
  const geometry=validateScene(gltf.scene,m);
  const nav=new Navigation(m);check(!nav.blocked(SPAWN,SPAWN),'Invalid spawn: '+nav.blocked(SPAWN,SPAWN));
  const gl=new WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
  gl.transmissionResolutionScale=.5;gl.setPixelRatio(Math.min(devicePixelRatio,1.5));gl.setSize(innerWidth,innerHeight);
  gl.outputColorSpace=SRGBColorSpace;gl.toneMapping=ACESFilmicToneMapping;gl.toneMappingExposure=1;
  gl.shadowMap.enabled=true;gl.shadowMap.type=PCFSoftShadowMap;gl.shadowMap.autoUpdate=false;
  const scene=new Scene();scene.background=new Color('#d9dedc');
  const pmrem=new PMREMGenerator(gl),env=new RoomEnvironment(),target=pmrem.fromScene(env,.04,.1,100);
  scene.environment=target.texture;scene.environmentIntensity=.30;env.dispose();pmrem.dispose();
  scene.add(new AmbientLight(0xffffff,.04),new HemisphereLight(0xe4efff,0xc1b7a2,.34));
  const sun=new DirectionalLight(0xfff4e3,2);sun.position.set(6.6,3.1,-5);sun.target.position.set(1.4,.1,-6.1);sun.castShadow=true;
  sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.near=.1;sun.shadow.camera.far=18;sun.shadow.camera.left=-5;sun.shadow.camera.right=5;sun.shadow.camera.top=5;sun.shadow.camera.bottom=-5;sun.shadow.normalBias=.012;sun.shadow.bias=-.0001;sun.shadow.radius=3;scene.add(sun,sun.target);
  RectAreaLightUniformsLib.init();for(const x of [1.4375,5.4625]){const light=new RectAreaLight(0xfff2dc,.95,.65,6.5);light.position.set(x,3.4,-4.6575);light.lookAt(x,0,-4.6575);scene.add(light);}
  // Same runtime material environment multipliers as frozen preview; no GLB edits.
  gltf.scene.traverse(node=>{if(!(node instanceof Mesh))return;node.castShadow=!node.name.includes('WINDOW_GLASS');node.receiveShadow=true;for(const mat of Array.isArray(node.material)?node.material:[node.material])if(mat instanceof MeshStandardMaterial){if(mat.name.includes('OFF_SCREEN'))mat.envMapIntensity=.12;if(mat.name.includes('TV_BEZEL'))mat.envMapIntensity=.35;}});
  scene.add(gltf.scene);gl.shadowMap.needsUpdate=true;
  const camera=new PerspectiveCamera(78,innerWidth/innerHeight,.04,60);camera.rotation.order='YXZ';
  let position:Point=[...SPAWN],yaw=-Math.PI/2,pitch=0,blocked:string|null=null,firstFrameMs:number|null=null,prior:number|null=null,paused=false;
  const raw:number[]=[];let measureStart=new Date().toISOString();
  function sync(){camera.position.set(position[0],PLAYER.eye,position[1]);camera.rotation.set(pitch,yaw,0,'YXZ');camera.updateMatrixWorld();}
  function reset(){position=[...SPAWN];yaw=-Math.PI/2;pitch=0;blocked=null;input.clear();if(document.pointerLockElement===canvas)document.exitPointerLock();sync();el('collision').textContent='';}
  reset();
  const known=new Set(m.instances.filter(i=>i.status!=='UNPLACED').map(i=>i.id)),ray=new Raycaster();
  let selected:string|null=null;
  function select(x=0,y=0){ray.setFromCamera(new Vector2(x,y),camera);const hit=ray.intersectObject(gltf.scene,true)[0];selected=hit?logicalId(hit.object,known):null;const record=m.instances.find(i=>i.id===selected),proxy=m.collision_proxies.find(i=>i.id===selected);
    el('selection').textContent=record?JSON.stringify({id:record.id,type:proxy?.kind,status:record.status,source:record.survey_transform.source_kind??'UNKNOWN',position_source:record.survey_transform.position_source??'UNKNOWN',rights:m.virtual_dimensions.rights??'UNKNOWN'},null,2):'KhÃ´ng cÃ³ logical object trong tÃ¢m ngáº¯m.';return selected;}
  function move(delta:Point){const result=nav.move(position,delta);position=result.position;blocked=result.reason;sync();el('collision').textContent=blocked?'BLOCKED_PATH: '+blocked:'';return result;}
  el('enter').addEventListener('click',()=>{try{const result=canvas.requestPointerLock();result?.catch(()=>{el('collision').textContent='Pointer lock bá»‹ tá»« chá»‘i; báº¥m Báº¯t Ä‘áº§u Ä‘á»ƒ thá»­ láº¡i.';});}catch{el('collision').textContent='UNSUPPORTED: pointer lock';}});
  el('reset').addEventListener('click',reset);
  document.addEventListener('pointerlockchange',()=>{input.lock(document.pointerLockElement===canvas && !document.hidden && document.hasFocus());prior=null;});
  document.addEventListener('pointerlockerror',()=>{input.clear();el('collision').textContent='Pointer lock bá»‹ tá»« chá»‘i.';});
  document.addEventListener('keydown',e=>{if(input.active&&['KeyW','KeyA','KeyS','KeyD'].includes(e.code)){e.preventDefault();input.key(e.code,true);}});
  document.addEventListener('keyup',e=>input.key(e.code,false));
  const clear=()=>{input.clear();prior=null;if(document.pointerLockElement===canvas)document.exitPointerLock();};
  window.addEventListener('blur',clear);document.addEventListener('visibilitychange',()=>{if(document.hidden)clear();});
  document.addEventListener('mousemove',e=>{if(!input.active)return;yaw-=e.movementX*.002;pitch=Math.max(-1.45,Math.min(1.45,pitch-e.movementY*.002));sync();});
  canvas.addEventListener('click',()=>{if(input.active)select();});
  window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();gl.setSize(innerWidth,innerHeight);});
  const context=gl.getContext(),debug=context.getExtension('WEBGL_debug_renderer_info');
  const snapshot=()=>({e0:'E0_PASS',geometry,assetHash:hash,assetSource:m.source_sha,assetCheckout:m.checkout_sha,transferBytes:bytes.byteLength,parsedMs,firstFrameMs,position:[...position],eyeHeight:PLAYER.eye,yaw,pitch,player:PLAYER,blocked,selected,inputActive:input.active,keys:[...input.keys],frameTimeMs:summarize([...raw]),measureStart,drawCalls:gl.info.render.calls,trianglesPerFrame:gl.info.render.triangles,canvas:[canvas.clientWidth,canvas.clientHeight],dpr:gl.getPixelRatio(),renderResolution:[canvas.width,canvas.height],gpu:{vendor:debug?context.getParameter(debug.UNMASKED_VENDOR_WEBGL):'UNKNOWN',renderer:debug?context.getParameter(debug.UNMASKED_RENDERER_WEBGL):'UNKNOWN'},browser:navigator.userAgent,hardwareConcurrency:navigator.hardwareConcurrency,quality:{antialias:true,shadows:1024,transmissionResolutionScale:.5,environmentIntensity:.3,toneMapping:'ACESFilmic',exposure:1,fov:78,cutaway:false},notice:'Web 3D experiment; not KPI, physical GPU or VR evidence'});
  window.__P507_E1__={snapshot,reset,move,select,measure:()=>{raw.length=0;prior=null;paused=false;measureStart=new Date().toISOString();},pause:()=>{paused=true;input.clear();}};
  (el('enter') as HTMLButtonElement).disabled=false;(el('reset') as HTMLButtonElement).disabled=false;
  show('LOADED Â· E0_PASS Â· 121 logical IDs Â· R4 báº¥t biáº¿n');
  let frames=0;
  function frame(now:number){requestAnimationFrame(frame);if(paused)return;if(document.hidden){prior=null;return;}const dt=prior===null?null:now-prior;prior=now;if(dt!==null){raw.push(dt);if(raw.length>120000){paused=true;show('Measurement buffer full; reset measurement explicitly.');return;}if(input.active){const [f,s]=input.axes();move(displacement(f,s,yaw,dt/1000));}}
    gl.render(scene,camera);if(firstFrameMs===null)firstFrameMs=performance.now()-loadStart;
    if(++frames%15===0){select();const summary=summarize(raw);el('stats').textContent=`${summary.fps?.toFixed(1)??'â€”'} FPS Â· p95 ${summary.p95?.toFixed(1)??'â€”'} ms Â· ${summary.sampleCount} frames`;}}
  requestAnimationFrame(frame);
}
