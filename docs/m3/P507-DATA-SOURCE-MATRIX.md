# P507 data source matrix

On 2026-11-19 the owner confirmed AIRC has no management API or existing device management software, selected manual-first and confirmed permission to inventory lab equipment for the thesis. The project owner enters observations through a named Admin account. R4 remains the provisional baseline and omits some small objects. See [Issue #3](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3) and the [PR decision](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#issuecomment-6999885792).

| Type | Operator and method | Scope and timestamp | Cadence / institutional status |
| --- | --- | --- | --- |
| room_schedule | Owner enters status and activity manually in Admin | P507 room; explicit time of observation/application and system mutation timestamp | Manual/on-change; official schedule source and SLA unconfirmed |
| equipment_status | Owner records equipment status manually | P507 object UUID; explicit time of observation and system mutation timestamp | Manual/on-change; R4 inventory coverage and authoritative device status pending |
| exhibit_info | Owner enters title, description and source note | P507 object UUID; observation/content revision time and system mutation timestamp | Manual/on-change; institutional content authority and SLA unconfirmed |

Timezone is explicit on the wire. The prototype browser interprets the wall time in the operator's local timezone and converts it to UTC. System time and version are assigned independently. Private observations remain in the Admin audience with `source_kind=unknown` for transport. The per-revision audit stores provenance separately. The UI labels explicit fixtures `SYNTHETIC_TEST / NOT_AIRC`, explicit owner entries `OWNER_ENTERED / PENDING_VERIFICATION`, and legacy entries without provenance `UNKNOWN`. Tests use generated fictional content and ephemeral credentials. Public readers remain synthetic-only.

| Data use / disclosure | Project owner statement, 2026-11-19 | Institutional/third-party authorization status |
| --- | --- | --- |
| Survey/inventory for thesis | Owner confirmed survey permission | Scope for restricted files and photographs not established |
| Private Admin display / manual entry | Yes (owner confirmation) | Private/manual workflow selected; actual records still need provenance |
| Demo for academic supervisor / examination committee | Yes (owner confirmation) | AIRC authorization for internal or restricted material not evidenced |
| Include information in thesis | Yes (owner confirmation) | Content/image copyright, privacy and institutional clearance not evidenced |
| Publish information/assets to website or GitHub | Yes (owner's intended scope) | **NOT AUTHORIZED by this statement alone**: specific AIRC and third-party rights/approved content remain PENDING |
| `real_verified` promotion | No owner evidence of institutional verification | BLOCKED until documented source verification and appropriate rights |

The four owner-selected "Yes" responses are recorded as **owner-reported scope only**, not AIRC authorization. Until actual permitted records/content are reviewed, keep unpublished real data within the protected Admin workflow, keep public Catalog/REST/WebSocket synthetic-only, do not upload raw/sensitive AIRC photos or details to GitHub, and do not classify data as `real_verified`. See Issue #3 owner-scope note. Admin-entry-to-UI latency can be measured with fixtures. Physical change to discovery, manual entry and panel update requires a separate field protocol. [Issue #2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/2) and #3 remain open.
