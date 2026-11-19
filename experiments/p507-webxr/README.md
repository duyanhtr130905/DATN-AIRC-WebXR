# CURRENT 2026-11-19 — M2 FUNCTIONAL PROTOTYPE ACCEPTED (PR #24 MERGED)

The P507 standalone desktop E1 prototype has passed scoped M2 acceptance at PR #24 head `b0a4e0f6`, merge `0b727a06`. This runbook still opens the DEV-only P507 demo via owner-only `--restore-vault`; its scripts and frozen R4 remain unchanged. [Issue #22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) privileged App CI is **NOT LIVE VERIFIED** (no token/secrets/grants configured, two jobs skipped) and is not a 7-DoD M2 blocker. [Issue #20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) 3D navigation/size/placement is deferred, G2 visual pending; no real mobile, XR, hardware FPS certification or AIRC rights. M3 work needs separate owner approval. Historical notes below are AS-OF and must not override this status.

---

# Issue22 — current secure CI status (18/11/2026)

[App CI security/setup and functional report](../../docs/3d-production/P507-ISSUE22-SECURE-CI.md). Explicit --restore-vault-ci is installation-token-only and trusted-main-only, no legacy artifact/generated fallback; --restore-vault remains unchanged owner-only local restore. App/secret/environment setup NOT authorized/performed, actual App proof BLOCKED / SECURITY_APPROVAL_REQUIRED. PR CI runs without App secrets and records NOT_RUN_PRIVILEGED_REQUIRED for actual asset checks.

Responsive rendering emulation: `node experiments/p507-webxr/browser-responsive.mjs` after verified bundle prep; not phone/touch locomotion acceptance. Original desktop15groups remain `browser.mjs`. Current setup/run commands below remain owner-only; do not pass owner PAT to CI path.

## AS-OF earlier owner-preservation runbook

# Owner-approved private restore — current 18/11/2026

Original ZIP preserved byte-identical in owner-controlled PRIVATE vault. [Preservation/restore runbook](../../docs/3d-production/P507-R4-PRESERVATION.md) supersedes the prior missing-storage statement below. Explicit owner-only restore in a clean checkout: `python experiments/p507-webxr/prepare_asset.py --restore-vault`, then validator --prepare and export-reference checks before Vite/browser. No original-artifact fallback; existing destination is refused. Owner remote restore proof and exact final HEAD results are recorded in that report and Draft PR21. CI cross-repo access remains BLOCKED, no PAT/secret or grant added. Historical --download remains pinned to original artifact, still expiry-dependent.

## AS-OF before private preservation — earlier integration runbook

# P507 E1 — current integration runbook (18/11/2026)

