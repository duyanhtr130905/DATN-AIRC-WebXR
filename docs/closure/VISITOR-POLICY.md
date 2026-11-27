# Đề xuất chính sách người tham quan và threat model

**Đang chờ quyết định.** [ADR-0002](../decisions/0002-m4-synthetic-visitor-scope.md) đang áp dụng synthetic opt-in, loopback và báo cáo Admin. P507 chưa ghi phiên. Đề xuất này dành cho việc đánh giá với chủ dự án, AIRC và giảng viên trước bất kỳ buổi thu thập thật nào.

| Quyết định cần ký | Phương án cần so sánh | Bằng chứng quyết định |
| --- | --- | --- |
| Mục đích và phạm vi | Nghiên cứu tác vụ có consent riêng hoặc chỉ demo không thu thập. Chốt trường tối thiểu, ai sử dụng, đâu là mục đích ngoài phạm vi. | Bản thông báo, ngôn ngữ, người phê duyệt, phiên bản, cách rút lại. |
| Danh tính | Phiên ngẫu nhiên một lần hoặc mã nghiên cứu do điều phối viên cấp trong hệ thống tách riêng nếu protocol yêu cầu đối chiếu. | Quy trình cấp/rút mã, lưu riêng nếu cần mapping, không dùng IP/UA/fingerprint để khôi phục. |
| Lưu giữ, xóa và backup | Chủ dự án và đơn vị có thẩm quyền chọn thời hạn, cách xóa DB/export/backup, quy trình với dữ liệu đã ẩn danh hoặc đã công bố. | Thời hạn, cách kiểm rút lại, ai xử lý, phạm vi backup, biên nhận và kênh liên hệ. |
| Mất proof | Giữ fail-closed và quy trình hỗ trợ có kiểm chứng độc lập. Chỉ cân nhắc mã khôi phục nếu có thiết kế được duyệt, giới hạn quyền, hết hạn, revoke và audit. | Định danh tối thiểu được duyệt, phương pháp xác minh quyền, từ chối khi không đủ, kiểm thử replay và audit. |
| Đọc và xuất | Xác định ai xem aggregates, ai cần xuất hàng chi tiết, lọc trường nào, phê duyệt và nơi giữ tệp. | Ma trận người/role × thao tác × scope, thời hạn quyền, access review. |
| P507 và M6 | Dùng mapping ổn định room ID + logical ID → Catalog UUID có version nếu được chấp thuận. Pin revision, validator theo room và phân biệt thiết bị chưa đặt/INFO_ONLY. | Data contract, phạm vi use, phê duyệt P507 riêng, không đưa pose/camera/media vào visitor event. |

## Mối đe dọa và điều kiện kiểm tra

| Rủi ro | Kiểm soát hiện hành hoặc thiết kế cần duyệt | Kiểm thử |
| --- | --- | --- |
| Xóa phiên khác hoặc sửa phiên cũ | Proof HttpOnly/SameSite strict, khóa session, expiry/rotation, kiểm session ID. | GET/POST/DELETE thiếu proof, sai proof, hết hạn hoặc proof cũ sau rotation → 401 và không đổi hàng. |
| Đưa khách vào tracking dù chưa consent hoặc origin lạ | Chỉ local synthetic khi bật cờ và opt-in rõ ràng; lọc origin/proxy, không tái nhận diện. | Backend tắt, no-opt-in, cross-origin, host ngoài loopback, storage denied; duyệt cảnh bình thường và không ghi. |
| Retry, hai tab và mất ACK gây trùng hoặc mất hàng | ID ổn định, atomic batch, kiểm canonical content, khóa PG, nhận ACK sau commit. | Retry cùng ID, conflict nội dung, writer song song, restart/fault, thu hồi proof, báo cáo CSV/JSON đối chiếu độc lập. |
| Mất proof để lại hàng trên máy chủ | Client báo thiếu xác nhận xóa server. Quy trình xử lý thật chờ phê duyệt. | Mất proof rồi xóa local, giữ bằng chứng xóa server ở trạng thái chưa xác nhận. Không trả dữ liệu phiên từ đường hỗ trợ chưa thẩm định. |
| Report làm lộ dữ liệu | Named Admin và local synthetic gate; giới hạn schema, filter/date/size, CSV chỉ giá trị typed. | Visitor/unauthenticated request bị từ chối, báo cáo không có cookie/proof/PII; xác minh quyền export bằng cả CSV và JSON. |

Sau lỗi ghi, giữ các ID chưa được ACK. Hàng đợi cũ đã vượt số slot còn lại, hoặc bị một writer API ngoài browser lấp chỗ, vẫn chịu 413 nguyên batch và báo rõ chưa đồng bộ. Thao tác xóa là lựa chọn rõ ràng của người giữ proof. Tài liệu này cần chữ ký của chủ dự án, người có thẩm quyền về dữ liệu và người duyệt protocol trước khi triển khai bất kỳ phương án mới nào.
