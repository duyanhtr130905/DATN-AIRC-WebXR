# Nghiệm thu M1-A — Database schema và Catalog API

Ngày 14/11/2026. [PR #9](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/9), branch feat/m1-a-catalog, base merge M0-B2 b4e4b910c9ed8cd43feeafccff66bbf3d5b6e811. Source/test/workflow commit đã kiểm: **4f6541935816b257ef052d420d2ed3e3014bd0b8**; follow-up chốt tài liệu/evidence. Latest HEAD được kiểm qua PR checks trước bàn giao. Không merge/deploy hoặc bắt đầu M1-B/C.

## Checklist đã kiểm

| Hạng mục | Kết quả | Bằng chứng thực tế |
|---|---|---|
| Catalog schema và ORM/DTO | PASS | rooms/objects, UUID PK, FK RESTRICT, unique code, non-null/CHECK, bounded JSONB, timestamptz và indexes |
| Alembic migration từ database trống | PASS | PG18.7 CI tạo DB riêng mới, upgrade head, exact tables rooms/objects/alembic_version, zero Catalog rows |
| Current / upgrade khi đã head / schema drift | PASS | revision0001_catalog, nâng cấp lặp, command.check và CLI check đều thành công |
| Constraints/timezone | PASS | duplicate room/object IDs, duplicate code, invalid/null source/name/room/type, invalid FK, RESTRICT, metadata/transform shape và byte limit, timezone round-trip |
| Catalog API thật với PostgreSQL | PASS | empty DB, multiple rooms, UUID keyset ordering/pagination,404/422, hidden source/parent, private fields filtering |
| Read-only / connection lifecycle | PASS | PG SHOW transaction_read_only=on, write attempt bị từ chối; connection trả về pool, lifespan dispose; health/readiness regression |
| Synthetic seed | PASS | CLI và function seed hai lần vẫn1room/4objects; UUID cố định, nhãn synthetic, collision rollback không overwrite |
| Migration/seed safety | PASS | loopback/dev-test allowlist/exact confirmation/current_database; reject URL query overrides trước kết nối; không startupDDL/seed/create_all |
| Backend lint/import/unit | PASS | ruff/compileall/OpenAPI import;29unit exit0; TestClient/httpx deprecation warning giữ nguyên |
| PostgreSQL suite | PASS | **23 passed,0failed,0errors,0skipped**, JUnit artifact đã tải và kiểm tra; bao gồm CLI migration và seed thật |
| Frontend foundation regression | PASS | typecheck/build/7unit/6browser; không thay scene hoặc client sang Catalog |
| M0-A / PoC A+B regression | PASS | CI syntax/checker/verifier/browser; hai PoC build/domain tests và WebGL/IWER browser suite |
| Secret/link/whitespace/YAML | PASS | verifier/pattern scan/internal links, git diff --check, YAML parser; không phải full security audit |
| PostgreSQL local | BLOCKED | không Docker/PostgreSQL local, không tự cài; CI PostgreSQL thật thay thế môi trường kiểm thử, không dùng SQLite |
| Downgrade | NOT RUN | chủ động chặn destructive downgrade; không DROP/reset DB hoặc xóa volume |
| AIRC real data/KPI/AR-VR hardware | NOT RUN | chưa survey/quyền/thiết bị; fixture không chứng minh MT1–MT3 |

## Evidence và môi trường

[Bản ghi lệnh, exit codes, SHA, từng job và tên 23 PG tests](evidence/m1-a-validation.json). Local Windows11/Python3.13.2/Node22.16/Chrome157.0.8103.51. CI Ubuntu24.04/Python3.13.18/PostgreSQL18.7; browser headless software WebGL, 390px viewport emulation, không Galaxy thật.

- [Application + Catalog CI](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43580467918):2jobs PASS,29unit+23PGtests và frontend/browser; artifact m1-a-postgres-pull_request có JUnit, m0-b2-browser-pull_request có report/3ảnh giao diện.
- [M0-A regression](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43580467951):2jobs PASS.
- [PoC A/B + IWER regression](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43580467911):3jobs PASS.
- [Push CI độc lập cùng source](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43580464382):2jobs PASS.

CI tạo database airc_test_catalog_UUID trống riêng cho từng integration case trên service disposable. TEST_DATABASE_URL chỉ base loopback airc_foundation_test cùng explicit ACK; kiểm current_database trước CREATE DATABASE, không DROP/reset database đã có. Initial migration không chứa seed AIRC hoặc synthetic; CLI seed riêng có guard. Chỉ2bảng Catalog ngoài Alembic bookkeeping, không state/session/event.

## Lỗi và review đã đóng

[CI đầu tiên](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43579935413) trên8e603b5 có21PASS/1FAIL: Alembic thực tế in0001_catalog(head), nhưng assertion đọc nhầm stdout stream. Sửa Config(stdout=StringIO), giữ current/repeat/drift assertions; bản sau có23PGtests PASS. Không skip hoặc tắt job để che lỗi.

Independent review phát hiện parent visibility race trong listobjects và test URL query có thể override host/dbname. Đã sửa JOIN Room/source trong cùng SQL; reject query trước engine creation và kiểm database nền; thêm regression tests. Reviewer xác nhận closure và rà CLI helper; không còn P1/P2 được phát hiện trong phạm vi review. Không thay review nghiệm thu của ChatGPT hoặc quyền dữ liệu của AIRC.

## Giới hạn và bước kế tiếp

[Model](13-data-model.md), [contract](14-api-contracts.md), [lệnh local](../apps/api/README.md). Catalog baseline được phép triển khai; domain metadata/transform semantics, state/session/event/outbox schema vẫn PROPOSED. Không frontend integration, public mutation, auth giả, admin, WebSocket hoặc AI/RAG. Phòng507 chưa khảo sát, không có inventory/ảnh/sơ đồ/kích thước/nguồn/quyền; fixture generic DEMO không phải507 và không đạt KPI20objects/3rooms. Issues#1–#5 giữ mở.

Cần chủ dự án chốt source/quyền, metadata/transform theo survey, auth/operator policy, retention, hosting, scope≥3phòng và VR acceptance. Đề xuất M1-B sau phê duyệt riêng: state types/version/history và state read contracts, outbox/concurrency tests; chỉ xem xét write khi authorization/data rights được chốt. Scene integration thuộc M1-C, chưa bắt đầu.
