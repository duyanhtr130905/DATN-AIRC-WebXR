# Current preservation follow-up — 18/11/2026

Owner-approved private preservation now implemented: see [R4 preservation and restore evidence](P507-R4-PRESERVATION.md). Original ZIP and all member bytes preserved in PRIVATE vault; independent owner remote restore PASS on clean `193720b`, E0/E1 15/15, final documentation HEAD regression/CI linked from PR21. CI cross-repo still BLOCKED without separately approved access. This supersedes earlier missing-storage decision statements below; M2 IN_PROGRESS, #20 DEFERRED, visual pending/circulation partial. Same Draft PR21, no merge/M3.

## AS-OF integration evidence before preservation

# M2 Issue #19 — integration acceptance evidence (18/11/2026)

Draft PR: [#21](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21). Status: IN_REVIEW / PARTIAL pending exact final HEAD checks and independent ChatGPT acceptance. Main baseline `458569026edc917fa38d945ecd190bd4574b925f`; branch `integrate/m2-p507-issue-19`. Authorized [Issue #19](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/19); [Issue #20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) deferred owner findings.

## Provenance and reconciliation

New branch starts from origin/main. No-ff merge `3f06344` has main as first parent and reviewed #15 `c3c800227cfd07426b4504f38607bb864b0b12f8` as second parent; #14 `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31` and merged G0 #13 remain ancestors. No rebase, retarget, force push or merge of source PRs. Four content conflicts: AGENTS.md, README.md, ROADMAP.md, PROJECT_STATUS.md. All initially resolved to main, then only current runbook/status additions applied. AGENTS stays byte-identical to main. Historical source snapshots remain accessible in their original commits/reports, never restored as current policy.

Whole-tree comparison to reviewed #15 restricts differences to main governance/doc changes, diagnostic fix/tests/workflow and this integration documentation. No production API/database/migrations, dependencies, frozen generator/inventory/geometry, asset-lock, export reference, collision, placement, sizes or runtime gate edits. No silent clean-merge regression was found; compare commands and final verification are recorded below.

## Frozen identity and diagnostic

Original bundle six hashes verified, source `acd21c62`, original CI merge checkout `9764b90f86317446bb585bf668171f81e1c57edb`; GLB 10,751,036 bytes / SHA256 `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`. Frozen input Git blobs match original reports. Asset lock and all experiments/p507-g1-g2 files match reviewed source. Original diagnostic JSON/report retained byte-for-byte. TV authoring drift 8.3055mm remains disclosed; operational bounds 3mm and proxy 1mm unchanged.

Diagnostic exit now uses final conclusion after Three comparison. CONFIRMED succeeds; UNRESOLVED fails in all modes; different-version PARTIAL succeeds only without --require-original-version. Two unit regressions plus real CLI matching/manual-mismatch/Box3-mismatch cases run in diagnostic CI.

## Regression on integration branch

Clean integration `69176aa`: 76 G1/G2 Python and 18 E0/reference/diagnostic Python PASS; six bundle hashes PASS; 45 frontend units/build/typecheck PASS; repository verifier 227 files/230 links PASS; diff/privacy/source-of-truth checks PASS. Final clean-HEAD local/CI results and links are appended after verification; pending checks are not PASS. Blender/Khronos/Chrome full pipeline runs independently on integration HEAD in CI. Generated regression exports never replace frozen R4.

## Demo and long-term reproducibility

[Current runbook](../../experiments/p507-webxr/README.md) opens http://127.0.0.1:5173/p507-webxr-e1.html using Vite only, without M1 backend. Verified local pinned bundle exists. Fresh download currently available; original artifact expires 24/11/2026 14:46:36 Asia/Saigon. Durable archival mechanism **BLOCKED / owner decision required**: propose restricted byte-preserved original artifact storage with provenance and restore checks. No Release publication or substitute export authorized/performed. Existing verified local copy works offline after dependencies are prepared; same-machine retention is not an independent backup.

## M2 DoD and outstanding gates

| Roadmap M2 DoD | Integration assessment |
| --- | --- |
| 1 Frozen source/GLB/provenance | Hash PASS; durable new-machine access BLOCKED after artifact expiry without approved storage |
| 2 E0 actual geometry and contract | Source #15 accepted TECHNICAL_PASS; clean `69176aa` local actual Chrome PASS; final HEAD CI in #21 |
| 3 E1 Chrome controls/collision | Source #15 15/15 accepted; clean `69176aa` local actual Chrome PASS; final HEAD CI in #21; full circulation PARTIAL |
| 4 Logical ID/panel provenance | Source implementation retained; clean `69176aa` actual Chrome PASS; final HEAD CI in #21; provisional USER_REPORTED metadata |
| 5 Error/retry/recovery | Source scenarios retained; clean `69176aa` actual Chrome PASS; final HEAD CI in #21 |
| 6 Browser evidence/performance | Functional smoke PASS on clean `69176aa`; no physical-GPU KPI30/VR72/mobile/XR certification |
| 7 Runbook/limitations/review | Current runbook supplied; independent ChatGPT acceptance pending; M2 IN_PROGRESS |

G1_CIRCULATION=PARTIAL, G2_VISUAL=PENDING_OWNER_APPROVAL. Owner deferred chair-row accessibility and inaccurate furniture sizes/positions under #20; no resolution or PASS claimed. Virtual 6.90×9.315×3.50m is owner-approved +15% adaptation of USER_REPORTED 6×8.1×3.5m, not 1:1. AIRC rights/fidelity, mobile/physical devices, G3, M3–M7 remain outside this task.

Next: finish final exact-HEAD checks; independent ChatGPT review of one Draft PR; owner decides archival mechanism and later #20 resumption. Codex does not merge or begin M3.

## Clean integration checkpoint and final verification protocol

Clean `69176aa0a005cc7db5433c2b82e24ed68a7b356f`: E0_PASS; all actual geometry/reference negatives PASS; E1 15/15 scenario groups PASS in Chrome 158.0.8127.36 on Windows, P507_GPU=default (inspect renderer in raw JSON; no performance certification). Three short frame runs preserved. 45 frontend units/build/typecheck, 10 capability-checker units, Python reference decoder (402482 positions, delta0), navigation exact blockers PASS. No API/DB/XR/media requests in E1 harness. Earlier ff4ac96 checkpoint raw files retained separately; clean 69176aa results are fresh reruns, not relabeled evidence.

Checkpoint workflows (not final-HEAD certification): E0/E1 [44247427593](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44247427593), G1/G2 [44247427630](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44247427630), diagnostic [44247427636](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44247427636). Final doc commit reruns all six workflows; workflow path filters include integration status/report so documentation synchronization cannot silently skip E0/diagnostic gates. Final actual branch HEAD, workflow run IDs/conclusions and artifact links are recorded in Draft PR #21 after completion, avoiding a self-referential commit hash. Checkout HEAD/dirty fields in raw E0/E1/diagnostic reports must agree with final PR HEAD, dirty=false.

Local same-version diagnostic replay could not run from old numeric-only CI artifact: isolated DIAGNOSTIC_EXPORT_ONLY GLBs are absent. This is NOT a PASS; full Blender4.0.2/exporter4.0.44 diagnostic and real CLI matching/manual/Box3 negative regression run fresh in CI. No old evidence is relabeled. Diagnostic helper reports stderr when inputs are missing.

Final checks also compare AGENTS to main and frozen/runtime/reference/evidence paths to c3c8002, verify source ancestor chain and all six lock hashes, run repository verifier/links/limited secret scan, inspect tracked binary/private paths and diff --check. Actual final results are in #21. Privacy scan is limited pattern checking, not a comprehensive security audit. No source photos/private data/generated GLB/.blend/node_modules/.env are newly tracked.

## Same-version diagnostic and current local demo evidence

On clean integration `69176aa0a005cc7db5433c2b82e24ed68a7b356f`, [TV CI 44247798568](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44247798568) SUCCESS. Downloaded numeric artifact inspected: Blender4.0.2/exporter4.0.44, ROOT_CAUSE_CONFIRMED; matching real CLI exit0; injected manual10mm and Box3 10mm mismatches both ROOT_CAUSE_UNRESOLVED/exit1; every case records exact head and dirty=false. Original diagnosis remains intact. Local old-artifact replay limitation above is resolved for acceptance by fresh CI, not by claiming missing local inputs existed.

Actual Chrome URL5173 smoke PASS on clean 69176aa, E0_PASS and no API/WS requests. Local E1 final rerun 15/15 PASS, Chrome158/RTX3050 backend, 1280×720/DPR1, default-GPU short smoke only. Local sanitized logs/JSON/screenshots retained ignored at `.local/p507-integration-19/`; software CI neutral evidence is downloadable through #21. Full final-documentation HEAD reruns the same checks and six workflows; final IDs/results live in PR #21 (not old SHA CI). This is the final documentation synchronization, with branch/main separation unchanged.

Proposed overall verdict remains **PARTIAL / IN_REVIEW**: functionality and diagnostic have fresh technical evidence, but independent ChatGPT acceptance and a durable original-bundle storage decision remain outstanding. Issue #20 is explicitly deferred, not an integration blocker by itself. No M2 DONE/G2_VISUAL acceptance implied.
