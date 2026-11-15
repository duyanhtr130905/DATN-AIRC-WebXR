# Quy tắc làm việc — DATN AIRC WebXR

## Phạm vi và an toàn

- Root duy nhất: `D:\Code\DATN`. Remote duy nhất được phép ghi: `https://github.com/duyanhtr130905/DATN-AIRC-WebXR.git`.
- Không truy cập, đọc, chỉnh sửa, sao chép, fork hay dùng dữ liệu/mã/tài liệu của KLTN-Factory-Agentic-DT. Không dùng repository cũ làm template.
- Trước mọi thao tác ghi GitHub: kiểm tra `Get-Location`, `git rev-parse --show-toplevel`, `git remote -v`, `git branch --show-current`, `git status --short`, diff và secret. Sai root/remote thì dừng.
- Không force push, merge PR, xóa nhánh/repo, thay visibility, deploy hoặc bắt đầu M1 nếu chưa được yêu cầu. Không sửa Git global config; không cài công cụ hệ thống nếu không cần.
- Lịch sử: M0-A chỉ tài liệu và checker; task M0-B1 ngày 14/11/2026 cho phép hai PoC cô lập trong experiments/ và test tooling dùng dữ liệu synthetic. Giới hạn lịch sử M0-B1; task M0-B2 ngày 14/11/2026 đã duyệt nền tảng chính thức apps/web, apps/api, infra. Stack/Modular Monolith/UI theo ADR-0001 ACCEPTED. Schema chi tiết/auth/hosting/retention/quyền dữ liệu/nghiệm thu VR vẫn chưa duyệt; không thay KPI, không triển khai M1 hoặc AI/RAG.

## Nguồn thông tin và quyền tiếp tục hiện hành

- [ROADMAP](docs/ROADMAP.md) là nguồn roadmap duy nhất; [PROJECT_STATUS](docs/PROJECT_STATUS.md) ghi hiện trạng và bằng chứng. Roadmap **PROPOSED không phải quyền tự triển khai**; không suy ra M0–M8 đã được phê duyệt.
- Chỉ thực hiện task được chủ dự án phê duyệt, trong phạm vi và DoD đã chốt. Không tự bắt đầu M2/M3 hoặc milestone tiếp theo sau khi PR trước merge.
- Không tự đổi tên, thứ tự hoặc nội dung milestone đã duyệt. Đề xuất thay đổi phải ghi riêng và chờ phê duyệt, không sửa KPI hoặc chia P507 thành ba phòng.
- Sau mỗi PR đã được nghiệm thu, cập nhật PROJECT_STATUS: kết quả, PR/HEAD, merge commit nếu có, evidence, giới hạn, blocker và bước tiếp đã được phép. Khi chưa nghiệm thu phải ghi IN REVIEW; merge kỹ thuật không đồng nghĩa KPI đạt.
- Nếu tài liệu mâu thuẫn, báo chủ dự án kèm nguồn, thời điểm và tác động; không tự chọn một cách hiểu, sửa quyết định hoặc dùng kế hoạch lịch sử làm quyền triển khai. Giữ nguyên acceptance/evidence lịch sử và dẫn trạng thái hiện tại.
- Task 15/11/2026 hiện hành chỉ chuẩn hóa bốn tài liệu trên branch `docs/project-roadmap-source-of-truth`, một PR vào main. M1-C DONE, PR #11 merged tại `33ba38b00e2d6c218c1ab97ba1cc7201d1e92a58`; chỉ prototype synthetic. Dừng sau bàn giao PR tài liệu; không merge, không thay mã nguồn/schema/API/dependencies/assets/CI và không bắt đầu milestone mới.

## Quy trình

