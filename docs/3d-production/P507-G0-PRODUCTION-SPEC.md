# G0 — P507 Art Direction & 3D Production Specification

**Baseline 1.0 | 16/11/2026 | DOCUMENTED DESIGN STANDARD**

**Quyết định đã chốt bởi chủ dự án trong trao đổi ngày 16/11/2026:** xây dựng P507 theo phương pháp **Hybrid Photorealistic Digital Twin**; hình học dựa trên khảo sát và đo đạc; Blender là nguồn asset có thể sửa; glTF/GLB là định dạng runtime; React Three Fiber/Three.js/WebXR là renderer đã được duyệt. Không chuyển Unreal/Unity, không copy asset Vietnam3D và không dựng đẹp toàn bộ phòng trước khi chủ dự án duyệt một khu vực mẫu.

**Phạm vi G0:** đặc tả nguồn, art direction, asset pipeline, photo/camera matching, performance và tiêu chuẩn bàn giao G1–G5. Đây **không** phải xác nhận ảnh/quyền của AIRC, không phê duyệt toàn bộ roadmap ĐX-P507/ĐX-XR hoặc việc đưa dữ liệu thật lên GitHub. G0 không tạo model, không khẳng định chất lượng đồ họa đã đạt.

Nguồn có thẩm quyền: [ROADMAP](../ROADMAP.md), [PROJECT_STATUS](../PROJECT_STATUS.md), [KPI](../02-requirements-kpi.md), [checklist khảo sát](../04-airc-survey-checklist.md), [data model](../13-data-model.md), [API contracts](../14-api-contracts.md), [ADR-0001](../decisions/0001-technology-options.md), [M1-C acceptance](../18-m1-c-vertical-slice-acceptance.md). Các acceptance M0/M1 là lịch sử đã merge; dữ liệu AIRC thực chưa được công bố.

> **One-shot rule:** đây là **một bản đặc tả G0 chuẩn**, không chia G0-fix-1/2/3. Khóa **phương pháp** nhưng KHÔNG khóa **dữ liệu**. Mọi số đo, asset, inventory, tọa độ chưa chắc có thể thay đổi qua revision khảo sát hoặc G1/G2 mà không sửa lại art direction. Một lỗi G0 chỉ được mở lại nếu là blocker có bằng chứng, mâu thuẫn với thiết kế đã duyệt hoặc vi phạm quyền/an toàn.

## 1. Mục tiêu và thứ tự ưu tiên

1. **Trung thực với P507:** đúng hình dạng, kích thước theo mức đo, vị trí tương đối, vật liệu và nhận diện; không tạo phòng văn phòng generic hay nhận sai số đo giả định là real.
2. **Chất lượng realtime có chủ ý:** bề mặt PBR, cạnh bo và chân bàn/ghế có silhouette, bóng tự nhiên, phối cảnh ổn định, color management nhất quán.
3. **Tương tác Digital Twin:** hình ảnh VISUAL tách biệt với vùng tương tác PROXY và dữ liệu Catalog/State. Một đồ vật nhiều mesh vẫn có một survey ID; UUID từ DB không sinh bằng vị trí.
4. **WebXR có giới hạn tài nguyên:** bản Blender đẹp không phải chứng cứ GLB đẹp hoặc FPS trình duyệt. Browser preview là môi trường nghiệm thu mỹ thuật và chất lượng xuất.
5. **Quyền dữ liệu:** không đưa ảnh chứa người, màn hình công việc, thông tin trên bảng, giấy tờ, số điện thoại, serial hoặc ảnh/logo chưa cấp quyền vào Git/build.

**Cảm hứng Vietnam3D:** chỉ mượn cảm giác môi trường game 3D, góc nhìn và chuyển động, mức đầu tư môi trường; không suy ra engine, pipeline, fidelity 1:1 của sản phẩm tham chiếu, không sao chép mỹ thuật/gameplay.

## 2. Nguồn khảo sát và chứng cứ ảnh

Trong cuộc trò chuyện ngày 16/11/2026, chủ dự án gửi bảng kiểm kê, sơ đồ sàn, sơ đồ trần và các ảnh P507. **Không có file ảnh đó trong repo chỉ vì chúng đã được gửi trong chat**. Tài liệu này ghi mô tả nguồn và không bịa filename/hash/EXIF/quyền AIRC.

