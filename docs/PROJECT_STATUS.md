# Trạng thái dự án — M1-B

Cập nhật 14/11/2026. Root D:\Code\DATN; repo duyanhtr130905/DATN-AIRC-WebXR; branch feat/m1-b-state-realtime. M1-A merge 99f65377746a0eb7c924b6493db3a8e4680a444d.

| Milestone | Trạng thái |
|---|---|
| M0-A / M0-B1 / M0-B2 | DONE |
| M1-A | DONE — PR#9 merged |
| M1-B | IN REVIEW — [PR#10](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/10) |
| M1-C | NOT STARTED |

Đã triển khai synthetic state/history/version/cursor/outbox, migration0002, internalCLI vàreadREST/WebSocket. Source 320c3bc PASS 38 unit +47 PG tests thật, actualTCP/concurrency/outage/retry/CLI vàfullM0/Catalog/frontend/PoC regression. [Acceptance](17-m1-b-state-realtime-acceptance.md), [evidence/metrics](evidence/m1-b-validation.json), [runbook](../apps/api/README.md). Follow-up chỉ tài liệu/evidence, latest HEAD checks xác minh trước bàn giao. Không merge/deploy/M1-C.

Giới hạn: một API process, multiinstancebroadcast chưa hỗ trợ; metrics20 samples loopback không source-to-render. LocalPostgreSQL BLOCKED, không tự cài/SQLite. PhysicalGalaxy/VR NOT RUN. Auth/retention/hosting/data rights/domain metadata/VR acceptance vẫn chưa chốt. Outbox retained/exhausted cần operations policy sau; không xóa DB/volume hoặc destructive downgrade.

Thầy chỉ đạo phòng 507 trước, chưa khảo sát/inventory/ảnh/sơ đồ/kích thước/nguồn/quyền vàchưa phần mềm thiết bị. Synthetic DEMO không phải507. KPI≥3phòng chưa điều chỉnh, MT1–MT3 chưa nghiệm thu; Issues1–5 giữ mở. Sau ChatGPT review và phê duyệt mới bắt đầu M1-C.
