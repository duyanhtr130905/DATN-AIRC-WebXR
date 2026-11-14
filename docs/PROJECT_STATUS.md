# Trạng thái dự án — M1-A Catalog

Cập nhật14/11/2026. Workspace D:\Code\DATN, repo duyanhtr130905/DATN-AIRC-WebXR, branch feat/m1-a-catalog. M0-B2 đã merge b4e4b910c9ed8cd43feeafccff66bbf3d5b6e811.

| Milestone | Trạng thái |
|---|---|
| M0-A / M0-B1 / M0-B2 | DONE |
| M1 | Đã bắt đầu theo phê duyệt chủ dự án |
| M1-A Catalog | IN REVIEW — [PR#9](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/9) |
| M1-B / M1-C | NOT STARTED |

Đã triển khai rooms/objects, Alembic0001_catalog,3GET Catalog chỉ synthetic, UUID cursor, metadata allowlist, sessionREADONLY và seed riêng cóguard/idempotency. Source commit4f65419 đã PASS29unit +23PGtests thật, CLI migration/seed, frontend7unit/6browser và M0/PoC regression. Follow-up chỉ tài liệu/evidence; latest HEAD checks xác minh trước bàn giao. [Acceptance](16-m1-a-catalog-acceptance.md), [evidence](evidence/m1-a-validation.json), [runbook](../apps/api/README.md).

Schema state/session/event/outbox, transform/domain metadata và chính sách auth/retention/hosting/source/quyền vẫn PROPOSED/chưa duyệt. ADR0001 ACCEPTED giữ nguyên; Catalog baseline được phép riêng trong task M1-A. Không publicwrite, WebSocket, admin hoặc scene integration.

PostgreSQL local BLOCKED vì khôngDocker, không tự cài; PostgreSQL CI PASS với database disposable mới, không SQLite/DROP/reset/volume cleanup. Downgrade NOT RUN/bị chặn. Thầy yêu cầu phòng507 trước, chưa khảo sát/inventory/ảnh/sơ đồ/kích thước/nguồn/quyền, chưa phần mềm quản lý thiết bị. KPI≥3phòng chưa đổi, MT1–MT3 chưa nghiệm thu từfixture1room/4objects. Galaxy ARsession chưa test, không kínhVR. Issues#1–#5 không đóng.

Sau review: ChatGPT nghiệm thu M1-A; khảo sát/quyền dữ liệu và quyết định còn mở; chỉ khi được cho phép mới bắt đầu M1-B. Không tự merge/deploy/M1-C.
