# P507 R5 — phương án bố trí và tương tác ghế

**R5 PROPOSAL / PROVISIONAL / SYNTHETIC / VIRTUAL ADAPTATION**
**OWNER_VISUAL_APPROVAL=PENDING** · **PHOTO_REFERENCE_UNAVAILABLE** tại thư mục ảnh cục bộ được chỉ định.

Phạm vi đã được chủ dự án giao ngày 27/11/2026, theo Issues [#33](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/33) và [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20). R5 là ứng viên riêng cho P507. Nghiệm thu hình ảnh, khảo sát thực địa, quyền AIRC và các chỉ tiêu trên thiết bị vật lý vẫn cần bằng chứng riêng.

## Nguồn và phiên bản

| Nguồn | Kích thước X × Y × Z | Phạm vi |
| --- | --- | --- |
| Khảo sát P507 | 6,00 × 8,10 × 3,50 m | USER_REPORTED |
| Frozen R4 | 6,90 × 9,315 × 3,50 m | OWNER_APPROVED_VIRTUAL_ADAPTATION |
| R5 | Tham số trong [layout.py](../../experiments/p507-r5/layout.py) | R5 PROPOSAL |

Base `bd2d0baf4a593e73dfe1c6e8d8a5e74fd45ae3be` là merge commit sau khi [PR #32](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/32) được nghiệm thu kỹ thuật độc lập ở head `f96df72d50c3f05796a6bc528f0f0ef77abbf892`. Báo cáo R4 gốc tiếp tục là hồ sơ riêng. [Runbook R4](../../experiments/p507-webxr/README.md)

D0 trên base này khớp SHA-256 archive R4, 28 member gồm 20 PNG và 6 file khóa. E0 thật, E1 15/15, R4 IWER/Chrome 9/9, fallback 2/2, web unit 56/56, API unit 75/75. Bộ PostgreSQL Windows lần đầu 88/89 vì thiếu cờ build diagnostics. Chạy lại M1-C bị ảnh hưởng và hai bài Admin/P507 trên frozen R4 với cờ đúng được 3/3. Đây là kết quả của hai lượt chạy. Chi tiết nằm trong `.local/p507-r5/d0-bd2d0ba/`.

## Hợp đồng kỹ thuật

- Survey dùng XYZ theo mét, gốc ở góc tường logo và tường cửa. Chuyển sang glTF/Three tại ranh giới dữ liệu theo `(x,z,-y)`.
- GLB và manifest riêng cho R5 được kiểm tra độc lập theo byte và SHA-256. Hai hồ sơ `P507-CHAIR-C-09` và `P507-CHAIR-C-10` vẫn UNPLACED. Kiểm từng ID trên hình học xuất từ Blender.
- Bố trí, bàn ghế, thiết bị và collider R5 dùng riêng trong điều kiện Vite DEV loopback. Mặc định truy cập visitor dùng R4. Admin và Catalog tiếp tục đọc dữ liệu và định danh R4.
- Lối đi dùng capsule bán kính 0,30 m và cao 1,80 m. Ghế dùng hình học theo trạng thái `stored`, `pulled-out` và `occupied`. Dữ liệu occupancy thử nghiệm là synthetic và local.
- Các bề mặt do mô hình tạo dùng vật liệu trung tính. Không đưa ảnh tham chiếu, tài liệu nội bộ, quan sát người thật hoặc hình ảnh có quyền hạn chế vào Git, GLB, log hay ảnh bàn giao.

## Mở demo sau khi chuẩn bị asset

Từ `D:\Code\DATN`, chuẩn bị R4 bằng quy trình owner-local, sau đó stage đúng bundle R5 đã có lock.

```powershell
Set-Location D:\Code\DATN
python experiments/p507-webxr/validate_asset.py --prepare
python experiments/p507-webxr/verify_export_reference.py
python experiments/p507-r5/verify_export.py .local/p507-r5/<thu-muc-export> --prepare
Set-Location D:\Code\DATN\apps\web
npm run dev -- --port 5173 --strictPort
```

- [Visitor R5](http://127.0.0.1:5173/?mode=p507-visit&revision=r5) · [Visitor R4](http://127.0.0.1:5173/?mode=p507-visit)
- [Ảnh đối chiếu R5](http://127.0.0.1:5173/p507-r5-review.html?revision=r5) · [Ảnh đối chiếu R4](http://127.0.0.1:5173/p507-r5-review.html?revision=r4)
- Dùng các nút thao tác theo trạng thái ghế. Tiếp cận ghế trước khi ngồi, chọn ghế, kéo ra, ngồi, đứng và cất. AR dùng mô hình tabletop, chỉ cho thao tác ghế phù hợp với chế độ đó.

Nếu cổng bận, chọn một cổng loopback trống và đổi URL tương ứng. Nếu asset thiếu hoặc sai hash, kiểm lại đúng bản export, chạy xác minh rồi tải lại trang. Bộ test ảnh đối chiếu chạy trên Chrome và lưu PNG cùng camera, hash GLB, kích thước, thời gian tải và raw frame intervals tại `.local/p507-r5/review-*/`.

```powershell
Set-Location D:\Code\DATN
node apps/web/tests/r5-review.mjs
```

## Các góc cần chủ dự án duyệt

- Mặt bằng và các cụm A/B/C, đúng hướng bàn và hoán đổi trạng thái ghế.
- Sáu workstation và máy in, hoa lan và bộ trà, poster và đồng hồ.
- Kệ bốn tầng, bốn bình nước đáy, thứ tự đồ dọc tường tiện ích và lối vào.
- Cửa hai cánh, cửa sổ và song, các cụm trang trí, vật liệu và ánh sáng.
- Lối A–B và B–C khi hai hàng ghế được kéo ra, các điểm tiếp cận sâu trong phòng và thao tác ngồi/đứng.

Khi xem ảnh so sánh, dùng thông số camera trong report. Vị trí camera bám theo hai kích thước phòng và các điểm neo của từng revision. Chrome SwiftShader và IWER là bằng chứng kỹ thuật; AR Galaxy A17, VR HMD, Web3D 30 FPS và VR 72 FPS vẫn cần thiết bị và protocol được duyệt.

## Đối chiếu yêu cầu và bằng chứng

| Yêu cầu | Triển khai | Bằng chứng để kiểm tra |
| --- | --- | --- |
| Q1/Q7 · Kích thước, thứ tự cụm, pose và cửa | `layout.py`, `generate_blender.py` | Manifest, map ID, các góc mặt bằng/cửa, bảng phương án kích thước |
| Q2 · Thiết bị, hoa, trà | `props.py`, `prop_meshes.py` | Kiểm support/bounds, ảnh cụm A/B/C |
| Q3 · Poster và đồng hồ | `props.py`, `verify_props.py` | Khoảng tường giữa cửa sổ, vị trí quanh TV và cạnh bảng, ảnh TV/cửa sổ |
| Q4/Q5 · Khu tiện ích | `layout.py`, `props.py`, `prop_meshes.py` | Bốn mặt đỡ, thứ tự tủ, ảnh kệ và khu tiện ích |
| Q6 · Toàn bộ ghế | `layout_checks.py`, `apps/web/src/p507-r5/chairs.ts` | Swept-volume, swept-capsule, state, kiểm thử trình duyệt |
| Nâng hình ảnh · Đối chiếu R4/R5 | `generate_blender.py`, `p507-r5-review.html` | Contact sheet, neutral camera metadata, raw frame timing |
| WebXR và hồi quy | `apps/web/src/p507-m5/` và các bài kiểm thử | Chrome/IWER, R4 9 kịch bản, E0/E1, CI trên SHA ứng viên |

## Bố trí đang kiểm chứng

| Phương án | Kích thước X × Y × Z (m) | Kết quả kiểm hình học |
| --- | --- | --- |
| R4 frozen | 6,90 × 9,315 × 3,50 | Lối A–B/B–C còn 0,20/0,15 m theo mô hình kéo ghế R4 |
| R5 thử nhỏ hơn | 8,55 × 14,915 × 3,50 | Thiếu lối tiếp cận ở nhiều cấu hình và phát hiện va chạm thành phần tại B06 |
| R5 thu hẹp tiếp | 8,60 × 15,49 × 3,50 | Thiếu điểm kéo ghế hợp lệ ở B-09/B-10 sát tường phía Đông |
| R5 ứng viên | 8,63 × 15,55 × 3,50 | Phương án nhỏ nhất đã thử thỏa bộ kiểm tra hiện có |
| R5 thử rộng hơn | 8,68 × 15,605 × 3,50 | Qua kiểm hình học ghế, tăng thêm 0,05 m X và 0,055 m Y |

Hai lối ứng viên đều 3,22 m khi ghế cất và 0,94 m khi cả hai hàng kéo ra, kể cả khi thêm 34 envelope người ngồi synthetic. Các hàng chính kéo 0,98 m so với pose tham chiếu, hai cặp ghế ở đầu dãy kéo 0,66 m. Phương án dùng vùng đứng phía trước ghế để tránh lưng ghế trong chuyển tiếp. Hành trình ghế dài và tỷ lệ phòng tăng đáng kể, cần xem trong demo. Đây là kích thước virtual và là kết quả của các phương án đã kiểm bằng bộ giải hiện tại.

TV lớn và giá treo tăng cao 0,04 m, từ đáy TV 1,78 m lên 1,82 m, để capsule cao 1,80 m tiếp cận tủ trưng bày. Hướng chéo và kích thước TV được giữ. Chạy lại `python experiments/p507-r5/layout_checks.py` để xem bề rộng từng trạng thái, các điểm biên và số tuyến đã tìm được.

Blender 4.5.9 xuất lại được mô hình và manifest từ nguồn đã xác minh. Hai lượt xuất Windows cùng kích thước GLB và JSON chunk, nhưng có khác biệt byte ở UV và index. Demo dùng đúng bản ứng viên ghim trong lock. Với bản xuất mới, giữ bundle đang ghim, chạy kiểm hình học, Khronos, kiểm thử trình duyệt và review trước khi cập nhật lock.

### Tạo lại ứng viên để kiểm tra

Chạy Blender 4.5.9 LTS, với R4 editable master đã xác minh từ archive ghim và thư mục đích mới. Công cụ đọc dữ liệu R4, xuất `.blend`, GLB và manifest R5 vào thư mục ignore.

```powershell
Set-Location D:\Code\DATN
$blender = '.local/tools/blender-4.5.9-windows-x64/blender.exe'
$r5Export = '.local/p507-r5/kiem-tra-moi'
& $blender -b -t 2 --python-exit-code 1 --python experiments/p507-r5/generate_blender.py -- --output-dir $r5Export
python experiments/p507-r5/verify_export.py $r5Export --record
node experiments/p507-r5/validate_glb.mjs $r5Export
python experiments/p507-r5/verify_export.py $r5Export --verify
```

`validate_glb.mjs` dùng gói `gltf-validator` đã ghim trong thư mục công cụ cục bộ theo quy trình G1/G2. Mỗi report giữ cùng thư mục với bản model tương ứng. Dùng `--prepare` cho bản khớp lock.

Ảnh Chrome ở giai đoạn kiểm tra phát hiện cụm khung ảnh cũ chồng với phụ kiện TV và ba vật trưng bày chưa đi theo tủ thấp. Ứng viên dịch cụm khung ảnh nguyên khối thêm 0,75 m dọc X, dịch các vật trưng bày theo tủ và dịch giá treo cùng TV. Kiểm tra độc lập xác minh hình chiếu các khung, mặt đỡ tủ và giao giữa giá treo với thân TV.

Khi tab bị ẩn, thao tác kéo/cất đang chạy dở quay về trạng thái ổn định. Trạng thái đã ngồi được giữ khi tab hiện lại. Tải lại, reset và kết thúc XR xử lý trạng thái ghế theo vòng đời của viewer. Fixture hành lang dùng 34 collider người ngồi tổng hợp; trong ảnh chỉ hiển thị mô hình ghế.