Owner-approved M2 [Issue #19](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/19), branch `integrate/m2-p507-issue-19`, based on main `458569026edc917fa38d945ecd190bd4574b925f`. E0/E1 scoped technical acceptance at source PR #15 does not certify this integration HEAD; current results are in [integration report](../../docs/3d-production/P507-M2-INTEGRATION-19.md). All notes below the historical divider are AS-OF evidence.

## Prepare and open the demo

Requirements: existing authenticated `gh`, Python 3, Node 22.12–22.x, npm and installed Chrome. Run at `D:\Code\DATN` in PowerShell:

```powershell
python experiments/p507-webxr/prepare_asset.py --restore-vault
python experiments/p507-webxr/validate_asset.py --prepare
python experiments/p507-webxr/verify_export_reference.py
npm ci --ignore-scripts --no-fund --prefix apps/web
npm run dev --prefix apps/web -- --port 5173 --strictPort
```

Open **http://127.0.0.1:5173/p507-webxr-e1.html** in Chrome. E1 is a DEV-only standalone page and needs no M1 API, database or backend. Keep Vite running. The asset is served locally from ignored `.local/p507-e0-e1/`; it is not published in the production build.

Wait for LOADED, then press Start to lock the mouse. Use W/A/S/D to walk and the mouse to look; click an object to inspect its logical ID and provisional metadata. ESC releases the mouse; Reset returns to the initial position. Blur/pagehide clear held keys. Retry reloads and reruns E0 after errors. E0 errors must be investigated; never disable the validator to open the scene.

Only the short west route is verified: X/Z `[1.25,-7.415] → [.95,-7.415] → [.95,-5.9] → [.95,-5.2]`. Its continuation blocks at `P507-CHAIR-B-11`. Chair-row A-B/B-C gaps, east gaps, cabinets/chairs, room edges and the unsurveyed outward doorway can block motion. Stop/no-slide is intentional. Capsule radius .30m/height1.80m and frozen colliders are unchanged. Owner observed inaccessible chair-row paths and inaccurate object dimensions/positions; these are deferred at [Issue #20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20). G1_CIRCULATION=PARTIAL; G2_VISUAL=PENDING_OWNER_APPROVAL.

## Offline reuse and artifact expiry

After downloading once, validate the preserved original local bundle without contacting GitHub:

```powershell
python experiments/p507-webxr/prepare_asset.py
python experiments/p507-webxr/validate_asset.py --prepare
python experiments/p507-webxr/verify_export_reference.py
npm run dev --prefix apps/web -- --port 5173 --strictPort
```

This is offline only after npm dependencies and the exact original bundle have been prepared. Retain original download-provenance.json, the complete artifact (including original .blend for diagnostics), and asset-lock.json together. Six locked files are checked by size/SHA; source Git blobs are checked separately. Do not substitute a fresh export.

Original artifact 14309207795 expires **24/11/2026 14:46:36 Asia/Saigon** (07:46:36 UTC); current regression artifacts also have seven-day retention. Fresh-machine preparation and future CI become BLOCKED after expiry without the original bundle. No permanent authorized repository exists yet: **RISK / durable reproducibility BLOCKED**. Proposal requiring owner approval: access-controlled storage of the original byte-preserved artifact plus provenance/hash inventory and restore verification; do not publish a GitHub Release or private survey material automatically. A verified existing local bundle remains usable after expiry; it is not an independent backup.

## Current regression commands

```powershell
python -m unittest discover -s experiments/p507-g1-g2 -p "test_*.py" -v
python -m unittest discover -s experiments/p507-webxr -p "test_*.py" -v
npm run build --prefix apps/web
npm test --prefix apps/web
node --experimental-strip-types experiments/p507-webxr/navigation-check.mjs
node experiments/p507-webxr/e0-inspect.mjs
node experiments/p507-webxr/browser.mjs
python tools/verify_repository.py
git diff --check
```

Browser scripts run installed Chrome and their own temporary Vite on test ports; do not confuse these with the user demo URL on 5173. P507_GPU=default selects the local default GPU; default harness uses SwiftShader. Smoke frame samples do not establish physical-GPU 30 FPS, VR72 or XR acceptance. Original diagnostic report/evidence is immutable; final process status now rejects ROOT_CAUSE_UNRESOLVED after the Three comparison. Different-version PARTIAL is permitted only without --require-original-version.

---

## AS-OF historical runbook — source PR #15

# Current M2 correction — 18/11/2026, IN_REVIEW

Option A separates authoring evaluated bounds from hash-bound actual frozen-export bounds. See [current report](../../docs/3d-production/P507-WEBXR-E0-E1-EXPERIMENT.md). Frozen inputs/lock and 3mm/1mm tolerances unchanged. Runtime imports the committed export-bounds-v1.json; it never generates expected values. Before browser tests run `python experiments/p507-webxr/verify_export_reference.py` after bundle preparation. Python and Chrome independently verify the same frozen bytes, with negative reference/ID/transform/proxy tests. Historical preview approximate AABBs are not the reference.

Browser smoke now exercises unlocked E1; no old known-TV failure is expected. ESC explicitly clears/unlocks; retry performs a full reload/gate. Software raw frames are retained, with a ten-frame minimum and up to 60s collection extension after the 10s target; actual measurement duration is sum(raw). Not hardware/KPI/VR evidence. Final result, clean HEAD and CI/artifacts are published in Draft PR #15. Old notes below describe the previous failure and are historical.

---

# P507 E0/E1 experiment — runbook

Approved task: owner prompt 17/11/2026. Only E0 + desktop Web 3D E1; stop at Draft PR for independent ChatGPT/owner acceptance. E2/E3/G3, immersive XR, production integration, merge and deployment are excluded.

**Current gate: E0_FAIL; E1 BLOCKED_BY_E0.** The exact artifact is available and its hashes pass, but the large TV's authored manifest bounds differ from exported GLB vertices by 8.3055 mm. Do not bypass the gate or silently change the asset. See the [technical report](../../docs/3d-production/P507-WEBXR-E0-E1-EXPERIMENT.md).

## Prepare the immutable export

Run at `D:\Code\DATN` with existing `gh` authentication (never paste a token). `asset-lock.json` pins all six files, original run, source SHA and CI checkout SHA. Download uses the original artifact; this task does not regenerate it.

```powershell
python experiments/p507-webxr/prepare_asset.py --download
python experiments/p507-webxr/validate_asset.py --prepare
npm ci --ignore-scripts --no-fund --prefix apps/web
npm run dev --prefix apps/web
```

Open `http://127.0.0.1:5173/p507-webxr-e1.html`. The present R4 bundle intentionally stops at an error before E1 renderer/controls. Assets stay under ignored `.local/p507-e0-e1/`; Vite's DEV-only allowlist serves three files under `/p507-e1-assets/`. This is why the Vite config has one small plugin addition. No production entry imports E1; no experiment entry is built; no E1 asset directory is copied into `public`/`dist`.

If the pinned artifact expires on 24/11/2026 UTC, preparation is BLOCKED. Preserve a verified local download; any renewed artifact or regenerated export needs an explicit reviewed provenance/lock update. Do not call a regenerated export byte-identical without checking. Partial or corrupt downloads fail validation and are not overwritten automatically; use a fresh explicitly chosen location rather than deleting user data.

## Reproduce checks

```powershell
python -m unittest discover -s experiments/p507-g1-g2 -p "test_*.py" -v
python -m unittest discover -s experiments/p507-webxr -p "test_*.py" -v
npm run build --prefix apps/web
npm test --prefix apps/web
node --experimental-strip-types experiments/p507-webxr/navigation-check.mjs
node experiments/p507-webxr/e0-inspect.mjs
node experiments/p507-webxr/browser.mjs
python tools/verify_repository.py
git diff --check
```

Set `CHROME_BIN` if Chrome is not at the existing Windows/Linux default. No browser download or global tool install is needed. Both browser commands currently exit 1 for the documented TV discrepancy. `e0-inspect.mjs` measures actual transformed vertices, proxy containment, ancestor IDs and rejects double transforms; it never enables E1. `browser.mjs` writes a failure report and screenshot, then stops before E1 lifecycle/performance tests. CI deliberately remains red at the E0 gate. A green logic job is not E0 acceptance.

## Provisional E1 behavior, awaiting E0 resolution

WASD and mouse look require the Start button's pointer lock; ESC, blur and hidden page clear held keys. Reset returns to proposed feet `[1.25,0,-7.415]`, eye 1.65 m, yaw -pi/2. Speed 1.2 m/s, radius .30 m, height 1.80 m, dt capped .05s. These are conservative engineering trial parameters, not measured anthropometry or accessibility certification. The footprint is a vertical circular cylinder (conservative capsule envelope); floor/ceiling position is fixed, no jump/free-fly.

Navigation uses manifest oriented polygons and Z intervals, static plus .15m-pulled chair envelopes. Full swept-circle/edge distance tests prevent tunneling, with stop instead of unverified sliding. Room rectangle closes the outward door because the corridor is unsurveyed. Only the short west segment to survey `[.95,5.2,0]` is verified in the pure navigation test; continuation towards B blocks. Central and east gaps are not through-routes. No model changes, smaller radius or mesh hiding are used.

Selection resolves a child mesh's ancestor `survey_instance_id` and displays manifest/proxy fields; unknown provenance stays UNKNOWN. No database UUID, production request, tracking, persistence, XR or media permission is created.

## Evidence and measurement

Ignored `.local/p507-e0-e1/` contains exact downloaded inputs, provenance, bundle report, scene report, navigation report, failure screenshot, browser report and local test logs. Only sanitized text summaries go to Git. GitHub E0/E1 workflow uploads neutral reports/PNGs for seven days, including failures.

After a separately accepted E0 resolution, the existing E1 smoke harness is intended to run 2s warmup + 3x10s software-rendered samples along the verified west segment, fixed yaw, full quality, rAF delta clamp .05s. This is **NOT RUN** now. `P507_WARMUP_MS`/`P507_SAMPLE_MS` change the protocol and are recorded in reports. It is not the proposed physical-GPU 30s+3x120s protocol. FPS uses `1000*n/sum(intervals)`, nearest-rank p50/p95, all slow samples retained, >33.33ms counts, browser/GPU/resolution/load timings. Cold parsed and first-render timings are separate. No physical GPU, Galaxy or VR 72 FPS result is claimed.


## Read-only TV bounds diagnostic follow-up

[Root cause report](../../docs/3d-production/P507-E0-TV-BOUNDS-DIAGNOSTIC.md) now confirms the evaluated-bevel vs original-mesh export mismatch using Blender4.0.2/exporter4.0.44. Original R4, lock, manifest, E0 3mm gate and navigation remain unchanged. E0 still FAIL, E1 still BLOCKED.

`diagnose_tv_blender.py` opens the original .blend read-only, snapshots five original/evaluated component meshes, reloads it for six isolated modifier/export cases and labels every generated GLB DIAGNOSTIC_EXPORT_ONLY under .local. `diagnose_tv_bounds.py` independently decodes actual frozen positions and oriented proxy containment; `diagnose_tv_bounds.mjs` compares actual GLTFLoader vertices with precise Box3 without enabling E1. Use the exact-version commands in the linked report. A different Blender version is only PARTIAL corroboration; `--require-original-version` refuses to call it same-version evidence.

The separate TV diagnostic CI job uploads numeric JSON only. Diagnostic SUCCESS is not E0_PASS, and the existing E0 browser failure is retained. Neither proposed correction option is authorized by this follow-up.