| ID tham chiếu | Mô tả và chức năng | Trạng thái |
| --- | --- | --- |
| SRC-01 | Bảng kích thước phòng, đồ vật, số lượng | USER_REPORTED, chưa AIRC verified |
| SRC-02 | Sơ đồ mặt bằng P507, ba cụm bàn, tường cửa và cửa sổ | USER_DRAWN, không phải bản vẽ CAD đúng tỷ lệ |
| SRC-03 | Sơ đồ trần cùng phương với mặt bằng, đèn/quạt/AC | USER_DRAWN |
| PHOTO-ENTRY-TV | Cửa, TV lớn, bình nước, tủ trưng bày | USER_PHOTO, rights PENDING |
| PHOTO-LOGO | Tường logo AIRC và hai dãy ảnh lục giác | USER_PHOTO, rights PENDING |
| PHOTO-UTILITY | Khu bảng trắng, kệ giày, TV nhỏ và kệ đồ | USER_PHOTO, có giấy tờ cá nhân/nội bộ |
| PHOTO-DESKS | Góc nhìn dọc ba cụm bàn và phía cửa sổ | USER_PHOTO, có người và màn hình |
| PHOTO-CEILING | Trần, 8 đèn, quạt, AC âm trần, máy chiếu, camera | USER_PHOTO, vị trí cần đối chiếu |

**Thứ tự ưu tiên khi có mâu thuẫn:** số đo thực có xác nhận và sai số > số đo do người dùng cung cấp > ảnh/điểm neo tương đối > sơ đồ phác > layout tự căn. Không sửa số đo đã xác nhận để cho ảnh trông đẹp; báo mismatch và phương án kiểm tra.

**Reference manifest LOCAL** (không commit raw assets): nguồn ID; file hash; ngày đo/chụp; phương pháp; ảnh gốc/lens/focal length nếu có; camera position/orientation nếu có; quyền lưu/dựng/PR/demo/luận văn; checksum; status VERIFIED / USER_REPORTED / ESTIMATED / PROPOSED_LAYOUT / UNKNOWN; allowed_outputs. Ảnh gốc phải lưu ở nơi được phép và hạn chế quyền. Ảnh đã blur để chia sẻ có thể làm hỏng camera matching; nếu cần dùng bản gốc để match thì chỉ xử lý offline theo quyền đã cấp.

## 3. Spatial & inventory baseline (OPEN)

| Trường | Giá trị tạm dùng | Bất định |
| --- | --- | --- |
| Không gian P507 | 8.10 m × 6.00 m × 3.50 m | USER_REPORTED, chưa đo đối chứng |
| Cửa | một cửa phía tường trái, gần TV; khoảng 1.50 m rộng × 2.50 m cao | vị trí, cung mở và bậc cửa chưa đo |
| Cửa sổ | bốn cái trên tường phải, mỗi cửa khoảng 1.50 m × 2.00 m | bậu/cao độ/khoảng cách chưa đo |
| Bàn | 16 bàn thường, khoảng 1.50 × 0.60 × 0.90 m; một bàn nhỏ | 17 bàn đã xác nhận, bàn nhỏ khoảng 1.20m dài suy từ hai cạnh ngắn bàn thường; rộng/cao chưa đo |
| Cụm A | 6 bàn: 3 bàn × 2 hàng; chiều dài bàn hướng tường cửa → tường cửa sổ | ảnh phải đối chiếu trước khi khóa placements |
| Cụm B | 6 bàn: 4 ghép 2×2, 1 bàn tiêu chuẩn quay dọc bên phải, 1 bàn nhỏ bên trái | vị trí và bàn nhỏ còn ước lượng |
| Cụm C | 5 bàn: 4 ghép 2×2, 1 bàn tiêu chuẩn quay dọc bên phải | vị trí còn ước lượng |
| Khoảng cách giữa cụm | người dùng ước lượng khoảng 1.50m | không phải lối đi thông thủy khi ghế kéo ra |
| Ghế | 36 chiếc | chưa phân bổ vị trí chính xác |
| Trần | 8 đèn 0.60×0.60m, 4 quạt, 2 điều hòa âm trần, 1 máy chiếu trần gần tâm | camera trên cao góc gần cửa sổ; cao độ chưa đo |
| TV | 1 lớn treo góc gần cửa (~80 inch theo bảng), 1 TV/màn hình nhỏ trên kệ | chưa đo kích thước màn nhỏ |
| Nội thất phụ | tủ trưng bày thấp, tủ tài liệu, tủ lạnh, kệ để đồ, kệ giày, bảng trắng, máy nước, thùng rác, đồng hồ | chưa đủ chiều sâu và vị trí chính xác |
| Nhận diện | logo AIRC và chữ trên tường cuối, 2 nhóm ảnh lục giác, khung ảnh/poster | số lượng chi tiết/quyền chưa được xác nhận |
| Thiết bị khác | máy tính/màn hình/quạt đứng/rèm và đồ phát sinh | mở rộng không giới hạn, chưa kiểm kê riêng |

