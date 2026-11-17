# P507 R4 — đóng băng bố cục ảo để bàn giao thử WebXR

Ngày17/11/2026. Tiếp tục PR#14, base G0/PR#13 không đổi. Task chỉ sáu chỉnh sửa chủ dự án vừa chốt; không merge, deploy, G3 hoặc WebXR runtime. Trạng thái asset: **READY FOR WEBXR EXPERIMENT**, chờ ChatGPT/chủ dự án nghiệm thu. Đây là đóng băng phạm vi thử, không chứng nhận fidelity hoặc photorealism.

## 1. Hai bộ kích thước và migration

| Bộ dữ liệu | X×Y×Z (m) | Nguồn |
| --- | --- | --- |
| survey_baseline |6.00×8.10×3.50|USER_REPORTED, chưa AIRC xác nhận|
| room / virtual_experience |6.90×9.315×3.50|OWNER_APPROVED_VIRTUAL_ADAPTATION|

Đây là quyết định virtual adaptation mới, thay ràng buộc không mở rộng phòng ở các task R3 trước; không sửa G0 hoặc đổi số đo gốc. Diện tích tăng32.25%, chiều cao không đổi. Preview có nhãn đầy đủ +15% và không phải phòng thật1:1. Schema3 giữ riêng survey_baseline và virtual_experience; migration v1/v2 bảo toàn số đo/ID cũ, không tự tạo phê duyệt mở rộng cho fixture lịch sử. [R3 fixture](../../experiments/p507-g1-g2/fixtures/schema-v2-r3-baseline.json) giữ nguyên dữ liệu trước sửa.

Không scale bàn/ghế/hero/cửa sổ/thiết bị. Chỉ shell, grid, vị trí và hạng mục kệ được chủ dự án cho phép thay kích thước. UV sàn theo600mm, không kéo giãn texture. Trục survey Z-up→glTF/Three(x,z,−y) chỉ chuyển trong export.

[Bản vẽ so sánh R3/R4](../evidence/p507-r4-layout.svg).

## 2. Layout và 34 ghế

BBox `[xmin,ymin,xmax,ymax]`, đơn vị mét.

| Cụm | R3 | R4 |
| --- | --- | --- |
| A6,3×2 |[1.35,5.75,5.85,6.95]|[1.80,6.40,6.30,7.60]|
| B6,lõi4+phảiB05+tráiB06 |[.98,3.15,5.18,4.65]|[1.70,3.45,5.90,4.95]|
| C5,lõi4+phảiC05 |[1.58,.50,5.18,2.00]|[2.30,.55,5.90,2.05]|

17 bàn giữ ID/kích thước1.5×.6×.9m; B06 dài1.2m, rộng/cao provisional.36 ID ghế lịch sử giữ nguyên, không khẳng định đã kiểm kê lại phòng thật:

- A01…A06 hàng dưới, A07…A12 hàng trên:6+6. X2.175…5.925, Y6.12/7.88; orientation0°/180° nhìn vào bàn.
- B01…B04 dưới, B05…B08 trên:4+4, Y3.32/5.08. B09/B10 đầu phải X6.20/Y3.85,4.55,90°. B11/B12 đầu trái X1.40/Y3.85,4.55,270°.
- C01…C04 dưới, C05…C08 trên:4+4, Y.42/2.18. C11/C12 đầu phải X6.20/Y.95,1.65,90°.
- C09/C10:UNPLACED/UNASSIGNED, placement_allocation=null, không center/mesh. Lý do ngoài sơ đồ34 ghế vừa được chủ dự án chốt; historical_cluster vẫn C.

Tổng inventory lịch sử36, bố cục được chốt34, đặt34, chưa bố trí2. Không đổi ID/thu nhỏ ghế hoặc dùng heuristic chia đều quanh bbox. Full-size chair proxy localX±.23/localY−.27…+.23, cao1.02m, giữ từ R3.

## 3. Clearance tĩnh và sử dụng

| Khoảng | Tĩnh | Proxy sử dụng |
| --- | ---: | ---: |
| Mép bàn A–B/B–C |1.45/1.40|Không dùng mép bàn thay lối đi|
| Envelope ghế A–B/B–C |.50/.60|.20/.30|
| Trục đi chính phía Tây, min theo lát cắt Y |1.08|.93|
| Sau ghế phải tới mặt trong tường cửa sổ |.38|.23|
| Mặt tủ thấp tới tựa ghế A gần nhất |.625|.475|

Proxy sử dụng dịch nguyên envelope ghế lùi0.15m ngược hướng ngồi, không thu nhỏ mesh hoặc envelope. Đây là giả định kỹ thuật có khai báo, không phải chair-pullout đo thực/người/đầu gối.0 collision trong hai trạng thái. Trục Tây dùng mục tiêu thiết kế đề xuất0.80m; kiểm tra lát cắt là bằng chứng hình học có giới hạn, chưa thay kiểm tra đường đi capsule/người dùng. Khoảng giữa cụm và sau ghế phải không coi là through-route. Tiếp cận tủ thấp vẫn hẹp khi kéo ghế, cần thực nghiệm sau; circulation **PARTIAL**, không xác nhận PCCC/an toàn/accessibility. Không triển khai locomotion trong task này.

## 4. Cửa mở ngoài

Giữ tường Tây, opening Y6.665…8.165, rộng dự kiến1.5m/cao2.5m. Vị trí mới giữ offset tương đối phía TV trong phòng mở rộng. Hai stable leaf IDs giữ nguyên, chiều mở OUTWARD theo chủ dự án; góc demo±60° vẫn PROPOSED_LAYOUT.

