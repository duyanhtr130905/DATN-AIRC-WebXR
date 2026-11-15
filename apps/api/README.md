# M1-B — state và realtime dev runbook

Chỉ project dev/test synthetic, không dữ liệu507 thật. Giữ setup Catalog bên dưới; cài lại requirements.lock có hash (thêm websockets17.4), PostgreSQL18 riêng nếu máy cóDocker. Không tự cài Docker/PG hoặc dùng DB không rõ nguồn gốc.

Từ root D:\Code\DATN, sau khi xác nhận .env/DATABASE_URL trỏ loopback project dev **airc_foundation**:

```powershell
.local/api-venv/Scripts/python.exe -m pip install --require-hashes -r apps/api/requirements.lock
.local/api-venv/Scripts/python.exe -m alembic -c apps/api/alembic.ini -x confirm_catalog_database=airc_foundation upgrade head
$env:PYTHONPATH = 'D:/Code/DATN/apps/api'
.local/api-venv/Scripts/python.exe -m app.modules.catalog.seed --confirm-database airc_foundation
.local/api-venv/Scripts/python.exe -m uvicorn app.main:create_app --factory --app-dir apps/api --host 127.0.0.1 --port 8000 --workers 1 --ws websockets-sansio --ws-max-size 8192 --ws-max-queue 1 --timeout-graceful-shutdown 5
```

0002 nối0001, không seed lúc startup/migration, không create_all hoặc destructive downgrade. Giữ PostgreSQL volume, không reset/drop/prune. Linux dùng .local/api-venv/bin/python. .env thật ignored; không đưa credentials vàoVITE_ hoặc CLI report/Git. `REALTIME_DISPATCHER_ENABLED=false` tạm dừng worker để thử backlog, bật lại và restartAPI sẽ xử lý các lease/pending còn lại; không phải production kill-switch.

## Update synthetic tường minh

Chỉ sau seed generic DEMO Catalog, từ root với PYTHONPATH ở trên:

```powershell
.local/api-venv/Scripts/python.exe -m app.modules.state.cli --confirm-database airc_foundation --room-id 10000000-0000-4000-8000-000000000001 --target-kind object --target-id 20000000-0000-4000-8000-000000000001 --state-type equipment_status --expected-version 0 --value-file apps/api/examples/equipment-available.json
.local/api-venv/Scripts/python.exe -m app.modules.state.cli --confirm-database airc_foundation --room-id 10000000-0000-4000-8000-000000000001 --target-kind object --target-id 20000000-0000-4000-8000-000000000001 --state-type equipment_status --expected-version 1 --value-file apps/api/examples/equipment-maintenance.json
```

JSON file được giới hạn4096bytes và phải resolve bên trong workspace; cách này tránh khác biệt native JSON quoting giữa PowerShell/Linux. Có thể dùng --value cho shell giữ nguyên JSON quoting. Các UUID là DEMO, không phòng507/thiết bị thật. CLI chỉ localhost/127.0.0.1, exactdatabaseconfirmation, dev/test allowlist và không URLquery override. Validation/expectedversion conflict làm rollback, không history/outbox mới. Service change_state phải được gọi trong Session.begin; không commit/publish trước transaction hoàn tất.

Room schedule dùng target-kind room,target-id=room-id,value {"status":"free","activity":"DEMO"}; exhibit dùng object vàvalue {"title":"DEMO","text":"Synthetic"}. Chỉ source_kind synthetic; không sửa unknown/real_verified hoặc hidden parent. Không có public POST/PATCH/DELETE/API admin token.

## Đọc và subscribe

REST: GET /api/v1/objects/{UUID}/states, /api/v1/rooms/{UUID}/states, object state history theo docs14. WS ws://127.0.0.1:8000/ws/v1/state?room_id=10000000-0000-4000-8000-000000000001; client phải gửi Origin http://localhost:5173 hoặc origin đã cấu hình. Browser không tự phát mutation; dùng terminalCLI riêng để tạo update rồi nhận delta. Reconnect nhận freshsnapshot; gap/backpressure/stall cần reconnect, không tự apply message cũ.

