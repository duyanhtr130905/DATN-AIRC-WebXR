# M2 Issue22 â€” secure PRIVATE-vault CI and functional evidence

18/11/2026. Owner authorized code/workflow/tests/docs/Draft PR only. **PARTIAL / SECURITY_APPROVAL_REQUIRED**. Main baseline `42a34979d5f48b31f3e58f17f59b7b7f6010bfe8`; new branch `feat/m2-secure-vault-ci-22`. PR21 MERGED, Issue19 CLOSED; Issue22 current; #20 DEFERRED. PR23 remained OPEN/DRAFT at `0f63a671cbea5f3160330d7a954761ff780d18bb` at intake. Its five-file reviewed documentation snapshot is preserved on this branch (AGENTS/README/.techlead byte-identical; ROADMAP/STATUS extended), with provenance instead of overwriting it or claiming PR23 merged. No source PR changed.

## Threat model and trust boundary

Assets: App private key/installation token, private ZIP, frozen identity, truthful E0/E1 evidence. Threats: fork/same-repo malicious PR modifying a script/workflow; broad/other installation token; public/fake vault; mutable branch/redirect; hash/lock/path tampering; credential leakage through HTTP errors or artifact collection; legacy-artifact substitution; green skipped tests.

Unprivileged PR CI retains existing required-check names, source read-only GITHUB_TOKEN and original artifact compatibility regression while available; **no App secret**. Logic includes Python security negatives and Node App identity negatives. No pull_request_target, workflow_run, arbitrary SHA input or premerge privileged execution. Newly pinned actions verified via official GitHub tags/releases API on18/11: checkout7.0.1,setup-node7.1.0,setup-python7.1.0,upload-artifact7.0.2 and create-github-app-token3.3.0 `64ab729a6294000f5aa4a4bc0b73d1f32bc45510` (Node24). No floating action tags in changed workflows.

Privileged jobs run only push/main or workflow_dispatch/main in source repository, exact github.sha and workflow SHA; no PR checkout. Activation requires repo variable P507_VAULT_CI_ENABLED=true and **environment-only** key in p507-vault-ci. Environment must enforce selected branch main (not protected-branches-only wildcard), required reviewer and no admin bypass/self-approval; main must require reviewed changes. Never store this key as repo/org secret: malicious PR workflows could reference such a secret regardless of our if-guard. Environment must exist and its server-side policy be independently approved before activation. Current read-only API checks found environment and activation variable absent; nothing created. GitHub documents private-plan restrictions on environment branch/reviewer protection: verify entitlement first. If unavailable, DO NOT enable; separate SECURITY_APPROVAL_REQUIRED for an independently approved trusted executor architecture.

Within protected job, app-identity.mjs signs five-minute JWT in memory using Node crypto; authenticates GET /app and /app/installations/{configured_id}; checks owner/clientID/AppID/installationID, selected repository policy, no suspension, exact contents:read + implicit metadata:read. A pinned official action mints an installation token restricted to owner + vault repository + permission-contents:read, with default post-job revocation enabled. CI restore checks the action installation output matches configured/JWT-verified ID, recent attestation and exact workflow SHA; GET /installation/repositories must expose exactly one Private vault with immutable repository ID1462515003. It also checks vault API identity/privacy before/after. The restricted token proves its own repository set; owner must additionally inspect the App installation's full selected-repository configuration (only vault); a narrowed token alone cannot enumerate any additional installation grants. This setup verification remains an explicit approval gate, not a claim proven without credentials.

Token enters only the restore step environment, never command arguments, gh config, Git credential helper, reports or test job environment. Key only reaches JWT preflight/pinned action. API calls use api.github.com HTTPS with redirects disabled, bounded reads/timeouts, binary-safe contents API at frozen commit; no user URL/branch fallback. HTTP bodies/errors/keys/tokens are not interpolated in logs; failure JSON uses fixed status codes. Action manages token revocation at job end; short-lived expiry bounds abnormal termination. Never upload runner.temp, key/JWT or credential state. Upload only explicit neutral report/PNG allowlists; no original ZIP/GLB/.blend into source artifacts. Normal GitHub action state is managed by the pinned token action, not copied into evidence.

