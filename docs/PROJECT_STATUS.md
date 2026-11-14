# Trạng thái dự án — M0-A

Cập nhật 14/11/2026. Repo độc lập: DATN-AIRC-WebXR; local `D:\Code\DATN`; account `duyanhtr130905`; main bootstrap `b3c4f43`; nhánh `docs/m0-foundation`.

## Gate hiện tại

Đang khắc phục review PR #6 (P1–P4), chưa được chấp thuận merge. Scope M0-A do người dùng cho phép, framework/kiến trúc vẫn PROPOSED. Không có product frontend/backend/database/AI/RAG và không deploy.

## Đã có

Charter, requirements/KPI, risks, survey/data strategy, device/technology/UI research, architecture options, ADR template + proposed ADR, source/version index, checker độc lập, tests và PR template. Các tài liệu giữ nguyên MT1–MT3.

## Evidence và hạn chế

Kết quả cũ ở commit cdf43fd chỉ là lịch sử. Regression trên bản sửa và browser report v2 được ghi trong evidence; không dùng kết quả cũ để nghiệm thu code mới. Xem [evidence](evidence/m0-validation.md). Không có chứng cứ vật lý AR/VR, FPS hay KPI sản phẩm. Dữ liệu AIRC, ba phòng và quyền sử dụng chưa được xác minh.

## Handoff

[Acceptance](10-m0-acceptance.md) là checklist trạng thái; [backlog](backlog/README.md) chứa năm blocker issues #1–#5 đã tạo và đang OPEN. Validation được ghi trong evidence; commit/PR xác thực bằng GitHub và báo cáo cuối sau thao tác tạo PR. Không coi PR mở là phê duyệt của người dùng/giảng viên.

## Bước tiếp theo cần người dùng quyết định

Review PR; bổ sung đầu mối/quyền AIRC, số phòng/inventory, nguồn dữ liệu; thử Galaxy; trao đổi phương pháp nghiệm thu VR. Đề xuất M0-B gỡ blocker và duyệt PoC; chưa bắt đầu. M1 bị chặn đến khi có phê duyệt riêng và ADR được chấp nhận bằng phản hồi có thẩm quyền.

## Thông tin trao đổi mới do người dùng cung cấp — 14/11/2026

Đây là nội dung người dùng thuật lại từ trao đổi với giảng viên và anh Nguyễn Tiến Nhật Quang, **chưa phải dữ liệu khảo sát hoặc xác nhận phạm vi chính thức**:

- Giảng viên cho biết AIRC hiện chỉ có phòng **507**. Người dùng đang hỏi lại về mâu thuẫn với KPI **≥3 phòng**; Issue #1 vẫn BLOCKED chờ quyết định phạm vi chính thức.
- Anh Quang đề nghị hỏi giảng viên để xác định phòng/khu vực cần mô phỏng; sau khi chọn phòng, anh có thể hỗ trợ danh mục thiết bị. Chưa có inventory được bàn giao, Issue #2 vẫn BLOCKED.
- Theo trao đổi, hiện chưa có phần mềm quản lý thiết bị. Không mặc định tồn tại API/database thiết bị của AIRC. Nguồn và quyền dữ liệu chưa được xác nhận chính thức, Issue #3 vẫn BLOCKED.
- Có thể cân nhắc dựng không gian theo quan sát trực quan, không nhất thiết đo quá chi tiết. Đây là đề xuất phương pháp cần giảng viên duyệt và ghi giới hạn độ chính xác; không phải khảo sát đã xong.

Giữ nguyên KPI ≥3 phòng, không chia phòng 507 thành ba phòng giả, không tự kết luận một phòng là đủ. Không đăng ảnh hội thoại cá nhân. Không thay các lựa chọn công nghệ PROPOSED hoặc triển khai quản trị/database ở M0.

## Review fixes P1–P3

Đã thêm workflow read-only gồm validation và browser job; runner portable CHROME_BIN/PATH với cleanup/report schema v2 và ảnh checker 390px có thể review trong PR. Local regression: Node 10/10, runner tests 8/8, Chrome native/mock/viewport PASS theo phạm vi utility; thử thiếu browser trả NOT RUN/exit 2. Checker.js không đổi. CI thực tế phải theo dõi sau push, không coi local là CI. Evidence và cách tái lập tại [báo cáo](evidence/m0-validation.md).
