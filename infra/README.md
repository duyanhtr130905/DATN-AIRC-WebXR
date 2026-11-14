# Hạ tầng phát triển cục bộ

Không tự cài Docker. Nếu máy có Docker: copy root `.env.example` thành root `.env` (ignored), tự đặt POSTGRES_PASSWORD riêng; Compose chặn password rỗng. Từ root:

```powershell
docker compose --env-file .env -f infra/compose.yml config --quiet
docker compose --env-file .env -f infra/compose.yml up -d
```

PostgreSQL 18.7 bind `127.0.0.1:55432`; project `datn-airc-foundation`, volume `airc_foundation_pg18` dành riêng. Không privileged, không mount ổ C/D. Set DATABASE_URL trong `.env` theo mẫu, percent-encode password; khởi động lại API để nhận config. Kiểm `/api/ready` trước khi dùng DB.

**Migration NOT RUN:** chưa có revision vì schema chi tiết chưa được duyệt. Không chạy create_all hoặc seed; sau duyệt v1 mới thêm Alembic và test upgrade database trống.

Dừng an toàn: `docker compose --env-file .env -f infra/compose.yml stop`. Có thể down container/network khi cần, **không dùng down -v**, không xóa volume. Ctrl+C API/Vite riêng. Không prune/reset/DROP, không tắt service khác nếu cổng đang bận.

Nếu thiếu Docker/PostgreSQL: backend vẫn chạy health200/ready503, unit/build/browser không DB vẫn kiểm được; integration PostgreSQL local BLOCKED. CI dùng PostgreSQL service độc lập. Không deployment hoặc production secrets.