Ví dụ Python (một terminal riêng, venv cówebsockets):

```python
from websockets.sync.client import connect

with connect(
    "ws://127.0.0.1:8000/ws/v1/state?room_id=10000000-0000-4000-8000-000000000001",
    origin="http://localhost:5173",
) as ws:
    print(ws.recv(timeout=5))  # snapshot
    print(ws.recv(timeout=10))  # delta hoặc heartbeat sau khi CLI cập nhật
```

MộtAPIprocess duy nhất; không --workers>1 hoặc nhiềuinstance và không tuyên bố multiinstancebroadcast. Chưa auth/hosting/retention production. Không dùng metrics backend thay source-to-render scene.

## Kiểm thử

```powershell
.local/api-venv/Scripts/python.exe -m ruff check apps/api
.local/api-venv/Scripts/python.exe -m compileall -q apps/api/app apps/api/alembic apps/api/tests
.local/api-venv/Scripts/python.exe -m pytest -q -m "not postgres" -c apps/api/pyproject.toml apps/api/tests
```

PostgreSQL suite từ apps/api với TEST_DATABASE_URL chỉbase loopbackairc_foundation_test và AIRC_ALLOW_TEST_DATABASES=1 (service riêng, không DB người dùng): pytest -v -m postgres --junitxml=../../.local/m1-b-postgres.xml. Suite tạo database UUID riêng, kiểm0001→0002 vàM1-A regression; state/writers/rollback/outbox retries/leases; TCP Uvicorn+websockets, snapshotrace/reconnect/gap/queuepressure và DBoutage. Fault injection chỉunique disposable DB: ALLOW_CONNECTIONS false vàterminate đúngdatname, restorefinally. Không DROP/reset database hoặc volume.

.local/m1-b-metrics.json có20samples thật khi test thành công, monotonic timings vàbacklog/retries/subscribers; artifacts chỉJUnit/metrics/browserUI, khôngprofile/credentials. Local thiếuPG ghiBLOCKED; không dùngSQLite thay. [Acceptance M1-B](../../docs/17-m1-b-state-realtime-acceptance.md) ghi actualCI/metrics. Ctrl+C dừngAPI/dispatcher, Docker stop giữvolume.

---

## Runbook Catalog và foundation lịch sử

# Catalog API + Alembic — M1-A

Chạy từ D:\Code\DATN, Python3.13. Giữ setup FastAPI ở phần lịch sử bên dưới; sau npm/frontend không có thay đổi M1-A. Cài hashlock:

```powershell
.local/api-venv/Scripts/python.exe -m pip install --require-hashes -r apps/api/requirements.lock
```

Nếu có Docker, dùng [infra runbook](../../infra/README.md) khởi động PostgreSQL loopback riêng; không tự cài Docker. Copy .env.example → .env, đặt password riêng, DATABASE_URL postgresql+psycopg tới127.0.0.1:55432/airc_foundation. Không dùng DB khác/production. Nếu local khôngPG, unit/offlineSQL vẫn chạy; integration local BLOCKED, dùng CI thật.

## Migration tường minh

Từ root, chỉ sau khi tự xác nhận DB project dev/test của mình:

```powershell
.local/api-venv/Scripts/python.exe -m alembic -c apps/api/alembic.ini -x confirm_catalog_database=airc_foundation upgrade head
.local/api-venv/Scripts/python.exe -m alembic -c apps/api/alembic.ini -x confirm_catalog_database=airc_foundation current
.local/api-venv/Scripts/python.exe -m alembic -c apps/api/alembic.ini -x confirm_catalog_database=airc_foundation check
# Preview SQL không kết nối DB:
.local/api-venv/Scripts/python.exe -m alembic -c apps/api/alembic.ini -x confirm_catalog_database=airc_foundation upgrade head --sql
```

