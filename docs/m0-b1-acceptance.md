# M0-B1 — checklist bàn giao PoC

- [x] Main đồng bộ fast-forward đúng merge #6; branch feat/m0-b1-renderer-poc, không repo con.
- [x] A và B renderer thật, dependencies/lock riêng, fixture/UI/domain chung; synthetic banner, không mô hình phòng 507.
- [x] Build/typecheck A và B, 6 domain tests trên mỗi package; browser suite 8 scenarios Windows/Chrome PASS theo report mới.
- [x] Desktop/mobile, real canvas click/touch, state/ECS projection, orbit/reset, hai UX modes, WebGL/native unsupported; screenshot thật đã xem.
- [x] IWER enter/exit và 2 input sources cho mỗi PoC; không runtime exception trong case đã thử; ray controller target selection NOT TESTED.
- [x] CI matrix độc lập + browser job/artifact; không deploy/write/merge. GitHub run phải theo dõi thật sau push, URL/conclusion ở PR và báo cáo cuối.
- [x] Verifier vẫn quét tracked + non-ignored files và secret patterns, không bỏ qua tracked file vì ignore; runtime metadata .iwsdk bị cấm track.
- [x] Chỉ đạo làm 507 trước và survey dự kiến 16/11/2026 được ghi theo người dùng; KPI ≥3 phòng không đổi, issue #1 còn blocker.
- [x] ADR-0001 PROPOSED, recommendation cần phê duyệt; không backend/admin/DB/auth production hoặc M1.

[Comparison](11-renderer-poc-comparison.md), [local browser JSON](evidence/m0-b1-local.json), [setup](../experiments/README.md). Kết quả M0 checker cũ được chạy hồi quy riêng, không nhầm với chức năng PoC. Phần thiếu: thiết bị vật lý, FPS/latency/recovery/99%/50 phiên/15 người và dữ liệu/quyền survey. Gate là ChatGPT review PR, không tự phê duyệt hoặc merge.
