# P507 data source matrix

On 2026-11-19 the owner confirmed AIRC has no management API or existing device management software, selected manual-first and confirmed permission to inventory lab equipment for the thesis. The project owner enters observations through a named Admin account. R4 remains the provisional baseline and omits some small objects. See [Issue #3](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3) and the [PR decision](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#issuecomment-6999885792).

| Type | Operator and method | Scope and timestamp | Cadence / institutional status |
| --- | --- | --- | --- |
| room_schedule | Owner enters status and activity manually in Admin | P507 room; explicit time of observation/application and system mutation timestamp | Manual/on-change; official schedule source and SLA unconfirmed |
| equipment_status | Owner records equipment status manually | P507 object UUID; explicit time of observation and system mutation timestamp | Manual/on-change; R4 inventory coverage and authoritative device status pending |
| exhibit_info | Owner enters title, description and source note | P507 object UUID; observation/content revision time and system mutation timestamp | Manual/on-change; institutional content authority and SLA unconfirmed |

Timezone is explicit on the wire. The prototype browser interprets the wall time in the operator's local timezone and converts it to UTC. System time and version are assigned independently. Private observations use `source_kind=unknown` and `OWNER_SURVEYED / PENDING_VERIFICATION`. Tests use generated fictional content and ephemeral credentials. Public readers remain synthetic-only.

| Right | Status |
| --- | --- |
| Survey/inventory to support the thesis | Confirmed by owner |
| Protected manual entry workflow | Selected by owner; verification of real records and exact operational cadence pending |
| Display of internal data in demo or inclusion of restricted details/photographs in thesis | Separate authority and precise boundaries pending |
| Public distribution and `real_verified` designation | Pending evidence |

Admin-entry-to-UI latency can be measured with fixtures. Physical change to discovery, manual entry and panel update requires a separate field protocol. [Issue #2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/2) and #3 remain open.
