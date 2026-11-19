import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import lock from "../../../../experiments/p507-webxr/asset-lock.json";
import { check, validateManifest, type Manifest } from "./core.ts";
import { validateScene } from "./scene-contract.ts";

export async function loadFrozenP507(signal?: AbortSignal) {
    const directory = "/p507-e1-assets/";
    const get = async (name: keyof typeof lock.files) => {
        const expected = lock.files[name];
        const response = await fetch(directory + name, { signal, credentials: "omit" });
        check(response.ok && response.body, `Thiếu asset ${name} (HTTP ${response.status}).`);
        const reader = response.body.getReader();
        const bytes = new Uint8Array(expected.bytes);
        let offset = 0;
        try {
            for (;;) {
                const { done, value } = await reader.read();
                if (done) break;
                check(offset + value.length <= bytes.length, "Frozen asset exceeds size budget");
                bytes.set(value, offset);
                offset += value.length;
            }
        } finally {
            await reader.cancel().catch(() => {});
        }
        const digest = await crypto.subtle.digest("SHA-256", bytes);
        const hash = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
        check(offset === bytes.length && hash === expected.sha256, `SHA-256/bytes mismatch: ${name}`);
        return bytes.buffer;
    };
    const manifestBytes = await get("asset-manifest.json");
    const manifest = validateManifest(JSON.parse(new TextDecoder().decode(manifestBytes)) as Manifest);
    const bytes = await get("P507_G1_G2_PROVISIONAL.glb");
    const hash = lock.files["P507_G1_G2_PROVISIONAL.glb"].sha256;
    check(manifest.model_sha256 === hash && manifest.model_bytes === bytes.byteLength, "GLB manifest identity mismatch");
    const gltf = await new GLTFLoader().parseAsync(bytes, directory);
    const geometry = validateScene(gltf.scene, manifest);
    return { gltf, manifest, geometry, hash };
}
