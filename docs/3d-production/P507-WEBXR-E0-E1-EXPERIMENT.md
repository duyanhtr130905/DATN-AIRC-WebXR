# P507 E0/E1 — technical implementation handoff (17/11/2026)

## Decision and scope

**E0_FAIL. E1 PARTIAL implementation / BLOCKED_BY_E0 runtime. NOT READY FOR ACCEPTANCE.** Owner-approved E0/E1 task dated 17/11/2026 permits a standalone desktop Web 3D experiment on frozen R4, tests and Draft PR. ChatGPT/owner must independently accept it. No E2/E3/G3, XR sessions, merge, deploy, production scene, backend/API/DB, visitor tracking or KPI changes.

Base: PR #14 HEAD `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31`, branch `feat/p507-g1-g2-blockout-hero`; new branch `feat/p507-webxr-e0-e1-experiment`. PR #14 remains stacked on PR #13. R4 asset checkpoint `3a11ec757168a59625a087ac83f28c433751a1f5`; the diff from checkpoint to base changes only PROJECT_STATUS. The experiment final HEAD and exact CI results are published in the Draft PR; this document does not mislabel the base SHA as the experiment SHA. Each runtime JSON records checkout HEAD and dirty state.

## E0 TV Bounds Root Cause Investigation — diagnostic follow-up

Owner-approved follow-up17/11/2026: **ROOT_CAUSE_CONFIRMED** on Blender4.0.2/exporter4.0.44. [Full diagnostic report](P507-E0-TV-BOUNDS-DIAGNOSTIC.md) provides original/evaluated/frozen per-component bounds, exact vertex witnesses, six controlled export cases, Three/Python cross-check and actual oriented-proxy audit. [Verified same-version run44065711842](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44065711842) applies to clean commit `6ae02b0397c88970c46618bbe5b4ba3d501edfcf`; final follow-up HEAD/checks are in Draft PR15.

Frozen authored bounds measured evaluated bevel geometry; actual export omitted `export_apply` (defaultfalse), exporting the TV's original uncombined meshes. Raw xmin comes from REAR_CASING accessor555/vertex6; evaluated xmin comes from BEZEL vertex30, explaining8.3055mm including a change of extremum owner. Weighted normals, matrix/axis/grouping/rounding and Box3 are not the cause of this bounds discrepancy. Independent containment checks402482POSITION samples/121IDs: zero violations at1mm.

**E0_FAIL remains; E1 remains BLOCKED.** No asset/lock/manifest/validator/tolerance/navigation changes or OptionA/B implementation. The new report recommends conditional review of OptionA (separate pre-export authoring diagnostic from actual-export operational gates), with OptionB for a separately approved corrected export/handoff revision. Initial investigation text below is preserved as history and superseded only on root cause, not on acceptance status.

## Asset provenance

Original [run 44038653564](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44038653564), [artifact 14309207795](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44038653564/artifacts/14309207795), name `p507-g1-g2-neutral-blender-chrome`, available at download. Created 17/11/2026 07:46:38 UTC, expires 24/11/2026 07:46:36 UTC. Downloaded with existing authenticated gh; no token in source/evidence. **Not a regenerated asset.**

- Asset source/head: `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31`.
- CI checkout (PR merge SHA): `9764b90f86317446bb585bf668171f81e1c57edb`, distinct from source/head.
- GLB: **10,751,036 bytes**, SHA-256 **`8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`**.
- [Asset lock](../../experiments/p507-webxr/asset-lock.json) pins size/hash of GLB, manifest, geometry, Blender, Khronos and browser reports. File hashes establish a single bundle, including browser-amended manifest camera metadata.
- Frozen generator/geometry/inventory Git blob hashes match original CI input hashes. Windows CRLF worktree is compared to Git LF content explicitly; no source rewrite occurs.
- All binaries, screenshots and raw reports remain ignored. [Runbook](../../experiments/p507-webxr/README.md) covers preparation, expiry and reproduction. Vite DEV middleware avoids copying E1 assets into production public/dist.

