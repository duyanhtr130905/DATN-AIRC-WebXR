# State REST/WebSocket M1-B — thực tế triển khai

Cập nhật14/11/2026. Chỉ synthetic, không client/browser writes. Catalog GET M1-A và health/ready giữ tương thích; các session/event/report/auth contracts trong lịch sử vẫn PROPOSED.

## REST

- GET /api/v1/rooms/{room_id}/states: mọi current state có visibility trong phòng, gồm target Room hoặc Object, không gán room_schedule vào thiết bị.
- GET /api/v1/objects/{object_id}/states: current states của object và parent đều synthetic.
- GET /api/v1/objects/{object_id}/states/{state_type}/history: history synthetic với current/target/parent còn công bố.

State DTO: id(UUID state),room_id,target_kind(room|object),target_id(UUID),state_type(room_schedule|equipment_status|exhibit_info),value(schema theo docs13),version>=1,source_kind literal synthetic,source_observed_at nullable vàcommitted_at RFC3339 timezone. Không metadata/evidence_ref/private fields. Value có validator theo state_type và cấm extra keys.

Lists dùng limit1..100(default25),cursor UUID keyset tăng theo state.id,scopebound; response {data:[State],meta:{schema_version:1,next_cursor:string|null}}. History dùng after_version>=0 vàlimit, sortversionASC, meta.next_after_version nullable. 404 CATALOG_NOT_FOUND;422 UUID/limit/state-type/cursor validation;503 DATABASE_UNAVAILABLE;500 INTERNAL_ERROR. Body error {error:{code,message}}, không rawSQL/credentials. Chưa auth provider/write routes.

## WebSocket single-process

URL `/ws/v1/state?room_id=<uuid>`. Origin bắt buộc thuộc explicit configured CORS_ORIGINS, UUID phải hợp lệ, Room phải synthetic; UUID không cấp quyền xem room hidden. Wrong Origin/UUID/connection cap: handshake close1008; hidden/nonexistent room hoặc DB lỗi: safe error rồiclose1011, không snapshot. Client gửi text/binary bất kỳ: READ_ONLY/close1008. Không nhận state update từ browser.

Mọi message có type,schema_version=1,message_id,room_id,sequence,timestamp. Shapes:

```json
{"type":"snapshot","schema_version":1,"message_id":"<uuid>","room_id":"<uuid>","sequence":7,"states":["State DTO"],"timestamp":"<RFC3339>"}
```

Delta: {type:'state.updated',schema_version,message_id(outboxUUID),room_id,sequence,published_at,state:StateDTO,timestamp}. Heartbeat: cùng envelope và cursor hiện tại, không thay state. resync.required thêm reason:'gap' hoặc'backpressure', sau đóclose1013. error thêm code:'STATE_UNAVAILABLE' hoặc'READ_ONLY', không rawdetails.

Đăng ký subscriber trước SQL snapshot; snapshot REPEATABLE READ lấy states và cursor cùng view. Outbox durable tail `sequence>snapshot_cursor` đóng khoảng trống giữa snapshot và subscribe; broker chỉ wake hint, không là kho dữ liệu. Replay luôn recheck source/parent và chỉ xử lý durable rows đã published. Queue hints có thể trùng, SQLcursor loại duplicate. Consumer reference rule: incoming<=cursor ignore, incoming=cursor+1 apply, lớn hơn yêu cầu resync. Controlled old/duplicate consumer injection không được coi là client frontend đã tích hợp.

Nếu gap, quá32delta một lượt, hoặc unpublished đầu tiên sau cursor bị đình trệ>2s (kể cả exhausted) →resync.required; reconnect fresh snapshot đọc current state. Không im lặng giữ state cũ khi publisher chết. Chưa resume cursor qua query hoặc retention window; prototype không hứa replay toàn lịch sử sau disconnect, snapshot mới là authoritative.

