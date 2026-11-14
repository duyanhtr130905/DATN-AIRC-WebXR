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
