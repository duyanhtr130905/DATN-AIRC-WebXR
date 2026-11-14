# 04 — Checklist khảo sát AIRC

> Cập nhật M0-B2 ngày 14/11/2026: stack/kiến trúc/UI đã được chủ dự án phê duyệt theo [ADR-0001 ACCEPTED](decisions/0001-technology-options.md). Phần M0-A/M0-B1 bên dưới là lịch sử; dữ liệu thực, quyền sử dụng và KPI cuối vẫn BLOCKED. Xem [trạng thái hiện tại](PROJECT_STATUS.md) và [acceptance foundation](15-m0-b2-acceptance.md).


Trạng thái: PROPOSED; chưa khảo sát. Không có bất kỳ tên/số phòng, số đo hay danh mục thiết bị nào được điền giả.

## Xin trước chuyến khảo sát

- [ ] Người đầu mối và lịch được phép; danh sách phòng được truy cập, tối thiểu ba phòng thực nếu tồn tại.
- [ ] Sơ đồ được phép dùng, tỷ lệ/đơn vị, revision/ngày cập nhật; xác định bản nào là chính thức.
- [ ] Danh sách thiết bị/trưng bày có thể giới thiệu; thông tin nào công khai, nội bộ, cấm thu thập.
- [ ] Xin quyền đo/chụp/dựng 3D/lưu trong GitHub PRIVATE/demo/báo cáo/công bố; mỗi mục có thể có quyền khác nhau.
- [ ] Xin đầu mối nguồn lịch, thiết bị, trưng bày; không xin token/password để đưa vào repo.

## Đo và ghi không gian

1. Chọn mốc gốc và trục tọa độ, đơn vị mét; ghi phương pháp/dụng cụ và sai số ước tính, người đo/ngày đo.
2. Đo chiều dài/rộng/cao, cửa, cửa sổ, vật cản, vị trí thiết bị; đo đường chéo để đối chiếu; không vào khu hạn chế.
3. Vẽ phác mã phòng, điểm nối, hướng đi, khu vực không được mô hình hóa. Ghi “chưa đo” thay số 0.
4. Chụp ảnh toàn cảnh từng góc, tường/sàn/trần, lối vào và liên phòng; ảnh tổng quan + trung cảnh + chi tiết object được phép; thêm thước/mốc khi an toàn.
5. Không chụp mặt người, thẻ, tài khoản, mạng, màn hình nghiên cứu, nhãn serial nếu không được phép. Tắt geotag hoặc xử lý EXIF trước chia sẻ theo quyền được cấp.
6. Soát bản đo với người phụ trách; lưu revision/provenance và danh sách điểm cần đo lại.

## Phiếu metadata đối tượng — mẫu trống

| Trường | Cách ghi |
| --- | --- |
| object_id | cấp ID bất biến sau khi xác nhận; không dùng serial thật |
| room_id / vị trí | liên kết phòng đã xác nhận, tọa độ + đơn vị/hệ trục |
| tên hiển thị / loại | được người phụ trách chấp thuận |
| kích thước | x/y/z, phương pháp đo, độ tin cậy; chưa biết ghi unknown |
| tương tác dự kiến | chọn/xem thông tin/đọc trạng thái; PROPOSED |
| loại trạng thái / nguồn | lịch phòng, tình trạng thiết bị, trưng bày; owner/cadence |
| ảnh/mô hình | mã asset, checksum, version; không đưa raw nhạy cảm lên Git |
| quyền | người cấp theo vai trò, ngày, phạm vi, hạn, hạn chế và nơi lưu bằng chứng riêng |
| provenance | survey record ID, người xác nhận, ngày cập nhật |
| chất lượng | verified / cần xác minh / bị loại; lý do |

- [ ] Thu đủ ≥20 object thực có thể tương tác; không nhân bản để đủ số lượng.
- [ ] Một thiết bị nhiều mesh vẫn cùng stable ID; mỗi object truy ngược được phiếu khảo sát.
- [ ] Danh mục sanitize được AIRC kiểm tra trước đưa vào PR.

## Câu hỏi cho người phụ trách

Có chính xác bao nhiêu phòng được phép dựng? Công năng và lối nối nào được công khai? Có khu vực/đối tượng cấm chụp? Lịch phòng và tình trạng thiết bị do ai cập nhật, ở đâu, bao lâu? Có API/export Excel hoặc chỉ thủ công? Thông tin trưng bày có chủ sở hữu bản quyền riêng không? Có thể cập nhật đủ để đo ≤5 giây từ nguồn không? Ai xác nhận độ đúng mô hình, ai có quyền yêu cầu xóa? Việc công bố ảnh/model trong luận văn khác gì quyền dùng nội bộ? Có thể tổ chức thử người dùng/mượn kính tại trung tâm không?

## Điều kiện kết thúc khảo sát

Có danh sách phòng xác nhận, quyền sử dụng, bộ đo/ảnh có provenance, inventory ≥20 đối tượng và nguồn ba loại trạng thái; thiếu mục nào ghi blocker cụ thể, không ký nghiệm thu thay AIRC.

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
