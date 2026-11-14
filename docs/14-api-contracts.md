# API và realtime contracts — foundation + đề xuất M1

14/11/2026. **Chỉ GET /api/health và /api/ready đã triển khai**; docs/OpenAPI FastAPI có thật. Mọi resource/write/WebSocket bên dưới PROPOSED, chưa có endpoint và chưa có auth production.

## Hiện có — status

GET /api/health →200 `{status:"alive",service:"airc-api",timestamp: RFC3339 UTC}`. Liveness chỉ process.
GET /api/ready →200 `{status:"ready",database:"ready",timestamp}` sau SELECT1 thật;503 `{status:"not_ready",database:"not_configured"|"unavailable",timestamp}`. Không trả raw credentials/exception. LỗiHTTP404/validation422/internal500 dùng `{error:{code,message}}`; hiện code HTTP_ERROR/VALIDATION_ERROR/INTERNAL_ERROR và message an toàn, chưa request_id. Readiness503 là status resource, không error envelope. OpenAPI định nghĩa typed status responses.

## Envelope và resources tương lai — PROPOSED

Base /api/v1; bắt buộc UUID stable IDs, schema_version=1, source_kind(synthetic|unknown|real_verified), timestamps RFC3339 UTC cótimezone, version>=1 cho state. Không dùng room507 làm khóa. response object `{data,meta:{schema_version,request_id}}`; lists data array và meta.next_cursor nullable, limit mặc định25,max100, sort stable `(created_at,id)`; cursor opaque bound filter. Không cho client quyết định role/quyền.

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

Các field theo docs13, metadata/payload validate theo loại và reject unknown unsafe fields; không accept arbitrary URL để fetch server-side. Hạn mức dự kiến100events/256KB/batch và body limit256KB; validate ở gateway/app, rate limit theo principal/session. 400 malformed/422schema,401unauthenticated,403forbidden,404unpublished/notfound,409version/idempotency conflict,413size,429rate,503dependency. Error `{error:{code,message,request_id,retryable}}`, không PII/stack trace. Quyền ghi phải kiểm server theo room/object/session và audit; chưa chọn provider/hosting/CORS credentials policy.

## WebSocket — PROPOSED /ws/v1/state

Handshake HTTPS/WSS same-origin, xác thực khi cópolicy, kiểm Origin và room scopes; token không đặt trong query log. Subscribe room_ids giới hạn20/phòng cấp quyền (giới hạn là đề xuất cần review), không client publish state trực tiếp. Envelope:

```json
{"type":"state.updated","schema_version":1,"message_id":"<uuid>","room_id":"<uuid>","object_id":"<uuid>","state_type":"equipment_status","version":4,"value":{"status":"available"},"source_kind":"synthetic","source_observed_at":null,"committed_at":"2026-11-14T00:00:00Z","published_at":"2026-11-14T00:00:00Z"}
```

snapshot: `{type,schema_version,snapshot_id,room_id,watermark,states:[{object_id,state_type,version,value,source_kind,committed_at}]}`. snapshot cóconsistent DBread/watermark; subscriber bufferdelta trong lúc nhận snapshot, sau đó replay >watermark. Paginate/chunk snapshot cóend marker, không ghi UI từng nửa snapshot làm mất data.
resync.required: `{type,reason:"gap"|"expired_cursor"|"backpressure",room_id}`; client fetchsnapshot, không đoán state thiếu. error: `{type,code,message,retryable}` không rawdetails.

Ordering per(object_id,state_type): version<=current bỏ duplicate/cũ; version>current+1 yêu cầu resync; chỉ phiên bản server mới authoritative. Session reconnect exponential backoff+jitter0.5–30s, cócancel lúc unmount/offline; cursor resume nếu server còn window, nếu không snapshot. Window/retention chưa duyệt, không hứa exactly-once. Heartbeat30s, disconnect90s, maxmessage256KB/maxqueue1000 đề xuất; slow consumer chuyểnresync thay queue vô hạn. State value privacy được lọc trước gửi; không đểvisitor subscribe phòng private bằng ID.

Transaction state+history+outbox atomic; worker gửi saucommit rồi markpublished. Publish fail không rollback DB đãcommit: retry bounded exponential, metric backlog, operator reconciliation; publish lại saucrash códuplicate, client version dedupe. Outbox chưa triển khai.

## Đo source-to-render và experience dự kiến

source_observed_at nullable là thời gian nguồn thật đo/cập nhật; committed_atserver, published_atserver, received_atclient, rendered_atclient saucommit scene. Chỉ gọisource-to-render nếu cósource timestamp và độlệch clock biết được; ghi monotonic duration client vàclockoffset/uncertainty. Khi nhập tay, source là thao tác ghi hệ thống, **không phải sensor/API AIRC**. Mục tiêu≤5s chưa được đo/chưa đạt. M1 cần thử latency cóload/độ trễ mạng, không dùngSELECT1 để thay KPI.

Session/event tương lai: stable client event UUID trước send, localoutbox cóconsent/privacy, server dedupe; receipt sauDBcommit, retry không tạodoublecount. Resume token storage/retention/multi-tab/offline policy chưa duyệt, M0-B2 không localstorage tracking hoặc persistence. 99% event/50sessions/90%tasks/15users vẫn chờ nghiệm thu đúngMT1–MT3.
