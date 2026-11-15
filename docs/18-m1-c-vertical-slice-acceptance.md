# Nghiệm thu M1-C — Synthetic Digital Twin vertical slice

Ngày 15/11/2026. Một branch `feat/m1-c-digital-twin-vertical-slice`, một PR vào main; không merge/deploy hoặc bắt đầu milestone sau. C1 → C2 → C3 được triển khai tuần tự sau gate kiểm thử, có checkpoint riêng.

## Kết luận và phạm vi bằng chứng

M1-C sẵn sàng review với PostgreSQL thật → FastAPI → REST/TCP WebSocket → Chrome WebGL → React/R3F → Information Panel. Dữ liệu hoàn toàn synthetic, không phải phòng507. **Không nghiệm thu KPI MT1–MT3 hoặc KPI≥3phòng.**

Snapshot evidence được chốt tại source `09f3e23ecde864e33763881a6ab2806d4564bbec`. Commit bàn giao theo sau chuẩn hóa định dạng source và tài liệu; kết quả trên HEAD cuối xem Checks/artifacts của PR. Không gọi snapshot evidence cũ là benchmark của một HEAD khác.

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| C1 scalable/atomic snapshot | PASS | Protocol2,0/1/32/33/41/80/120states;513capacity reject; PostgreSQL/TCP và unit malformed cases |
| C2 Catalog/UUID/scene/state | PASS |20objects,41states, scene pick, CLI update, Canvas pixels/Panel, room switch |
| C3 real E2E | PASS |16browser scenarios,20render samples; không mock happy path |
| Backend unit/config/guards | PASS |70tests, exit0 |
| PostgreSQL18 migrations/Catalog/state/outbox/concurrency/TCP/browser | PASS |67tests,0failure/0error/0skip, exit0; JUnit artifact |
| Frontend typecheck/build/unit | PASS | npmci/build/typecheck,25tests, exit0 |
| M0-B2 browser regression | PASS |7scenarios, desktop/390px/WebGL fallback/backend errors |
| M0-A regression | PASS |10Node +8Python runner tests và browser smoke |
| PoC A/B và IWER | PASS | Cả hai build/domain suites và8browser scenarios; không sửa experiments |
| Links/secret patterns/whitespace | PASS | verifier và git diff --check, exit0; đây là pattern scan, không phải security audit toàn diện |
| Local PostgreSQL | BLOCKED | Máy không có Docker/PostgreSQL; không tự cài, không dùng SQLite thay bằng chứng |
| Galaxy AR/VR vật lý/hardware presentation | NOT RUN | Không thiết bị/method được kiểm thử; viewport390px không phải Galaxy |
| Dữ liệu/quyền/mô hình thật507 | BLOCKED | Chưa khảo sát/inventory/ảnh/kích thước/nguồn/quyền |

## CI và artifact có thể kiểm tra lại

Source09f3e23:

- [Application/PostgreSQL/Chrome](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376007).
- [M0 regression](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376107).
- [PoC A/B + IWER](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376051).
- [JUnit, raw report và ảnh thật](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376007/artifacts/14146130518): `m1-b-postgres.xml` giữ tên lịch sử; `m1-c-browser/report.json`, desktop/mobile-390/unsupported-live và canvas-available/canvas-maintenance PNG. Không chứa browser profile/cache.
- [Snapshot JSON trong repository](evidence/m1-c-validation.json) giữ source SHA, raw20samples, clock calibration, frame intervals, bundle sizes và scenario results. Ảnh đã tải và xem trực quan; desktop chụp sau functional updatev2, mobile sau measurementv22.

Các command CI thực sự chạy: `npm ci --ignore-scripts --prefix apps/web`; `npm run build --prefix apps/web`; `npm test --prefix apps/web`; `npm run test:browser --prefix apps/web`; `python -m ruff check apps/api`; `python -m compileall -q apps/api/app apps/api/alembic apps/api/tests`; unit pytest; `python -m pytest -v -m postgres`; verifier và diff check. Tất cả exit0 trên source trên. Workflow giữ permissions contents:read, action SHA pins, Python hashlock, PG18.7 service riêng; không secrets thật/deploy/auto-merge.

## C1 — Snapshot protocol và scalability

