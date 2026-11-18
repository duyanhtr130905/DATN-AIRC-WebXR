import {Box3,Mesh,Object3D,Vector3} from 'three';
import {check,logicalId,validateManifest,type Manifest} from './core.ts';
import reference from '../../../../experiments/p507-webxr/export-bounds-v1.json';
export {reference};
export type ExportReference = typeof reference;
/** Validate actual GLTFLoader world geometry against an offline, hash-bound independent export reference. */
export function validateScene(root:Object3D,m:Manifest,ref:ExportReference=reference) {
  validateManifest(m); root.updateMatrixWorld(true);
  check(ref.schema_version===1 && ref.model_sha256===m.model_sha256 && ref.model_bytes===m.model_bytes,'E0_REFERENCE_ASSET: frozen SHA/bytes mismatch');
  const expectedIDs=m.instances.filter(i=>i.status!=='UNPLACED').map(i=>i.id);
  check(ref.records.length===121 && new Set(ref.records.map(r=>r.id)).size===121 && ref.records.every(r=>expectedIDs.includes(r.id)&&r.bounds.length===6&&r.bounds.every(Number.isFinite)),'E0_REFERENCE_RECORDS: missing/duplicate/invalid ID or bounds');
  const counts=new Map<string,{primitives:number;vertices:number}>();let vertexSamples=0;
  const proxies=new Map(m.collision_proxies.map(p=>[p.id,p]));
  check(root.position.length()<1e-9 && root.rotation.toArray().slice(0,3).every(v=>v===0) && root.scale.toArray().every(v=>v===1),'Model must load with identity transform');
  const placed=m.instances.filter(i=>i.status!=='UNPLACED'),known=new Set(placed.map(i=>i.id));
  const bounds=new Map<string,Box3>(),windows:Box3[]=[],floors:Box3[]=[];
  let meshes=0,triangles=0;const geometries=new Set(),materials=new Set(),textures=new Set();
  root.traverse(node=>{
    const own=node.userData.survey_instance_id;
    if(typeof own==='string')check(known.has(own),'Unknown/unplaced GLB ID '+own);
    if(!(node instanceof Mesh))return;
    meshes++;geometries.add(node.geometry);triangles+=(node.geometry.index?.count??node.geometry.attributes.position.count)/3;
    for(const mat of Array.isArray(node.material)?node.material:[node.material]){materials.add(mat);for(const value of Object.values(mat))if(value && typeof value==='object' && 'isTexture' in value)textures.add(value);}
    const b=new Box3().setFromObject(node,true),id=logicalId(node,known);
    if(id){
      const count=counts.get(id)??{primitives:0,vertices:0};count.primitives++;count.vertices+=node.geometry.attributes.position.count;counts.set(id,count);
      const proxy=proxies.get(id)!;const poly=proxy.polygon;
      const area=poly.reduce((sum,a,i)=>{const b=poly[(i+1)%poly.length];return sum+a[0]*b[1]-b[0]*a[1];},0);
      check(Math.abs(area)>1e-12,'E0_PROXY_DEGENERATE: '+id);
      const winding=Math.sign(area),v=new Vector3(),pos=node.geometry.attributes.position;
      for(let j=0;j<pos.count;j++){
        v.fromBufferAttribute(pos,j).applyMatrix4(node.matrixWorld);vertexSamples++;
        check(v.toArray().every(Number.isFinite),'E0_VERTEX_NONFINITE: '+id);
        const distances=poly.map((a,i)=>{const b=poly[(i+1)%poly.length],length=Math.hypot(b[0]-a[0],b[1]-a[1]);check(length>1e-12,'E0_PROXY_EDGE: '+id);return winding*((b[0]-a[0])*(-v.z-a[1])-(b[1]-a[1])*(v.x-a[0]))/length;});
        check(Math.min(...distances,v.y-proxy.bottom_z,proxy.top_z-v.y)>=-.001,'E0_PROXY_CONTAINMENT: '+id+' node '+node.name+' vertex '+j);
      }
      const total=bounds.get(id)??new Box3();total.union(b);bounds.set(id,total);}
    if(node.name.startsWith('P507_ARCH_FLOOR'))floors.push(b);
    if(node.name.startsWith('P507_ARCH_WINDOW_GLASS'))windows.push(b);
  });
  check(bounds.size===121,'Missing actual logical geometry');
  const differences:unknown[]=[],authoringDrift:unknown[]=[];let maxReferenceDeltaM=0;
  for(const item of placed){
    const b=bounds.get(item.id),a=item.authored_bounds_survey;
    check(b&&a&&a.length===6,'Missing authored bounds '+item.id);
    const record=ref.records.find(r=>r.id===item.id)!;
    const count=counts.get(item.id)!;
    check(count.primitives===record.primitive_count && count.vertices===record.vertex_samples,'E0_COMPONENT_RECORDS: '+item.id);
    const authored=[a[0],a[2],-a[4],a[3],a[5],-a[1]],expected=record.bounds,actual=[...b.min.toArray(),...b.max.toArray()];
    const drift=Math.max(...actual.map((v,i)=>Math.abs(v-authored[i])));
    if(drift>1e-6)authoringDrift.push({id:item.id,authoredEvaluated:authored,actualExport:actual,maxDeltaM:drift});
    maxReferenceDeltaM=Math.max(maxReferenceDeltaM,...actual.map((v,i)=>Math.abs(v-expected[i])));
    if(!actual.every((v,i)=>Math.abs(v-expected[i])<.003))differences.push({id:item.id,actual,expected,maxDelta:Math.max(...actual.map((v,i)=>Math.abs(v-expected[i])))});
  }
  check(floors.length>0 && floors.every(b=>Math.abs(b.max.y)<.003 && Math.abs(b.min.x)<.003 && Math.abs(b.max.x-6.9)<.003 && Math.abs(b.min.z+9.315)<.003 && Math.abs(b.max.z)<.003),'Actual floor/room dimensions differ');
  check(windows.length===4 && windows.every(b=>Math.abs(b.getCenter(new Vector3()).x-6.9)<.1),'Four east windows mismatch');
  const doors=[...bounds.entries()].filter(([id])=>id.startsWith('P507-DOOR-LEAF-'));
  check(doors.length===2&&doors.every(([,b])=>b.max.x<.003&&b.min.x<-.5),'Outward west door geometry mismatch');
  check(differences.length===0,'E0_EXPORT_BOUNDS: independent actual-export reference differs from GLB vertices: '+JSON.stringify(differences));
  return {result:'E0_SCENE_PASS',referenceVersion:1,maxReferenceDeltaM,authoringDrift,vertexSamples,proxyToleranceM:.001,exportBoundsToleranceM:.003,placedIDs:bounds.size,meshCount:meshes,geometryCount:geometries.size,triangleCount:triangles,materialCount:materials.size,textureCount:textures.size,identityTransform:true,floorY:0,windows:4,worldBoundsMatched:121};
}
