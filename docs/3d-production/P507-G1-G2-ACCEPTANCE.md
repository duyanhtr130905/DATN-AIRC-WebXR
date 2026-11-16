# P507 G1/G2 — Implementation Evidence & Acceptance Status

**As-of 16/11/2026 — PARTIAL (G1 technical build, G2 visual NOT ACCEPTED).**

Source: [G0 art direction](P507-G0-PRODUCTION-SPEC.md) in stacked [PR #13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13), code in [Draft PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14). Neither PR has been merged or deployed at time of writing. Verify GitHub live before using these snapshots.

## 1. Exact evidence

- Successful source+Blender+Chrome+Khronos CI on commit \`e04427e739668e2414aae5acb4eb00c3da1c3f6b\`: [Run 43804659514](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43804659514).
- [Artifact 14198205321](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43804659514/artifacts/14198205321): editable \`.blend\`, \`.glb\`, actual Chrome screenshots (hero/overview/logo/mobile), \`report.json\`, \`gltf-validation-report.json\`, \`browser-report.json\`. **Temporary CI artifact; access controlled and retention only 7 days**. SHA and source code are durable; screenshots should be copied to a permission-approved evidence store if permanent retention needed.
- The artifact contains **only synthetic-neutral generated geometry and procedural materials**, no real photos, people, AIRC brand textures or private screen/bảng nội dung.
- Latest code changes since this CI run were documentation only as-of this record; verify current PR HEAD and latest checks independently.

## 2. G1: Geometry

| Check | Outcome | Limitations |
| --- | --- | --- |
| Inventory stays open, stable survey IDs | PASS (test appends 18th object) | Survey data is not AIRC-verified |
| 16 standard + 1 small table across A6/B6/C5 | PASS, 17/17 IDs unique | Small B06 size still proposed |
| Desk geometry in 6×8.1m floor, no desk–desk overlap | PASS | Proposed coords; not certified physical layout |
| Desk edge gaps between clusters | A–B 1.25m, B–C 1.30m | **Not actual free aisle widths**; chairs, cabinets, door swing excluded |
| 36 chairs | GENERATED placeholders | Seat locations have NOT been measured |
| Walls/openings/ceiling | Blender build/export PASS | Opening offsets, furnishings, ceiling real positions approximate |
| Blender \`.blend\`, GLB | PASS on disposable Ubuntu Blender CI | Need local editor validation for art changes |
| glTF 2.0 binary format, custom IDs | PASS | \`extras.survey_instance_id\` carried into GLB |
| Khronos glTF Validator | **0 ERRORS, 0 WARNINGS** | 431 INFO UNUSED_OBJECT TEXCOORD_0; optimization issue |
| Collision with cabinets/door/people and egress | NOT VERIFIED | Survey + collision analysis needed; not part of current automated PASS |

## 3. G2: Hero-zone browser lookdev

**Real first-pass browser screenshots exist** for entrance–TV–low cabinet–water dispenser, top-down room, logo wall and 390px viewport. Browser HTML dev-only; does not replace M1-C runtime.

CI source output: 432 meshes, ~7200 triangles, ~853 KiB GLB. Browser recorded draw calls ~626 for desktop HERO and ~557 mobile HERO (software WebGL, values are screenshot-sample dependent). **Only ~7–8 frames were sampled on that run**, so the extreme p95 frame intervals from software GPU are not statistically adequate for KPI; they do identify possible rendering overhead. No physical GPU/Galaxy/VR evidence.

**Independent visual review by ChatGPT:** **NOT ACCEPTED for G2 art target**. The room is visibly a procedural, simplified blockout, with neutral abstract frames and basic desk/chair geometry; materials, edges, scene dressing, coherent lighting, comparison to authorized P507 photos and GPU performance remain insufficient for the target "game-environment realism". No source photos were used in CI, so camera matching cannot be claimed.

**Release gate:** G2 requires actual review and positive visual sign-off by the project owner after the hero visual is refined. Do not move to G3 or treat glTF validator PASS as art PASS.

## 4. Fixing the *asset* is not re-opening G0

G0 design methodology is frozen. Further allowed work within **same G2 workstream/PR** may improve chair/TV/cabinet/water geometry, accurate sizes, PBR textures from licensed sources or authorized local photos, lighting parity and camera matching. Preserve IDs and do not automatically change room dimensions or invent survey evidence. Commit only rights-cleared assets. Continue using browser evidence and inspect actual images rather than declaring success based on code/tests.

Missing authorized photo references, AIRC data rights, precise door/window positions, small desk measurements and physical XR devices remain BLOCKED/UNKNOWN. KPI ≥3 actual rooms and user tracking MT3 remain unchanged and not verified.

## 5. Explicit stop conditions

- Keep [PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14) **Draft / NOT MERGE READY** until G2 visual sign-off, reference matching and performance review.
- Do not merge PR #13/#14 automatically, deploy, import P507 as \`real_verified\`, alter REST/WS or start G3.
- Survey inventory and geometry revisions can continue without creating any "G0-fix" task.
