# Trạng thái dự án — M0-B1

Cập nhật 14/11/2026. Workspace duy nhất D:\Code\DATN; repo duyanhtr130905/DATN-AIRC-WebXR; PR #6 đã merge bằng `1a736d558f6b721921cd5f38de069d63a733721e`. Nhánh hiện tại feat/m0-b1-renderer-poc, không sửa main hoặc tạo repo con.

## Đã triển khai trong phạm vi PoC

Hai prototype A R3F/XR và B IWSDK World/ECS dùng chung fixture/domain/UI: 1 phòng DEMO, 5 primitive, 3 nhóm trạng thái. Có chọn canvas/danh mục, trạng thái/metadata, reset/orbit, Guided Tour và Scene + Panel, mobile/loading/error/WebGL/native XR fallback. DataAdapter và validation mẫu, không network/backend/database. [README chạy](../experiments/README.md), [so sánh bằng chứng](11-renderer-poc-comparison.md).

Build/typecheck và domain tests đã chạy; browser suite Windows/Chrome thực đã thử mouse/touch/DOM/viewport và IWER, có lịch sử lỗi và khắc phục trong comparison. Kết quả latest local tại docs/evidence/m0-b1-local.json. CI được kiểm tra live trên PR sau push; local không thay CI. Ảnh thật trong .local/poc-browser và CI artifacts; không commit hàng loạt binary, không profile/cache/SDK runtime credential.

## Gate và blocker

Chờ ChatGPT review PoC và chủ dự án phê duyệt bước tiếp; chưa chọn framework/kiến trúc/UI chính thức, ADR-0001 PROPOSED. Không bắt đầu M1, không deploy/merge PR. Galaxy/iPhone/kính thật, FPS/latency và MT1–MT3 sản phẩm NOT TESTED/NOT RUN. Ray controller target selection chưa test, IWER chỉ chứng minh lifecycle/input sources.

Issues #1–#5 vẫn mở; scope cuối ≥3 phòng, survey/inventory/nguồn/quyền chưa được giải quyết. Hướng admin nhập tay chỉ PROPOSED.

## M0-B1 — chỉ đạo phòng 507 và PoC synthetic (14/11/2026)

Theo thông tin người dùng cung cấp, giảng viên chỉ đạo “Cứ làm 1 phòng 507 trước.” Phòng 507 là phạm vi triển khai đầu tiên; KPI ≥3 phòng chưa được điều chỉnh chính thức, Issue #1 vẫn BLOCKED về phạm vi nghiệm thu cuối. Dự kiến khảo sát khoảng 16/11/2026, chưa có số đo/ảnh/sơ đồ/inventory/quyền dữ liệu. Không giả lập 507 rồi coi là dữ liệu thật, không chia phòng giả.

Task M0-B1 đã cho phép hai PoC trong experiments/ dùng chung 1 room/5 objects synthetic; đây là thử nghiệm renderer/UI, không phải sản phẩm hoặc M1. Framework, kiến trúc, UX và contract vẫn PROPOSED. [Kết quả và giới hạn](11-renderer-poc-comparison.md). Chưa có quản trị, API/DB/auth/WebSocket production; không mặc định AIRC có phần mềm/API thiết bị.
