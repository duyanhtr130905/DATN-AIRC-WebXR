# State + realtime schema M1-B

Cập nhật 14/11/2026. Chủ dự án đã cho phép baseline kỹ thuật M1-B dùng **synthetic**. Revision `0002_state_realtime` nối tiếp `0001_catalog`; không sửa source revision0001, không đổi Catalog columns hoặc seed khi startup/migration. Schema state/session/event dành người tham quan trong phần lịch sử không được coi là đã triển khai toàn bộ.

| Bảng mới | Trường và ràng buộc thực tế |
|---|---|
| current_states | UUID id PK; room_id FK rooms RESTRICT; target_room_id FK rooms nullable, object_id nullable/composite FK(object_id,room_id)→objects(id,room_id); state_type; value JSONB object<=4096bytes; version bigint>=1; source_kind CHECK3giá trị; source_observed_at nullable/committed_at NOT NULL timestamptz |
| state_history | UUID id PK; state_id FK current_states RESTRICT; version/value/source_kind/source timestamps; UNIQUE(state_id,version); JSONB bound; trigger chặn UPDATE/DELETE, không CASCADE |
| room_state_cursors | room_id PK/FK rooms RESTRICT; sequence bigint>=0, được tăng trong business transaction; không dùng PostgreSQL sequence/serial như commit ordering |
| outbox | message_id UUID PK; room_id FK RESTRICT; sequence>=1; event_type='state.updated'; payload JSONB object<=8192bytes; committed_at/published_at/next_attempt_at/lease_until timestamptz; attempts0..5,lease_owner UUID,exhausted; UNIQUE(room_id,sequence); pending index |

Target mapping DB CHECK: room_schedule phải target_room_id=room_id và object_id NULL; equipment_status/exhibit_info phải object_id NOT NULL và target_room_id NULL. Hai unique constraints(target_room_id,state_type)/(object_id,state_type) giữ một current state mỗi loại/target. Unique objects(id,room_id) được thêm trong0002 **để composite FK enforce đúng room scope**, không sửa0001 hoặc hardcode507. Chỉ thêm constraint Catalog cần thiết, không thêm bảng dư.

Value schemas thực thi ở internal service và response validation: equipment_status.status∈available/maintenance/offline; room_schedule.status∈free/occupied/closed và activity1..160chars; exhibit_info.title1..160/text<=800chars. Extra keys bị chặn. DB thêm object/size/type-target/version/FK checks; không coi schema JSON thử nghiệm là nghiệp vụ AIRC đã xác minh. source_kind unknown/real_verified có thể tồn tại làm bản ghi được bảo vệ, nhưng service không sửa và API/WS không công bố chúng. Negative test labels trong database disposable không phải dữ liệu thật.

Business transaction: khóa Room→Object (nếu có)→CurrentState→Cursor, kiểm expected_version (0khởi tạo), tăng version1 và room sequence1, ghi current/history/outbox atomically; CAS UPDATE thêm điều kiện expected version. Rollback không để history/outbox/cursor phát sinh. committed_at là clock_timestamp tại mutation trong transaction, **không phải timestamp WAL COMMIT chính xác**; source_observed_at nullable, không bịa timestamp từ sensor.

Outbox claim lease5s bằng FOR UPDATE SKIP LOCKED, commit claim trước notify; finish theo owner, timeout notify1s, retry backoff2–30s tối đa5claims, exhausted giữ record. Claim bị crash có thể reclaim sau lease; xử lý ít nhất một lần, không exactly-once. published_at là notification đã xử lý/đánh dấu, không phải browser ACK/render. Rows chưa purge; retention/rearm exhausted/production operations cần quyết định sau. Một API process/broker hiện tại; claim concurrency đã test riêng không chứng minh multi-instance broadcast.

Xem [acceptance M1-B](17-m1-b-state-realtime-acceptance.md) và [contract](14-api-contracts.md). Catalog M1-A bên dưới giữ làm lịch sử; session/event visitor, auth, data rights, retention/hosting và phạm vi KPI còn mở.

---

## Lịch sử Catalog M1-A và mô hình đề xuất

# Catalog schema M1-A — đã được cho phép triển khai

