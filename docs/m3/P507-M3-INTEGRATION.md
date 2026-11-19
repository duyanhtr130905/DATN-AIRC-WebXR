# P507 M3 technical integration and acceptance

## Synthetic baseline and AS-OF evidence

The sections below preserve synthetic baseline evidence. See the manual-first workflow and acceptance gates at the end of this document.

### Mapping and architecture

The provisional revision `p507-r4-synthetic-v1` uses the 121 placed IDs from the frozen R4 export reference. The browser mapping lists each logical ID and Catalog UUID in `apps/web/src/app/p507-mapping.json`. The backend derives the same UUIDv5 from a fixed P507 namespace and the logical ID. The asset revision is evidence associated with the mapping and does not enter the UUID calculation. `P507-CHAIR-C-09` and `P507-CHAIR-C-10` are UNPLACED. Manifest SHA-256 is `5240cb6674fb93b7ad46205d6788fa6bd0ad7a468a2bf1eb29e255ff7e28afd3`. GLB SHA-256 is `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`.

Catalog uses `objects.external_reference` and a fixed room UUID, with a locked transaction validating the complete mapping and refusing collisions or overwrites. This accommodates the disposable fixture without a schema migration. Restrict all M3 fixture writes to its guarded CLI. Existing global M1 database contracts still allow unrelated writers and the mapping gate validates again at ingest. Catalog fetch remains paged and bounded. The browser accepts exactly 121 known UUIDs for P507, then binds validated 3D ancestor logical IDs to those UUIDs. The DOM selector uses the same IDs when WebGL or the asset fails.

The DEV page reuses E0 scene validation and M1 Catalog, state, WS protocol 2 and replica contracts. Synthetic observations come through a local CLI that enforces size, type, offset-aware timestamps, target scope and explicit fixture authorization. Immediate retry of the exact current transition is a no-op. Older retries and out-of-order observations fail. M1 CAS, history, cursor and outbox share a transaction. Real adapter activation requires a separate AIRC decision recorded against the [source matrix](P507-DATA-SOURCE-MATRIX.md).

## Runbook

1. Use the project disposable PostgreSQL 18 environment and a confirmed fresh `airc_test_catalog_<uuid>` database created through the guarded test harness. Apply Alembic through the existing tooling. Use local development only.
2. Verify the existing authorized frozen bundle with the [M2 runbook](../../experiments/p507-webxr/README.md). Keep the R4 bundle under the ignored local directory.
3. From `apps/api`, set `DATABASE_URL` to that validated disposable DB and run `python -m app.modules.p507_cli --confirm-database <name> --authorize-synthetic p507-r4-synthetic-v1 --seed-manifest <prepared-manifest-path>`. This independently validates the frozen manifest before seeding. Use `--observation <fixture.json>` in place of `--seed-manifest` for a single update. Fields are `state_type`, `logical_id` (null for room schedule), `expected_version`, `observed_at` (ISO 8601 with offset), and `value` (M1 schema).
4. Launch the documented FastAPI server and Vite dev with the existing API proxy. Open `http://127.0.0.1:5173/?mode=p507`. Select a frozen mesh or logical ID from the dropdown. Schedule is room scoped. Equipment and exhibit state follow the selected object.
5. Run `python -m pytest -v -m postgres tests/test_p507.py` from `apps/api` with the existing PostgreSQL test guards and web dependencies. Set `M3_REQUIRE_FROZEN=1` only with the prepared R4 asset for the owner-local Chrome raycast path. Secretless CI runs the DOM fallback and real PostgreSQL / FastAPI / WebSocket path. Privileged App CI remains tracked by #22.

## Evidence and interpretation

Implementation checkpoint `d7130ee3e2c483719b1471f26a0e1dddb87d9e91` passed three M3 PostgreSQL tests on Windows with genuine Chrome 158 and the hash-bound R4. The separate [CI run](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44450871031) ran the DOM fallback in Chrome 157 and passed all 70 PostgreSQL tests. Its PR merge checkout was `2b2d58e841e7aec572f2daa0d14c7cb26fa33928`. Each run exercised 121 selections, schedule free to occupied, equipment available to maintenance to offline, a different object update, and an exhibit revision. The candidate's latest SHA and rerun results are recorded in [Draft PR #25](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25).

The local eight-sample median receive-to-DOM interval was 6.6 ms. For the same samples the median of the approximate commit-to-apply lower and upper endpoints was 251.11 and 264.36 ms. These wall-clock endpoints have unquantified cross-process clock error. The eight synthetic records provide no AIRC KPI qualification.

The harness emits `.local/m3-browser/report.json` and synthetic panel PNGs. Report samples contain source fixture time, ingest process timestamp, DB mutation time, commit acknowledgement, publish record from outbox, WebSocket receive and React DOM apply. Match by room sequence. `render.at - receive.at` measures receive-to-DOM-apply in browser monotonic milliseconds. For a same-host approximate internal commit-to-render interval, convert browser apply using `timeOrigin + render.at`, then subtract the upper/lower commit bounds given by CLI acknowledgement and database mutation time. These wall clocks require a separately measured error bound before the interval can support a timing guarantee. No AIRC source-to-render or MT1-04 result follows from these synthetic samples.

