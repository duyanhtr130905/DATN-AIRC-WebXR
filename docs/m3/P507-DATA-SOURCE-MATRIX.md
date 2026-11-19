# P507 data source matrix

Checked against GitHub on 2026-11-19. [Issue #2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/2) and [Issue #3](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3) are open. Their discussions record proposals and requests for confirmation. The owner authorized technical implementation in the 2026-11-19 M3 task.

| Type | Intended scope and M1 schema | AIRC system of record / owner / access method | Source timestamp / cadence / timezone | Read / store / demo / report / public | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| room_schedule | P507 room; status free, occupied or closed and activity | Unconfirmed | Unconfirmed | All unconfirmed | #3 and discussion | BLOCKED |
| equipment_status | Mapped P507 object; status available, maintenance or offline | Unconfirmed | Unconfirmed | All unconfirmed | #2 and #3 and discussions | BLOCKED |
| exhibit_info | Mapped P507 object; title and text | Unconfirmed | Unconfirmed | All unconfirmed | #2 and #3 and discussions | BLOCKED |

The schemas above describe application payloads. AIRC must confirm actual source schemas, object scope, access methods, timestamps and accountable owners. Record the AIRC decision reference and revision for each right before enabling any real adapter. For a manual source also record who enters observations, how timestamps are assigned and how the workflow is governed. Manual observations remain manual.

The technical fixture uses synthetic observations with explicit offsets. Connected status reports transport health. Display an observation age and unverified cadence until an approved SLA exists. Mark retained data stale following a disconnect. Apply any future approved freshness threshold to the source observation time with documented clock uncertainty. Real ingestion and publication remain disabled.