Cập nhật 14/11/2026. Yêu cầu M1-A của chủ dự án cho phép baseline **rooms + objects** và Alembic; không phê duyệt toàn bộ mô hình Digital Twin. Migration `0001_catalog`, models ở apps/api/app/database/models.py. Kết quả PostgreSQL thật xem [acceptance M1-A](16-m1-a-catalog-acceptance.md). Phần đề xuất M0-B2 bên dưới là lịch sử, không thay trạng thái hiện tại.

## Catalog thực tế

| Bảng | Trường và constraints triển khai |
|---|---|
| rooms | id UUID PK (stable); code varchar64 UNIQUE NOT NULL/nonblank; name varchar256 NOT NULL/nonblank; source_kind varchar16 NOT NULL/default unknown/CHECK ba giá trị; metadata JSONB NOT NULL/default {}; evidence_ref text nullable; created_at/updated_at timestamptz NOT NULL/default now() |
| objects | id UUID PK; room_id UUID NOT NULL FK rooms.id ON DELETE RESTRICT; name varchar256 và type varchar64 NOT NULL/nonblank; source_kind/metadata/evidence_ref/timestamps như rooms; transform JSONB nullable; external_reference varchar256 nullable |

CHECK source_kind: synthetic, unknown, real_verified. real_verified cần evidence_ref nonblank ở mức DB, **không có nghĩa DB đã xác minh quyền hoặc nội dung bằng chứng**; không có pipeline nhập dữ liệu thật ở M1-A. API chỉ đọc synthetic và parent room cũng synthetic. Seed chính thức chỉ gắn synthetic; một số test âm trên DB disposable dùng source labels khác để kiểm ràng buộc/không công bố, không được coi là dữ liệu AIRC đã xác minh.

Metadata phải là JSON object và kích thước biểu diễn JSONB::text tối đa8192 bytes. Transform nếu có cũng phải object/tối đa8192 bytes, dùng SQL NULL khi chưa biết. Chưa duyệt đơn vị/trục/transform semantics hoặc domain metadata thiết bị; không tự sinh kích thước507. Giới hạn byte là baseline kỹ thuật, không schema khảo sát cuối. API chỉ công bố metadata.label(str<=256) và description(str<=512), bỏ trường lạ/nested/oversized; evidence_ref, external_reference và transform không công bố ở M1-A.

Indexes: ix_rooms_source_id(source_kind,id), ix_objects_room_source_id(room_id,source_kind,id), ngoài PK và unique rooms.code. Không CASCADE; không hardcode507 hoặc giới hạn số phòng. UUID do application/import cấp một lần, không đổi theo code/tên/vị trí. ORM updated_at có onupdate=now(); nếu sau này viết SQL trực tiếp phải cập nhật timestamp trong cùng transaction, hiện không có write API.

## Migration và seed

Alembic1.20.1, initial revision0001_catalog chỉ tạo2bảng, constraints/indexes; không seed, không create_all/startup DDL. CLI chỉ nhận PostgreSQL loopback, database project dev airc_foundation hoặc test airc_test_catalog_*, không query parameters và phải xác nhận đúng database name; kiểm current_database trước online migration. Downgrade phá hủy bị chặn, chưa thử; không DROP/reset DB hoặc xóa volume.

CI tạo database trống tên airc_test_catalog_UUID trên PG service riêng cho từng integration test, chạy upgrade head/current/upgrade head lại/check model drift, test constraints và API. Không dùng SQLite. Base TEST_DATABASE_URL phải là loopback airc_foundation_test và AIRC_ALLOW_TEST_DATABASES=1; không DROP các database, chúng kết thúc cùng CI service.

Fixture có1phòng genericDEMO +4objects, UUID cố định, nhãn SYNTHETIC — NOT AIRC REAL DATA. Lệnh seed riêng có xác nhận DB, transaction và advisory lock; chạy lại idempotent khi fixture khớp, conflict thì rollback không overwrite. Không tự seed khi startup/migration. Đây không phải phòng507, không đạt KPI20objects.

## Chưa triển khai

object_states/state_history/sessions/events/outbox/room_state_cursors và các semantics phía dưới vẫn PROPOSED. Auth, retention, quyền sử dụng, source integration và scope≥3phòng chưa chốt. Chỉ Catalog baseline được cho phép trong M1-A; không tự bắt đầu M1-B/C.