| Gate | Expected | Actual | Evidence | Result |
| --- | --- | --- | --- | --- |
| Mapping | 121 placed matched, 0 duplicates/orphans/wrong room, 2 excluded | Committed fixture and independent reference reconcile all 121 IDs. AIRC confirmation absent. PostgreSQL validation and 121 browser selections passed. Chrome on frozen R4 selected P507-CHAIR-C-08 via raycast. | Mapping JSON, M3 tests, frozen hashes | PARTIAL |
| Sources and rights | Three approved sources, owners, cadence, timestamps and explicit rights | All three blocked | Source matrix, #2/#3 | BLOCKED |
| E2E three types | Controlled ingest to PostgreSQL, REST and WS to React panel | PASS for all three synthetic types on owner-local Chrome with frozen R4 and PostgreSQL 18.6, and separately on secretless CI with PostgreSQL 18.7 and DOM fallback. Eight transitions and eight published outbox entries per run. | Chrome report and panel images | PASS (synthetic), BLOCKED (AIRC) |
| Freshness and recovery | Unknown, stale, resync and authoritative reconnect | Chrome observed gap/resync, STALE, reconnect snapshot and reload recovery. Backend-unavailable and corrupt asset fallback verified separately. AIRC SLA unconfirmed. | M1 tests and M3 Chrome report | PARTIAL |
| Evidence and review | Exact SHA and independent acceptance | Candidate SHA and check status in Draft PR. | GitHub run and independent review | PENDING REVIEW |

Overall `M3_PARTIAL / DATA_RIGHTS_BLOCKED`. Claim `M3_TECHNICAL_INTEGRATION_PASS` only with the required frozen R4 integration run and exact-head evidence. M3 real-source acceptance also requires AIRC confirmation and source-to-UI evidence for all three types.

## Manual-first Admin runbook

Apply Alembic revision 0003_admin_manual explicitly on a confirmed project development or disposable PostgreSQL database. From apps/api with the existing DATABASE_URL configured:

```powershell
alembic -x confirm_catalog_database=<database> upgrade head
python -m app.modules.admin_bootstrap --confirm-database <database> --username <operator>
```

The interactive CLI prompts without echo. It creates an active identity once and refuses a duplicate name. Seed the baseline with the existing P507 CLI --seed-manifest and the verified manifest. That explicit seed supports confirmed airc_foundation or a disposable database. The synthetic observation CLI remains disposable-only. Start the API with ADMIN_ENABLED=true, loopback binding and ADMIN_ORIGIN matching the exact local browser origin. Start Vite and open http://127.0.0.1:5173/?mode=admin. For local HTTPS, configure HTTPS end-to-end at the trusted local proxy and use the HTTPS loopback origin. Cookies use Secure on HTTPS. Default settings disable the Admin backend.

The protected preview uses R4 OrbitControls and a Catalog selector. E1 first-person navigation remains in its standalone page. Small objects use NOT_MODELED or INFO_ONLY with no frozen mesh binding. Rename or archive the private metadata without changing an R4 ID or editing public fixture records. Archive removes the object from the default private picker and blocks new state writes while retaining history.

## Admin architecture and review gates

Authentication uses salted Python stdlib scrypt, N=2^17, r=8, p=1, following the [OWASP password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html). The database stores only digests of opaque session tokens. Sessions expire in eight hours, rotate on login and revoke on logout; only active named accounts can operate. Cookie mutations require the exact origin and a session-bound CSRF value. The database serializes login attempts and limits failures. Passwords and sessions stay out of API logs, audit, browser storage and URLs.

Revision 0003 adds accounts, sessions, narrow audit records and the private Catalog overlay. It widens existing state/outbox uniqueness by audience, preserving legacy rows in public. Private observations use the existing state/history/outbox transaction and a P507-scoped private sequence. The authenticated WebSocket sends published outbox sequence hints only. The private protected REST snapshot supplies authoritative values and account attribution. Public REST, history, replay and snapshot keep synthetic visibility predicates.

| Gate | Expected evidence | Status |
| --- | --- | --- |
| Auth and scope | Expiry, revocation, rotation, invalid cookie/CSRF, throttle, protected writes and public data isolation | Review against exact HEAD and tests in Draft PR #25 |
| Catalog and 121 IDs | Create/update/archive, NOT_MODELED without mesh, R4 UUID and stable logical ID preserved | Review against exact HEAD and tests in Draft PR #25 |
| Private state | Admin login to PostgreSQL, outbox, authenticated WebSocket and P507 panel for all three types | Review separate frozen owner-local and CI DOM fallback evidence in Draft PR #25 |
| Timestamp presentation | Invalid/missing to UNKNOWN, future/skew to TIME_UNCERTAIN, no assumed AIRC SLA | Review under the same PR |
| Field sources and rights | Authorized real records, permitted disclosure and validated field observation workflow | PARTIAL / BLOCKED |

Use the existing disposable PostgreSQL test guard and run pytest -m postgres tests/test_admin.py from apps/api. Set M3_REQUIRE_FROZEN=1 only with the prepared original bundle. Inspect .local/m3-admin-browser/report.json and its cropped panel images. Draft PR #25 records final-head regression evidence. M3 remains IN_REVIEW / PARTIAL.
