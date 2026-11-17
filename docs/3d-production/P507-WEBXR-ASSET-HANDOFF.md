# P507 — asset handoff cho nhiệm vụ thử WebXR riêng

Trạng thái: **READY FOR WEBXR EXPERIMENT**, chờ ChatGPT/chủ dự án xác nhận dùng model. Đây là gói asset đóng băng của R4, không cài runtime/UI/locomotion mới hoặc khởi động XR/camera/headset.

Đọc [R4 layout/acceptance](P507-G1-G2-R4-VIRTUAL-FREEZE.md) trước sử dụng. Không nhầm survey6×8.1×3.5m USER_REPORTED với virtual6.9×9.315×3.5m OWNER_APPROVED_VIRTUAL_ADAPTATION. Model không tỷ lệ phòng thật1:1.

## Các file bàn giao

Artifact CI `p507-g1-g2-neutral-blender-chrome` / bản local handoff có:

- `P507_G1_G2_PROVISIONAL.glb`: model runtime trung tính, không nguồn ảnh riêng tư.
- `P507_G1_G2_PROVISIONAL.blend`: nguồn chỉnh sửa, architectural/hero/ceiling collections.
- `asset-manifest.json`: hash/bytes/sourceSHA,room/baseline/unit,123stable records/121placed,transforms/bounds/proxies/materials/textures,pose đầu vào và camera presets từ lần chụp thật.
- `geometry-report.json`: static occupancy, support/door exceptions/clearance/occupied-use assumptions.
- `report.json`: Blender version/evaluated vertex/ray proof/source+checkoutSHAs/inputhash/modelhash.
- `gltf-validation-report.json`: official Khronos result.
- `browser-report.json`: actual browser geometry/performance/cameras/GPU/viewports/raw timings; screenshot/contact sheet.

Không dùng UUID database giả. Stable IDs nằm trong glTF node extras `survey_instance_id`; một ID có thể gồm Group/nhiều primitive. Tương tác cần gom các node cùng ID hoặc đi lên ancestor có ID, không coi mỗi primitive là đồ vật độc lập. C09/C10 không mesh, vẫn giữ trong manifest UNPLACED/UNASSIGNED. Tổng lịch sử36,allocation34,placed34,unplaced2.

## Đơn vị, trục và pose đề xuất

Metre; Blender surveyXYZ Z-up đã được exporter chuyển một lần sang glTF/Three `(x,z,-y)`. Nhiệm vụ WebXR sau nạp ở identity scale/rotation; không thêm scale1.15 hay quay model lần nữa. Object dimensions giữ nguyên, room adaptation đã nằm trong asset.

Entrance trên tường Tây Y6.665…8.165. Pose chân đề xuất survey `[1.25,7.415,0]` / glTF `[1.25,0,-7.415]`, mắt1.65m, nhìn+X survey, yawThree−π/2. Đây là starting pose đề xuất trong vùng trống, không chứng minh user height/locomotion. Cần validation capsule và thực nghiệm riêng khi task WebXR được duyệt. Không cộng eye height hai lần nếu XR camera runtime đã cung cấp chiều cao.

Cameras review (position,target,FOV,cutaway,doorPose) được browser capture ghi vào `asset-manifest.json.preview_camera_presets` và từng view trong browser-report. Không dùng camera outside/overview làm starting pose người dùng. Camera matching chỉ định tính, chưa calibrated.

## Sàn và collision

Sàn visual prefix `P507_ARCH_FLOOR`, mặt đi surveyZ0 / glTFY0. Room width6.90,length9.315,height3.50. Nội thất bounds/proxies là oriented prisms surveyXY+bottom/topZ; chuyển từng vertex qua `(x,z,−y)` khi nhiệm vụ sau cần collision Three. Không thêm wall collision xuyên opening.

`collision_proxies` gồm121 logical instances đã đặt. Desk proxies bảo thủ bao cả khung, không coi khoảng dưới bàn là lối người đi. Door leaf OUTWARD là ngoại lệ có kiểm soát bên ngoài X<0, có hinge/sweep/angle; không biến thành quyền cho mọi object ra ngoài room. Ngoại cảnh/hành lang ngoài UNKNOWN và chưa được dựng.

`occupied_use`: full chair envelope kéo lùi.15m, không mô phỏng người/chân/tay. West route min static1.08m/use.93m, target đề xuất.80m. Centraluse.20/.15m và sau ghế phải.23m không là through-route; tủ thấp còn.475m khi kéo ghế. Không certified safety/PCCC/accessibility. Task mới phải quyết định locomotion/capsule/navigation policy và xử lý các khoảng này trước nghiệm thu trải nghiệm.

## Vật liệu, ánh sáng và performance

PBR glTF; wall sRGB#F5E6C8,roughness.92; kính tủ3pane alpha.18; TV tối; tile/oak256px tự tạo. Không ảnh người/màn hình/nội dung nội bộ hoặc logo/art thật. Texture estimate RGBA8+mips loại trừ IBL/shadow/framebuffers, không tổng VRAM.

Blender lights không tự thành ánh sáng Three. Preview hiện dùng procedural IBL/daylight/shadow và2area strips xấp xỉ8diffuser; nhiệm vụ WebXR sau phải đánh giá renderer/hardware được chọn. `.blend` đẹp/validator green không chứng minhFPS hoặc chủ dự án đã duyệt art.

Model bytes/meshes/triangles/materials/geometries/drawcalls/load/frame p50/p95/raw sample count trong reports của exactHEAD. SoftwareSwiftShader/mobile viewport không đại diện điện thoại/headset thật. Không đạtKPI72/30FPS bằng số liệu này. Không giảm chất lượng hoặc bỏ object để che performance issue; đề xuất tối ưu phải là task riêng được duyệt.

## Hướng dẫn cho nhiệm vụ riêng sau này

1. Chủ dự án/ChatGPT xác nhận artifact/hash/exactSHA được dùng; giữ bản R4 bất biến để tái lập.
2. Trong experiment riêng đã được phép, nạp GLB bằng loader đang có và giữ metre/identity transform; xác minh all121IDs,34chairs và trục floor/window.
3. Tạo ánh sáng tương thích runtime sau khi được duyệt; không đưa asset này vào M1-C production Scene mặc định.
4. Dùng manifest để đề xuất collision/starting pose; kiểm model load/display/navigation trước, ghi browser/GPU/device/viewport/raw metrics.
5. Chỉ requestSession sau user gesture trong task riêng có phê duyệt; lần bàn giao này không mở session/camera/headset và chưa chọn policyVR/AR.

**Dừng ở asset handoff. G2_VISUAL PENDING OWNER APPROVAL; REAL_DEVICE_WEBXR NOT RUN; không G3/merge/deploy/backend/API/PostgreSQL/KPI changes.**
