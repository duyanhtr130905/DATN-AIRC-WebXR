# P507 G1/G2 — đối chiếu nguồn trước khi sửa geometry

Ngày16/11/2026. Baseline775f01d603adf6cbcde8fb0cdb45123db1004b80, PR#14. Tài liệu này được lập **trước khi thay geometry** trong vòng triển khai tổng hợp; cập nhật quan sát/triển khai sau này phải phân biệt rõ.

## Nguồn đã thực sự mở

13ảnh thực PHOTO-01…13 và3sơ đồ SKETCH-FLOOR/SKETCH-CEILING/CEILING-DIGITAL đã được mở trực tiếp. Manifest public chỉ chứa source ID/mô tả, không filename/ảnh gốc/nội dung riêng tư. Hash/đường dẫn gốc ở.local/p507-reference-analysis/reference-manifest-private.json, không Git/CI. Thư mục private được chỉ ban đầu không tồn tại; chủ dự án sau đó cấp quyền bộ ảnh D:/Photos/AIRC và ba attachment. Không tìm dữ liệu ngoài các vị trí được cấp.

| Nguồn | Phạm vi quan sát |
| --- | --- |
| PHOTO-01/13 | Góc TV/cửa/máy nước/tủ; hai cánh cửa, TV tại góc, mặt lấy nước quay vào trong |
| PHOTO-02/09 | Tường khung ảnh: A, I và một nhóm khung liền bên; frame trắng/viền gỗ, không phải bố cục ngẫu nhiên |
| PHOTO-03/06/07/08 | Các cụm bàn, ghế tối màu, chân kim loại, bốn cửa sổ và rèm; có người/màn hình nên không xuất nguồn |
| PHOTO-04/05/11 | Tủ tài liệu, tủ lạnh, kệ xanh nhiều tầng + TV nhỏ, kệ giày dưới bảng trắng, thùng rác |
| PHOTO-10 | Nhận diện tường logo và hai nhóm ảnh lục giác; quyền logo/nội dung chưa có |
| PHOTO-12 + các ảnh trần | Trần thả/khung ô, panel, quạt, hai AC, máy chiếu có giá; camera nhỏ chỉ quan sát tương đối |
| SKETCH-FLOOR | A3×2, B4+lateral2, C4+right1, west utility zone, corner TV, cabinet, west door/east windows |
| SKETCH-CEILING + CEILING-DIGITAL | Hai cột4panel,4quạt giữa các hàng,2AC ở trục giữa; cùng hướng mặt bằng |

## Đối chiếu baseline

A. **Đã đúng có giới hạn:** phòng6×8.1×3.5m,16bàn thường+1bàn nhỏ,36IDghế, lõi B/C và bốn ghế phải; trục survey→glTF một lần; cửa có void; bốn cửa sổ. Các tọa độ đều provisional.

B. **Sai/thiếu quan hệ vị trí:** TV baseline phẳng trên tường thay vì chéo góc; máy nước mặt điều khiển nhìn−Y thay vì xoay90° sang+X; B/C chưa dịch sang cửa sổ; .20/.40m giữa chair proxies không phải lối dùng được. Tủ/máy nước/cửa chỉ cách5–9cm không được coi là corridor. Cần giải quyết bằng layout/placement công khai, không thu nhỏ phòng/bàn hay ẩn ghế.

C. **Đối tượng thiếu:** file cabinet/fridge/shelf/shoe rack cònUNPLACED, thiếu smallTV/whiteboard/bin; thiếu camera trần; ceiling modules còn sơ lược. Sơ đồ và ảnh xác nhận thứ tự utility từ phía logo: tủ tài liệu→tủ lạnh→kệđồ/TVnhỏ→thùngrác/kệgiày+bảngtrắng→cửa. Không dựng giấy tờ/chai lọ/cốc/dây riêng tư.

D. **Kích thước chưa xác minh:** cửa/window offsets, đồ utility, cabinet, chair models và độ cao thiết bị; B06 chỉ có chiều dài dự kiến1.2m. Giữ1.5×.6×.9m bàn chuẩn. Sơ đồ vẽ tay không đúng tỷ lệ; ảnh JPEG không camera calibration, không suy thànhMEASURED.

E. **Bàn/ghế:** kiểu ghế thực có lưng hơi cong và khung kim loại chạy dạng cantilever/sled, khác ghế bốn chân thẳng baseline. Vị trí ảnh cho thấy một số ghế thu sát/luồn dưới mặt bàn; không giả định đủ khoảng kéo ghế. Giữ36ID, cho phépUNPLACED có lý do nếu tủ/circulation không vừa. Giữ chính xác bốn right-end IDs.

F. **Nhận diện cần ưu tiên:** TV chéo/góc cửa hai cánh; cabinet trắng viền gỗ với ngăn kéo; dispenser xám mặt lấy nước vào phòng; AI photo arrangement; utility shelves xanh/kim loại + whiteboard; rèm cuốn hạ từng cửa khác nhau; trần ô600mm có thiết bị có housing/vents. Logo/ảnh thật chỉ dùng silhouette/layout trung tính chưa có quyền.

G. **Không thể kết luận từ nguồn:** đo tọa độ tuyệt đối, opening swing angle chính xác, góc TV chính xác, lens/camera heights và clearance an toàn. Góc xoay/coords dự kiến phải có PROPOSED_LAYOUT. Diamond của sơ đồ trần là ký hiệuAC, không chứng minh AC quay45°. Một hình dọc bên phải C chưa có nhãn rõ: không tự biến thành bàn thứ18.

## Hướng xử lý được phép và giới hạn

Tạo một revision có ràng buộc hình học: B/C dịch nhẹ+X; tách utility placements khỏi chairs; tăng static inter-cluster corridor bằng tái bố trí vàUNPLACED khi cần; không ép36ghế vào lối. TV góc chéo đề xuất, dispenser quay+90° thật, door two-leaf theo ảnh nhưng góc mở đề xuất. Frame layout lấy quan hệ trực quan PHOTO-09:10frame tạoA,9frame tạoI,8frame nhóm kề bên (đếm thủ công, tỉ lệ và cao độ vẫn ước lượng). Mỗi frame độc lập, không ảnh người/nội dung thật. Trần theo2cộtpanel/fans+2centralAC, projector giữa, camera theo vị trí tương đối ownerreported.

PHOTO_MATCH hiện **PARTIAL** vì đã đối chiếu nguồn thật; chưa calibrated1:1. Sẽ lưu camera preset/sourceID/FOV/height/ước lượng và overlay nội bộ nếu phù hợp. Mọi ảnh overlay có nguồn thật phải giữlocal, tách khỏi artifactneutral. Không tự chấmG2_VISUAL PASS.
