# Nghiệm thu M1-B — State management & realtime

Ngày 14/11/2026, [PR#10](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/10), branch feat/m1-b-state-realtime từ M1-A merge 99f65377746a0eb7c924b6493db3a8e4680a444d. Source/test/workflow commit đã kiểm **320c3bc76568733838b3cd75e1ad1853f75fd161**; follow-up chỉ chốt tài liệu/evidence. Latest HEAD checks xác minh trước bàn giao. Không merge/deploy/M1-C.

## Checklist theo bằng chứng thực

| Hạng mục | Kết quả | Bằng chứng / giới hạn |
|---|---|---|
| Migration0001→0002 trên PostgreSQL18.7 | PASS | Catalog được giữ, current/history/cursor/outbox mới, schema drift check; SHA0001 bất biến lưu trong evidence |
| Constraints/FK/unique/JSONB/timestamptz | PASS | target mapping, composite room/object FK, version, unique history/outbox sequence; immutable history trigger; RESTRICT |
| Synthetic state service | PASS | ba loại state đúng target; expected_version=0 create; version tăng 1; protected unknown/real_verified và hidden parent bị từ chối |
| Concurrent/stale/duplicate update | PASS | hai writer PostgreSQL thật: một thành công, một conflict; không history/outbox dư |
| Atomic rollback / no precommit publish | PASS | current/history/outbox/cursor rollback; actual TCP client không nhận delta trong transaction chưa commit hoặc sau rollback |
| State REST và history | PASS | typed responses, pagination/order,UUID/404/422/source/parent filters, không private metadata/evidence hoặc public write |
| Outbox claim/retry/crash | PASS | SKIPLOCKED claim commit, concurrent owner claims, lease expiry/recovery/finish; publisher failure5attempts→exhausted, business state không rollback |
| WebSocket TCP thực | PASS | Uvicorn SansIO +websockets client: snapshot/update, reconnect, snapshot-subscribe race, out-of-order/gap, queue-pressure resync, wrongOrigin/room/hidden parent, no client writes |
| Publisher pause/restart/backlog | PASS | dừng actual dispatcher, commit thay đổi, restart xử lý tồn đọng; durable outbox không mất |
| Database disconnect/outage | PASS | terminate backend rollback; WS safe error khi unique disposable DB bị chặn kết nối, restorefinally và reconnect snapshot thành công |
| Cleanup/shutdown | PASS | subscriptions/receive task/server thread/listener vàpool scopes được dọn; startup failure cófinally; unit fault injection stop lỗi vẫn dispose |
| Backend lint/import/unit | PASS |38 unit,ruff/compileall/import exit0; TestClient/httpx warning giữ nguyên |
| PostgreSQL suite | PASS |47 passed,0 failure,0 error,0 skipped; actual JUnit artifact đã tải kiểm |
| Frontend/M0-A/PoC A+B regression | PASS | web typecheck/build/7unit/6browser; M0 checker vàhai PoC build/domain/WebGL/IWER; source frontend không đổi |
| Secret/internal links/whitespace | PASS | verifier,git diff --check; không phải full security audit |
| Local PostgreSQL | BLOCKED | không có Docker/PG, không tự cài hoặc dùngSQLite thay bằng chứng |
| PhysicalAR/VR/source-to-render KPI | NOT RUN | không scene render integration hoặc thiết bị thật, chưa dữ liệu507/quyền |
| Multi-instance/production auth/deploy | NOT RUN | prototype chỉmột API process, không hỗ trợ broadcast đa-instance hiện tại |

## Schema, transaction và delivery semantics

[Model chi tiết](13-data-model.md), [REST/WS contracts](14-api-contracts.md), [runbook](../apps/api/README.md). Revision0002 tạo4 bảng, thêm UNIQUE objects(id,room_id) cho compositeFK scope, giữ0001 source bất biến. room_schedule→Room; equipment_status/exhibit_info→Object. Value schemas chỉbaseline thử nghiệm synthetic, không nghiệp vụ AIRC đã xác minh.

Khóa theo Room→Object→State→Cursor, kiểm expectedversion và CAS, ghi current/history/outbox/cursor trong cùng business transaction. Caller phải dùng Session.begin; service không commit/publish. committed_at là DB mutation timestamp trong transaction, không WAL commit chính xác. SQLAlchemy version_id_col không được coi là bảo vệ bulkSQL; service kiểm version rõ ràng bằng điều kiện SQL và locks.

Claim outbox bằng FOR UPDATE SKIP LOCKED, commit lease 5s trước notify. Broker RAM chỉ wake hint; finish kiểm owner, retry hữu hạn5 claims/backoff 2–30s/exhausted, không xóa event. Lease expired có thể xử lý lại; **at-least-once notification processing, không exactly-once hoặc clientACK**. published_at không chứng minh browser/render đã nhận. Retention/rearm exhausted/production monitoring chưa được chọn.

Register trước snapshot REPEATABLE READ/cursor nhất quán; đọc durable published tail sau watermark. Gap, quá32 delta hoặc publication đình trệ>2s →resync.required/close1013; reconnect lấy fresh authoritative snapshot. Queue hints trùng không đổi cursor; reference consumer ignore old/duplicate vàresync gap đã được thử với các delta TCP thực được nhận. Frontend reducer chính thức chưa triển khai.

Bounded prototype:32 connections/process,8 wake tokens/client,32 states/snapshot,32 deltas/replay,256 KiB outgoing,sendtimeout1s; Uvicorn incoming8KiB/queue1 trong test/runbook. Queue-pressure fault injection khác benchmark mạng chậm vật lý (NOT RUN). SQL sync chạy to_thread với connection scope ngắn, không giữ DBconnection suốt WS session. Single-process broker, claim-worker race test không đồng nghĩa multi-instance broadcast.

## CI và evidence

[Bản ghi SHA/lệnh/exit codes/tên47tests/raw20 samples](evidence/m1-b-validation.json). Các run trên source đã kiểm:

- [Application + state/realtime CI](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43585383896):2 jobs PASS,38 unit+47 PG tests vàfrontend/browser.
- [M0-A regression](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43585383828):2 jobs PASS.
- [PoC A/B + IWER](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43585383771):3 jobs PASS.
- [Push CI cùng source](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43585380097):2 jobs PASS.
- [JUnit + metrics artifact](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43585383896/artifacts/14109659900), [browser report/ảnh](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43585383896/artifacts/14109837373),14ngày; không profile/credentials.

CI tạo database UUID riêng theo guard M1-A, không làm hỏng test factory. Test outage chỉ database prefix UUID đã xác minh, lọc PID đúng datname và restore trongfinally. Không DROP/reset DB/volume; destructive downgrade bị chặn. Các assertion cũ chỉ đổi exacthead/tables từ0001/2bảng sang0002/6bảng, giữ toàn bộ Catalog coverage. Không skip hoặc xóa test để xanhCI.

## Metrics thực đo —20 samples, đơn vị ms

Linux CI7.0.0-1014-aws, Python3.13.18, PostgreSQL18.7 Debian, Uvicorn0.54.0, một API process, mộtTCPclient loopback cùnghost, primitive synthetic state. Mẫu được cập nhật tuần tự sau khi nhận delta trước; không load/capacity benchmark.

| Phép đo | p50 | p95 (nearest rank, n=20) |
|---|---:|---:|
| Service transaction (bao gồm commit trả về) | 6.389 | 7.670 |
| Commit-return → notification | 44.990 | 93.203 |
| Notification → TCP client nhận | 257.763 | 258.714 |
| Update start → client nhận | 308.874 | 357.626 |

Dùng monotonic_ns trên cùng process/test host. Transaction duration bao gồm validation/SQL/commit trả về; commit-return là proxy sau commit, không timestamp WAL chính xác. Publish trong phép đo là broker notification được enqueue, trước mark-published SQL; notification→client bao gồm persistence/replay/polling/WebSocket/TCP. DB mutation→published_at riêng dùng clock DB, raw số có trong JSON. Không clip số hoặc chuyển thành source-to-render.

Backlog cuối0, retry count0 trong lượt stream bình thường; subscriber đo thực tế1 khi stream và0 sau disconnect. Failure/retry/cap5 kiểm riêng trên database disposable khác, không trộn vào20 samples latency này. N20 chỉ mô tả một lượt CI, không đại diện Galaxy/Quest, multi-instance, production hoặcKPI≤5s. M1-C mới có render timestamp scene.

## Review và phần còn mở

Review độc lập đã phát hiện và xác nhận sửa: latest exhausted event giữWSstale, stopfailure ngăn pooldispose, startup fixture khôngcleanup. CLI thêm project-local value-file bound 4096 bytes để tái lập trênWindows/Linux; DB confirmation/loopback/query-override guards vẫn giữ. Test async/publicationfailure/queuepressure có fault injection được ghi riêng, không gắn nhãn mock thành PostgreSQL/TCP thật. Không có CI FAIL trong các run source đã liệt kê; lỗi local mocked-engine regression ban đầu đã sửa bằng không chạy worker khi chưa cấu hình DB và cleanupfinally.

Nguồn kiểm 14/11/2026: [SQLAlchemy versioning](https://docs.sqlalchemy.org/en/21/orm/versioning.html), [PostgreSQL locks](https://www.postgresql.org/docs/18/explicit-locking.html), [FastAPI WS](https://fastapi.tiangolo.com/advanced/websockets/), [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [websockets metadata](https://pypi.org/pypi/websockets/json), [sync client docs](https://websockets.readthedocs.io/en/stable/reference/sync/client.html). Giữ baseline packages; thêmwebsockets17.4 release30/10/2026/Python>=3.11/BSD3, hashlock/càiCI. Stable docs đang hiển thị17.3; API17.4 vàUvicornSansIO được xác minh bằngactualTCP47tests, không giả định chỉ từdocs. Uvicorn website fetch timeout, không coi trang đó là nguồn đã đọc.

Dữ liệu507/source/quyền/inventory/survey chưa có, KPI≥3phòng vàMT1–MT3 giữ nguyên/chưa nghiệm thu. Auth/writeauthorization, retention, hosting, full domain metadata, VR acceptance vẫn PROPOSED/chưa chốt; Issues#1–#5 mở. Khôngvisitor session/event tracking, adminproduction, AI, public write, sceneintegration hoặcdeploy. M1-C đề xuất sau phê duyệt riêng: Catalog+state adapters/reducer/snapshot-resync trong scene, loading/error/reconnect UI và render timestamp thực; chưa bắt đầu.