## Restoration contract

Owner path restore_asset.py remains unchanged (gh owner/private/admin). New explicit prepare_asset.py --restore-vault-ci uses a separate installation identity path; a user PAT cannot satisfy /installation/repositories. Archive is fetched at vault commit908a5cbb1f77b75b28666fd424cbd85f2aba4c1f; original ZIP11369216bytes/SHA2564255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8,28members,manifest/source lock/all six locked files checked, then original bundle/provenance/GLB validation and actual export reference. Existing target refused, extraction staged and path/hash/duplicate checks reused. Frozen GLB10751036bytes/SHA2568662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49;3mm/1mm unchanged. No model/IDs/collision/position/size changes.

Codes include CREDENTIAL_MISSING, CREDENTIAL_INVALID_OR_EXPIRED, VAULT_ACCESS_DENIED, PINNED_SOURCE_UNAVAILABLE, NETWORK_FAILURE, UNTRUSTED_CONTEXT/SHA/WORKFLOW, APP_IDENTITY_MISMATCH, TOKEN_REPOSITORY_SCOPE_MISMATCH, VAULT_IDENTITY_MISMATCH, FILE_LOCK_MISMATCH, DESTINATION_EXISTS. Remaining invalid bundle conditions use INVALID_OR_UNAVAILABLE_BUNDLE without exception text. No legacy /actions/artifacts request or generated GLB fallback exists in CI restore.

## Owner setup â€” separate approval REQUIRED, not performed

1. Approve/create dedicated owner GitHub App, repository Contents Read-only (Metadata Read-only implicit), no other permissions, webhooks unused. Install only DATN-AIRC-WebXR-asset-vault; verify full selected set and record App/installation numeric IDs and Client ID. Do not grant source repo contents or administration.
2. In source repo create/verify protected environment p507-vault-ci after checking plan supports required protection for Private repo. Main-only branch policy, required reviewer, no self-review/admin bypass; independently inspect exact merged SHA/job. No premerge dispatch of PR code with secrets is supported.
3. In **that environment only**, enter variables P507_VAULT_APP_CLIENT_ID, P507_VAULT_APP_ID, P507_VAULT_INSTALLATION_ID and secret P507_VAULT_APP_PRIVATE_KEY via secure UI. Never send private key/token into chat, repo, issue, logs or artifacts. Do not use owner PAT. Codex has not created App/installation/environment/secret or modified permissions.
4. After independent security review and approved merge, owner may set repository variable P507_VAULT_CI_ENABLED=true and dispatch each workflow from main. Existing compatibility checks remain until activation; after enabling main jobs restore from vault, not Actions. Before enabling, review branch protection/required checks and decide when new vault jobs become required; this Draft is not permission to break checks on main.
5. Require actual CI_VAULT_BUNDLE_PASS, E0_PASS/E1 15groups, diagnostic original-version positive/negative, pinned ZIP/hash/member/source proof on exact new HEAD. A skipped App job or green readiness job on PR is **NOT** this evidence. Current state: live App proof BLOCKED/no credentials. Owner-local vault proof is separate and does not close #22.

## Test evidence and M2 DoD

Precommit:76geometry,30E0/reference/restore/diagnostic/security Python and13Node identity tests PASS; these include mock/synthetic API fixtures only, not live App proof. YAML parse for all three P507 workflows PASS (PyYAML6.0.3 tooling-local, no app dependency changes). Responsive actual Chrome emulation390x844/768x1024 PASS render/selection label/panel bounds, not touch locomotion or physical mobile.

Clean checkpoint `6ed7c820147a36678fe0416664fcd6fc4604e8d2` owner-only remote restore PASS (28members/six hashes,0original-artifact calls), E0 Chrome PASS, E1 15/15 PASS and responsive390/768PASS; [sanitized checkpoint](../evidence/p507-issue22-functional-6ed7c82.json) explicitly labels this LOCAL_OWNER_NOT_APP. Final clean HEAD will rerun owner-only remote restore in a fresh checkout and actual E0/E1 plus responsive harness; all applicable CI (legacy actual frozen E0/E1, Blender/Khronos/Chrome, TV negatives, frontend/API/PostgreSQL, repository) must bind to final PR HEAD. Exact final SHA/run links/raw evidence live in Draft PR to avoid self-referential SHA. App credential proof remains BLOCKED even if legacy CI is green. No forged positive App result.