CLI chặn thiếu/sai confirmation, DB ngoài allowlist, host ngoài loopback hoặc query parameters trong URL. Không tự migration/seed lúc startup. Revision0001_catalog chỉ rooms/objects, không dữ liệu AIRC. Downgrade bị chặn; không chạy DROP/reset/down -v. Backup/review riêng trước mọi thay đổi trên DB có dữ liệu; không tự chạy trên DB không rõ nguồn gốc.

## Seed synthetic riêng

Từ root, sử dụng Python venv và đặt PYTHONPATH=apps/api (Linux export tương đương):

```powershell
$env:PYTHONPATH = 'D:/Code/DATN/apps/api'
.local/api-venv/Scripts/python.exe -m app.modules.catalog.seed --confirm-database airc_foundation
```

Một generic DEMO room +4primitive objects, nhãn SYNTHETIC — NOT AIRC REAL DATA. UUID cố định. Transaction/advisory lock; seed lại khớp thì không thêm hàng; collision thì rollback, không overwrite. Không gọi seed trên data thật; không coi fixture là phòng507 hoặc MT1đạt. Không in DATABASE_URL/password trong report.

## Chạy API và kiểm thử

```powershell
.local/api-venv/Scripts/python.exe -m uvicorn app.main:create_app --factory --app-dir apps/api --host 127.0.0.1 --port 8000
.local/api-venv/Scripts/python.exe -m pytest -q -m "not postgres" -c apps/api/pyproject.toml apps/api/tests
.local/api-venv/Scripts/python.exe -m ruff check apps/api
```

GET /api/v1/rooms, /api/v1/rooms/{UUID}/objects, /api/v1/objects/{UUID}. Health/ready/docs vẫn hoạt động; ready200 chỉ chứng minh connection, không thay migration/catalog test. UUID/limit/cursor invalid422, thiếu resource404, DBunavailable503; filters chỉ synthetic, metadata allowlist, không evidence_ref. Không public write endpoints.

PostgreSQL integration từ apps/api: đặt TEST_DATABASE_URL tới **loopback database disposable airc_foundation_test** của dự án và AIRC_ALLOW_TEST_DATABASES=1, rồi chạy Python venv `-m pytest -v -m postgres`. Test role cần CREATE DATABASE; suite tạo airc_test_catalog_UUID mới mỗi test và **không DROP/reset database đã có**. Không dùng URLdev/cá nhân. CI provision base/service riêng và kiểm upgrade từ trống/current/repeat/schema drift/constraints/timezone/API/seed. Không dùng SQLite. Nếu thiếu env, nhóm postgres FAIL có lý do, không skip thành PASS. Chỉ chọn not postgres khi ghi rõ local BLOCKED.

Linux dùng .local/api-venv/bin/python, PYTHONPATH="$PWD/apps/api". Dừng server Ctrl+C, pool dispose; Docker stop giữ volume. Nghiệm thu xem [docs16](../../docs/16-m1-a-catalog-acceptance.md).

---

## Lịch sử hướng dẫn foundation M0-B2

# FastAPI foundation

Python 3.13; chạy từ root `D:\Code\DATN`. Không business tables, DDL hoặc seed. DATABASE_URL là optional để process khởi động; khi thiếu DB, health 200 nhưng ready 503.

```powershell
python -m venv .local/api-venv
.local/api-venv/Scripts/python.exe -m pip install --require-hashes -r apps/api/requirements.lock
.local/api-venv/Scripts/python.exe -m uvicorn app.main:create_app --factory --app-dir apps/api --host 127.0.0.1 --port 8000
```

Linux dùng `.local/api-venv/bin/python`. Copy root `.env.example` thành root `.env` (ignored), tự đặt password riêng theo [infra](../../infra/README.md). Percent-encode ký tự đặc biệt trong DATABASE_URL, không in URL/password vào report/Git. Không kết nối database của người khác.

