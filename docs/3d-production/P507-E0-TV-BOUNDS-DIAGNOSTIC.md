# E0 TV Bounds Root Cause Investigation

17/11/2026 — owner-approved diagnostic follow-up on Draft PR #15. **ROOT_CAUSE_CONFIRMED. E0_FAIL and E1_BLOCKED remain unchanged.** This report proposes correction options; it does not apply either option or accept the experiment.

## Provenance and exact reproduction

Diagnostic baseline: `a37bb86f1153dfd743187f532edb303364279922`. Verified source evidence commit: `6ae02b0397c88970c46618bbe5b4ba3d501edfcf`, clean checkout, [same-version CI run 44065711842](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44065711842), [numeric diagnostic artifact 14318919955](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44065711842/artifacts/14318919955). Final PR HEAD/CI are reported in [Draft PR #15](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/15); do not attribute the above run to a later documentation commit.

Original R4 [run 44038653564 / artifact 14309207795](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44038653564/artifacts/14309207795) was downloaded again to a separate ignored diagnostic folder. All six locked file hashes agree with the original lock. No regenerated GLB was substituted.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Frozen GLB | 10,751,036 | `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49` |
| Frozen .blend | 10,503,972 | `3c092018ce2ed7ebd1c3065cf0e4aa7ef1ab5750aa109ffd771e72f8805689e2` |
| Frozen manifest | 172,895 | `5240cb6674fb93b7ad46205d6788fa6bd0ad7a468a2bf1eb29e255ff7e28afd3` |

Asset source SHA `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31`; original CI checkout merge SHA `9764b90f86317446bb585bf668171f81e1c57edb`. Frozen generator/geometry/inventory input hashes also pass. The .blend hash is a new diagnostic identity of the file obtained from the original authenticated artifact, not an invented original manifest field.

The decisive controlled run used **Blender 4.0.2 / glTF exporter 4.0.44**, matching the original report/GLB. Preliminary local **Blender 4.5.9 LTS / exporter 4.5.51** reproduced the same positions but was correctly labeled ROOT_CAUSE_PARTIAL until the original-version test completed. Three.js **0.185.0** (REVISION185) and actual headless Chrome were used only for E0 read-only inspection, not E1 rendering or performance.

Reproduce with the existing pinned artifact and Blender 4.0.2, from repository root:

```powershell
python experiments/p507-webxr/prepare_asset.py --download
python experiments/p507-webxr/validate_asset.py --prepare
blender --background --disable-autoexec --python-exit-code 1 --python experiments/p507-webxr/diagnose_tv_blender.py -- --artifact-dir .local/p507-e0-e1/artifact --output-dir .local/p507-tv-diagnostic/blender-original-version
node experiments/p507-webxr/diagnose_tv_bounds.mjs
python experiments/p507-webxr/diagnose_tv_bounds.py --artifact-dir .local/p507-e0-e1/artifact --blender-dir .local/p507-tv-diagnostic/blender-original-version --three-report .local/p507-tv-diagnostic/three-tv-report.json --output .local/p507-tv-diagnostic/tv-bounds-diagnostic.json --require-original-version
```

Use an explicit path to an existing Blender executable when needed. CI installs the same Ubuntu24.04 system package environment as R4. An initial diagnostic run failed because setup-python changed the embedded Python environment and Blender could not import system numpy; removing that extra environment setup fixed the tooling, without changing a test or asset. That failed run is not used as geometry evidence.

The Python decoder reads actual FLOAT POSITION accessors, byte offsets/strides, primitive mapping, scene hierarchy, TRS/quaternion or column-major matrices. It performs independent double-precision world transforms. Blender original/evaluated positions are compared as point sets, allowing normal/UV vertex splits and triangle index ordering. Matching tolerance **2 micrometres** is solely for diagnostic numerical equivalence, not a replacement for the unchanged E0 3mm gate. Full numeric evidence, including transforms/modifiers/vertex extrema, is [committed separately](../../experiments/p507-webxr/evidence/tv-bounds-6ae02b0.json).

## Root cause and component mapping

The mismatch is a **pre-export evaluated-metadata vs original-mesh export configuration mismatch**, not a proved Blender/Three implementation bug:

1. Frozen `cube()` adds BEVEL and WEIGHTED_NORMAL modifiers ([generator](../../experiments/p507-g1-g2/generate_blender.py), line124).
2. `hero_assets()` builds five separate TV parts and calls `pose_asset(..., merge=False)` (lines1480–1527). All five have `survey_instance_id=P507-TV-LARGE`, no Blender parent, unit scale and rotation25 degrees about survey Z. Their world/local matrices and glTF equivalents are included in the JSON.
3. `validate_authored_bounds()` uses dependency-graph `evaluated_get().to_mesh()` (lines1923–1937). The frozen manifest union exactly equals this evaluated mesh union, with max delta **0 m** on Blender4.0.2.
4. The export invocation (line2407) supplies selection/Y-up/extras, but omits `export_apply`. Actual RNA operator default on exporter4.0.44 is **false**. The frozen GLB local position sets equal the original eight cube corners exactly; it does not contain the evaluated bevel positions.
5. Explicit `export_apply=True` on a separately labeled diagnostic export produces the evaluated position sets to sub-micrometre precision. Turning off bevel restores the original/frozen geometry; turning off weighted normals leaves vertex positions unchanged. All six diagnostic export matrices match frozen matrices exactly. No source file or frozen asset was edited.

| Blender object / glTF node | Frozen node / mesh / primitive / POSITION accessor | Original / evaluated / GLB POSITION vertices | Bevel width |
| --- | --- | --- | --- |
| REAR_CASING | 130 / 97 / 0 / 555 | 8 / 96 / 24 | .025m |
| BEZEL | 131 / 98 / 0 / 558 | 8 / 96 / 24 | .016m |
| BLACK_SCREEN | 132 / 99 / 0 / 561 | 8 / 96 / 24 | .009m |
| REAR_MOUNT_RAIL | 133 / 100 / 0 / 564 | 8 / 96 / 24 | .005m |
| STANDBY_INDICATOR | 134 / 101 / 0 / 567 | 8 / 96 / 24 | .001m |

Names above have prefix `P507_HERO_TV_`. Each maps to one frozen mesh primitive with 36 triangle indices; original cube has six quads. The split to24 POSITION records and12 triangles duplicates existing corners rather than moving them. All five retain BEVEL (3segments, overlap clamp enabled) and WEIGHTED_NORMAL stacks in .blend. They are separate logical components of **one** stable object, not five survey objects. Unlike `combine()`, the TV's merge=False path leaves modifiers unapplied before export. Other objects need their own fidelity audit; 120 passing E0 AABBs do not prove every other modifier was exported.

## Bounds and delta tables

All bounds below are **Three/glTF world axes**, metres, `[xmin,ymin,zmin,xmax,ymax,zmax]`. Conversion from Blender survey axes is exactly `(x,z,-y)`. Display rounds to9 decimals; JSON retains full precision.

| Source union | Bounds |
| --- | --- |
| original_blender | `[0.153189272, 1.779999971, -9.233558655, 1.772579312, 2.779999971, -8.387026787]` |
| evaluated_blender | `[0.161494792, 1.779999971, -9.231895447, 1.768088460, 2.779999971, -8.389651299]` |
| frozen_glb | `[0.153189282, 1.779999971, -9.233558515, 1.772579355, 2.779999971, -8.387026921]` |
| manifest | `[0.161494792, 1.779999971, -9.231895447, 1.768088460, 2.779999971, -8.389651299]` |

| Component | Source | Bounds |
| --- | --- | --- |
| BEZEL | Original | `[0.157003835, 1.779999971, -9.159531593, 1.772579312, 2.779999971, -8.387026787]` |
| BEZEL | Evaluated | `[0.161494792, 1.779999971, -9.155040741, 1.768088460, 2.779999971, -8.391517639]` |
| BEZEL | Frozen GLB | `[0.157003837, 1.779999971, -9.159531459, 1.772579355, 2.779999971, -8.387026921]` |
| BLACK_SCREEN | Original | `[0.183187872, 1.808000088, -9.129236221, 1.759919167, 2.763999939, -8.388320923]` |
| BLACK_SCREEN | Evaluated | `[0.184518576, 1.808000088, -9.127905846, 1.758588433, 2.763999939, -8.389651299]` |
| BLACK_SCREEN | Frozen GLB | `[0.183187869, 1.808000028, -9.129236399, 1.759919139, 2.763999999, -8.388320745]` |
| REAR_CASING | Original | `[0.153189272, 1.807500005, -9.209538460, 1.739203572, 2.752500057, -8.416775703]` |
| REAR_CASING | Evaluated | `[0.161505952, 1.807500005, -9.201222420, 1.730886936, 2.752500057, -8.425091743]` |
| REAR_CASING | Frozen GLB | `[0.153189282, 1.807499975, -9.209538750, 1.739203592, 2.752499968, -8.416775413]` |
| REAR_MOUNT_RAIL | Original | `[0.691092670, 2.230000019, -9.233558655, 1.697751522, 2.329999924, -8.747833252]` |
| REAR_MOUNT_RAIL | Evaluated | `[0.692755997, 2.230000019, -9.231895447, 1.696088195, 2.329999924, -8.749496460]` |
| REAR_MOUNT_RAIL | Frozen GLB | `[0.691092704, 2.229999971, -9.233558515, 1.697751547, 2.329999972, -8.747833392]` |
| STANDBY_INDICATOR | Original | `[1.579201341, 1.795499921, -9.041096687, 1.588142276, 1.798499942, -9.034090996]` |
| STANDBY_INDICATOR | Evaluated | `[1.579534054, 1.795499921, -9.040763855, 1.587809563, 1.798499942, -9.034423828]` |
| STANDBY_INDICATOR | Frozen GLB | `[1.579201340, 1.795499931, -9.041096930, 1.588142276, 1.798499931, -9.034090753]` |

| Component | Frozen minus evaluated, mm (six bounds) | Original-vs-frozen point-set distance, m |
| --- | --- | ---: |
| BEZEL | `-4.490954, +0.000000, -4.490718, +4.490895, +0.000000, +4.490718` | 1.451737081e-07 |
| BLACK_SCREEN | `-1.330706, -0.000060, -1.330553, +1.330706, +0.000060, +1.330553` | 5.048246124e-07 |
| REAR_CASING | `-8.316671, -0.000030, -8.316330, +8.316656, -0.000089, +8.316330` | 3.498289942e-07 |
| REAR_MOUNT_RAIL | `-1.663293, -0.000048, -1.663068, +1.663353, +0.000048, +1.663068` | 2.02162433e-07 |
| STANDBY_INDICATOR | `-0.332713, +0.000010, -0.333075, +0.332713, -0.000010, +0.333075` | 2.455322788e-07 |

Maximum union delta is **8.305509641076014mm** in the original Three result. The independent Python result differs by only5.55e-17m due to double-precision arithmetic ordering.

### Vertex responsible for 8.3055mm

- Frozen xmin: **REAR_CASING**, node130 / primitive0 / POSITION accessor555 / accessor vertex6, world `[0.153189281866645,1.8074999749660492,-8.484748502690783]`.
- Evaluated union xmin: **BEZEL**, evaluated vertex30, world `[0.16149479150772095,1.7934999465942383,-8.406133651733398]`.
- Difference: `0.16149479150772095 - 0.153189281866645 = 0.008305509641075959m`.
- The rear casing's own evaluated xmin is `.16150595247745514`; bevel moves its supporting extreme inward sufficiently that bezel becomes the union xmin. Therefore the union delta is **not** simply the displacement of one vertex on one mesh. The independent extreme identities are essential to explaining the number.

| Union axis | Frozen component / POSITION vertex | Evaluated component / evaluated vertex | Frozen minus manifest, mm |
| --- | --- | --- | ---: |
| xmin | REAR_CASING / 6 | BEZEL / 30 | -8.305510 |
| ymin | BEZEL / 0 | BEZEL / 0 | 0 |
| zmin | REAR_MOUNT_RAIL / 18 | REAR_MOUNT_RAIL / 78 | -1.663068 |
| xmax | BEZEL / 12 | BEZEL / 54 | +4.490895 |
| ymax | BEZEL / 3 | BEZEL / 13 | 0 |
| zmax | BEZEL / 0 | BLACK_SCREEN / 6 | +2.624378 |

There can be tied extrema because glTF duplicates corners for faces. Reported indices identify one actual witness per extreme, not an assertion that the extreme vertex is unique.

## Controlled hypothesis tests

Each case reloads the immutable original .blend in memory, selects only the five TV parts and writes `DIAGNOSTIC_EXPORT_ONLY_*.glb` under ignored `.local/`. File hashes are recorded; none is claimed byte-identical to frozen R4 or used by E0. Only vertex sets and matrices are compared. All unmentioned options remain fixed.

Distances below are maximum per-component symmetric point-set (Hausdorff) distances in metres:

| Export case | Versus frozen GLB | Versus evaluated Blender | Matrix entry delta |
| --- | ---: | ---: | ---: |
| omitted_apply | 0 | 0.03535561124 | 0 |
| apply_false | 0 | 0.03535561124 | 0 |
| apply_true | 0.0353553437 | 5.023969781e-07 | 0 |
| apply_true_without_weighted_normals | 0.0353553437 | 5.023969781e-07 | 0 |
| apply_true_without_bevel | 0 | 0.03535561124 | 0 |
| apply_false_without_bevel | 0 | 0.03535561124 | 0 |

| Hypothesis | Assessment and falsifying/control evidence |
| --- | --- |
| Bevel changes extrema, then is omitted from frozen geometry | **CONFIRMED**: raw local corner sets match frozen exactly; apply=true matches evaluated; removing only bevel restores frozen |
| Weighted normals cause the positional mismatch | **REJECTED for positions**: disabling WN changes position sets by0; apply=true without WN matches evaluated. This does not assess normal/shading quality |
| Wrong local/world or parent transform | **REJECTED for this mismatch**: no TV parents, unit scale, same pose; six export cases have matrix delta0; raw local positions already match |
| Axis conversion or second scene scale | **REJECTED**: single `(x,z,-y)` and independent transforms reproduce frozen points; no runtime scene transform or E1 code is used |
| Triangulation or primitive grouping moves geometry | **REJECTED**: 5nodes/5meshes/5primitives, correct extras; raw8corners vs split24positions have local point-set distance0 |
| Float32 export/rounding creates8.31mm | **REJECTED as primary cause**: original-world vs frozen max point-set distance5.05e-7m, orders smaller; controlled bevel toggle accounts for the discrepancy |
| Box3 precise AABB inflates rotated bounds | **REJECTED**: actual vertex loop vs Box3(...,true) delta0; Python vs Three max bound delta5.55e-17m. Installed Three source iterates POSITION/getVertexPosition then matrixWorld in its precise path |
| Source/artifact mixing | **REJECTED for the compared files**: same authenticated original artifact, six locked hashes/source/checkout and .blend identity verified |

## Geometry and collision implications

These are three distinct conclusions:

1. **Metadata:** current `authored_bounds_survey` describes evaluated Blender geometry before export; it does **not** equal the frozen GLB's bounds. Current E0 continues to FAIL exactly as designed.
2. **Actual containment:** independent decoder tested **402,482 POSITION samples across121 placed logical IDs** using each real oriented polygon and vertical interval, not its AABB. **0 violations at1mm**. TV has120 samples; minimum signed clearance is `-2.8610229518832853e-8m`, a tiny floating-point boundary overshoot. Worst global clearance is about `-4.696846e-7m`, still far below1mm tolerance. Original and diagnostic files were re-hashed; frozen bytes remain unchanged.
3. **Operational consequence:** current navigation consumes the unchanged manifest proxies, not authored bounds, so this metadata discrepancy does not change that algorithm's blocking envelope. The frozen visual TV remains inside its proxy. However omitted bevels mean an actual **visual geometry/fidelity** difference from evaluated Blender, not merely a mislabeled decimal. No evidence here certifies route usability, head clearance for real people, PCCC, accessibility or physical safety; E1 is not run or unlocked.

No GEOMETRY/SAFETY CONTRACT ISSUE was found by the specified vertex-within-convex-prism test. This is limited evidence, not a safety endorsement. It does not validate opening operations, proxy completeness against real furniture, users or unsurveyed space, or every rendered triangle/normal. Collision containment is not an automatic reason to waive the current hard gate.

## Proposed correction options — neither applied

**Option A — revise E0 validation semantics, conditional recommendation for independent review.** Evidence establishes the pre-export meaning of authored bounds. If ChatGPT/owner agree that the exact frozen GLB and oriented proxies are the operational reference, propose treating evaluated-vs-exported bounds as a monitored authoring diagnostic, and using separately derived, hash-bound **actual exported** bounds for operational agreement. This must be a general contract, not a TV exception or a tolerance increase. Preserve hard gates for artifact/source/checkout/hash/bytes/schema, actual stable IDs and UNPLACED exclusion, metres/identity/no mirror/axes/floor/room/windows/door, actual vertices inside the correctly oriented proxies at existing1mm, and spawn/navigation policy. Keep the 3mm check for the agreed actual-export reference; retain per-component pre-vs-post-export deltas and modifier/export settings in evidence. Any new mismatch, proxy violation or transform defect still fails. Owner acceptance of visual fidelity remains independent.

A would preserve frozen bytes but change the interpretation and failure classification in future validator code; that carries a risk of hiding authoring/export drift unless pre/post diagnostics stay visible and expected actual export geometry is pinned. **Not authorized or implemented by this task. E0 remains FAIL now.**

**Option B — correct metadata/export handoff in a separately approved asset task.** If authored bounds must describe actual export, add explicit pre/post semantics and measured exported bounds to `write_asset_manifest()`/handoff, or deliberately export evaluated geometry using an approved apply/bake policy. The former changes metadata hashes/lock/handoff even if GLB stays fixed; the latter changes TV geometry/normals/counts/GLB hash and requires a new asset revision and all relevant Blender/Khronos/browser/visual/proxy regression. Exact affected scope includes frozen `generate_blender.py`, generated manifest/report and possibly GLB/.blend, PR #14/handoff/freeze references and downstream asset lock. Do not overwrite or silently relabel the current frozen R4; owner must decide baseline/revision and PR handling. Inventory/layout/material changes are unnecessary to diagnose or resolve this specific mismatch.

**Recommendation:** review Option A first if the intent is to keep the already frozen GLB as the runtime asset; choose Option B if export must reproduce evaluated authoring/visual relief or a self-consistent refreshed handoff is required. This recommendation selects no implementation path. ChatGPT/owner must accept the diagnostic and authorize a correction task first.

## Verification and remaining limits

- Local regression:76 G1/G2 Python tests,13 E0/diagnostic Python tests (5existing+8new),45 frontend unit tests, build/typecheck, repository verifier and diff check PASS.
- Same-version diagnostic CI cited above: SUCCESS, ROOT_CAUSE_CONFIRMED; raw numeric reports include clean source commit. Preliminary failed numpy environment run is documented and superseded, not omitted from history.
- Existing E0 browser workflow still fails at the unchanged TV hard gate. A green diagnostic job is not E0_PASS.
- E0 actual Chrome inspection and independent Three vertex diagnostic run. E1 controls, renderer, browser performance, physical GPU/VR and human safety are NOT RUN in this follow-up.
- Full current-HEAD CI links and any still-running G1/G2 regression are maintained in the Draft PR. No earlier check is attributed to final HEAD.
- No attempt to establish byte identity across newly exported GLBs, visual acceptance of missing bevels, or fidelity of all other objects. The evidence is sufficient for this TV bounds root cause, not final art or navigation acceptance.

**STOP: Draft PR #15 stays Draft. No correction, E1 unlock, merge, deploy, E2 or E3.**
