# 08 — UI/UX research

> Lịch sử M0-A/M0-B1 được giữ nguyên bên dưới. Cập nhật 14/11/2026: chủ dự án đã duyệt stack/kiến trúc/UI trong M0-B2; xem [ADR-0001 ACCEPTED](decisions/0001-technology-options.md) và [kiến trúc chính thức](12-official-system-architecture.md). Các phát biểu “chưa chọn/PROPOSED” về framework bên dưới mô tả thời điểm nghiên cứu, không phải trạng thái hiện tại. Schema chi tiết/auth/hosting/retention/quyền dữ liệu/KPI cuối/VR acceptance vẫn chưa duyệt.


> Ghi chú lịch sử: nội dung M0-A dưới đây là snapshot trước PoC. M0-B1 nay có hai mode UI đã chạy; xem [comparison](11-renderer-poc-comparison.md). Kiến trúc/framework/UI sản phẩm vẫn PROPOSED.

Trạng thái: PROPOSED. Ngày 14/11/2026. Đây là desk research từ nguồn sản phẩm; không phải usability test hoặc thiết kế giao diện chính thức. Chưa thao tác tour XR trên thiết bị thật. Nhận xét áp dụng AIRC là suy luận thiết kế.

## Sản phẩm tham khảo

| Sản phẩm và nguồn | Điều nguồn xác nhận | Bài học đề xuất cho AIRC |
| --- | --- | --- |
| [Smithsonian NMNH virtual tour](https://naturalhistory.si.edu/visit/virtual-tour) | tour từng phòng trên desktop/mobile; mũi tên sàn, bản đồ góc phải, camera close-up và thông tin exhibit | floor navigation + danh sách phòng tương đương; hotspot mở panel, có lối quay lại thay vì mất ngữ cảnh |
| [Google Arts & Culture Museum Views](https://artsandculture.google.com/project/streetviews) | bộ sưu tập tham quan panorama 360° của bảo tàng/di sản | màn chọn điểm đến trước khi load; giúp khách hiểu mình ở đâu; panorama không tự chứng minh Digital Twin trạng thái |
| [Autodesk Tandem](https://www.autodesk.com/products/tandem/overview) | liên kết BIM, tài sản, tài liệu và dữ liệu vận hành theo bối cảnh không gian | object panel có nguồn/last updated; dashboard hỗ trợ tìm tài sản và đọc trạng thái; không cần sao chép độ phức tạp BMS |
| [Matterport editing features](https://support.matterport.com/s/article/Overview-of-Matterport-s-Editing-Features?language=en_US) | search index chính thức mô tả start location và tag có icon/mô tả/tệp; trang trực tiếp trả CSS Error | chỉ tham khảo ý tưởng hotspot; xác minh UI tour trực tiếp còn BLOCKED, không khẳng định đã quan sát toàn bộ Dollhouse/floor UI |

[Sổ nguồn](research/sources.md) nêu hạn chế truy cập. Không suy ra sản phẩm trên đáp ứng KPI đồ án, accessibility hoặc WebXR chỉ vì có tour 3D. Không tải/sao chép assets của họ.

## So sánh theo ngữ cảnh

| Bối cảnh | Ưu tiên đề xuất | Rủi ro cần kiểm thử |
| --- | --- | --- |
| Desktop | canvas + danh sách phòng + panel có thể đóng; phím/tab, click và tìm object | phụ thuộc hover, keyboard trap, panel che scene |
| Mobile | danh sách phòng gọn, tap hotspot, bottom sheet, một tác vụ chính mỗi màn | hotspot nhỏ/chồng, gesture xung đột, xoay màn hình, GPU/nhiệt |
| XR | vào XR rõ ràng bằng user gesture; ray/touch và teleport nếu phù hợp; nút thoát, panel vừa tầm | DOM overlay không đồng nhất runtime, text xa/mỏng, motion sickness; phải thử kính |

## Ba hướng để người dùng chọn

1. **Tour có hướng dẫn**: lộ trình phòng → hotspot → nội dung; tối giản cho khách lần đầu, có skip và tự do khám phá. Hợp đánh giá task completion; tránh khóa người dùng vào tour bắt buộc.
2. **Không gian + bảng thông tin**: canvas là trung tâm, danh sách phòng và object panel; desktop dùng side panel, mobile bottom sheet. Đề xuất thử trước vì cân bằng tham quan và ba loại trạng thái.
3. **Dashboard vận hành nhẹ**: overview trạng thái, tìm/filter phòng/thiết bị rồi mở scene; hợp người phụ trách, có nguy cơ quá tải khách tham quan. Chỉ đưa dữ liệu người dùng được phép xem.

Chưa chọn palette, wireframe, component library hoặc UI chính thức. Trước duyệt cần xác nhận ưu tiên khách/nhân viên và đánh giá mock với người dùng.

## Accessibility và trạng thái hệ thống

Tham chiếu [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) ngày 14/11/2026; **PROPOSED** mục tiêu WCAG 2.2 AA cho luồng DOM, chưa tuyên bố conformance. Cung cấp danh sách phòng/object và nội dung chữ tương đương 3D; keyboard focus rõ, thứ tự hợp lý, label, không truyền trạng thái chỉ bằng màu, vùng tap đủ lớn, text co giãn, reduced motion, tùy chọn di chuyển ít gây chóng mặt. Cần review XR riêng, không áp conformance DOM để kết luận XR accessible.

Loading: progress theo giai đoạn metadata/asset, placeholder, cancel/retry và chất lượng thấp; không bịa phần trăm khi chưa biết tổng. Lỗi: asset fail có danh sách chữ, WebGL/context lost có retry, WebXR unsupported có Web 3D, permission denied giải thích cách thử lại. Realtime disconnected phải hiển thị stale + last updated, không “đang live”. Session recovery phải thông báo thành công/không thể phục hồi; queue pending không hiển thị là đã lưu server.

PoC UX cần kiểm tra cold load, mạng yếu/offline, denial, orientation, object không có dữ liệu, ≥20 hotspot và focus khi đóng panel. Protocol ≥15 người được duyệt ở milestone sau; chưa có kết quả nghiên cứu người dùng.