Giới hạn:32connections/process,8wake tokens/client,32states/snapshot,32delta/page,256KiB outgoing,sendtimeout1s, polling fallback250ms/heartbeat khoảng10ticks. Incoming giới hạn8KiB/queue1 bằng cấu hình Uvicorn trong runbook/test. Slow queue→resync/close; network sendtimeout→cleanup. Không giữ DBconnection suốt WS; SQLsync chạy to_thread trong scope ngắn; task receive và subscription được hủy/dọn khi disconnect. Shutdown đợi dispatcher hiện tại hoàn tất boundedSQL/notify rồi dispose trongfinally, không cancel một DBthread đang chạy.

Chỉ một API worker/process được kiểm. Durable lease/claim có concurrency tests, **multi-worker/multi-instance WebSocket broadcast chưa hỗ trợ** vì broker RAM không dùng chung. Không Redis/Kafka mới. Auth, data rights, retention, scale/production và phép đo source-to-render vẫn cần quyết định/kiểm chứng. [Acceptance và metrics](17-m1-b-state-realtime-acceptance.md).

---

## Lịch sử contracts M1-A/M0-B2 và phần mở rộng

# Catalog API M1-A — READ ONLY / SYNTHETIC

Cập nhật14/11/2026. Ba endpoint dưới đây đã triển khai; status endpoints M0-B2 giữ nguyên. Các state/session/event/report/write/WebSocket contracts trong phần lịch sử phía dưới **vẫn PROPOSED**.

| Endpoint hiện có | Input | Response200 |
|---|---|---|
| GET /api/v1/rooms | limit1..100(default25),cursor? max400chars | {data:[Room],meta:{schema_version:1,next_cursor:string|null}} |
| GET /api/v1/rooms/{room_id}/objects | UUID room_id,limit,cursor | {data:[Object],meta:{schema_version:1,next_cursor}}; room không tồn tại/không synthetic →404 |
| GET /api/v1/objects/{object_id} | UUID object_id | {data:Object,meta:{schema_version:1,next_cursor:null}}; object hoặc parent không synthetic →404 |

Room: id UUID,code,name,source_kind literal synthetic,metadata:{label?:string|null,description?:string|null},created_at và updated_at RFC3339 cótimezone. Object: id,room_id,name,type,source_kind,metadata,timestamps. API không trả evidence_ref/external_reference/transform hoặc metadata tùy ý. Tất cả field ở response models; OpenAPI mô tả cả error envelopes. Không dùng ORM trực tiếp làm response.

Ordering thực tế M1-A là **UUID id tăng dần**, keyset `id > after`; chọn vì identity bất biến, không phụ thuộc code/timestamp thay đổi. Khác phương án created_at,id trong lịch sử M0-B2. next_cursor là base64url JSON {v:1,scope:'rooms'|'room:<uuid>',after:'<uuid>'}; kiểm version/shape/UUID và scope, không là token auth. Server luôn áp synthetic filters; cursor giả mạo không bỏ được bộ lọc. Không count tổng; chèn UUID thấp hơn cursor giữa các request không thuộc snapshot, client refresh để thấy; chưa có consistency snapshot xuyên trang.

404 CATALOG_NOT_FOUND;422 INVALID_CURSOR hoặc VALIDATION_ERROR (UUID/limit/length);503 DATABASE_UNAVAILABLE;500 INTERNAL_ERROR; unsupported method405 HTTP_ERROR. Body {error:{code,message}}, không raw driver/SQL/URL/credentials. M0-B2 HTTP_ERROR cho lỗi HTTP khác giữ tương thích. Chưa request_id hoặc auth provider. Source filter là hàng rào tạm cho synthetic, không thay authorization production.

Session mỗi request dùng transaction PostgreSQL READ ONLY, đóng/rollback khi lỗi, không connection leak. Objects query JOIN parent với filter synthetic trong cùng SQL để tránh đọc children sau khi parent được ẩn giữa hai query. Không có POST/PATCH/DELETE Catalog và không auth giả/admin token. Catalog rỗng trả200 data[]; nếu phòng hợp lệ chưa có object trả200 data[]. Chưa DB/migration hoặc DB mất kết nối trả503 an toàn.