**Mỗi bàn có ID độc lập**: A01–A06, B01–B06, C01–C05; B06 là bàn nhỏ. Số lượng là dữ liệu theo phiên khảo sát, không được hardcode thành giới hạn của hệ thống. Object bổ sung dùng ID mới; không renumber hoặc tái sử dụng ID khi sửa kích thước/tên. Mỗi item ghi category, dimensions + source/confidence, transform + source, room, rights, evidence, interaction type, state source, revision. Không đánh đồng 17 bàn với ≥20 đối tượng tương tác được xác minh theo KPI.

**Tọa độ chuẩn khảo sát:** Blender Z-up, đơn vị m; gốc khảo sát tại góc tường logo gần tường cửa, X hướng sang tường bốn cửa sổ (0..6), Y về phía TV (0..8.10), Z lên trần (0..3.50). Trong Three.js Y-up: chỉ đổi hệ trục **một lần** tại boundary bằng phép chuyển tay phải có test, ví dụ survey (x,y,z) -> Three (x,z,-y); không double convert trục vì GLTFLoader đã xử lý root orientation.

**Lưu ý cực kỳ quan trọng:** Bản tọa độ G0-v0.4 từng đề xuất A Y=6.25..7.45, B Y=3.50..5.00, C Y=0.70..2.20, khoảng trống 1.25m/1.30m chỉ là **PROPOSED_LAYOUT**. Không khóa thành mặt bằng thực; chưa tính 36 ghế, tủ, cửa, đường đi hoặc an toàn PCCC. G1 phải xây occupancy 2D và cảnh báo va chạm khi đủ đồ vật; nơi chưa có dữ liệu ghi UNKNOWN.

## 4. Art Direction: grounded architectural realism

**Không lựa chọn phong cách tùy ý trong Codex.** Mọi vật liệu, mô hình và hậu kỳ theo ảnh P507, không chạy theo phong cách game fantasy hoặc studio showroom.

| Loại bề mặt | Look mục tiêu | Không được làm |
| --- | --- | --- |
| Tường | sơn kem nhạt, góc/chân tường rõ, nhám nhẹ | tường phẳng trắng generic hoặc tự đổi màu bão hòa |
| Sàn | gạch sáng, đường ron đúng tỷ lệ, phản chiếu rất nhẹ | sàn gương/bề mặt nhiễu, texture kéo giãn |
| Trần | ô trần lưới, tấm 600×600 và đèn panel, cassette AC/quạt/projector | trần một mặt phẳng trống với đèn giả |
| Bàn | laminate trắng, độ dày cạnh, chân/khung kim loại, bevel vừa | các khối hộp trắng không chân |
| Ghế | lưng nhựa tối hơi cong, khung kim loại, chân thực tỷ lệ | cube/chair clipping; nhân bản hình học thừa |
| TV, màn hình | viền/độ dày/giá đỡ, màn kính đen phản xạ mềm | hiển thị nội dung màn hình làm việc thật |
| Tủ, kệ, bảng | silhouette tách lớp, tay nắm, kính và phản xạ có kiểm soát | in ảnh bản gốc chứa PII lên surface |
| Logo, ảnh, poster | giữ bbox/tông và vị trí; placeholder trung tính khi chưa có quyền | chèn logo hoặc ảnh nhạy cảm vào public GLB |
| Ánh sáng | daylight qua bốn cửa sổ + LED ấm/trung tính trên trần, contact shadows mềm | bề mặt cháy sáng, AO đen bệt, bóng gắt vô lý |

**Presets roughness/metallic chỉ là thông số khởi tạo lookdev, không phải phép đo:** tường roughness 0.8–1.0; laminate 0.35–0.65; chân kim loại metallic 0.7–1; màn hình roughness 0.15–0.45; gạch sàn 0.25–0.5. Phải chỉnh dựa trên ảnh và **Three.js thực** thay vì lấy ảnh render Blender để tuyên bố hoàn thành.

