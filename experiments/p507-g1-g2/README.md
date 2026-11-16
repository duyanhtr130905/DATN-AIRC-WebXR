# P507 G1/G2 — provisional layout and hero review

Continue Draft PR #14, stacked on G0 PR #13. No merge, retarget, production integration, deploy or G3. Read [G0](../../docs/3d-production/P507-G0-PRODUCTION-SPEC.md), [revision report](../../docs/3d-production/P507-G1-G2-LAYOUT-LOOKDEV-REVISION.md) and [acceptance](../../docs/3d-production/P507-G1-G2-ACCEPTANCE.md).

## Inventory/schema

Schema v2 keeps17 stable desks A6/B6/C5 and36 explicit chair instances. Each chair has ID, cluster, status, centre, orientation, full seat/back envelope, role and provenance. 0° faces+Y;90° faces−X. B09/B10 and C11/C12 are right-end chairs. No count-distribution heuristic remains. v1 imports without invented poses: old chair IDs become UNPLACED/UNKNOWN. Additional objects/chairs remain supported; no system capacity ceiling.

All positions PROPOSED_LAYOUT, AIRC rights PENDING. Unknown utility shelves/cabinets/fridge/shoe rack and door swing remain UNKNOWN. All36 chairs are provisionally placed; .20/.40m static chair-envelope gaps are **not usable walkway clearance**. No photographs, people, private screens, artwork or authentic logos are included.

## Run from root

```sh
python experiments/p507-g1-g2/geometry.py --report .local/p507-g1-g2/geometry-report.json
python -m unittest discover -s experiments/p507-g1-g2 -p test_geometry.py -v
blender --background --python-exit-code 1 --python experiments/p507-g1-g2/generate_blender.py -- --output-dir .local/p507-g1-g2
npm install --no-save --package-lock=false --ignore-scripts --prefix .local/p507-gltf-validator gltf-validator@2.0.0-dev.3.10
node experiments/p507-g1-g2/validate_glb.mjs
npm ci --ignore-scripts --prefix apps/web
npm run build --prefix apps/web
```

Copy generated GLB to ignored `apps/web/public/p507-local-preview/`. Run `node experiments/p507-g1-g2/browser_preview.mjs` (set CHROME_BIN on Windows), or Vite dev and open `/p507-g1-g2-preview.html`. This dev-only page is not linked from production App and never starts microphone/camera/XR or writes backend data.

## Evidence

SAT covers desks, chair seat/back, hero/positioned generic furniture, entry and inner walls. Edge contact allowed; support relations require correct height; generator honors bottom_z. Regression fixtures preserve old cabinet–chair overlap and original v1 data. Blender independently checks evaluated mesh bounds against proxies and west-wall door void before export. Linked chair geometry and per-asset joins preserve independent IDs.

Ignored `.local/p507-g1-g2/` contains editable .blend, GLB, geometry-report.json, report.json (input hashes/actual mesh bounds), Khronos gltf-validation-report.json, browser-report.json (unfiltered rAF timings/sample count/p50/p95, materials/geometry/texture memory estimate, bytes/hash, GPU/browser/viewports/cameras/source and checkout SHA) plus HERO/wide/overview/B-C/mobile screenshots. Architectural cutaways hide walls/ceiling only. `P507_SHOTS=hero,overview` restricts capture; `P507_BASELINE=1` labels old invalid layout instead of applying new-layout assertions; `P507_EVIDENCE_DIR` changes output location.

CI actually runs Blender/build/Khronos/Chrome and retains neutral artifacts7 days. Verify exact final PR HEAD, never cite old runs as final evidence. Software WebGL/mobile viewport is not physical GPU/phone/WebXR performance. Screenshots are reviewed manually; mesh count and checks do not establish art quality. Label differing camera/lighting in before/after comparisons.

**G1_SURVEY_ACCURACY PROVISIONAL; G2_VISUAL PENDING OWNER APPROVAL; PHOTO_MATCH BLOCKED; REAL_DEVICE_WEBXR NOT RUN; REAL_AIRC_DATA NOT VERIFIED; G3 NOT STARTED.** Still a simplified procedural architectural study, not photorealistic complete. Stop after handoff.