## E0 matrix

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Original artifact, six hashes/bytes, source/checkout/run | PASS | prepare_asset.py + validate_asset.py; source and merge checkout kept distinct |
| Khronos/source geometry reports, frozen input content | PASS | original reports inspected; no re-export or validator rerun claimed |
| Schema/metres/survey vs virtual | PASS | survey 6 x 8.1 x 3.5 USER_REPORTED; virtual 6.9 x 9.315 x 3.5 OWNER_APPROVED_VIRTUAL_ADAPTATION |
| 123 records / 121 placed proxies and actual IDs | PASS | 489 actual meshes; not counted as logical objects |
| 17 desks A6/B6/C5; chairs 36 historical/34 placed | PASS | A12/B12/C10; C09/C10 UNPLACED with no mesh/center |
| Identity, floor Y=0, room dimensions, four east windows, outward west door | PASS | actual GLTFLoader transformed geometry; double scale/rotation negative tests PASS |
| Mesh child to ancestor ID | PASS, E0 diagnostic | 394 child meshes resolved; actual raycast returns stable IDs; not MT1-02 business acceptance |
| Actual vertices inside oriented proxies | PASS, E0 diagnostic | 121 IDs, 0 violations at frozen source's 1mm containment tolerance |
| Authored bounds manifest vs exported vertices | **FAIL** | large TV maximum delta **0.008305509641076014 m**; other 120 logical bounds agree within 3mm experiment threshold |
| Proposed spawn against navigation proxy | PASS, pure logic | radius .30 m / height 1.80 m; not a running E1 control result |
| Aggregate E0 | **E0_FAIL** | do not unlock E1 on bundle/hash PASS alone |

### Unresolved TV metadata discrepancy

Coordinates below are actual Three world axes `[xmin,ymin,zmin,xmax,ymax,zmax]`:

| Source | Bounds |
| --- | --- |
| Manifest authored bounds converted once | `[0.161494792,1.779999971,-9.231895447,1.768088460,2.779999971,-8.389651299]` |
| Actual GLB transformed vertices | `[0.153189282,1.779999971,-9.233558515,1.772579355,2.779999971,-8.387026921]` |

The original artifact's browser-report already records these actual GLB bounds. Therefore this is not an E1 transform or mixed-download defect. All TV vertices remain inside the frozen collision proxy. The **3mm bounds agreement threshold is an E0 experiment validation choice, not a newly approved asset/KPI standard**; it is larger than the source's 1mm proxy containment tolerance, yet the 8.31mm discrepancy still exceeds it. No tolerance was increased to pass this finding.

Initial handoff hypothesis (superseded by the confirmed diagnostic above): source inspection shows authored bounds are measured from evaluated Blender vertices before export; export does not explicitly set export_apply. An evaluated-vs-export bevel difference is a hypothesis, **not a proven root cause**. Resolution needs independent review: clarify whether `authored_bounds_survey` is an exact exported-geometry contract, or approve a separate asset/handoff correction. This task neither repairs the frozen exporter/manifest nor accepts that discrepancy on the owner's behalf. The implementation keeps the stricter gate and stops dependent runtime work.

## E1 matrix and route

| Capability | Implementation / verification |
| --- | --- |
| Separate DEV page, R4 hash load and E0 gate | implemented; actual Chrome confirms E0 error stops before E1 initialization |
| Desktop pointer lock / WASD / mouse / reset / lifecycle | implemented; pure input tests PASS; actual lifecycle tests **NOT RUN, blocked by E0** |
| Oriented, vertical, continuous collision | pure logic PASS; static + occupied chair envelopes, boundary including unsurveyed doorway |
| Selection panel and ancestor ID | implemented; actual raycast/mapping checked in E0-only inspection; E1 UI NOT RUN |
| Frame/load/geometry/GPU instrumentation | implemented; E1 measurement **NOT RUN**, no FPS or first-render result |
| Loading/error/unsupported and negative asset browser scenarios | harness written; actual current-bundle error observed; remaining E1 harness scenarios NOT RUN |
| Production M1-C | source unchanged; frontend build/unit regression PASS; full production browser/backend/PG tests NOT RUN in this task |

The navigation report is **manifest-based logic evidence**, not a completed browser walkthrough. Proposed conservative cylinder/capsule envelope radius .30m, height 1.80m, eye 1.65m, speed 1.2m/s, clamp .05s; engineering trial choices, not anthropometric measurement. Full swept-circle segment checks, stop/no slide; no vertical locomotion.

Verified short route (Three X/Z): `[1.25,-7.415] -> [.95,-7.415] -> [.95,-5.9] -> [.95,-5.2]`. All three swept segments PASS. Continuation towards B blocks; no claim of whole-room access. Wall, actual desk/chair/cabinet, central A-B/B-C gaps, open outward doorway and large jump cases all block. Union of static and pulled chair envelopes is conservative. The frozen 0.93m west slice clearance does not guarantee a continuous capsule route. Central .20/.15m occupied-use gaps and east .23m gap remain non-through-routes. No collision radius reduction, layout edit, hidden interior mesh or proxy disable occurred.

