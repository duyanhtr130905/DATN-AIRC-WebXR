# 01 — Project Charter

Ngày 14/11/2026. Chủ phạm vi: sinh viên/chủ dự án; giảng viên nghiệm thu học thuật chưa được xác định trong task. Charter diễn giải đề bài; các giải pháp đều PROPOSED.

## Vấn đề và giá trị

Xây dựng biểu diễn số không gian AIRC gắn đối tượng và trạng thái có nguồn, cho khách tham quan tương tác qua Web 3D/XR, đồng thời lưu vết để khôi phục và phân tích trải nghiệm. Mô hình đẹp đơn thuần chưa đủ chứng minh Digital Twin: phải chỉ ra liên kết đối tượng thực, nguồn trạng thái và độ mới dữ liệu.

## Stakeholder

| Vai trò | Trách nhiệm cần xác nhận |
| --- | --- |
| Sinh viên/chủ dự án | triển khai, quản lý bằng chứng, xin quyền khảo sát |
| Giảng viên | duyệt scope, phương pháp đo, framework/kiến trúc và nghiệm thu |
| Người phụ trách AIRC | xác nhận phòng, thông tin thiết bị, nguồn dữ liệu và quyền sử dụng |
| Khách tham quan/người thử | thực hiện tác vụ, đồng thuận tham gia |
| Quản trị dữ liệu dự kiến | xác thực cập nhật, xử lý yêu cầu xóa/retention |

Chưa có danh tính, cam kết thời gian hay quyền truy cập của các vai trò ngoài chủ dự án; không tự liên hệ thay người dùng.

## Cốt lõi

Giữ nguyên MT1–MT3 tại [KPI](02-requirements-kpi.md). Bao gồm 3D assets có căn cứ thực địa; tương tác desktop/mobile/XR; ba loại trạng thái; session/event logging, recovery và xuất báo cáo. AR/VR chỉ trên thiết bị tương thích, vẫn phải cung cấp bằng chứng phần được nghiệm thu.

Mở rộng: AI/RAG, dẫn tour thông minh, phân tích nâng cao. Không triển khai mở rộng ở M0. Không giả định tích hợp IoT, hệ thống lịch hay quyền ghi dữ liệu AIRC đã có.

## Những gì đã biết và chưa biết

- Theo thông tin người dùng: Galaxy A17 5G; iPhone chưa rõ model; không có kính VR; chưa có sơ đồ, số đo, danh mục thiết bị, chưa xác nhận đủ ba phòng.
- Giả định PROPOSED: có thể được phép khảo sát và có người xác nhận dữ liệu; phải kiểm chứng trước mô hình hóa.
- Câu hỏi: ba phòng nào? Có quyền chụp/công bố đến đâu? Nguồn nào là system of record? Có thể mượn kính nào? Ai duyệt phương pháp đánh giá?

## Milestone và phụ thuộc — PROPOSED

| Milestone | Điều kiện ra |
| --- | --- |
| M0-A | repo độc lập/private, nghiên cứu có nguồn, checker, checklist, PR review được |
| M0-B | có phản hồi AIRC, thử điện thoại, thống nhất cách nghiệm thu VR, duyệt kế hoạch PoC |
| M1 | chỉ sau phê duyệt: PoC so sánh, chọn stack bằng ADR; chưa thực hiện |
| M2 | assets thực và vertical slice dữ liệu/tương tác sau khi scope được xác nhận |
| M3 | realtime, tracking/recovery và kiểm thử tích hợp |
| M4 | đo hiệu năng, ≥15 người, ≥50 phiên, báo cáo và nghiệm thu trước hạn dự kiến 4/2027 |

Không chia tuần, không cam kết ngày giả khi chưa có quyền khảo sát và thiết bị. Critical path: phòng/quyền → survey → asset đại diện → PoC → duyệt stack → sản phẩm → thử người dùng. Thiếu ba phòng phải báo giảng viên, không tự đổi KPI thành ba khu vực.

## Definition of Done M0-A

Đủ tài liệu yêu cầu, nguồn kiểm chứng, checker không có network ngoài/camera, test trung thực và PR mở vào main; blocker thực địa vẫn mở. M0-A sẵn sàng review khác với đề tài hoàn thành.

## Thông tin trao đổi mới do người dùng cung cấp — 14/11/2026

Đây là nội dung người dùng thuật lại từ trao đổi với giảng viên và anh Nguyễn Tiến Nhật Quang, **chưa phải dữ liệu khảo sát hoặc xác nhận phạm vi chính thức**:

- Giảng viên cho biết AIRC hiện chỉ có phòng **507**. Người dùng đang hỏi lại về mâu thuẫn với KPI **≥3 phòng**; Issue #1 vẫn BLOCKED chờ quyết định phạm vi chính thức.
- Anh Quang đề nghị hỏi giảng viên để xác định phòng/khu vực cần mô phỏng; sau khi chọn phòng, anh có thể hỗ trợ danh mục thiết bị. Chưa có inventory được bàn giao, Issue #2 vẫn BLOCKED.
- Theo trao đổi, hiện chưa có phần mềm quản lý thiết bị. Không mặc định tồn tại API/database thiết bị của AIRC. Nguồn và quyền dữ liệu chưa được xác nhận chính thức, Issue #3 vẫn BLOCKED.
- Có thể cân nhắc dựng không gian theo quan sát trực quan, không nhất thiết đo quá chi tiết. Đây là đề xuất phương pháp cần giảng viên duyệt và ghi giới hạn độ chính xác; không phải khảo sát đã xong.

Giữ nguyên KPI ≥3 phòng, không chia phòng 507 thành ba phòng giả, không tự kết luận một phòng là đủ. Không đăng ảnh hội thoại cá nhân. Không thay các lựa chọn công nghệ PROPOSED hoặc triển khai quản trị/database ở M0.

## M0-B1 — chỉ đạo phòng 507 và PoC synthetic (14/11/2026)

Theo thông tin người dùng cung cấp, giảng viên chỉ đạo “Cứ làm 1 phòng 507 trước.” Phòng 507 là phạm vi triển khai đầu tiên; KPI ≥3 phòng chưa được điều chỉnh chính thức, Issue #1 vẫn BLOCKED về phạm vi nghiệm thu cuối. Dự kiến khảo sát khoảng 16/11/2026, chưa có số đo/ảnh/sơ đồ/inventory/quyền dữ liệu. Không giả lập 507 rồi coi là dữ liệu thật, không chia phòng giả.

Task M0-B1 đã cho phép hai PoC trong experiments/ dùng chung 1 room/5 objects synthetic; đây là thử nghiệm renderer/UI, không phải sản phẩm hoặc M1. Framework, kiến trúc, UX và contract vẫn PROPOSED. [Kết quả và giới hạn](11-renderer-poc-comparison.md). Chưa có quản trị, API/DB/auth/WebSocket production; không mặc định AIRC có phần mềm/API thiết bị.
