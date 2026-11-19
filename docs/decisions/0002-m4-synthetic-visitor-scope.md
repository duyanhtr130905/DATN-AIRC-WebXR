# Quyết định phạm vi M4 — 19/11/2026

Chủ dự án phê duyệt một nhánh và một Draft PR cho toàn bộ phần kỹ thuật M4 qua [Issue #27](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/27). GitHub xác nhận PR #26 đã merge và main ở `ae21efd2359779aa5bc6a889624a4705cd830ee1` lúc đối chiếu.

Roadmap 2.0 cho phép triển khai M4 khi được giao và đã có luồng tương tác M1. Cảnh mô phỏng hiện hữu và xác thực Admin nội bộ đủ cho phần kỹ thuật M4. #2/#3 tiếp tục chặn phần thực địa M3. Thiết kế dùng đúng ADR-0001, tách hai bảng M4 khỏi Catalog/State/History/Outbox, giữ frozen R4, các ID và toàn bộ KPI. Không thay đổi thứ tự nghiệm thu hay DoD.

Quyền triển khai chỉ áp dụng với dữ liệu mô phỏng, một môi trường loopback tường minh và PostgreSQL local kiểm soát. Chế độ mặc định tắt. Chưa có phê duyệt thu thập phiên người tham quan thật, định danh, consent, retention, xóa dữ liệu thật hoặc quyền sử dụng/công bố báo cáo thật. Phần đó vẫn bị chặn. Mọi kết quả 50 phiên/1.000 sự kiện giả lập chỉ là bằng chứng phát triển M4. Việc nghiệm thu độc lập vẫn thuộc ChatGPT trước khi chủ dự án quyết định merge hay tiến tới M5.
