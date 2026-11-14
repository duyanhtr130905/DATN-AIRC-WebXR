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