Nguồn kiểm lại14/11/2026: [SQLAlchemy typed declarative](https://docs.sqlalchemy.org/en/21/orm/declarative_tables.html), [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html), [FastAPI yield dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/). Giữ SQLAlchemy2.1.8/FastAPI0.162.7/psycopg3.3.9/Python3.13 đã kiểmCI; bổ sungAlembic1.20.1 (release22/10/2026,Python>=3.10,SQLAlchemy>=2.0,MIT) và Mako/MarkupSafe transitive trong hashlock, không nângbaseline. [PyPI Alembic metadata](https://pypi.org/pypi/alembic/json).

---

## Lịch sử đề xuất M0-B2

# Data model v1 — PROPOSED

14/11/2026. PostgreSQL đã ACCEPTED, **schema chi tiết chưa được duyệt**. M0-B2 chỉ có connection management và SELECT1; không tables/migrations/seed, không create_all. Alembic được nghiên cứu cho migration khi duyệt schema. Không thể coi tài liệu là schema đã hoạt động.

## Những gì biết và chưa biết

Theo người dùng, thầy yêu cầu làm phòng507 trước; chưa khảo sát, chưa số đo/ảnh/inventory/API/quyền dữ liệu. KPI≥3 phòng giữ nguyên. Các trường dưới đây là đề xuất kỹ thuật; metadata thiết bị, quy trình lịch, trạng thái thực, retention/session identity chưa xác định. Demo trong apps/web sourceKind synthetic; không có dữ liệu real_verified.

## Kiểu dữ liệu và quan hệ dự thảo

UUID cấp một lần bởi server/import tool, không dùng vị trí/mã phòng/tên làm PK. external_reference nullable, không thay identity khi đổi tên hoặc chuyển phòng. source_kind enum/check: synthetic, unknown, real_verified; real_verified chỉ khi có evidence_ref và quyền phù hợp. Tất cả timestamps timestamptz, UTC qua API RFC3339. JSONB metadata phải validate theo type, không chứa secrets/PII mặc định.

| Bảng | Trường chính và ràng buộc PROPOSED |
|---|---|
| rooms | id UUID PK; code text UNIQUE; name text NOT NULL; source_kind; metadata JSONB; evidence_ref nullable; created_at/updated_at timestamptz NOT NULL |
| objects | id UUID PK; room_id UUID FK rooms RESTRICT; external_reference nullable; name/type NOT NULL; transform JSONB (chưa chốt đơn vị/trục); metadata JSONB; source_kind; evidence_ref; asset_id nullable; created_at/updated_at |
| object_states | object_id FK objects RESTRICT + state_type composite PK; value JSONB; version bigint CHECK>0; source_kind; source_observed_at nullable; committed_at timestamptz NOT NULL; UNIQUE object_id/state_type/version cho history FK nếu cần |
| state_history | id UUID PK; object_id/state_type FK object_states; version bigint>0; value JSONB; source_kind; source_observed_at nullable; committed_at; UNIQUE(object_id,state_type,version) |
| sessions | id UUID PK; anonymous_resume_token_hash nullable (chưa duyệt cơ chế khôi phục); started_at/last_seen_at/ended_at nullable; source_kind; consent_version nullable; không account/PII trước khi có policy |
| events | id UUID PK do client tạo để retry idempotent; session_id UUID FK sessions; object_id UUID nullable FK objects; event_type; sequence bigint>=0; occurred_at/received_at timestamptz; schema_version; payload JSONB giới hạn; UNIQUE(session_id,sequence) đề xuất, cần chốt semantics offline/multi-tab |

rooms 1→n objects, object 1→n state types/history; session 1→n events. object_id nullable cho event navigation tổng quát. Không hardcode507 hoặc room count; room có thể nhiều. Không tạo20 objects giả để đạtMT1.

Indexes dự kiến: objects(room_id,id), state_history(object_id,state_type,version DESC), sessions(started_at,id), events(session_id,sequence), events(received_at,id). Tránh index JSONB toàn bộ khi chưa có query thật. Delete policy RESTRICT/soft archive cho catalog; retention xóa/anonymize session/events phải duyệt, chưa tự cascade dữ liệu.

## Atomicity và dedupe

State write tương lai: kiểm quyền + expected_version, UPDATE WHERE version=expected, tăngversion; history và outbox cùng transaction. 409 nếu stale. Không overwrite mới bằng message cũ. Duplicate event.id cùng nội dung trả receipt cũ; cùng ID khác nội dung409, unique constraint là hàng rào cuối cùng; hash canonical payload đề xuất. Server nhận batch transaction với giới hạn100events/256KB dự kiến; partial acceptance semantics phải chốt trước triển khai.

Outbox là bảng bổ sung **đề xuất cho M1**, không triển khai M0-B2: id UUID PK, aggregate_key, version, type, payload bounded, committed_at,published_at nullable, attempts,next_attempt_at. UNIQUE aggregate_key/version/type, index unpublished retry. Giải quyết DBcommit thành công nhưng publish lỗi, at-least-once delivery; client dedupe. Không thêm message broker lúc này.

## Gate trước migration

Chủ dự án/giảng viên duyệt schema v1 sau survey: chuẩn object types/trạng thái, ID import, tọa độ/đơn vị, quyền dữ liệu và privacy/retention. Sau đó pin Alembic, review revision SQL PostgreSQL, chạy upgrade database test trống → constraints/index/unique/rollback strategy test → CI. Không auto-generate rồi chạy thẳng vào DB người dùng. Không DROP/RESET/seed real AIRC; backup/restore trước bất kỳ migration có dữ liệu. Migration M0-B2: **NOT RUN**, vì chưa tạo revision, không bị đánh đồng với connection test PASS.

Tham khảo14/11/2026: [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html), [date/time](https://www.postgresql.org/docs/18/datatype-datetime.html), [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html). Các quyết định schema còn PROPOSED dù stack đã ACCEPTED.

### Cursor đề xuất, chưa migration

Để snapshot/delta có ordering kiểm chứng được, phương án ở docs14 thêm bảng dự kiến `room_state_cursors(room_id PK/FK rooms,last_sequence bigint >=0)` và `outbox.room_sequence`, UNIQUE(room_id,room_sequence). Writers khóa counter trong transaction, không dùng serial/timestamp như commit order. Chi tiết và concurrency tests cần duyệt ở M1, không bổ sung bảng thật trong foundation.

M1-A dependency additions (kiểm14/11/2026): Mako1.4.3 release22/09/2026/Python>=3.10/MIT, MarkupSafe3.0.4 release02/10/2026/Python>=3.9/BSD3; dependency transitive bắt buộc của Alembic, pin hashlock và cài thành công trên LinuxCI. [Mako metadata](https://pypi.org/pypi/mako/json), [MarkupSafe metadata](https://pypi.org/pypi/MarkupSafe/3.0.4/json). Các package baseline giữ nguyên.

Làm rõ bounded delivery: retry hữu hạn và lease có thể dẫn tới xử lý trùng; “at-least-once” ở đây mô tả **processing attempts**, không bảo đảm notify thành công cho mọi event. Event exhausted có thể chưa notify thành công lần nào; outbox vẫn giữ dấu vết, client cần resync snapshot. Chính sách/rearm operator chưa triển khai hoặc phê duyệt production, không tự xóa hay retry vô hạn.

## M3 private manual data supplement

Forward-only revision 0003_admin_manual adds named accounts, server-side sessions, a private Catalog overlay and narrow audit refs. Revision 0004_admin_provenance adds nullable provenance and source context to private audit revisions. Existing missing provenance reads as UNKNOWN. Observation rows and events remain in the M1 State/History/Outbox tables with a separate Admin audience. See the [M3 runbook and architecture](m3/P507-M3-INTEGRATION.md).

## M4 — Visitor storage synthetic/local

Revision `0005_visitor_sessions` adds `visitor_sessions` and `visitor_events` as a separate storage boundary. Sessions have server UUID, SHA-256 proof digest, absolute proof expiry, schema version 1, synthetic source, synthetic_local scope, synthetic_opt_in_v1 marker, start/last committed event/end timestamps and event count. Events use a UUID PK, session FK with cascade for explicit synthetic cleanup, version, event type, allowlisted room/object scope, occurred and received timestamps, and unique per-session receipt ordinal. The session row lock shares the transaction with ordinal allocation and event inserts. The (session_id, occurred_at, id) index supports deterministic view recovery. See the [M4 runbook](m4/VISITOR-SESSIONS.md).
