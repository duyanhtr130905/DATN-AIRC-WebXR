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
