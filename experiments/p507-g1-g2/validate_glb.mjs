/** Validate the generated GLB using the official Khronos glTF Validator.
 * Install pinned gltf-validator in ignored .local/p507-gltf-validator.
 * No production/lockfile dependency, network used only in disposable CI.
 */
import fs from "node:fs";
import {createHash} from "node:crypto";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,"../..");
const require=createRequire(import.meta.url);
const validator=require(path.join(root,".local","p507-gltf-validator","node_modules","gltf-validator"));
const artifactDir=process.env.P507_EVIDENCE_DIR || path.join(root,".local","p507-g1-g2");
const asset=path.join(artifactDir,"P507_G1_G2_PROVISIONAL.glb");
const out=path.join(artifactDir,"gltf-validation-report.json");
const bytes=fs.readFileSync(asset);
const jsonLength=bytes.readUInt32LE(12);
const document=JSON.parse(bytes.subarray(20,20+jsonLength).toString("utf8"));
for(const image of document.images || []) {
  if(!image.name?.startsWith("P507_SELF_GENERATED_") || !Number.isInteger(image.bufferView) || image.uri) throw new Error("Unapproved image embedded or referenced in GLB: "+image.name);
}
if((document.buffers || []).some(buffer=>buffer.uri)) throw new Error("External buffer URI is not permitted in neutral review artifact");
const manifest=JSON.parse(fs.readFileSync(path.join(artifactDir,"asset-manifest.json"),"utf8"));
const ensure=(condition,message)=>{if(!condition)throw new Error(message);};
ensure(manifest.model_sha256===createHash("sha256").update(bytes).digest("hex"),"Manifest/GLB hash mismatch");
ensure(manifest.unit==="metre" && manifest.virtual_dimensions.width_x===6.9 && manifest.virtual_dimensions.length_y===9.315 && manifest.survey_baseline.width_x===6 && manifest.survey_baseline.length_y===8.1,"Handoff virtual/survey dimensions invalid");
const nodeIds=new Set(document.nodes.map(n=>n.extras?.survey_instance_id).filter(Boolean));
for(const instance of manifest.instances)ensure(nodeIds.has(instance.id)===(instance.status!=="UNPLACED"),"Manifest/rendered instance mismatch: "+instance.id);
ensure(manifest.instances.filter(i=>i.id.startsWith("P507-CHAIR-")&&i.status!=="UNPLACED").length===34,"Manifest needs34 real rendered chairs");
ensure(manifest.collision_proxies.length===manifest.instances.filter(i=>i.status!=="UNPLACED").length,"Handoff collision proxy coverage differs from placed IDs");
ensure(document.materials.some(m=>m.name==="P507_PBR_FILE_CABINET_CLEAR_GLASS"&&m.alphaMode==="BLEND"&&m.pbrMetallicRoughness.baseColorFactor[3]<.4),"Clear cabinet glass did not export as translucent material");
const report=await validator.validateBytes(new Uint8Array(bytes),{
  uri:"P507_G1_G2_PROVISIONAL.glb", format:"glb", maxIssues:1000, writeTimestamp:false
});
fs.writeFileSync(out,JSON.stringify(report,null,2)+"\n");
console.log("glTF validator: "+JSON.stringify({errors:report.issues.numErrors,warnings:report.issues.numWarnings,infos:report.issues.numInfos, asset:report.info}));
if(report.issues.numErrors > 0) {
  console.error("Validator reported errors. See:",out);
  process.exitCode=1;
}