Không nối scene frontend trong M1-A; scene DEMO M0-B2 và API status client giữ nguyên. Việc nối Catalog vào scene thuộc M1-C.

---

## Lịch sử contracts M0-B2 và đề xuất mở rộng

# API và realtime contracts — foundation + đề xuất M1

14/11/2026. **Chỉ GET /api/health và /api/ready đã triển khai**; docs/OpenAPI FastAPI có thật. Mọi resource/write/WebSocket bên dưới PROPOSED, chưa có endpoint và chưa có auth production.

## Hiện có — status

GET /api/health →200 `{status:"alive",service:"airc-api",timestamp: RFC3339 UTC}`. Liveness chỉ process.
GET /api/ready →200 `{status:"ready",database:"ready",timestamp}` sau SELECT1 thật;503 `{status:"not_ready",database:"not_configured"|"unavailable",timestamp}`. Không trả raw credentials/exception. Lỗi HTTP 404 / validation 422 / internal 500 dùng `{error:{code,message}}`; hiện code HTTP_ERROR/VALIDATION_ERROR/INTERNAL_ERROR và message an toàn, chưa request_id. Readiness 503 là status resource, không error envelope. OpenAPI định nghĩa typed status responses.

## Envelope và resources tương lai — PROPOSED

Base /api/v1; bắt buộc UUID stable IDs, schema_version=1, source_kind(synthetic|unknown|real_verified), timestamps RFC3339 UTC có timezone, version>=1 cho state. Không dùng room 507 làm khóa. response object `{data,meta:{schema_version,request_id}}`; lists data array và meta.next_cursor nullable, limit mặc định 25, tối đa 100, sort stable `(created_at,id)`; cursor opaque bound filter. Không cho client quyết định role/quyền.

| Endpoint dự kiến | Request bắt buộc | Response / semantics | Quyền dự kiến |
|---|---|---|---|
| GET /rooms | query cursor?,limit? | id,code,name,source_kind,updated_at,metadata đã lọc | visitor thấy phòng được công bố |
| GET /rooms/{room_id}/objects | room UUID; cursor?,limit?,type? | id,room_id,name,type,asset_ref?,metadata,source_kind,updated_at | visitor theo quyền phòng |
| GET /objects/{id} | object UUID | object details với evidence_ref chỉ khi được phép | quyền object |
| GET /objects/{id}/states | object UUID | state_type,value,version,source_kind,source_observed_at?,committed_at | quyền đọc state |
| PATCH /objects/{id}/states/{type} | value,expected_version,source_kind; If-Match dự kiến | state + version mới;409 stale | operator riêng, không public write |
| POST /sessions | schema_version,consent_version?; anonymous policy chưa duyệt | session_id,started_at,resume token chỉ nếu cơ chế duyệt | anonymous opt-in hoặc user; chưa chọn auth |
| POST /sessions/{id}/events | events[{id,event_type,sequence,occurred_at,object_id?,payload}] | receipts[{id,status:accepted|duplicate}],received_at | owner của session; resume proof |
| GET /reports/sessions | from,to,cursor?,limit? | aggregate không PII, sample counts | analyst có scope |
| POST /reports/exports | from,to,format |202 export_id,status; polling có quyền | analyst, hạn chế tải |

Các field theo docs13, metadata/payload validate theo loại và reject unknown unsafe fields; không accept arbitrary URL để fetch server-side. Hạn mức dự kiến 100 events / 256KB / batch và body limit 256KB; validate ở gateway/app, rate limit theo principal/session. 400 malformed, 422 schema, 401 unauthenticated, 403 forbidden, 404 unpublished/not found, 409 version/idempotency conflict, 413 size, 429 rate, 503 dependency. Error `{error:{code,message,request_id,retryable}}`, không PII/stack trace. Quyền ghi phải kiểm server theo room/object/session và audit; chưa chọn provider/hosting/CORS credentials policy.

