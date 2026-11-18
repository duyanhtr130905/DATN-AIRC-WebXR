# 02 — Requirements và KPI

> Chú thích phạm vi 18/11/2026: theo [Roadmap 2.0 APPROVED](ROADMAP.md), M2 chỉ prototype một phòng P507. MT1-01 **≥3 phòng giữ nguyên**, là điều kiện nghiệm thu **M6**; Issue #1 vẫn OPEN, `DEFERRED_FOR_M2; REQUIRED_FOR_M6`, không chặn E0/E1/nghiệm thu chức năng prototype M2. Các KPI khác giữ nguyên con số và phương pháp kiểm chứng; bảng trạng thái/thiếu survey ngày 14/11 bên dưới là AS-OF lịch sử, xem [PROJECT_STATUS](PROJECT_STATUS.md) cho hiện trạng. Không KPI nào được tự gán PASS.

Các ngưỡng do đề bài quy định; phương pháp đo dưới đây là PROPOSED, cần giảng viên duyệt trước thử nghiệm. Ngày 14/11/2026, **không KPI sản phẩm nào đã PASS**. Có thể VERIFIED độ đầy đủ của kế hoạch M0, chưa thể xác minh kết quả MT1–MT3.

| ID | Yêu cầu giữ nguyên | Tiêu chí và bằng chứng dự kiến | Trạng thái hiện tại |
| --- | --- | --- | --- |
| MT1-01 | ≥3 phòng | danh sách ≥3 phòng thực được AIRC xác nhận; sơ đồ, ảnh có quyền, mapping room ID ↔ scene; đi đủ từng phòng trong build | BLOCKED: trao đổi người dùng nói chỉ phòng 507; chờ xác nhận scope, KPI ≥3 phòng chưa đổi |
| MT1-02 | ≥20 đối tượng tương tác | ≥20 object ID duy nhất có đối chiếu thực địa; kiểm thử mở thông tin/tương tác từng ID, không đếm nhiều mesh của một thiết bị thành nhiều đối tượng | BLOCKED: chưa có inventory |
| MT1-03 | ≥3 loại trạng thái | lịch phòng, tình trạng thiết bị, thông tin trưng bày; test cập nhật từng loại từ nguồn đã xác nhận đến UI, kèm provenance | BLOCKED: chưa có nguồn |
| MT1-04 | độ trễ hiển thị ≤5 giây | trace từ thời điểm thay đổi được ghi tại nguồn đến frame UI áp dụng; mọi mẫu đo hợp lệ ≤5s trong workload đã duyệt; lưu raw timestamp, clock offset, cấu hình mạng, log lỗi | NOT TESTED |
| MT2-01 | tham quan Web 3D | mở/chuyển phòng/điều hướng/xem object bằng desktop và mobile; ghi video, task log, build SHA | NOT TESTED |
| MT2-02 | hỗ trợ VR và AR trên thiết bị tương thích | requestSession thật với user gesture, tương tác/thoát/khôi phục theo test script trên thiết bị đã chọn; capability chỉ là preflight | BLOCKED: điện thoại chưa thử, thiếu kính |
| MT2-03 | Web 3D ≥30 FPS | đo frame time ở scene đại diện ≥3 phòng/≥20 object, ghi render resolution, CPU/GPU, OS/browser, chất lượng, cache, mạng, nhiệt độ nếu đo được | NOT TESTED |
| MT2-04 | mục tiêu VR ≥72 FPS trên kính được lựa chọn | chọn kính/refresh rate được duyệt; đo frame timing XR runtime và dropped frames trên kính thật; emulator không thay thế | BLOCKED: không có kính |
| MT2-05 | ≥90% tác vụ hoàn thành, ≥15 người | ít nhất 15 người đồng thuận; script tác vụ cố định, đánh dấu thành công/thất bại/bỏ cuộc; tỷ lệ = số lượt tác vụ thành công / tổng lượt tác vụ được giao ×100%; không bỏ người thất bại khỏi mẫu | BLOCKED: chưa có build và protocol duyệt |
| MT3-01 | lưu phiên và sự kiện | kiểm tra session ID, event ID, object ID, thời điểm, thứ tự và persistence; đối chiếu hành vi với log/DB | NOT TESTED |
| MT3-02 | khôi phục sau reload | reload giữa phiên, xác minh cùng phiên, phòng/view và trạng thái tương tác có thể phục hồi; retry không trùng event; kiểm tra token hết hạn/storage bị chặn | NOT TESTED |
| MT3-03 | ghi nhận ≥99% sự kiện bộ kiểm thử | tập event ID kỳ vọng độc lập; tỷ lệ = unique event ID hợp lệ đã lưu / unique event ID phát sinh kỳ vọng ×100%; log duplicate riêng, không dùng tổng hàng để thổi tỷ lệ | NOT TESTED |
| MT3-04 | xuất báo cáo ≥50 phiên mẫu | ≥50 session ID phân biệt, tái tính số sự kiện và thống kê từ raw đối chiếu CSV/JSON; nếu synthetic phải gắn nhãn, không gọi là 50 người thật | NOT TESTED |

## Protocol cần phê duyệt

- Độ trễ: t_source, t_ingest, t_send, t_render; đồng bộ clock hoặc đo offset + sai số. Báo cả max, phân vị và mẫu lỗi; không lấy p95 thay ngưỡng 5 giây. Nếu source poll 10 giây sẽ không đáp ứng mục tiêu này. Cần thống nhất ranh giới khi nguồn bên ngoài không cung cấp thời điểm thay đổi.
- FPS: đề xuất warm-up 30s, đo 3 lượt ×120s cho cold/warm và các tuyến di chuyển cố định; trình bày median, low percentile, min, frame time và số frame chậm. Cách kết luận “tối thiểu” theo cửa sổ đo cần giảng viên duyệt; không dùng trung bình để che tụt frame. Chưa có ngân sách triangle/texture cố định; xác lập bằng PoC.
- Người dùng: đề xuất tác vụ tìm phòng, đọc lịch, tìm thiết bị, xem tình trạng, mở thông tin trưng bày, quay lại phiên; cân bằng desktop/mobile, tách XR nếu không đủ thiết bị. Giới hạn thời gian và mức trợ giúp cần duyệt, báo rõ tỷ lệ theo tác vụ và nhóm thiết bị.
- Event reliability: đề xuất ≥1.000 event ID synthetic cố định, gồm online/offline, timeout, retry, reload, out-of-order; oracle ghi trước khi gửi, đối chiếu sau thời hạn flush được duyệt. Với 1.000 event, cần ≥990 unique hợp lệ; báo cả missing và duplicate. Đây là kế hoạch, chưa sinh dữ liệu kiểm thử sản phẩm.
- Mỗi evidence pack: test ID, ngày giờ/múi giờ, người thực hiện được ẩn danh, build SHA, script/input hash, thiết bị và version, expected/actual, raw log/video đã biên tập quyền riêng tư, kết luận có giới hạn.

## Có thể kiểm tra tại M0

Link, nguồn, syntax/logic/DOM của capability checker, không gọi camera/requestSession/network ngoài; trạng thái repo và PR. Không có scene/backend nên latency, FPS, recovery, 99%, 50 phiên và thử ≥15 người đều chưa đo. Emulator nếu dùng sau này chỉ là evidence phát triển.
