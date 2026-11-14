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