## WebSocket — PROPOSED /ws/v1/state

Handshake HTTPS/WSS same-origin, xác thực khi có policy, kiểm Origin và room scopes; token không đặt trong query log. Subscribe room_ids giới hạn 20 phòng đã cấp quyền (giới hạn là đề xuất cần review), không client publish state trực tiếp. Envelope:

```json
{"type":"state.updated","schema_version":1,"message_id":"<uuid>","room_id":"<uuid>","object_id":"<uuid>","state_type":"equipment_status","version":4,"value":{"status":"available"},"source_kind":"synthetic","source_observed_at":null,"committed_at":"2026-11-14T00:00:00Z","published_at":"2026-11-14T00:00:00Z"}
```

snapshot: `{type,schema_version,snapshot_id,room_id,watermark,states:[{object_id,state_type,version,value,source_kind,committed_at}]}`. snapshot có consistent DB read / watermark; subscriber buffer delta trong lúc nhận snapshot, sau đó replay >watermark. Paginate/chunk snapshot có end marker, không ghi UI từng nửa snapshot làm mất data.
resync.required: `{type,reason:"gap"|"expired_cursor"|"backpressure",room_id}`; client fetch snapshot, không đoán state thiếu. error: `{type,code,message,retryable}` không raw details.

Ordering per(object_id,state_type): version<=current bỏ duplicate/cũ; version>current+1 yêu cầu resync; chỉ phiên bản server mới authoritative. Session reconnect exponential backoff + jitter 0.5–30s, có cancel lúc unmount/offline; cursor resume nếu server còn window, nếu không snapshot. Window/retention chưa duyệt, không hứa exactly-once. Heartbeat 30s, disconnect 90s, max message 256KB / max queue 1000 đề xuất; slow consumer chuyển resync thay queue vô hạn. State value privacy được lọc trước gửi; không để visitor subscribe phòng private bằng ID.

Transaction state+history+outbox atomic; worker gửi sau commit rồi mark published. Publish fail không rollback DB đã commit: retry bounded exponential, metric backlog, operator reconciliation; publish lại sau crash có duplicate, client version dedupe. Outbox chưa triển khai.

## Đo source-to-render và experience dự kiến

source_observed_at nullable là thời gian nguồn thật đo/cập nhật; committed_at server, published_at server, received_at client, rendered_at client sau commit scene. Chỉ gọi source-to-render nếu có source timestamp và độ lệch clock biết được; ghi monotonic duration client và clock offset/uncertainty. Khi nhập tay, source là thao tác ghi hệ thống, **không phải sensor/API AIRC**. Mục tiêu≤5s chưa được đo/chưa đạt. M1 cần thử latency có load/độ trễ mạng, không dùng SELECT 1 để thay KPI.

Session/event tương lai: stable client event UUID trước send, local outbox có consent/privacy, server dedupe; receipt sau DB commit, retry không tạo double count. Resume token storage/retention/multi-tab/offline policy chưa duyệt, M0-B2 không localstorage tracking hoặc persistence. 99% event/50 sessions / 90% tasks / 15 users vẫn chờ nghiệm thu đúng MT1–MT3.

## Cụ thể hóa snapshot/cursor — phương án M1 PROPOSED

Đề xuất thêm `room_sequence` vào mỗi delta/outbox; đây là cursor theo phòng, tách biệt version theo (object_id,state_type). Không dùng auto-increment sequence hoặc timestamp đơn thuần làm commit ordering: transaction có thể commit lệch thứ tự.

Mỗi state transaction khóa một dòng `room_state_cursors(room_id PK, last_sequence)` bằng SELECT FOR UPDATE, tăng số trong cùng transaction rồi ghi state/history/outbox với UNIQUE(room_id,room_sequence). Giữ khóa tới commit để writers của một phòng được tuần tự hóa; rollback trả lại counter. Nếu sau này có multi-room transaction, lấy khóa theo stable room ID để tránh deadlock. Đổi room membership hoặc quyền visibility cũng phải tạo delta/tombstone theo cùng cursor; chưa triển khai catalog mutation ở M0-B2.