**Levels of detail:** HERO (góc TV lớn/cửa/tủ/bình nước/bàn gần camera) phải có silhouette, cạnh bo, phụ kiện và vật liệu chi tiết; MID (bàn ghế lặp, tủ, bảng, cửa sổ) có mesh modular; BACKGROUND (đồ trang trí nhỏ và ảnh) ưu tiên texture/placeholder được cấp quyền. Scan/photogrammetry chỉ cho các vật thể hợp lý và được phép; không lấy Gaussian Splat làm scene tương tác chính. Không bắt buộc máy LiDAR.

## 5. Asset architecture & Blender-to-WebXR

**Blender master** (.blend có thể sửa): collections 10_ARCH, 20_FURNITURE, 30_EQUIPMENT, 40_CEILING, 50_DECOR, 60_INTERACTION_PROXY, 80_LOOKDEV_CAMERAS, 90_REFERENCE_LOCAL. Không xuất reference images, helper, camera reference/rig Blender vào production GLB. Tên mesh có survey instance ID, ví dụ P507_FUR_TABLE_A01, và asset manifest có mapping ID ổn định.

**Tách VISUAL khỏi INTERACTION:** cùng một geometry bàn có thể instance 16 lần, nhưng userData/metadata/survey ID riêng trên từng instance và raycast proxy riêng theo nhu cầu. Đối tượng nhiều meshes vẫn một ID. State equipment_status, room_schedule và exhibit_info từ API phải cập nhật panel/overlay rõ ràng mà không làm toàn bộ TV/bàn biến thành khối đỏ mất chân thực.

**Quy trình asset:** hi-poly source (khi cần) -> retopology/low-poly -> UV -> PBR -> kiểm normals/scale/meshes -> glTF 2.0 GLB -> Khronos glTF Validator -> browser Three.js preview -> đo hiệu năng -> kiểm với ảnh khảo sát -> mới sử dụng production khi có quyền. Giữ source và derivative riêng; theo dõi hash, phiên bản Blender/exporter, version ảnh/quyền, unit/basis, triangle, materials, textures, dung lượng, dependencies, license.

**Không overengineer bằng magic number:** chưa ấn định giới hạn MB/triangle/texture vô căn cứ. Các ngưỡng được thiết lập sau benchmark G2 trên máy mục tiêu. Ưu tiên reuse, instancing, atlas, KTX2, mesh compression, LOD/lazy loading chỉ sau đo và kiểm tương thích; không cho nén làm vật liệu/UV sai.

**Color & lighting parity:** Blender glTF exporter xuất những vật liệu/glTF-supported nodes; **Area lights và Blender World không xuất thành lighting tương đương**. Ánh sáng runtime phải thiết kế trong Three.js hoặc bake tĩnh phù hợp. Color base/emissive sRGB; normal/roughness/metalness non-color; output color management/tone mapping nhất quán. Không bake bóng của vật thể có thể chuyển động cố định vào nền. Vì vậy **Blender screenshot không thay cho browser screenshot**.

**Kiểm nghiệm trục:** Blender Z-up và GLB root orientation phải khớp Three Y-up; test vị trí TV trái, bốn cửa sổ phải, logo cuối, pháp tuyến tường, không bị gương/mirror hoặc áp chuyển trục 2 lần.

## 6. Camera matching & visual QA

**Bộ shot nghiệm thu tham chiếu**, ảnh gốc phải được cấp quyền và file thực cần mở được tại môi trường kiểm thử:
- CAM-ENTRY: từ cửa nhìn vào toàn bộ cụm bàn;
- CAM-TV: góc cửa/TV lớn/tủ thấp/bình nước;
- CAM-LOGO: mặt trước tường logo AIRC;
- CAM-UTILITY: khu bảng/kệ giày/kệ đồ/TV nhỏ;
- CAM-WINDOW: nhìn dọc dãy cửa sổ.

G1 dùng tối thiểu **ba góc** để so anchor geometry; G2 dùng tối thiểu **hai góc**, bắt buộc CAM-TV. Với ảnh thiếu EXIF/lens hoặc lens distortion, fSpy/vanishing points chỉ ước tính camera, không chứng minh tọa độ vật thể. Camera height/focal length/FOV, aspect ratio, crop, exposure, lighting và renderer SHA phải được ghi lại.