1. Trước mọi task, đọc `docs/ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/02-requirements-kpi.md`, task hiện hành và các ADR liên quan; đọc README để tìm runbook, giữ thay đổi người dùng.
2. Branch theo task; M0-A dùng `docs/m0-foundation`; M0-B1 dùng `feat/m0-b1-renderer-poc`, M0-B2 dùng `feat/m0-b2-app-foundation`; PR vào `main`. Commit nhỏ, mô tả đúng nội dung.
3. Ưu tiên nguồn chính thức; ghi URL, ngày truy cập, phiên bản và giới hạn. Ghi VERIFIED/PROPOSED/BLOCKED/NOT TESTED đúng nghĩa.
4. Chỉ sửa trong phạm vi task. Thay đổi kiến trúc đã duyệt cần ADR và phê duyệt mới; không ghi ACCEPTED khi chưa có người duyệt.
5. Test tương xứng; `node --check tools/webxr-capability-check/checker.js`, `node --test tools/webxr-capability-check/tests/checker.test.cjs`, `python tools/verify_repository.py`, `git diff --check`. Chạy browser smoke khi có môi trường.
6. Không giả mạo kết quả: test mock khác browser thật, emulator khác kính, capability khác AR session. Test không chạy ghi NOT RUN và lý do; thiết bị không có ghi NOT TESTED.
7. Không commit ảnh/người/serial, token, `.env`, raw survey hoặc session có định danh. Cất dữ liệu thực hạn chế quyền ở nơi được AIRC chấp thuận, ngoài Git.
8. Cập nhật status, acceptance, evidence; kiểm tra link, diff và secret trước commit/push. Tạo PR có summary, files, findings, tests, limitations, questions và next milestone proposal. Không tự coi review AI là phê duyệt của giảng viên/người dùng.

## Kiểm tra ứng dụng chính thức

Xem apps/web/README.md và apps/api/README.md. Build/typecheck/unit/browser frontend; ruff/compileall/pytest backend. Test PostgreSQL yêu cầu TEST_DATABASE_URL của database kiểm thử riêng; không dùng SQLite làm bằng chứng PostgreSQL. Không DDL/seed tự động. Khi chưa duyệt schema, migration NOT RUN, không gọi create_all. Giữ regression M0-A và hai PoC.

## Lịch sử quyền triển khai theo task — không cấp quyền tiếp tục

M0-A/B1/B2 và M1-A/B/C đã merge; các giới hạn theo giai đoạn dưới đây giữ ngữ cảnh task lịch sử. Các câu cấm/chưa triển khai M1 trong baseline ở trên không phủ nhận những task M1 đã được phê duyệt và hoàn thành. Phạm vi task mới phải được chủ dự án duyệt riêng; xem ROADMAP/status trước khi diễn giải lịch sử.

## M1-A được phê duyệt

Task M1-A cho phép Catalog rooms/objects, initial Alembic, read-only API và fixture synthetic riêng; branch feat/m1-a-catalog. Không M1-B/C, auth giả, write endpoints, state/session/event schema hoặc scene integration. User task mới thay giới hạn lịch sử chưa M1 ở trên. Không create_all/startup DDL/seed. Migration/seed phải xác nhận DB project dev/test loopback, không DROP/reset hoặc xóa volume. CI PostgreSQL riêng tạo database airc_test_catalog_UUID; TEST_DATABASE_URL chỉ base airc_foundation_test và AIRC_ALLOW_TEST_DATABASES=1. Chạy ruff/compileall/unit và toàn bộ PG migrations/constraints/API tests, giữ M0/PoC/frontend/browser regression.

## M1-B được phê duyệt

Task M1-B cho phép state/history/outbox/cursor, migration0002, internal synthetic service/CLI, readREST/WebSocket vàPG/TCP/concurrency tests. Branch feat/m1-b-state-realtime; không M1-C/publicwrites/authgiả/real507data. Giữ nguyên revision0001; assertion cũ vềhead/tables phải cập nhật đúng0002 nhưng giữ coverage Catalog. PGfaultinjection chỉunique disposable database đãguard, không đụng databasekhác. LocalPG khôngcó ghiBLOCKED, CIphảichạy thật.

## M1-C được phê duyệt

Task15/11/2026 cho phép C1 snapshot scalability →C2 frontend Catalog/state/3D integration →C3 realPG/TCP/Chrome render evidence, mộtbranch feat/m1-c-digital-twin-vertical-slice vàmộtPR cuối. Không chuyển giai đoạn khi gate trước chưaPASS. Mỗi giai đoạn commit/push vàcập nhật docs/18-m1-c-progress.md. Không visitor tracking/publicwrites/auth giả/GLB507/AI/multiinstance/deploy/milestone sau. Giữ protocol1 compatibility hoặc testpolicyđổiwire rõràng; protocol2 explicit opt-in. Synthetic chỉdev/test đãguard, khôngstartupseed/migrations destructive.
