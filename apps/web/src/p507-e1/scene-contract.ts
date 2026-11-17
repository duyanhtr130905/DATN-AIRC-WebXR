import {Box3,Mesh,Object3D,Vector3} from 'three';
import {check,logicalId,validateManifest,type Manifest} from './core.ts';
/** Validate actual GLTFLoader world geometry against authored frozen bounds. */
export function validateScene(root:Object3D,m:Manifest) {
  validateManifest(m); root.updateMatrixWorld(true);
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
    if(id){const total=bounds.get(id)??new Box3();total.union(b);bounds.set(id,total);}
    if(node.name.startsWith('P507_ARCH_FLOOR'))floors.push(b);
    if(node.name.startsWith('P507_ARCH_WINDOW_GLASS'))windows.push(b);
  });
  check(bounds.size===121,'Missing actual logical geometry');
  const differences:unknown[]=[];
  for(const item of placed){
    const b=bounds.get(item.id),a=item.authored_bounds_survey;
    check(b&&a&&a.length===6,'Missing authored bounds '+item.id);
    const expected=[a[0],a[2],-a[4],a[3],a[5],-a[1]],actual=[...b.min.toArray(),...b.max.toArray()];
    if(!actual.every((v,i)=>Math.abs(v-expected[i])<.003))differences.push({id:item.id,actual,expected,maxDelta:Math.max(...actual.map((v,i)=>Math.abs(v-expected[i])))});
  }
  check(floors.length>0 && floors.every(b=>Math.abs(b.max.y)<.003 && Math.abs(b.min.x)<.003 && Math.abs(b.max.x-6.9)<.003 && Math.abs(b.min.z+9.315)<.003 && Math.abs(b.max.z)<.003),'Actual floor/room dimensions differ');
  check(windows.length===4 && windows.every(b=>Math.abs(b.getCenter(new Vector3()).x-6.9)<.1),'Four east windows mismatch');
  const doors=[...bounds.entries()].filter(([id])=>id.startsWith('P507-DOOR-LEAF-'));
  check(doors.length===2&&doors.every(([,b])=>b.max.x<.003&&b.min.x<-.5),'Outward west door geometry mismatch');
  check(differences.length===0,'E0_FAIL: manifest authored bounds differ from GLB vertices: '+JSON.stringify(differences));
  return {result:'E0_SCENE_PASS',placedIDs:bounds.size,meshCount:meshes,geometryCount:geometries.size,triangleCount:triangles,materialCount:materials.size,textureCount:textures.size,identityTransform:true,floorY:0,windows:4,worldBoundsMatched:121};
}
