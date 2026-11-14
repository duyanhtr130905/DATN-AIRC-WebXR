# 05 — Data source strategy

Toàn bộ thiết kế dữ liệu là PROPOSED; chưa có schema database cuối cùng, tài khoản nguồn hay dữ liệu thực AIRC.

| Loại | Nguồn cần khảo sát | Tần suất và kiểm soát dự kiến |
| --- | --- | --- |
| Không gian/phòng | sơ đồ được phép + số đo xác nhận | revision khi không gian thay đổi; model phải trỏ survey version |
| Đối tượng/thiết bị | inventory AIRC, Excel được phép hoặc phiếu khảo sát | đối chiếu ID, tên, vị trí; sanitize serial/thông tin nội bộ |
| Lịch phòng | API, database view read-only, Excel hoặc nhập tay | owner và cadence cần xác nhận; ghi thời điểm thay đổi tại nguồn |
| Tình trạng thiết bị | hệ thống quản lý nếu có, export hoặc nhập tay | không mặc định có sensor; phân biệt thời điểm quan sát và nhập liệu |
| Thông tin trưng bày | nội dung đã duyệt | tác giả/quyền, revision, effective date |
| Phiên/sự kiện | ứng dụng tạo sau này | pseudonymous session/event ID; retention/consent cần duyệt |
| GLB/glTF/ảnh | tự dựng từ survey hoặc asset có license | checksum, nguồn, quyền, đơn vị/trục, LOD, revision |

## Thứ tự chọn nguồn

Ưu tiên nguồn có người chịu trách nhiệm và quyền rõ. API/database read-only giúp đồng bộ nhưng phải xác minh auth, quota, timestamp, timezone, lỗi và quyền lưu. Excel chỉ phù hợp khi có quy trình version/validation và lịch nhập. Manual là nguồn hợp lệ nếu được AIRC xác nhận, hiển thị “cập nhật thủ công”, người cập nhật và thời điểm; không gọi đó là tự động realtime.

Độ trễ ≤5 giây tính từ thay đổi tại nguồn đã thống nhất đến hiển thị, không chỉ từ lúc backend nhận được. Nếu chỉ nhận file hàng ngày, phải báo không đủ chứng cứ KPI thay vì đổi định nghĩa nguồn âm thầm.

## Thật, mô phỏng và không biết

Mỗi record dự kiến có nhãn `real_verified`, `real_unverified` hoặc `synthetic`, nguồn, observed_at, ingested_at, verified_by theo vai trò, quality và revision. Đây là vocabulary đề xuất, không phải schema đã chốt. Mock phải hiện banner “MÔ PHỎNG”, không trộn báo cáo thực; unknown/stale khác trạng thái hoạt động tốt.

## Stable object ID

Cấp opaque ID bất biến, ví dụ minh họa `obj_<uuid>` và `room_<uuid>` (không phải dữ liệu AIRC). ID không chứa tên người/serial và không phụ thuộc mesh name, thứ tự trong Blender hoặc tên phòng. Đổi tên/chuyển phòng giữ ID; thay thế thiết bị cấp ID mới, ghi mapping lịch sử. Xóa dùng tombstone theo chính sách được duyệt, không tái dùng ID. Asset manifest map object ID → node/asset revision; validator phát hiện orphan/duplicate trước publish asset.

## Ranh giới dữ liệu

Backend dự kiến là chủ dữ liệu chuẩn đã xác thực; frontend chỉ là cache/render. Có adapter ingest riêng, validation + provenance trước commit, không ghi vào nguồn AIRC khi chưa được cấp quyền. Session queue không mang quyền quản trị. Không lưu raw ảnh/phiên định danh trong repo; nơi lưu, retention, quyền xem/xuất/xóa và consent phải được duyệt trước thu thập. Dữ liệu synthetic thử nghiệm sau này phải tách rõ khỏi dataset khảo sát.

Điểm cần PoC: mapping GLB ID qua export, import Excel lỗi, delta/reconnect, độ mới dữ liệu, dedupe và recovery. Chưa triển khai ở M0-A.