**Phương pháp QA:** chụp render tại camera khớp, overlay 50% và side-by-side; đánh dấu chân tường, cạnh cửa, cửa sổ, ô trần, mép bàn, chân bàn, logo placeholder, TV và tủ. Kiểm shape/scale/silhouette trước; sau đó vật liệu (tường/gạch/kim loại/kính), exposure, bóng, specular và chiều sâu. Nếu thiếu ảnh đủ hợp lệ, báo BLOCKED ở tiêu chí photomatch; tuyệt đối không bịa điểm ảnh hoặc tỷ lệ similarity. Pixel diff chỉ dùng regression khi camera và render conditions giống nhau, **không** dùng pixel diff một mình làm bằng chứng thẩm mỹ.

**Visual lookdev G2:** hoàn thiện **một khu vực mẫu** quanh cửa → TV lớn → tủ trưng bày thấp → bình nước → phần bàn gần cửa. Phải thấy được điểm khác biệt so với prototype khối hộp; render trong Three.js và có screenshot/video. **Chủ dự án** duyệt mắt sau khi xem bằng chứng; Codex/test xanh không thay sign-off.

## 7. Performance & compatibility

KPI nguồn không đổi: ≥3 phòng, ≥20 đối tượng tương tác có đối chứng, ba trạng thái, source-to-render ≤5s, Web 3D ≥30 FPS, VR mục tiêu ≥72 FPS, MT2/MT3 khác theo [KPI](../02-requirements-kpi.md). **Chưa được nghiệm thu trên P507.**

- Profile LOW/MEDIUM/HIGH cho desktop/mobile/XR; adaptive DPR và shadows/texture based on measured capability, không render mọi thứ ở ultra để giảm FPS.
- Báo cáo raw/transfer GLB bytes, triangle/vertex, draw calls, materials, textures, texture memory estimate, load time, frame-time p50/p95/min/max và GPU/browser/viewport/build SHA. Browser desktop+mobile viewport là smoke, **không phải Android/Galaxy vật lý**.
- Dùng công cụ validator và render/browser thật với 3 góc; WebGL fallback và loading/error handling; không tự mở camera/XR session.
- G1 ưu tiên geometry; G2 giữ chất lượng trong real browser và đánh giá mục tiêu ≥30fps trên thiết bị thử; FPS software renderer CI không thay bằng chứng GPU thực.
- Chưa có kính VR thì ghi BLOCKED, không claim 72 FPS.
- Bài kiểm tra latency source-to-render phải có nguồn trạng thái thực/t_source, không suy từ CLI synthetic hoặc CSS color change.

## 8. One-pass gates và phân chia quyền

| Gate | Deliverable | Tiêu chí | Dừng ở đâu |
| --- | --- | --- | --- |
| G0 **hiện tại** | Tài liệu production spec, nguồn/unknown/rights, art/asset standards, QA/DoD, handoff | Một PR tài liệu, review tập trung các mâu thuẫn/thiếu sót có ảnh hưởng; **không sản xuất GLB trong G0** | Chỉ bàn giao PR, không tự merge |
| G1 Geometry | Blender editable scene, data-driven inventory, shell/cửa/cửa sổ/trần, đủ 17 bàn, ghế và tủ placeholders, collision report | Bounds/ID/non-overlap, scale/axis, G1 ≥3 photomatch shots nếu có ảnh hợp lệ; GLB hợp lệ và browser blockout | Được triển khai khi chủ dự án giao |
| G2 Hero visual | Một khu vực cửa–TV–tủ–bình nước, vật liệu PBR, ánh sáng, browser preview và 2 camera incl. CAM-TV | có hình dáng/thẩm mỹ tốt, ảnh đối chiếu, glTF validation và measured FPS; người dùng sign-off | **Không mở rộng G3 trước khi người dùng duyệt hình** |
| G3 Full room | tất cả item đã duyệt trong inventory revision mới, uniform art quality | room walkthrough, scene correctness, privacy | chỉ sau G2 sign-off |
| G4 WebXR runtime | production-allowed GLB và runtime integration | fidelity/performance, controlled XR sessions/collision/fallback | riêng task có scope |
| G5 Digital Twin | Catalog UUID mapping, selection, state, provenance | backend source permissions, end-to-end, no fake real_verified | riêng task có scope |

