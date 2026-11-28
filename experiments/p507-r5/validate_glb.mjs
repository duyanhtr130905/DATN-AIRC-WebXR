import { readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { isAbsolute, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const local = fileURLToPath(new URL("../../.local/p507-r5/", import.meta.url));
const directory = process.argv[2] && resolve(process.argv[2]);
const subdirectory = directory && relative(local, directory);
if (!subdirectory || isAbsolute(subdirectory) || subdirectory.split(sep).includes("..")) {
    throw new Error("Use a generated directory below ignored .local/p507-r5");
}
const dependency = fileURLToPath(new URL("../../.local/p507-gltf-validator/node_modules/gltf-validator", import.meta.url));
const validator = createRequire(import.meta.url)(dependency);
const model = "P507_R5_PROPOSAL.glb";
const bytes = await readFile(resolve(directory, model));
const report = await validator.validateBytes(new Uint8Array(bytes), {
    uri: model,
    format: "glb",
    writeTimestamp: false,
    maxIssues: 1000,
});
await writeFile(resolve(directory, "gltf-validation-report.json"), JSON.stringify(report, null, 2) + "\n", { flag: "wx" });
console.log(JSON.stringify({
    errors: report.issues.numErrors,
    warnings: report.issues.numWarnings,
    infos: report.issues.numInfos,
    asset: report.info,
}, null, 2));
if (report.issues.numErrors > 0) process.exitCode = 1;
