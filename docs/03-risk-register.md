# 03 — Risk register

Ngày 14/11/2026. Mức độ định tính là đánh giá PROPOSED, không phải xác suất đo. Owner dưới đây là vai trò đề xuất; chưa có cam kết từ AIRC/giảng viên.

| ID | Rủi ro / mức | Trạng thái | Xử lý và điều kiện gỡ blocker | Owner đề xuất |
| --- | --- | --- | --- | --- |
| R01 | không đủ 3 phòng / cao | BLOCKED | xin danh sách, xác nhận ≥3 phòng; nếu thiếu trình giảng viên quyết định, không thay phòng bằng khu vực | sinh viên + AIRC |
| R02 | thiếu sơ đồ, số đo, inventory / cao | BLOCKED | khảo sát theo 04; người phụ trách xác nhận, mẫu ảnh/số đo có provenance; không bịa mô hình thực | sinh viên + AIRC |
| R03 | không có kính VR / cao | BLOCKED | mượn/đặt lịch thiết bị, ghi model/refresh rate; giảng viên thống nhất phương án; emulator không chứng minh 72 FPS hay comfort | sinh viên + giảng viên |
| R04 | Galaxy A17 5G thực tế không chạy WebXR AR / cao | NOT TESTED | đối chiếu variant, OS, Chrome, Play Services for AR, secure context; chạy checker rồi sample session bằng user gesture; lưu evidence | sinh viên |
| R05 | ảnh, mặt người, màn hình, thiết bị nhạy cảm / cao | BLOCKED | văn bản đồng ý thu thập, dựng mô hình, private repo, demo và công bố riêng; loại bỏ thông tin bị cấm trước upload | AIRC + sinh viên |
| R06 | scene nặng làm tụt FPS / cao | PROPOSED | PoC asset đại diện; LOD/instancing/culling/compression theo đo; budget cụ thể chờ kết quả | sinh viên |
| R07 | nguồn trạng thái không đủ tươi / cao | BLOCKED | xác định system of record, SLA/poll/change timestamp; đo end-to-end; manual update không gọi live IoT | AIRC + sinh viên |
| R08 | mất/trùng event hoặc hỏng recovery / cao | PROPOSED | event ID, ACK sau persist, durable queue, retry/dedupe; oracle độc lập và test reload/offline | sinh viên |
| R09 | lộ session/dữ liệu quản trị / cao | PROPOSED | tối thiểu hóa dữ liệu, server authorization, retention, giới hạn payload/rate; không dùng session ID như quyền admin | sinh viên |
| R10 | tiến độ đến 4/2027 bị chặn khảo sát/kính / cao | PROPOSED | milestone có gate, ưu tiên gỡ R01–R05; replan cùng giảng viên khi gate trễ, không tự giảm KPI | chủ dự án |
| R11 | lock-in/API mới hoặc dependency lệch / vừa | PROPOSED | pin version sau PoC, kiểm tra peer dependency/license; tách adapter XR khỏi domain | sinh viên |
| R12 | iPhone chưa rõ model, Quick Look khác WebXR / vừa | BLOCKED | ghi model/iOS/Safari, test USDZ riêng sau khi được phép; không tính Quick Look là chứng cứ WebXR | sinh viên |
| R13 | tuyển người thử/consent thiếu / cao | PROPOSED | chuẩn bị protocol và đồng thuận trước thu thập; ≥15 người, không dùng synthetic thay người | sinh viên + giảng viên |

Blocker R01–R05/R07/R12 chưa được giải quyết bằng tài liệu hoặc code. Issues chính và điều kiện đóng nằm tại [backlog](backlog/README.md). Không đặt thời hạn giả cho người chưa cam kết; chủ dự án thống nhất trước M0-B.