HingeX−.05m, leaf01 tạiY6.665, leaf02 tạiY8.165. Tâm demo X≈−.37476, Y6.8525/7.9775, Z1.25. Mesh thật mở ngoài, giữ khung/kính/handle. Sweep từng cánh là sector theo hinge+angle; envelope ngoài X−.85…0,Y6.665…8.165. Bounds exception chỉ chấp nhận đúng hai IDs/type/size/hinge/angle/pose OUTWARD; ghế/đồ vật khác ngoài phòng vẫn FAIL. Tường có void thật, không mô tả hành lang ngoài chưa khảo sát.

Preview chụp ngoài cửa ở pose mở và pose đóng; pose đóng biến đổi cứng cùng mesh GLB quanh hinge đã export, không dựng ảnh/cửa giả. Các đồ khác luôn giữ nguyên. Demo đóng/mở phục vụ inspection, không WebXR runtime.

## 5. Tủ kính/kệ/màu tường

R4 mở lại trực tiếp PHOTO-04/05 tại nguồn local đã được cấp quyền, so với render R3. PHOTO-04 có ba bay đứng kính/khung xám và các tay nắm; model dựng ba khoang đứng, ba pane kính độc lập, khung/vách/đế, tay nắm và binder tự tạo. Không dùng tấm front thép kín che kính, không kính đen kiểu TV, không giấy tờ thật. Kích thước/ID P507-CABINET-FILES giữ nguyên.

Kệ P507-UTILITY-SHELF rộng dọc Y **1.50m đề xuất**, thay1.10m; depthX vẫn.47m. Rect[.10,2.05,.57,3.55]. Các đợt/thanh theo width mới, TV nhỏ rect[.15,2.40,.40,3.20], bottomZ1.45 bằng mặt đỡ kệ. Có support containment/height. Tủ lạnh/file cabinet giữ chỗ; bin chuyểnY4.86…5.18, shoe rack5.28…6.58, whiteboard5.18…6.63 phía trên. Không bỏ đồ vật để dễ đặt ghế.

Paint `P507_PBR_CREAM_PAINT`: **sRGB #F5E6C8**, chuyển sRGB→linear đúng một lần khi tạo material, roughness.92. Đây là màu tương đối đề xuất theo hướng kem vani của owner, không đo màu vật lý. Giữ tone mapping/exposure1, đổi material thực xuấtGLB, cùng material choTV/AI/logo/window walls. Browser kiểm tra actual base color và screenshot; không override riêng trong Three.js.

Giữ TV25° chéo, dispenser90°, cabinet thấp, AI wall, logo placeholder, fridge,shoe/bin/board,4windows/4blinds,ceiling8lights/4fans/2AC/projector/camera. Đồ bám tường Bắc dịchY+1.215, cửa sổ/thiết bị phân bố lại theo room mới nhưng kích thước không đổi. TV mount theo room length mới.

## 6. Kiểm thử/evidence và giới hạn

75 unit tests bảo vệ migration/baseline/adaptation,34chairs/36IDs,hai rows A/B/C,ghế trái/phải,không scale đồ,occupied proxy,collision/support,sector/hinge/outward exception có giới hạn, nguồn không giả verified. Regression cũ vẫn bảo vệ. Bộ test mới đã RED trên R3 trước sửa, GREEN sau triển khai.

Blender phải xuất thật.blend/GLB, kiểm evaluated vertex của121 placed IDs và10raychecks đèn/AC. Khronos Validator + contract asset-manifest hash/IDs/room/unit/glass. Browser kiểm121IDs thật,34chairbacks từ vertex transform (không chỉ metadata),3pane kính thật, hướng máy nước/TV,room/window bounds,door open/closed,vanilla material,smallTV support,không giấu nội thất.16góc desktop +hero mobile, inventory disclosure/contact sheet. CI40min giữ actual Blender/Chrome pipeline, không dùng run R3 làm finalHEAD evidence.

Raw reports gồm bytes/hash/inputSHAs,mesh/triangle/geometry/material/drawcalls/texture estimate,load,rAF p50/p95/n/raw,GPU/browser/viewport/camera/PRhead/checkoutSHA. Software rendering và mobile viewport không là thiết bị thật; không KPI72/30FPS hoặc real source-to-render. Source photos không Git/CI/cloud; chỉ hai texture tự tạo.

Artifact và exact finalHEAD/CI được ghi trong PR handoff khi run hoàn tất. Before/after chỉ GLB thật R3 và R4, **camera/room/light positions thay đổi theo room mới**, không gọi là camera-matched. Ảnh riêng tư không có trong contact sheet public.

## 7. Gate và điểm dừng

G1_GEOMETRY/G1_LAYOUT_34_CHAIRS theo tests+Blender+Chrome exactHEAD; G1_CIRCULATION PARTIAL; G2_PIPELINE theo exactHEAD CI; G2_VISUAL PENDING OWNER APPROVAL; PHOTO_MATCH PARTIAL về đặc điểm/hình dáng, room cố ý không1:1; WEBXR_HANDOFF READY FOR WEBXR EXPERIMENT (asset preparation only); REAL_DEVICE_WEBXR NOT RUN; REAL_AIRC_DATA NOT VERIFIED; G3 NOT STARTED.

[Tài liệu bàn giao WebXR riêng](P507-WEBXR-ASSET-HANDOFF.md). Sau handoff dừng thiết kế3D; không tự mở task/runtime WebXR, không productionScene/API/PostgreSQL/KPI changes.
