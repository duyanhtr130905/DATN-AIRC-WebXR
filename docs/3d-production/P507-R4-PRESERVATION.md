# P507 R4 — private preservation and independent restore (18/11/2026)

Owner authorization: [PR21 decision](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21#issuecomment-6973024761), within M2 Issue19. Continue Draft PR21; no merge/deploy/M3. Existing main remains `458569026edc917fa38d945ecd190bd4574b925f`; source baseline for this task `faa12d20a55a5d0dbf8e4b81cd0b1289d61f04bf` including ChatGPT's dependency-table fix.

## Original acquisition and private remote

Owner account `duyanhtr130905` authenticated through existing gh; source repo PRIVATE/admin verified. Original artifact14309207795/run44038653564 was unexpired. Binary-safe `gh api .../zip` stdout was written directly to a binary file handle; no PowerShell text redirection, re-zip, re-export or model edit. Original ZIP **11369216 bytes**, SHA256 **4255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8**, exactly matching GitHub metadata digest and size. ZIP CRC verified; all28 members preserved, including original .blend and neutral screenshots/reports; all six locked file hashes/bytes match.

[Private vault](https://github.com/duyanhtr130905/DATN-AIRC-WebXR-asset-vault), commit `908a5cbb1f77b75b28666fd424cbd85f2aba4c1f`. Created only after confirming absent; PRIVATE verified before and after upload, owner/admin confirmed; collaborators list contains owner only, Pages=false, no Releases published. ZIP plus original safe metadata, immutable source asset-lock, per-member hash manifest and restore README committed. No raw survey photos or files outside approved original bundle added. No global Git config, PAT, new secret or cross-repo grants. Repository accepted upload; account remaining storage quota is not exposed by current API (plan fields null), so no exact quota claim. Vault is separate from source, no asset binaries committed in application source.

Archive path `p507-r4/artifact-14309207795/original-artifact-14309207795.zip`. Manifest SHA256 `d0a9aaeb6899d2c8ecdca909f7c6e30f413d8ecc28ae59ae6ffde0c15971194a`. Original source `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31`, original CI checkout `9764b90f86317446bb585bf668171f81e1c57edb`. Frozen GLB10751036bytes/SHA256 `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`. All original member identities are in restricted archive-manifest.json; source-side vault-lock.json pins archival commit/archive/manifest/asset-lock without credentials.

## Owner restore runbook — explicit, no fallback

Use a fresh application clone of PR21 branch (after review use accepted commit); run PowerShell at its root:

```powershell
gh api user --jq .login
gh repo view duyanhtr130905/DATN-AIRC-WebXR-asset-vault --json isPrivate,viewerPermission
python experiments/p507-webxr/prepare_asset.py --restore-vault
python experiments/p507-webxr/validate_asset.py --prepare
python experiments/p507-webxr/verify_export_reference.py
npm ci --ignore-scripts --no-fund --prefix apps/web
node --experimental-strip-types experiments/p507-webxr/navigation-check.mjs
node experiments/p507-webxr/e0-inspect.mjs
node experiments/p507-webxr/browser.mjs
npm run dev --prefix apps/web -- --port 5173 --strictPort
```

Open http://127.0.0.1:5173/p507-webxr-e1.html. No M1 backend. Start/WASD/mouse/select/ESC/Reset as in [E1 runbook](../../experiments/p507-webxr/README.md). Restore refuses an existing destination instead of replacing it; use a fresh checkout or a new path inside that checkout .local via restore_asset.py --destination. It checks current owner authentication and PRIVATE/admin before/after remote fetch; reads pinned Git blobs directly to avoid CRLF corruption; checks ZIP size/hash, manifest, every28member, six locks and provenance; rejects traversal/duplicate/symlink/corrupt archives. Only then moves verified files to the new destination. Failure is BLOCKED, no Actions-artifact fallback, regeneration or repin. --download remains the original historical Actions path and is mutually exclusive with --restore-vault.

The independent proof must clone the application and vault from their GitHub remotes, with no old .local bundle. Preserve vault-restore-report.json (exact app HEAD/dirty, vault commit, original downloads0, existing bundle false), bundle/reference/Chrome reports and neutral screenshots. App CI still fetches original Actions artifact; owner restore alone does not certify future CI access.

## Results and remaining boundary

Acquisition/archive verification PASS; remote upload/private access PASS. Independent clean remote restore PASS on clean `193720b1770de119d5f87e732d5594a0f10b8b62`: [sanitized numeric evidence](../evidence/p507-r4-owner-restore-193720b.json). All28members/six locks/archive SHA, export reference402482positions/delta0, actual E0 Chrome and negative tests PASS, Chrome E1 15/15 PASS with no M1 backend. App and vault fetched from GitHub remotes into fresh directories, no existing bundle and no original Actions download. 76 geometry+23 E0/restore/diagnostic tests,45 frontend units/build/typecheck,repository/diff checks PASS. Final documentation HEAD will rerun remote restore/local tests and all CI; exact final SHA/results in PR21, not relabeled checkpoint evidence. Negative restore tests23total E0/reference/diagnostic/restore suite PASS, including corruption/path/duplicate/existing-target/private-owner rejection. No asset-lock, frozen generator/inventory, E0 tolerance3mm/proxy1mm, scene/runtime/collision changes.

**OWNER_RESTORE=PASS**; **CI_CROSS_REPO_RESTORE=BLOCKED**. Source repository's GITHUB_TOKEN has not been granted access to private vault. Existing CI remains dependent on original artifact until24/11/2026 14:46:36 Asia/Saigon. Future options requiring owner approval: narrowly scoped GitHub App or read-only credential for vault; alternatively owner-prepared/self-hosted restore runner. No credential provisioned automatically. This CI expiry risk remains explicit even if owner restore passes.

Issue20 DEFERRED, G1_CIRCULATION PARTIAL, G2_VISUAL PENDING_OWNER_APPROVAL, M2 IN_PROGRESS. No hardware KPI30/VR72/mobile/XR/fidelity acceptance; M3–M7 unchanged. Stop Draft PR21 for independent ChatGPT review.

## Verification limits and final gate

Original artifact identity, vault Git commit, archive and member hashes are pinned independently from application HEAD. Final document commit records successful code checkpoint above; final-HEAD local restore/Chrome and CI are reported in PR21 after completion (avoid self-referential SHA). No source/asset lock or runtime/collision changes; dependency table row is byte-identical to ChatGPT fix at faa12d2. Proposed verdict **PARTIAL / IN_REVIEW** while cross-repository automated restore remains BLOCKED and independent acceptance is pending.

npm ci/audit reported four HIGH findings in the unchanged frontend development-tool dependency chain (vite/fdir/picomatch/tinyglobby). Build/tests pass; no automatic npm audit fix or dependency upgrade performed in this preservation scope. Advisory impact/remediation requires separate triage; no security clearance inferred from CI. Remaining account storage quota was unavailable, but actual archive upload and independent download succeeded.
