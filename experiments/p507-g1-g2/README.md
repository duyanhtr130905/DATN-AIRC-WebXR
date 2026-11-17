# P507 G1/G2 — provisional layout and hero review

## Current R4 — owner-approved virtual experience freeze

Schema3 separates survey baseline6×8.1×3.5 from owner virtual6.9×9.315×3.5m. No object scale1.15.36 historical chair IDs/34 placed A12B12C10/C09C10 unassigned. Outward2leaf door,3clear-glass cabinet bays,1.50m shelf alongY/depth.47m,vanilla#F5E6C8. Read [R4](../../docs/3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md) and [asset handoff](../../docs/3d-production/P507-WEBXR-ASSET-HANDOFF.md).75tests;121evaluated placed proxies; occupied-use .15m pullback/circulation PARTIAL.16desktop+mobile hero screenshots include clusterA/B/C and exterior door open/closed; asset-manifest.json carries IDs/transforms/proxies/cameras. READY FOR WEBXR EXPERIMENT is asset freeze only, no runtime or owner visual approval.

## Historical R3 runbook (commands remain valid; data/status above supersedes counts)

Continue Draft PR #14, stacked on G0 PR #13. No merge, retarget, production integration, deploy or G3. Read [G0](../../docs/3d-production/P507-G0-PRODUCTION-SPEC.md), [revision report](../../docs/3d-production/P507-G1-G2-LAYOUT-LOOKDEV-REVISION.md) and [acceptance](../../docs/3d-production/P507-G1-G2-ACCEPTANCE.md).

## Inventory/schema

Schema v2 keeps17 stable desks A6/B6/C5 and36 explicit chair instances. Each chair has ID, cluster, status, centre, orientation, full seat/back envelope, role and provenance. 0° faces+Y;90° faces−X. B09/B10 and C11/C12 are right-end chairs. No count-distribution heuristic remains. v1 imports without invented poses: old chair IDs become UNPLACED/UNKNOWN. Additional objects/chairs remain supported; no system capacity ceiling.

All positions PROPOSED_LAYOUT, AIRC rights PENDING. Revision3 places utilities from16 inspected references.24 chairs are placed,12 remain UNPLACED with reasons; .51/.71m static chair-envelope gaps are **not usable walkway clearance**, right wall gap .26m/utility choke .53m remain limitations. Door swing/TV angle are proposed. No photographs, people, private screens, artwork or authentic logos are included.

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

Oriented SAT prisms cover desks, chair seat/back, hero, utilities, wall frames, ceiling, entry and inner walls.56 tests cover provenance/support and historical overlap regressions;111 placed meshes receive evaluated vertex proof and10 underside ray checks. Edge contact allowed; support relations require correct height; generator honors bottom_z. Regression fixtures preserve old cabinet–chair overlap and original v1 data. Blender independently checks evaluated mesh bounds against proxies and west-wall door void before export. Linked chair geometry and per-asset joins preserve independent IDs.

Ignored `.local/p507-g1-g2/` contains editable .blend, GLB, geometry-report.json, report.json (input hashes/actual mesh bounds), Khronos gltf-validation-report.json, browser-report.json (unfiltered rAF timings/sample count/p50/p95, materials/geometry/texture memory estimate, bytes/hash, GPU/browser/viewports/cameras/source and checkout SHA) plus10 desktop views/hero mobile/inventory/contact sheet. Architectural cutaways hide walls/ceiling only. `P507_SHOTS=hero,overview` restricts capture; `P507_BASELINE=1` labels old invalid layout instead of applying new-layout assertions; `P507_EVIDENCE_DIR` changes output location.

CI actually runs Blender/build/Khronos/Chrome and retains neutral artifacts7 days. Verify exact final PR HEAD, never cite old runs as final evidence. Software WebGL/mobile viewport is not physical GPU/phone/WebXR performance. Screenshots are reviewed manually; mesh count and checks do not establish art quality. Label differing camera/lighting in before/after comparisons.

**G1_SURVEY_ACCURACY PROVISIONAL; G2_VISUAL PENDING OWNER APPROVAL; PHOTO_MATCH PARTIAL (qualitative, no calibrated camera match); REAL_DEVICE_WEBXR NOT RUN; REAL_AIRC_DATA NOT VERIFIED; G3 NOT STARTED.** Still a simplified procedural architectural study, not photorealistic complete. Stop after handoff.

Current R3 sources/layout/limits: [comprehensive review](../../docs/3d-production/P507-G1-G2-COMPREHENSIVE-REVIEW.md), [survey comparison](../../docs/3d-production/P507-G1-G2-SURVEY-COMPARISON.md). Private reference analysis stays outside the neutral CI output folder.
