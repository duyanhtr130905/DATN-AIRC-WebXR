# P507 G1/G2 — vòng hoàn thiện tổng hợp R3

Ngày 17/11/2026. Tiếp tục [Draft PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14), base `docs/g0-p507-3d-production-spec`; không merge, deploy hoặc G3. Báo cáo này thay trạng thái hiện hành của revision 2, giữ nguyên bằng chứng lịch sử.

## Nguồn và quyền

Đã mở trực tiếp **13 ảnh thực + 3 sơ đồ**. Xem [đối chiếu trước geometry](P507-G1-G2-SURVEY-COMPARISON.md) và [manifest đã loại thông tin riêng tư](../../experiments/p507-g1-g2/reference-manifest.json). Có ảnh/sơ đồ sàn, trần, góc cửa/TV, AI wall, utility, bàn/ghế/cửa sổ và logo. Không có camera calibration, focal length/EXIF tin cậy hoặc số đo chính thức cho đồ phụ. Hình minh họa B/C riêng chưa được cung cấp; dùng sơ đồ sàn và mô tả chủ dự án.

Ảnh gốc, hash/đường dẫn nguồn và đối chiếu có ảnh thật giữ local, ngoài Git/CI. Không tái tạo nội dung màn hình, người, giấy tờ, logo hoặc artwork thật. Chỉ hai texture tile/oak tự sinh được nhúng GLB. Không tải texture bên ngoài. Các kích thước phòng/bàn vẫn USER_REPORTED/PROVISIONAL; tọa độ là PROPOSED_LAYOUT.

## Bố cục trước/sau

Đơn vị mét, bbox `[xmin,ymin,xmax,ymax]`, X cửa→cửa sổ, Y logo→TV. Baseline `775f01d603adf6cbcde8fb0cdb45123db1004b80`.

| Cụm | Baseline | R3 | Dịch chuyển |
| --- | --- | --- | --- |
| A, 6 bàn 3×2 | [1.35,6.25,5.85,7.45] | [1.35,5.75,5.85,6.95] | X giữ gần cửa sổ, Y−0.50 |
| B, 4 lõi + B05 phải + B06 trái | [0.90,3.50,5.10,5.00] | [0.98,3.15,5.18,4.65] | X+0.08, Y−0.35 |
| C, 4 lõi + C05 phải | [1.50,0.70,5.10,2.20] | [1.58,0.50,5.18,2.00] | X+0.08, Y−0.20 |

Phòng giữ **6×8.1×3.5m**, 16 bàn **1.5×0.6×0.9m**, B06 dài dự kiến1.2m, rộng/cao provisional. Không kéo giãn phòng hoặc thu nhỏ bàn để qua test. A đã dịch về cửa sổ trong revision2; R3 giữ X đó vì phần ghế phía cửa sổ đã hẹp.

[So sánh layout](../evidence/p507-r3-layout-before-after.svg). Giữ **36 ID ghế**, **24 PLACED_PROVISIONAL /12 UNPLACED**: A07/A08, B01…B08/B11/B12. Đây là phương án hiện tại ưu tiên khu tiện ích và giảm chật, không chứng minh mọi cách bố trí36 ghế đều bất khả thi. Preview liệt kê rõ từng ghế chưa đặt và lý do.

B09/B10, C11/C12 vẫn là bốn ID ghế phải, X5.42, góc90° nhìn−X vào B05/C05. Hai ghế mỗi đầu được lưu trong dữ liệu, không sinh theo bounding box.

| Khoảng tĩnh | Baseline | R3 | Giới hạn |
| --- | --- | --- | --- |
| Mép bàn A–B / B–C | 1.25 /1.30 | 1.10 /1.15 | Không bao gồm ghế |
| Envelope ghế A–B / B–C | 0.20 /0.40 | 0.51 /0.71 | Không mô phỏng kéo ghế/người |
| Ghế phải → mặt trong tường cửa sổ | khoảng0.30 theo proxy cũ | 0.26 | Vẫn chật; proxy thật có tựa lùi |
| Mặt trước tủ trưng bày → bàn A | — | 0.61 | Khoảng tĩnh, chưa là lối sử dụng |
| Nút thắt kệ giày / thùng rác | — | 0.53 /0.56 | Cần đo/điều chỉnh tiếp sau review |
| Kệ đồ → envelope ghế gần nhất | — | 1.10 | Chưa tính người dùng kệ |

