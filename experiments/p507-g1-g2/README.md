# P507 G1 + G2 — geometry & hero-zone lookdev (provisional)

**Status: IN PROGRESS — not visually accepted, not production, not AIRC-verified.** This work is based on [G0 art/production baseline](../../docs/3d-production/P507-G0-PRODUCTION-SPEC.md). The G0 PR #13 must be merged before this stacked PR is integrated into main. Only synthetic-neutral shapes and P507 user-reported geometry are committed: **no raw photos, recognizable people, live displays, copyrighted posters, private lab notes or AIRC brand textures**.

## Scope / truth levels

- **G1 geometry:** room shell 8.10 × 6.00 × 3.50 m; west entrance; 4 windows on east side, glass/frames; 17 independently ID'd desks (16 standard, 1 small), 36 **unmeasured chair placeholders**, ceiling modules (8 LEDs, 4 fans, 2 ceiling AC, 1 projector). Initial positions are all \`PROPOSED_LAYOUT\`.
- **G2 lookdev first implementation:** one **hero corner** (entrance, large TV, low cabinet, water dispenser, part of nearest desks), PBR-compatible materials and Blender lookdev camera plus a **dev-only** Three.js GLB viewer with three camera presets and frame stats.
- **Not included:** real photo alignment (originals and camera metadata not provided to local pipeline), exact measured desk/door clearances, AIRC logo/textures or privacy-sensitive images, full-room art pass (G3), production Catalog UUID mapping, real source state or source-to-render KPI, hardware XR acceptance.

This is an **open inventory**. The included provisional fixture is not a locked/final device list; adding another object changes the fixture revision, not the G0 art direction. Position changes must not rename established survey IDs. Frontend production M1-C remains unchanged. No P507 fixture is loaded automatically by the application/backend or written to PostgreSQL.

## Input / geometry check

- \`p507-provisional.json\`: unit meter, proposed rectangles, metadata sources, 17 desk instance IDs, 36 chair count, openings and hero positions. **No permission to treat any source as AIRC real_verified.**
- \`geometry.py\`: no dependencies beyond Python standard library. Checks unique IDs, positive dimensions, bounds, table-table overlap and proposed inter-cluster desk-edge gaps. **Does NOT certify aisles**, escape clearance, furniture-to-furniture collisions, or door swing.
- \`test_geometry.py\`: unit tests for 17 desks, A6/B6/C5, new-object append, duplicate IDs, overlap, out-of-bounds, provenance and gaps.

From repository root:

    python experiments/p507-g1-g2/geometry.py
    python -m unittest discover -s experiments/p507-g1-g2 -p "test_geometry.py" -v
    python -m py_compile experiments/p507-g1-g2/geometry.py experiments/p507-g1-g2/generate_blender.py

If you correct a measurement, change the inventory \`size_source\` and \`position_source\` field **only with evidence**. On future instances, add stable IDs and update generators as necessary; no fixed object-cap imposed by validator.

## Blender G1 + G2 generation (requires locally installed Blender)

This runtime **is not available in the ChatGPT execution environment that created the PR**. Therefore we have not actually exported or rendered the source; never label GLB/Blender/G2 acceptance PASS until it has been executed and reviewed on a machine with Blender.

From repo root, example:

    blender --background --python experiments/p507-g1-g2/generate_blender.py -- --inventory experiments/p507-g1-g2/p507-provisional.json --output-dir experiments/p507-g1-g2/out

Files **expected if generation succeeds**, all ignored:
- \`experiments/p507-g1-g2/out/P507_G1_G2_PROVISIONAL.blend\`
- \`experiments/p507-g1-g2/out/P507_G1_G2_PROVISIONAL.glb\`
- \`experiments/p507-g1-g2/out/report.json\`

Manually verify Blender version, dimensions, wall openings, normals, material compatibility, and object IDs. Run [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) against the generated GLB. If this fails, report the stack trace and environment; **do not change G0 target or fabricate evidence**.

**Provisional art:** no advanced image textures; hero uses neutral materials and editable geometry silhouettes. This is the first procedural lookdev pass, **not a guarantee of game-demo quality**. Blender Area Lights are preview only; Three.js runtime defines independent lighting.

## Three.js browser review (dev-only, does not affect official App)

1. Copy the generated \`P507_G1_G2_PROVISIONAL.glb\` into \`apps/web/public/p507-local-preview/\` (ignored).
2. \`cd apps/web\`, \`npm ci\`, \`npm run dev\`.
3. Open \`http://127.0.0.1:5173/p507-g1-g2-preview.html\`.
4. Inspect HERO, OVERVIEW and LOGO camera presets. Check WebGL2/errors, shading, window orientation, actual frame-time samples, asset statistics, and absence of source photos or AIRC claims.
5. Capture browser screenshots (desktop + mobile viewport), and **compare with locally authorized** reference shots PHOTO-ENTRY-TV, PHOTO-DESKS and PHOTO-LOGO. Report camera differences if lens/EXIF absent.
6. User must **visually accept G2** before any G3 full-room modeling.

The viewer is **development-only**: \`import.meta.env.DEV\` guard, not linked from \`App.tsx\`; it fetches the ignored local GLB and does not touch the official API, database or real-time data.

## How to review & pass gates

| Check | Current evidence / acceptance |
| --- | --- |
| G1 static inventory/geometry checks | Python tests/CI (if green) |
| G1 Blender source + editable .blend | Script exists; Blender **NOT RUN**, until local export |
| G1 real photomatch (3 shots) | **BLOCKED** pending authorized reference photos/measurements |
| G1 36 chairs/door swing/egress | Placeholders, **NOT MEASURED/NOT CERTIFIED** |
| G2 PBR geometry + web viewer source | Implemented as code; browser image **NOT RUN** until GLB exists |
| G2 hero visuals and 2 matched shots | **BLOCKED** until real Blender + authorized references + user review |
| glTF Validator | **NOT RUN** until GLB exists |
| Physical mobile/VR and product KPI | **NOT RUN**, not part of G1/G2 acceptance |

Do not merge/claim G2 PASS just because CI and Python tests are green. A reviewer must inspect actual **Three.js screenshots/video** and compare with reference images. G2 can be revised within its asset/lookdev pass without creating any "G0-fix" task. **Never begin G3 without explicit owner approval.**

## Privacy and open issues

Survey snapshots were supplied in a ChatGPT conversation, not in this repo or the local generator workspace. Original photos show people, screens and a whiteboard; they are not committed or fetched. Rights for authentic AIRC logo, posters and images are **pending**. Keep private/ and out/ folders ignored, and get AIRC confirmation on publishing conditions before any public asset.

The ≥3-room academic KPI, real status sources, room measurements, session tracking, and real-device WebXR remain out of scope and unresolved.
