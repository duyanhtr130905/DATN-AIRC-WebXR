# M3 manual-first Admin

The owner selected manual entry and confirmed permission to inventory AIRC lab equipment for the thesis on 2026-11-19. The lab has no existing management API. See [Issue #3](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3) and the [owner decision in PR #25](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#issuecomment-6999885792).

The ADR-0001 stack applies. This scoped implementation uses a named account provisioned offline, opaque server sessions, and same-origin private REST and realtime. It is intended for operator-controlled local use. Hosting and publication require separate approval.

Admin Catalog metadata overlays the existing R4 UUIDs without modifying the frozen mapping or exposing private descriptions through Catalog. Newly surveyed objects have stable UUIDs and private Catalog visibility. Private observations reuse the M1 current state, history and outbox tables in a separate audience with its own sequence space. Public readers keep their synthetic checks. AIRC publication, broader sources and KPI criteria remain open.

Select fixture provenance for synthetic prototype content. Owner-entered observations require an explicit observation timestamp with timezone. Save the source note when available. Catalog revisions preserve provenance when the operator leaves the source unchanged. Naming an Admin account does not verify data. Only a separate evidence and rights decision can authorize verified data. The Admin contract offers no verified write mode.

R4 identifies 121 modeled placements. Record operating equipment, exhibits, furniture, room construction, and decoration as separate inventory categories after the owner confirms their classification. Small items use NOT_MODELED or INFO_ONLY with the existing room scope and stable UUIDs.