V1 mặc định giữ snapshot đơn≤32states để client M1-B không âm thầm đổi wire contract. V2 opt-in `?protocol=2`, mọi envelope schema_version2: snapshot.start → snapshot.chunk → snapshot.end. Common fields: message_id, snapshot_id, room_id, watermark, sequence=watermark, timestamp. Start/end có totals, chunk có index liên tiếp và public DTOs.

Giới hạn512states/2MiB snapshot,16states/chunk,32KiB/frame; safe JavaScript integers. Đọc cursor/rows trong một PostgreSQL REPEATABLE READ READ ONLY view, đóng DB trước network. Subscriber đăng ký trước đọc; outbox replay sau watermark đóng khoảng trống snapshot→delta. Queue8wakeups coalesce, không chứa delta vô hạn; replay bounded32/batch, gap/backpressure/stalled outbox dẫn resync.32connections/process; send timeout1s.

Revalidate parent/source từng chunk và toàn bộ IDs trước end. Nếu visibility đổi, abort staging; không thể thu hồi bytes đã gửi và không cam kết revocation tức thời sau check cuối. Client chỉ swap state sau end đủ totals/index/scope/IDs; missing/duplicate/reordered/wrong-watermark/disconnect không hiển thị partial snapshot. TCP fault tests bổ sung corruption thật qua transport; unit tests kiểm các malformed envelopes chi tiết. Race writer khi gửi chunk vẫn nhận durable delta sau watermark. Migrations0001/0002 không đổi.

## C2 — Kiến trúc tích hợp

REST DTO validators kiểm UUID/source/timestamps/value/public metadata. Pagination keyset tới null, chặn repeated cursor/duplicate ID/empty page có next, max32pages/512rows; abort/timeout bao gồm response body. Scene render tối đa100objects, UUID làm React key và selection identity. Layout sorting deterministic với cùng inventory, không phải transform đo đạc; inventory đổi có thể đổi vị trí và cần tải lại Catalog.

Reducer thuần, server-authoritative: old/duplicate sequence bỏ; sequence+1 và state version+1 mới apply; forward gap/version inconsistency gây resync. Snapshot authoritative thay toàn bộ states, room switch reset scope và callback cũ bị generation guard. Retry tốiđa12attempts với exponential backoff/jitter, watchdog10s và cleanup; hết budget cần người dùng tải lại.

Defaultlive không âm thầm dùng hardcoded fixture khi API lỗi. Offline foundation DEMO được chọn riêng qua `/?mode=offline`. Loading/no-room/no-object/backend/DB unavailable/connecting/synchronizing/connected/stale/reconnecting/resync/WebGL fallback hiển thị riêng. Mouse raypick, keyboard và touch qua danh sách; responsive390px; XR tương thích baseline nhưng không tự mở session/camera. Equipment status đổi material của mesh thật, không chỉ DOM text.

## C3 — Kịch bản end-to-end

16scenario groups kiểm tra: empty DB; explicit guarded seed/idempotency; UUID Catalog/41states/Canvas; actual raypick; CLI→commit→WS→Panel/material/pixels;20samples; duplicate/old/gap injection; actual socket disconnect/stale/reconnect; room switch/keyboard; empty-room/zero-state snapshot;390px touch; injected WebGL failure; public DTO/no write endpoints; actual disposable DB outage/503/recovery; frame/network/bundle observations; actual backend shutdown/no fallback.

Fault injection được gắn nhãn trong report: duplicate/gap đưa lại message vào read-side test hook; WebGL context unavailable; socket close; PostgreSQL ALLOW_CONNECTIONSfalse + terminate connections chỉ unique disposable DB; backend owned by test được dừng. Đây không phải dữ liệu mock cho happy path. Parent/helper/Node đều có restore/cleanup khi fault lỗi một phần; timeout180s và test-owned process tree cleanup, không chạm process/profile cá nhân. Không DROP/reset/destructive migration.

## Phép đo và kết quả source09f3e23

Linux CI, Python3.13, PostgreSQL18.7, Chrome157.0.8103.50, software ANGLE WebGL2, một API process,20synthetic objects.20samples không lỗi/timeout. p50/p95 dùng **nearest-rank** `ceil(n*p)-1`, max là mẫu lớn nhất; không phải median trung bình hai giá trị ở n chẵn.

