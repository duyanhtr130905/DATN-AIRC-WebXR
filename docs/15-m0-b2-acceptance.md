# Nghiệm thu M0-B2 — nền tảng ứng dụng

Ngày 14/11/2026. Nhánh `feat/m0-b2-app-foundation`, base `3ebd2ec780db80caacd5871ecda911236598f9be`. SHA triển khai và URL CI sẽ được bổ sung sau push; chưa tự merge. M1 NOT STARTED, MT1–MT3 chưa đạt. [Bằng chứng local](evidence/m0-b2-local.json) ghi environment, lệnh, exit code và kết quả thực.

## Checklist

| Mục | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| ADR stack/kiến trúc/UI | PASS | ADR-0001 ACCEPTED theo yêu cầu chủ dự án 14/11/2026; quyết định khác giữ PROPOSED |
| Frontend npm ci/typecheck/build | PASS | exit0; React19/R3F9 baseline; scene lazy; chunk warning >500KB còn mở |
| Frontend unit | PASS | 7 tests, 0 failed; API contract, network/body timeout, health độc lập readiness, chọn object |
| Browser native Chrome + FastAPI thật | PASS | 6 scenarios, report và 3 PNG ở .local/app-browser; không lỗi page runtime trong các luồng đã thử |
| Responsive 390px/desktop | PASS | screenshot đã xem trực quan; touch/focus/no overflow; viewport emulation, không Galaxy thật |
| WebGL unsupported/network failure | PASS | getContext null và route abort được inject, không bằng chứng phần cứng |
| Backend startup/health/ready failure | PASS | pytest 14 passed; browser health200/ready503 not_configured; kết nối thật đến cổng đóng trả unavailable |
| Config/CORS/error/lifecycle | PASS | ruff, compileall; URL/cors validation, safe errors, pool return/dispose; readiness success unit là mock |
| PostgreSQL local | BLOCKED | không Docker/PostgreSQL local; không tự cài |
| PostgreSQL CI thật | NOT RUN | chờ GitHub job với PostgreSQL18.7 riêng; không dùng SQLite |
| Migration/schema constraints | NOT RUN | schema chi tiết PROPOSED, chưa tạo revision; không DDL/seed/create_all |
| CI mới và hồi quy trên GitHub | NOT RUN | chờ workflow thực, local không thay CI |
| Security/verifier/internal links | PASS | 115 files,121 links; secret patterns và generated/env checks; không phải full security audit |
| Whitespace/YAML | PASS | git diff --check exit0; PyYAML6.0.3 BaseLoader parse 3 workflows và Compose |
| Documentation | PASS | docs12–14, ADR, runbooks; lịch sử nghiên cứu giữ nguyên kèm cập nhật quyết định |
| M0-A local regression | PASS | 10 Node,8 Python,3 browser scenarios exit0 |
| PoC A/B local regression | PASS | mỗi PoC build/typecheck +6 shared tests; 8 browser scenarios gồm IWER lifecycle/input sources |
| AR Galaxy/iPhone/VR kính/FPS/KPI | NOT RUN | thiếu thiết bị/survey/load test; không tuyên bố đạt |

## Môi trường và lệnh

Local Windows11 10.0.26300; Node22.16.0/npm11.10.1; Python3.13.2; Chrome157.0.8103.51 headless ANGLE software WebGL. Chưa đo FPS/latency. Lệnh tái lập trong [web](../apps/web/README.md), [API](../apps/api/README.md), [infra](../infra/README.md); commands/exit0 trong evidence JSON. Browser thực tạo ảnh desktop/mobile390/unsupported, chỉ giao diện ứng dụng, không profile/private data. CI upload artifact14ngày.

App browser scenarios: scene+health API thật, DB chưa cấu hình; mouse ray pick/keyboard/reset; 390px touch/focus/no overflow; injected WebGL2 unsupported; lỗi readiness không làm mất trạng thái backend alive; lỗi toàn API hiển thị retry. Không XR mock trong ứng dụng, không AR/VR session hoặc camera.

## Lỗi đã sửa và review

Browser lần đầu FAIL do selector mojibake khi đọc file cp1252; sửa UTF-8 và chạy lại PASS. Independent review tìm root runner sai trước khi chạy, đã sửa ../../.. và guard trước mkdir; chỉ xóa đúng tên ảnh/report runner sở hữu để không dùng ảnh cũ. Redact validation input; tách health/readiness; timeout bao cả body. Reviewer độc lập thử server loopback gửi headers nhưng treo body, timeout100ms đã reject và server đóng sạch. Không còn P1/P2 được phát hiện trong phạm vi review, không thay review độc lập của ChatGPT.

## Giới hạn và gate

Chưa business CRUD, admin/auth, session persistence/tracking/export, WebSocket production, AI/RAG, assets507 hoặc hosting. Schema/migration/outbox, auth provider, retention/quyền dữ liệu, phạm vi≥3phòng và VR acceptance chờ duyệt. Issues#1–#5 giữ mở. Mock/headless/emulator không thay hardware test. TestClient có warning httpx deprecation hướng sang httpx2; tests hiện vẫn chạy, không tắt warning. Chunk3D cần budget/asset optimization ở M1, không suy ra30/72FPS.

Đề xuất M1 sau review: duyệt schema dựa survey507; migration và PostgreSQL constraint tests; catalog read API + adapter có provenance; state version/history/outbox và instrumentation latency; kiểm Galaxy thật riêng. Chưa tự triển khai M1.