**Không tạo G0-fix vòng lặp:** style, tools, coordinate, QA and ownership trong tài liệu này được chốt. Những việc như đo lại tủ, bổ sung màn hình hoặc sửa vị trí bàn được cập nhật **survey revision**, không mở một phiên G0 mới. Nếu có phát hiện thực sự ngăn triển khai (sai trục, quyền không đủ, số đo mâu thuẫn), báo một nhóm issues có evidence và xử lý trong G1; chỉ thay baseline G0 khi chủ dự án chủ động yêu cầu sửa quyết định. Có thể nghiệm thu G0 một lần, nhưng không cam kết G2 sẽ đạt ngay lần dựng đầu tiên vì đánh giá mỹ thuật là kiểm chứng thực tế.

**Ownership:** chủ dự án xác nhận ảnh/quyền/art acceptance; ChatGPT/Codex lập đặc tả, kiểm source/tests; Codex hỗ trợ Blender scripting, automation, glTF/browser QA; Blender artist/user kiểm visual. Không mở rộng G3 khi G2 chưa được duyệt.

## 9. G1/G2 executable handoff (không cần thiết kế lại)

Khi user giao G1–G2, Codex đọc [AGENTS](../../AGENTS.md), ROADMAP, PROJECT_STATUS, KPI, tài liệu này và hồ sơ survey được phép. Tạo **một branch/PR**, hai checkpoint G1 geometry → G2 hero lookdev; commit tách biệt. Không cần hỏi giữa các bước nếu dữ liệu đủ và không vi phạm quyền, nhưng **dừng trước G3**, không tự merge.

Deliverable G1/G2 bắt buộc:
1. Inventory input schema **mở**, stable instance IDs; explicit measured/proposed/unknown/rights.
2. Blender script/source có thể sửa; vị trí 17 bàn, optional ghế/tủ có provisional collision checks.
3. Nếu Blender unavailable: script + tests, đánh NOT RUN đối với GLB; không giả định đã render.
4. Camera reference/overlay có kiểm quyền và dữ liệu thực được cấp; nếu chưa có, không commit raw photos hoặc tự chế evidence.
5. 3D browser preview riêng hoặc cờ dev rõ, không phá M1-C synthetic live production.
6. glTF Validator, basis/scale/normals/mesh/material checks, mobile+desktop screenshot, raw timing/draw-call/asset stats.
7. Đối chiếu hero material/lighting trực tiếp ở Three.js, thu phản hồi của chủ dự án trước khi mở rộng.
8. Báo cáo issue còn thiếu, tests executed/NOT RUN, exact SHA, quyền, vết nguồn, xác nhận chưa real_verified hoặc KPI PASS.
9. Không tạo write API, migration hoặc triển khai AIRC thật khi chưa có approval.

## 10. Các điểm phải bổ sung trong survey revision, không phải G0-fix

- Vị trí chính xác 1 cửa, 4 cửa sổ và bậu/mép; kích thước cửa, chiều sâu tủ/kệ; tọa độ các cụm, ghế lúc kéo ra; bàn B06.
- Danh sách chi tiết các máy tính/màn hình, quạt phụ, khung ảnh, poster, vật thể phát sinh.
- Quyền đo/chụp/lưu trong repo/dựng 3D/chiếu demo/báo cáo và logo/ảnh AIRC, chính sách xử lý PII.
- Ba nguồn trạng thái, người cập nhật, t_source để đo ≤5s.
- KPI ba phòng với giảng viên; hỗ trợ AR/VR vật lý và kế hoạch kiểm thử. Issues #1–#5 vẫn mở.

## 11. Official technical references

- Blender glTF exporter: https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
- Three.js color management: https://threejs.org/manual/pages/color-management.html
- fSpy camera matching: https://fspy.io/basics/
- Khronos glTF Validator: https://github.com/KhronosGroup/glTF-Validator
- Khronos glTF format: https://github.com/KhronosGroup/glTF
- Three.js GLTFLoader: https://threejs.org/docs/#examples/en/loaders/GLTFLoader
- CC0 materials (license must be confirmed per asset): https://polyhaven.com/license and https://ambientcg.com/license

**Change log:** v1.0, 16/11/2026 — standardized G0 one-shot art direction, open survey input, exact boundary of Blender-vs-WebGL, reference/photo QA, rights and G1/G2 acceptance. No survey image/GLB was committed as part of G0.