| Chỉ số | p50 ms | p95 ms | max ms |
|---|---:|---:|---:|
| Node CLI-start → mapped Three afterRender |1311.916|1552.365|1588.791|
| Python transaction tới commit-return |78.225|118.369|125.955|
| Browser WS received → afterRender |27.500|106.700|136.000|
| Browser requestAnimationFrame intervals (90samples) |50.000|83.400|116.700|

Reconnect quan sát812.312ms. Browser page18requests/9socket creations qua các lần reconnect/đổi phòng, không polling storm; chỉ5assets được tải, không tải emulator/example-room chunks. Bundle raw bytes đầy đủ trong JSON; scene chunk khoảng1.08MB trước gzip là known optimization concern, không phải build failure.

`t0` là Node hrtime trước spawn guarded CLI, gồm Python startup. CLI đo transaction duration bằng perf_counter cùng process. `t1` commit được map sang khoảng bảo thủ bằng spawn/commit-ack ordering, không lấy origin Python trừ origin Node trực tiếp. `t2` WS receive, `t3` React layout-effect sau commit, `t4` Three onAfterRender sau draw submission, đều có raw browser performance.now.

12request/reply calibration trước và sau; dùng hull hai bounds cộng allowance1ms, endpoint drift budget10ms. Run này drift0.107ms, width bounds2.779ms (xấp xỉ±1.390ms). Interval ước lượng giả định clock rate ổn định trong cửa sổ; không khẳng định đồng bộ clock hoàn hảo. Mỗi mẫu có Python commit interval và commit→render bounds riêng. t4 là20material/draw observations; pixel trước/sau kiểm một update đại diện. Không chứng minh hardware scanout hoặc source-to-render AIRC≤5s; rAF intervals không phải FPS Galaxy/VR.

M1-B đo service→TCP client cùng process/loopback, không gồm CLI startup/Chrome/render và dùng median ở p50. Hai môi trường/phương pháp khác nhau: chỉ đối chiếu ranh giới đo, không gộp distribution hoặc suy ra cải thiện hiệu năng.

## Cách chạy local và tái lập

1. Dùng PostgreSQL dự án local đã xác nhận; xem [infra](../infra/README.md), không cài Docker tự động, không xóa volume.
2. Cài API hashlock và web npmci theo [API](../apps/api/README.md)/[web](../apps/web/README.md).
3. Trong apps/api, đặt DATABASE_URL đúng dev loopback `airc_foundation`; chạy `python -m alembic upgrade head` tường minh.
4. `python -m app.modules.catalog.vertical_seed --confirm-database airc_foundation` tạo20objects/41states ở phòng đầu và1object/3states ở phòng thứ hai, không seed khi startup.
5. Khởi động FastAPI factory ở127.0.0.1:8000; Vite dev ở127.0.0.1:5173. Origin allowlist giữ đúng trang thật, không wildcard. Chọn Synthetic vertical room1.
6. Lấy UUID từ Catalog/Panel; chạy guarded state CLI với expected_version và fileJSON workspace `{"status":"maintenance"}` như API runbook. Quan sát Panel/mesh đổi; ngắtWS thì stale, nối lại snapshot.
7. Tái lập CI tests cần TEST_DATABASE_URL base `airc_foundation_test`, allowflag và quyền tạo database riêng; test tự tạo unique DB, không migration lên DB người dùng. C3 build test cần VITE_TEST_DIAGNOSTICS=1 và Chrome sẵn. Mọi artifacts nằm .local ignored.

## Giới hạn và quyết định còn mở

Chưa khảo sát/GLB/quyền dữ liệu507, auth/hosting/retention, multi-instance, public mutation/admin, visitor session/event persistence, reports50sessions, Guided Tour đầy đủ, AI/RAG và production AR/VR. Không thay KPI≥3phòng; Issues1–5 giữ mở. Dữ liệu thật/provenance/transform và phương pháp nghiệm thu VR cần chủ dự án/GVHD phê duyệt. Đề xuất tiếp theo là khảo sát507, chốt quyền/mapping dữ liệu và kế hoạch tối ưu asset; chưa bắt đầu milestone mới.