**G1_CIRCULATION PARTIAL; usable walkway UNKNOWN.** Không tuyên bố an toàn/PCCC/accessibility. Không giấu ghế đã đặt để che va chạm; UNPLACED được loại khỏi render theo trạng thái công khai.

## Góc hero và nội thất

- TV P507-TV-LARGE: tâm `[0.95,7.59,2.28]`, góc25° đề xuất, giá treo có ID riêng gắn tường bắc. Mesh màn hình/viền/độ dày thật quay chéo; kiểm tra không xuyên tường.
- Máy nước P507-WATER-DISPENSER: `[0.40,7.30,0.55]`, xoay90° so với revision2; bảng điều khiển/mặt lấy nước thực nhìn+X. Thân xám/đỏ, bình có cổ/nắp/gân, vòi và khay. Bên trong phòng, ngoài vùng cửa.
- Tủ P507-CABINET-LOW: tâm `[2.25,7.82,0.525]`, kích thước dự kiến1.5×0.4×1.05m. Ngăn kéo/cánh/tay nắm/chân/viền gỗ, ba đồ trưng bày trung tính có support relation; không đè ghế.
- Cửa: vẫn Y5.45…6.95, opening dự kiến1.5×2.5m, hai cánh theo ảnh; một cánh mở60° là proposal. Tường có khoảng mở thật, khung/độ sâu/hinge/swing proxy, không phải texture trên tường đặc.
- Khu tây theo thứ tự từ logo tới cửa: tủ tài liệu `[.10,.25,.59,1.25]`, tủ lạnh `[.10,1.40,.64,2.00]`, kệ `[.10,2.15,.57,3.25]` + TV nhỏ phía trên, thùng rác `[.10,3.35,.42,3.67]`, kệ giày `[.10,3.80,.45,5.10]` dưới bảng trắng. Tất cả kích thước/tọa độ đều ước lượng, có ID/provenance/rights/mesh liên kết.
- Tường AI:27 frame riêng, A10/I9/nhóm kề8 theo đếm thủ công ảnh PHOTO-09, tỷ lệ/cao độ ước lượng. Dùng card tự tạo, không ảnh người. Tường logo dùng ring/bars và hai nhóm hex trung tính; không giả làm logo AIRC được cấp quyền.13 hex mỗi nhóm là thiết kế placeholder, không số lượng khảo sát.
- Bàn có mặt/cạnh/khung/chân; ghế navy có tựa cong, khe tay, mặt ngồi, khung sled/cantilever kim loại. Geometry dùng lại nhưng mỗi instance giữ ID.

## Trần, cửa sổ và lookdev

[Sơ đồ trần trung tính](../evidence/p507-r3-ceiling-plan.svg):8 panel ở hai cột X1.25/4.75, Y0.8/2.8/5.3/7.3;4 quạt tại Y1.8/6.3;2 AC trục X3,Y1.8/6.3; máy chiếu gần tâm, camera gắn cao. Kim cương trên sơ đồ là ký hiệu AC, không suy thành góc quay45°.

Trần thả theo ô600mm có khung/rãnh, panel có housing/diffuser, quạt có trục/cánh, AC có khung/miệng gió, projector có lens/giá. Camera: hình dáng PHOTO-09, vị trí góc cửa sổ theo owner report, LOW confidence; ảnh không chứng minh tọa độ chính xác. Bốn cửa sổ/bốn rèm riêng, độ hạ khác nhau là proposal. Top-down ẩn trần/thiết bị/tường ngoài theo camera; giữ mọi nội thất.

PBR metallic-roughness cho kem tường, gạch sáng/ron, laminate trắng, navy molded plastic, kim loại, nhựa máy nước, kính TV, gỗ/laminate tủ, thạch cao/panel. UV/texture tile/oak tự sinh, không ảnh riêng tư. Three.js dùng daylight từ phía cửa sổ, PMREM trung tính tự tạo, shadow map mềm và hai area strips xấp xỉ tổng indirect fill của8 diffuser. Đây không phải GI vật lý; ánh sáng Blender không được coi là tự chuyển sang GLB. Main canvas đầy đủ viewport; refraction target half-resolution được ghi trong metrics.