Snapshot lấy states và last_sequence trong một transaction READ ONLY REPEATABLE READ, gửi snapshot_id + watermark và kết thúc bằng end marker. Server bắt đầu buffer subscription trước khi lấy snapshot; sau khi client xác nhận snapshot hoàn chỉnh, đọc outbox bền vững `room_sequence > watermark`, gửi theo cursor rồi nối live buffer và loại duplicate. Không chỉ dựa vào buffer RAM vì process có thể crash; gap/retention expiry hoặc quyền đổi phải trả resync.required. Client chỉ tăng cursor sau khi apply toàn bộ delta; snapshot chunk không trộn vào current state trước end marker.

Đây là thiết kế cụ thể để PoC concurrency ở M1, **chưa schema được duyệt và chưa bằng chứng runtime**. Cần test writer đang commit trong lúc snapshot, publish đảo thứ tự, reconnect, tombstone và policy change; xét throughput do khóa theo phòng. Cơ sở isolation: [PostgreSQL transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html), truy cập 14/11/2026. Quyết định cursor retention và offline/multi-tab session sequence vẫn chờ duyệt.


## M1-C C1 — Snapshot protocol2 (opt-in)

Client mới kết nối `/ws/v1/state?room_id=UUID&protocol=2`. Thiếu protocol vẫn là1, snapshot đơn tối đa32states và compatibility tests M1-B được giữ. Protocol2 mọi message có schema_version=2; version khác bị từ chối.

Snapshot gồm snapshot.start, snapshot.chunk, snapshot.end. Envelope: snapshot_id, room_id, watermark, sequence=watermark, message_id, timestamp. Start/end: total_chunks/total_states; chunk: chunk_index bắt đầu0 và states DTO public. Max512states,2MiB JSON conservative,16states/chunk và32KiB/frame. Vượt capacity trả STATE_UNAVAILABLE rồi đóng1011, không partial success. RAM bounded theo32connections; chưa multi-instance.

Một transaction REPEATABLE READ READ ONLY đọc visibility/cursor/rows (limit513 phát hiện overflow), đóng connection trước framing/network await. Không pagination bằng nhiều DB snapshots. Revalidate parent/source từng chunk và toàn bộ stateIDs trước end; thay đổi visibility abort staging. Đây là kiểm tra tại thời điểm gửi, không thu hồi bytes hoặc cam kết revocation tức thời sau lần kiểm tra cuối.

Client staging bounded512states/2MiB, chưa render chunk. Chỉ swap khi end có scope/watermark/sequence/IDs, index liên tiếp, totals và unique stateIDs hợp lệ. Missing/duplicate/reordered chunks, scope sai hoặc disconnect: bỏ staging, stale/reconnect. Delta sau end bắt đầu watermark+1; old/duplicate bỏ qua, gap resync. Không mutation.

Subscriber đăng ký trước snapshot. V2 queue8wakeups coalesce vì SQL outbox giữ delta durable. Replay bounded32, backlog/gap vượt năng lực dẫn resync. Send timeout1s và cleanup khi đóng; DB không mở suốt session. Protocol1 giữ chính sách queue overflow cũ.