| M2 functional DoD | Scope/status to verify on final HEAD |
| --- | --- |
| Frozen provenance/E0 reference | Owner remote restore + actual E0 required; App CI BLOCKED |
| Desktop spawn/pointer lock/WASD/mouse/reset | Original15group actual Chrome smoke, no M1 backend |
| Logical selection/panel | Actual ancestor ID and PROVISIONAL/USER_REPORTED labels |
| Loading/error/retry/recovery/WebGL fallback | Original15group smoke; unsupported WebGL scenario |
| Responsive/mobile | Viewport emulation rendering PASS precommit; touch navigation/physical phone NOT TESTED/NOT IMPLEMENTED, overall PARTIAL |
| Basic performance | Raw short samples OS/browser/GPU/resolution/build; not KPI30/VR72 |
| Independent acceptance | PENDING ChatGPT; M2 IN_PROGRESS |

Issue20 chair-row access, dimensions and placements remain DEFERRED; G1_CIRCULATION=PARTIAL,G2_VISUAL=PENDING_OWNER_APPROVAL. M3 PLANNED/DEPENDENCY_BLOCKED, no coding M3; M0/M1 DONE; M3â€“M7 unchanged.

## Read-only dependency triage

18/11 npm audit reports4HIGH, all dev=true in unchanged package-lock; npm audit --omit=dev reports0. All four are propagated from **one** picomatch ReDoS advisory GHSA-fc5q-39xc-vjpf / CVE-2026-112366, not four independently established exploits. npm ls: vite7.3.8â†’picomatch4.0.7; viteâ†’fdir6.5.0â†’picomatch; viteâ†’tinyglobby0.2.17â†’fdir/picomatch; @vitejs/plugin-react5.1.1 uses same Vite.

| Package/version | Direct | Location | Finding/fix |
| --- | --- | --- | --- |
| vite7.3.8 | yes | dev server/build tooling | inherited fdir/picomatch/tinyglobby HIGH; npm proposes major downgrade6.2.7, NOT applied or accepted as safe remediation |
| fdir6.5.0 | no | dev file walker under Vite/tinyglobby | inherited picomatch; no independent advisory/verified fixed fdir version in audit |
| tinyglobby0.2.17 | no | dev glob discovery | inherited fdir/picomatch; audit fixAvailable=true does not identify verified clean version |
| picomatch4.0.7 | no | dev glob matcher | repeated attacker-controlled extglob can exhaust Node event loop; advisory affected<=4.0.7, patched version listed None at review |

Observed exposure: development/build/CI process, not browser production bundle or API runtime; Vite default host127.0.0.1, no application feature accepting arbitrary glob patterns found in examined config/runtime. This is scope analysis, not exploitability clearance. Untrusted repo/config/glob input in build tooling can cause DoS; privileged jobs run reviewed main only. Separate remediation task should validate upstream patch/advisory, dependency paths and locked update with regression when authorized. No lockfile edits, npm audit fix or major changes.

## Primary references (verified18/11/2026)

- [Official token action pinned release](https://github.com/actions/create-github-app-token/tree/64ab729a6294000f5aa4a4bc0b73d1f32bc45510): exact inputs/client-id/scope/revoke and Node24 reviewed through API action.yml.
- [GitHub App workflow auth](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow).
- [JWT App/installation endpoints](https://docs.github.com/en/rest/apps/apps), [installation repository scope](https://docs.github.com/en/rest/apps/installations).
- [Environment protection/Private plan restrictions](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).
- [Reviewed advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf); audit JSON and dependency tree retained in ignored local evidence.

Registry read-only check18/11: latest picomatch4.0.7,fdir6.5.0,tinyglobby0.2.17,Vite8.3.8. A newer Vite major is not proof that the picomatch advisory is fixed; no upgrade/downgrade applied.