Kiểm http://127.0.0.1:8000/api/health, /api/ready, /docs, /openapi.json. Factory tạo pool lazy trong lifespan, dispose khi dừng. Readiness SELECT 1 thật; lỗi kết nối/thiếu cấu hình không giả READY. CORS chỉ explicit local origins, không credentials.

## Kiểm thử

Từ root:

```powershell
.local/api-venv/Scripts/python.exe -m ruff check apps/api
.local/api-venv/Scripts/python.exe -m compileall -q apps/api/app apps/api/tests
```

Từ `apps/api`, gọi Python venv bằng đường dẫn tuyệt đối:

```powershell
D:/Code/DATN/.local/api-venv/Scripts/python.exe -m pytest -q -m "not postgres"
# Chỉ khi TEST_DATABASE_URL trỏ PostgreSQL test riêng:
D:/Code/DATN/.local/api-venv/Scripts/python.exe -m pytest -q -m postgres
```

Integration trả FAIL có giải thích nếu thiếu TEST_DATABASE_URL; không tự skip để báo PASS. Khi local chưa có PostgreSQL, ghi BLOCKED và chỉ chạy nhóm unit. CI chạy cả hai nhóm với PG 18.7 riêng. Integration chỉ SELECT, không DDL/drop/reset; SQLite không được dùng thay bằng chứng PostgreSQL. Unit có injected probe thành công/lỗi, khác với PostgreSQL thật.

core/config, database/connection, modules/status đã triển khai. Catalog/state/realtime/experience/reporting/auth chỉ là ranh giới đề xuất trong docs12, chưa có nghiệp vụ. Schema docs13 PROPOSED; chưa tạo Alembic revision nên chưa có migration command. Không gọi create_all. Dừng API bằng Ctrl+C để lifespan đóng pool.


## M1-C: chạy vertical slice synthetic tường minh

Không tự seed/startupDDL. Dùng database dự án dev/test loopback đã xác nhận, migrations0001/0002 giữ nguyên. PostgreSQL18 local nếu có: khởi động cấu hình infra theo hướng dẫn phía trên, không dùng volume của dự án khác và không xóa volume. DATABASE_URL chỉ đặt phía API; không đưa vào VITE_.

Từ apps/api, sau upgrade head và cấu hình DATABASE_URL đúng database dev airc_foundation:

```powershell
python -m app.modules.catalog.vertical_seed --confirm-database airc_foundation
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Seed tạo2phòng generic: phòng thứ nhất20objects/41states, phòng thứ hai1object/3states. Nhãn SYNTHETIC — NOT AIRC REAL DATA. UUID cố định từ namespace synthetic; không507/inventory thật. Rerun không overwrite Catalog mismatch hoặc reset trạng thái đã cập nhật; transaction rollback khi collision. Chọn Synthetic vertical room1 trong web. Guard từ chối thiếuconfirm/nonloopback/URLquery/database ngoàiallowlist.

Dùng GET Catalog để lấy room/object UUID thực; update bằng CLI hiện có:

```powershell
python -m app.modules.state.cli --confirm-database airc_foundation --room-id ROOM_UUID --target-kind object --target-id OBJECT_UUID --state-type equipment_status --expected-version 1 --value-file D:\Code\DATN\.local\maintenance.json
```

File JSON trong workspace có nội dung `{"status":"maintenance"}`; expected_version phải đúng hiện tại. Không publicwriteAPI. Quan sát Panel/mesh đổi và sequence tăng. Room schedule/exhibit cũng synthetic. Restart/reconnect lấy snapshot authoritative, dữ liệu mấtWS đánh stale.

Real browser integration yêu cầu npmci/build apps/web và Chrome sẵn. Chạy suite PostgreSQL như phần M1-A/B; test_vertical_slice_postgres tạo DB riêng theo guard cũ và khởi động realUvicorn/Vite5173/Chrome; không mock happy path. Artifact trong .local/m1-c-browser, không commit profile/cache. Local thiếuPostgreSQL ghiBLOCKED; CI PostgreSQL18 thật bắt buộc.