Nguồn kiểm tra15/11/2026: [PostgreSQL18 isolation](https://www.postgresql.org/docs/18/transaction-iso.html), [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/). Runtime evidence chờ CI PostgreSQL18/TCP thật, không dùng unit làm bằng chứng PostgreSQL.


### M1-C frontend áp dụng protocol2

Frontend defaultlive chỉ dùng DTO synthetic đãvalidate (UUID, scope, timestamps timezone, enum/value/bounds, metadata public label/description nullable/rỗng hợp lệ). List REST dùng limit25 vànext_cursor tới null, chặn duplicateIDs/repeatedcursor/empty-page-next/32pages/512rows; render max100objects. Các GETrooms/roomobjects/objectdetail/roomstates/objectstates có typedclient, không mutation route. State realtime authoritative riêng, không trộn pages REST thiếu watermark vào snapshot WS.

Client giữ trạng thái cũ đánh STALE khi mấtWS; không gọi dữ liệu cũ là current. Roomswitch reset Catalog/selection/subscription; callback cũ bịgenerationguard. Snapshot đủend thay authoritative toàn bộ, kể cả xóa states không còn trongsnapshot. Deltas oldseq bỏ; forwardgap hoặc versionkhôngliền resync; heartbeatseq khác cursor resync. Missingchunk/disconnect khôngcommit staging. Reconnect lấy fullsnapshotv2, không clientsidepublish. Khôngtoken trongURL. Dev/preview proxy/ws giữOrigin; backendallowlistexplicitcùngorigin, khôngwildcard. Retry12 rồimanualreload, queue/timerscleanup.

## M3 private operator API

The loopback-only Admin supplement defines private session, Catalog and observation routes. Public M1 contracts above retain their read-only synthetic scope. Admin snapshot entries carry provenance, revision, actor, observation timestamp, system timestamp and an optional source note. The Admin write contract accepts only fixture and unverified owner provenance. The private GET `/api/v1/admin/p507/state/{state_id}/history?after_version=0` returns at most 100 revisions with their audit actor and provenance. Pass `next_after_version` from a page to request the next page. Private Catalog changes produce sequence-only invalidations on the authenticated Admin stream. See the [M3 runbook and architecture](m3/P507-M3-INTEGRATION.md) and [owner decision](m3/P507-ADMIN-DECISION.md).

## M4 — Local synthetic visitor and reporting API

Visitor writes require explicit configuration, loopback, exact web origin and `X-AIRC-Visitor: 1`. `GET /api/v1/visitor/status` announces synthetic-local capability. `POST /api/v1/visitor/sessions` accepts only `{"consent":"synthetic_opt_in_v1"}` and returns the server-created session ID plus an HttpOnly proof cookie. `GET /api/v1/visitor/sessions/{id}` returns fixed room, selection, info visibility and ended state. `DELETE` on the same resource deletes that authorized fixture session plus its events.

`POST /api/v1/visitor/sessions/{id}/events` takes `{"events":[...]}`, 1–32 rows and 8 KiB body. Each row contains `id` (UUIDv4), `schema_version: 1`, `event_type`, `room_id: "demo-room-foundation"`, `object_id` (null or one of the two allowed demo IDs), and timezone-aware `occurred_at`. `room_enter` and `session_end` require null object. `object_select`, `info_open` and `info_close` require an allowed object. `session_start` is generated once by the server. A session permits up to 500 events. New events must be within the synthetic session clock window (one second before start through five seconds ahead of server time); after ending, earlier queued events can still arrive. Each receipt contains ID, accepted/duplicate, stable ordinal and the original received timestamp. Same ID and canonical content returns duplicate, changed content or reuse across sessions returns 409 and aborts the batch. Order for analysis is available by received ordinal. Recovery orders view actions by (occurred_at, id). 401 indicates missing/expired proof, 403 a denied request, 404 disabled or unavailable route, 413 a size cap, 415 wrong media type, 422 invalid contract and 503 unavailable database. Receipts are transmitted after commit.

`GET /api/v1/admin/visitor-reports?start=YYYY-MM-DD&until=YYYY-MM-DD&page=1&limit=25` requires the named Admin session. Dates bound start time in UTC, inclusive start and exclusive until, up to 31 days. Up to 50 session summaries per page, ordered by (started_at, id). Counts reflect the current database snapshot for the filter. `POST /api/v1/admin/visitor-reports/export` takes start/until and format=csv|json with `X-Admin-CSRF`. Export is synchronous and capped at 200 sessions and 10,000 event rows. Reports and attachments are labeled synthetic_local and use allowlisted values, typed IDs and timestamps. CSV uses CRLF and RFC 4180 field escaping. See the [M4 runbook](m4/VISITOR-SESSIONS.md).
