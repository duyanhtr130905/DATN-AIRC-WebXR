# P507 G1/G2 — Implementation Evidence & Acceptance Status

## Current R4 — virtual adaptation và bố cục34ghế

Xem [R4 acceptance/limits](P507-G1-G2-R4-VIRTUAL-FREEZE.md) và [WebXR asset handoff](P507-WEBXR-ASSET-HANDOFF.md). Survey baseline giữ6×8.1×3.5m; virtual6.9×9.315×3.5m do owner chốt. G1_LAYOUT_34_CHAIRS theo actualGLB/browser, historical36IDs giữ nguyên. G1_CIRCULATION PARTIAL; G2_VISUAL PENDING OWNER APPROVAL; PHOTO_MATCH PARTIAL về chi tiết/không room1:1; REAL_DEVICE_WEBXR NOT RUN. FinalHEAD/CI/artifacts theo PRhandoff. R3 bên dưới là lịch sử.


## Historical revision 3 — 17/11/2026, chờ review

Xem [báo cáo tổng hợp R3](P507-G1-G2-COMPREHENSIVE-REVIEW.md). G1_GEOMETRY PASS có giới hạn111 instance đặt/12ghế UNPLACED;36 ID được giữ. G1_SURVEY_ACCURACY PROVISIONAL; G1_CIRCULATION PARTIAL; PHOTO_MATCH PARTIAL sau khi mở16 nguồn thật, camera chưa calibrated. G2_PIPELINE theo exact-HEAD CI/handoff; G2_VISUAL PENDING OWNER APPROVAL; REAL_DEVICE_WEBXR NOT RUN; REAL_AIRC_DATA NOT VERIFIED; G3 NOT STARTED. Các mục36ghế đặt/PHOTO_MATCH BLOCKED bên dưới là lịch sử, không mô tả R3.

## Historical revision 2 — 16/11/2026 layout correction (PR #14)

See [layout/lookdev revision and exact coordinates](P507-G1-G2-LAYOUT-LOOKDEV-REVISION.md), [before/after occupancy](../evidence/p507-layout-before-after.svg) and final PR handoff for exact HEAD/CI artifacts. This section supersedes the desk-only verdict in the historical snapshot below.

- **G1_GEOMETRY: PASS** for 17 desks + 36 explicit placed chair instances + cabinet/water/entry/bounds. Zero invalid proxy collisions; actual Blender evaluated bounds must fit those proxies. Previous cabinet–chair overlap regression fails as expected. Unknown unplaced utility items and door swing remain UNKNOWN.
- **G1_SURVEY_ACCURACY: PROVISIONAL**. Desk-edge gaps 1.25/1.30m differ from static chair-envelope gaps .20/.40m; neither certifies usable circulation.
- **G2_PIPELINE:** actual local Blender/GLB/Khronos/Chrome checks run; final exact-HEAD CI is linked in the handoff after completion. Reports record both PR head and checkout SHA.
- **G2_VISUAL: PENDING OWNER APPROVAL.** More developed hero silhouettes/materials and reusable curved chairs; still simplified procedural art. No automatic artistic acceptance.
- **PHOTO_MATCH: BLOCKED; REAL_DEVICE_WEBXR: NOT RUN; REAL_AIRC_DATA: NOT VERIFIED; G3: NOT STARTED.** No authorized reference photos were used or embedded.

## Historical first-look evidence (before layout correction)

The following dated snapshot describes the old `2c23fd1` lineage; old PASS/checks and images are not evidence for the revised HEAD.


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