Renderer settings in provisional E1 match preview lighting: procedural RoomEnvironment IBL .30, ambient .04, hemisphere .34, directional 2, two .95 area strips, 1024 shadow map, ACES exposure1, antialias, DPR capped1.5, transmission resolution .5, same TV runtime env-map multipliers. FOV78 is the walking camera; no cutaway, all interiors visible. Because E0 blocks rendering, no E1 lighting parity screenshot or visual acceptance is claimed.

## Executed tests and evidence

Local initial validation used Chrome **157.0.8103.79**, Windows **10.0.26300**, Intel **i5-12450HX**, headless ANGLE SwiftShader software WebGL. E0 audit confirmed 489 meshes/121 logical IDs, 394 ancestor-resolved meshes, zero proxy containment violations and two rejected double transforms. Browser output `E0_FAIL`, `BLOCKED_BY_E0`; raw E1 sample array is empty. Local pre-commit reports explicitly record base checkout plus dirty worktree; exact final HEAD evidence is supplied by CI, never relabeled retrospectively.

| Command / check | Result |
| --- | --- |
| Frozen Python regression | 76 PASS |
| E0 negative Python tests | 5 PASS |
| Frontend build/typecheck | PASS; existing chunk-size warning retained |
| Frontend unit suite | 45 PASS (25 existing + 20 E1) |
| Actual-manifest navigation cases | PASS, limited route only |
| E0-only actual Chrome audit | FAIL on TV bounds; other listed diagnostics PASS |
| E1 browser entry | FAIL at E0 gate, dependent scenarios NOT RUN |
| Repository verifier, checker regression, diff whitespace | PASS locally |
| Physical GPU 30s + 3x120s | NOT RUN |
| Galaxy hardware / immersive VR / 72 FPS | NOT TESTED |

[Independent workflow](../../.github/workflows/p507-e0-e1.yml) checks logic and downloads the pinned asset for actual Chrome. It checks out the PR HEAD explicitly. Browser job is expected to remain **red** while the E0 finding exists; diagnostic collection does not bypass it. Artifacts upload even on failure; no green-old-SHA claim. Exact run, final HEAD and artifact links are recorded in the Draft PR.

[Source artifact screenshots](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44038653564/artifacts/14309207795) are original G1/G2 evidence only. New neutral error screenshot, E0 scene JSON and navigation JSON are in the E0/E1 CI evidence artifact; no raw screenshot is committed. No E1 rendered screenshot exists because the gate stops before rendering. No raw browser profile, source photographs, auth information or private artwork is included.

## Performance facts and limitations

Actual E0 load parsed the pinned GLB, but E1 runtime never reaches renderer setup. Therefore GLB bytes/hash and E0 mesh count above are factual; **E1 load-start/parsed/first-frame timings, draw calls, rendered resolution, WebGL vendor/renderer, frame sample counts/p50/p95/FPS and >33.33ms counts are NOT RUN**. Do not reuse original G1/G2 preview FPS as E1 metrics. The code records those fields only after the gate passes. The prepared short software smoke protocol is documented in the runbook; it is not the physical-GPU protocol or KPI evidence.

G1_CIRCULATION remains PARTIAL; G2_VISUAL PENDING OWNER APPROVAL; virtual room +15% X/Y, not real 1:1; AIRC data/rights not verified. WebGL parsing, emulated mobile viewport and CI checks do not establish real GPU, Galaxy, WebXR session, VR72 or any MT1-MT3 acceptance.

## Next proposals — not implemented

1. ChatGPT/owner independently adjudicate the TV metadata/export difference and agree exact E0 contract handling. Any asset revision is a separate approved task; do not silently repin this experiment.
2. Once E0 genuinely passes, run the already written E1 lifecycle/browser/performance scenarios and review route/lighting screenshots. Investigate western route clearance without reducing radius or changing R4 in this task.
3. Propose E2 only after accepted E0/E1: approved device/protocol, user-gesture XR session lifecycle and explicit navigation policy. E2/E3/production remain NOT STARTED.

**Stop at Draft PR. No merge/deploy. Await independent ChatGPT/owner acceptance.**
