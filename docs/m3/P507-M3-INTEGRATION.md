# P507 M3 technical integration and acceptance

## Mapping and architecture

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

The harness emits `.local/m3-browser/report.json` and synthetic panel PNGs. Report samples contain source fixture time, ingest process timestamp, DB mutation time, commit acknowledgement, publish record from outbox, WebSocket receive and React DOM apply. Match by room sequence. `render.at - receive.at` measures receive-to-DOM-apply in browser monotonic milliseconds. For a same-host approximate internal commit-to-render interval, convert browser apply using `timeOrigin + render.at`, then subtract the upper/lower commit bounds given by CLI acknowledgement and database mutation time. These wall clocks require a separately measured error bound before the interval can support a timing guarantee. No AIRC source-to-render or MT1-04 result follows from these synthetic samples.

| Gate | Expected | Actual | Evidence | Result |
| --- | --- | --- | --- | --- |
| Mapping | 121 placed matched, 0 duplicates/orphans/wrong room, 2 excluded | Committed fixture and independent reference reconcile all 121 IDs. AIRC confirmation absent. DB and raycast evidence require their dedicated runs. | Mapping JSON, M3 tests, frozen hashes | PARTIAL |
| Sources and rights | Three approved sources, owners, cadence, timestamps and explicit rights | All three blocked | Source matrix, #2/#3 | BLOCKED |
| E2E three types | Controlled ingest to PostgreSQL, REST and WS to React panel | Chrome TCP harness covers schedule, equipment, exhibit and wrong-target update. Check exact-head CI for execution. Owner-local actual R4 and CI DOM fallback are separate results. | Chrome report and panel images when executed | PENDING EVIDENCE |
| Freshness and recovery | Unknown, stale, resync and authoritative reconnect | Existing v2 client and new P507 test scenarios. AIRC SLA unconfirmed. | M1 tests and M3 Chrome report when executed | PARTIAL |
| Evidence and review | Exact SHA and independent acceptance | Candidate SHA and check status in Draft PR. | GitHub run and independent review | PENDING REVIEW |

Overall `M3_PARTIAL / DATA_RIGHTS_BLOCKED`. Claim `M3_TECHNICAL_INTEGRATION_PASS` only with the required frozen R4 integration run and exact-head evidence. M3 real-source acceptance also requires AIRC confirmation and source-to-UI evidence for all three types.
