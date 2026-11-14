# Trạng thái dự án — M1-B

M0-A/M0-B1/M0-B2 DONE; M1-A DONE, PR#9 merged99f65377746a0eb7c924b6493db3a8e4680a444d. M1-B IN PROGRESS trênfeat/m1-b-state-realtime (IN REVIEW khi bàn giao); M1-C NOT STARTED.

Scope đượcduyệt: synthetic state/history/version/cursor/outbox, readREST/WebSocket/internalCLI; khôngpublicwrite hoặcsceneintegration. [Acceptance M1-B](17-m1-b-state-realtime-acceptance.md) ghi kiếntrúc/checks/giớihạn; PostgreSQLlocalBLOCKED, CIđangchuẩnbịchạy. ChưaAIRC507realdata, quyềnnguồn/inventory/survey; KPI≥3phòng vàMT1–MT3giữnguyên/chưanghiệmthu. GalaxyARsession/kínhVRchưatest; Issues1–5mở.

## Trạng thái lịch sử M1-A

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
