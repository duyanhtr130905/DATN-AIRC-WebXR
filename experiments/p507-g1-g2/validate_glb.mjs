/** Validate the generated GLB using the official Khronos glTF Validator.
 * Install pinned gltf-validator in ignored .local/p507-gltf-validator.
 * No production/lockfile dependency, network used only in disposable CI.
 */
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,"../..");
const require=createRequire(import.meta.url);
const validator=require(path.join(root,".local","p507-gltf-validator","node_modules","gltf-validator"));
const asset=path.join(root,".local","p507-g1-g2","P507_G1_G2_PROVISIONAL.glb");
const out=path.join(root,".local","p507-g1-g2","gltf-validation-report.json");
const bytes=fs.readFileSync(asset);
const report=await validator.validateBytes(new Uint8Array(bytes),{
  uri:"P507_G1_G2_PROVISIONAL.glb", format:"glb", maxIssues:1000, writeTimestamp:false
});
fs.writeFileSync(out,JSON.stringify(report,null,2)+"\n");
console.log("glTF validator: "+JSON.stringify({errors:report.issues.numErrors,warnings:report.issues.numWarnings,infos:report.issues.numInfos, asset:report.info}));
if(report.issues.numErrors > 0) {
  console.error("Validator reported errors. See:",out);
  process.exitCode=1;
}