Kết quả có nhiều chi tiết nhận diện hơn baseline nhưng **vẫn là mô hình kiến trúc procedural giản lược, chưa đạt photorealistic hoàn chỉnh**. Owner phải xem ảnh thực WebGL để phê duyệt.

## Kiểm thử và bằng chứng

-56 unit tests: schema v1/v2 compatibility, stable/open IDs, bố cục,36 inventory, góc xoay/chuyển trục, ghế phải, collision3D/support, cửa/bounds, utilities, thiết bị, frames/blinds/provenance. Các fixture cũ tủ–ghế, nước ngoài cửa, ghế–bàn/ghế sai hướng vẫn phải FAIL. Sáu regression mới đã chạy RED trước fix và GREEN sau fix: không cho verified giả, support cấu trúc giả, bàn baseline UNPLACED để né collision.
- Collision dùng oriented polygons + Z interval; support phải đúng height/containment và cấu trúc gắn tường/trần được allowlist. Không tắt collision toàn cục.111 instance đã đặt có evaluated vertex proxy proof trong Blender, không chỉ kiểm danh sách JSON.12 ghế còn lại được công khai UNKNOWN.
-10 ray checks từ dưới lên bảo vệ8 mặt tán sáng và2 recess AC khỏi bị vỏ che. Đây là kiểm tra hình học bề mặt nhìn thấy, không chấm chất lượng nghệ thuật.
- Blender chạy thực, xuất editable .blend/GLB; Khronos Validator; frontend build/unit; Chrome/WebGL desktop/mobile; checker regression; repository verifier/diff/privacy checks. Kết quả cuối và exact SHA/run URL nằm trong PR handoff, không gán CI baseline775 cho R3.
- Browser chụp10 góc desktop + hero mobile, inventory disclosure và contact sheet. Kiểm tra actual exported IDs, hướng TV/máy nước từ component bounds, ghế–tủ/bounds, cửa sổ/rèm/trần, cutaway không giấu nội thất, không console errors.
- Reports có GLB bytes/hash, mesh/geometry/triangle/material counts, draw calls, texture memory estimate, load time, mọi rAF interval/p50/p95/sample count, GPU/browser/viewport/camera, input hashes và source/checkout SHA. Software GPU/mobile viewport không chứng minh FPS laptop/điện thoại/kính thật hoặc KPI72/30FPS.

Artifact CI `p507-g1-g2-neutral-blender-chrome` chỉ lấy `.local/p507-g1-g2/` (7 ngày). Chứa `.blend`, `.glb`, geometry-report/report/gltf-validation-report/browser-report JSON,11 screenshot và contact-sheet. Ảnh nguồn/overlay có ảnh thật không nằm thư mục đó. Public before/after chỉ so render GLB trung tính, cùng camera/light khi được ghi như vậy.

## Camera và nghiệm thu

Camera presets/source IDs/FOV/position/height được ghi theo từng view trong browser-report. CAM-01 hero/corner, CAM-02 entry/overview/clusters, CAM-03 photo_wall, CAM-04 logo, CAM-05 windows/ceiling. Tất cả camera **ESTIMATED, not calibrated**. Đã đối chiếu ảnh thật định tính và sơ đồ, chưa camera match1:1; thiếu lens/calibration/đo vật phụ, chưa được phép công bố side-by-side ảnh thật.

| Gate | Trạng thái |
| --- | --- |
| G1_GEOMETRY | PASS cho111 instance đã đặt;12 ghế UNPLACED được công khai |
| G1_SURVEY_ACCURACY | PROVISIONAL |
| G1_CIRCULATION | PARTIAL; usable clearance UNKNOWN |
| G2_PIPELINE | Kết quả chạy cuối theo exact-HEAD handoff/CI |
| G2_VISUAL | PENDING OWNER APPROVAL |
| PHOTO_MATCH | PARTIAL, định tính; chưa calibrated1:1 |
| REAL_DEVICE_WEBXR | NOT RUN |
| REAL_AIRC_DATA | NOT VERIFIED |
| G3 | NOT STARTED |

Cần chủ dự án xác nhận: vị trí12 ghế còn lại; lối sử dụng thực/chair pullout; kích thước utility/B06/cửa; góc TV/cánh cửa; tọa độ camera; quyền logo/art/ảnh public; chất lượng G2. Sau handoff dừng, không tự triển khai các đề xuất tiếp theo.
