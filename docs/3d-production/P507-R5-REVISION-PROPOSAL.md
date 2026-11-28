# P507 R5 — phương án bố trí gọn, nâng hình ảnh và tương tác ghế

**R5 PROPOSAL / PROVISIONAL / SYNTHETIC / VIRTUAL ADAPTATION**
**OWNER_VISUAL_APPROVAL=PENDING** · **PHOTO_REFERENCE_UNAVAILABLE** tại thư mục ảnh cục bộ được chỉ định.

Phạm vi R5 được chủ dự án giao ngày 27/11/2026 theo Issues [#33](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/33) và [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20), và được điều chỉnh ngày 28/11/2026 để **thu gọn phòng về kích thước gần R4**, giữ toàn bộ nội thất/tương tác 34 ghế, đồng thời nâng chất lượng ánh sáng, vật liệu và chi tiết trong cùng lượt bàn giao trên nhánh `feat/p507-r5-fidelity-circulation-chair-interaction` ([Draft PR #34](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/34)). Mọi dữ liệu tại đây vẫn ở mức đề xuất synthetic; nghiệm thu hình ảnh của chủ dự án, khảo sát thực địa, quyền AIRC và hiệu năng thiết bị vật lý chưa được chứng nhận.

## Nguồn, kích thước và các mốc nền

| Nguồn / Ứng viên | Kích thước X × Y × Z | Ghi chú |
| --- | --- | --- |
| Khảo sát P507 | 6,00 × 8,10 × 3,50 m | `USER_REPORTED` |
| Frozen R4 | 6,90 × 9,315 × 3,50 m | `OWNER_APPROVED_VIRTUAL_ADAPTATION` (bảo toàn nguyên bản) |
| R5 cũ (`80b5d6f`, đã thay thế) | 8,63 × 15,55 × 3,50 m | Bị chủ dự án bác kích thước vì phòng quá rộng; chỉ giữ làm mốc đối chiếu lịch sử |
| **R5 compact hiện hành** | **7,26 × 10,76 × 3,50 m** | **Ứng viên R5 PROPOSAL đã chọn (78,12 m²; giảm 41,79% diện tích so với R5 cũ, gần R4 nhất đạt toàn bộ ràng buộc)** |

Base `bd2d0baf4a593e73dfe1c6e8d8a5e74fd45ae3be` là merge commit sau khi [PR #32](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/32) được nghiệm thu kỹ thuật độc lập ở head `f96df72d50c3f05796a6bc528f0f0ef77abbf892`. Báo cáo R4 gốc và archive R4 không thay đổi. [Runbook R4](../../experiments/p507-webxr/README.md)

## Hợp đồng kỹ thuật và tối ưu hình học compact

- Survey dùng XYZ theo mét, gốc tại góc tường logo và tường cửa (`+X` sang Đông, `+Y` lên Bắc, `+Z` lên trần). Chuyển sang glTF/Three tại ranh giới dữ liệu theo `(x, z, -y)`.
- **Khắc phục nguyên nhân phòng quá rộng ở R5 cũ (`8,63 × 15,55 m`):** R5 cũ đẩy ghế cất vào sâu thêm `0,16 m` và kéo hàng chính ra tới `0,98 m` (tổng hành trình `1,14 m`), làm hai hàng đối diện rút `2,28 m` và buộc phải kéo dài phòng để bù lối `0,90 m`. Bản R5 compact tối ưu lại khoảng dịch thực sự theo kích thước chân bàn/chân ghế và đầu gối người ngồi tổng hợp:
  - `STORED_FROM_DESK = 0,05 m` từ mép bàn;
  - `PULLED_FROM_DESK = 0,295 m` (hành trình kéo `0,245 m`);
  - `STAND_BEHIND_CHAIR = 0,585 m` sau điểm neo ghế kéo ra, kết hợp `approach_alternatives` bên hông `(±0,56 m, -0,15/+0,20 m)` cho hai hàng ngoài (dãy Bắc cụm A và dãy Nam cụm C) khi khoảng lưng sát tường/thiết bị hẹp.
- **Bảo toàn toàn bộ 150 logical ID bố trí và 2 hồ sơ UNPLACED:** 121 logical ID đặt từ R4 (17 bàn, 34 ghế cụm A/B/C, cửa hai cánh, 4 cửa sổ + 4 rèm, tủ hồ sơ, tủ lạnh, kệ bốn tầng `2,25 × 0,47 × 2,175 m`, thùng rác, kệ giày, bảng trắng, TV lớn, TV nhỏ, tường logo, khung ảnh, thiết bị trần) + **29 logical ID mới của R5** (6 máy tính, 1 máy in bắc cầu qua `A03–A06`, hoa lan, bộ trà, 5 poster, 1 đồng hồ, máy pha cà phê và đồ sinh hoạt trên 4 tầng kệ, 4 bình nước đáy). Hai hồ sơ `P507-CHAIR-C-09` và `P507-CHAIR-C-10` giữ `UNPLACED`.
- **Phân bổ lại thiết bị dọc tường theo kích thước `7,26 × 10,76 m`:** TV lớn dịch `dx = +0,45 m` và nâng đáy `+0,04 m` lên `1,82 m`; cụm khung ảnh dịch `dx = +0,55 m`; dãy tiện ích tường Tây phân bố tuần tự `CABINET-FILES (0,35–1,35)` → `FRIDGE (1,65–2,25)` → `UTILITY-SHELF (2,50–4,75)` → `WASTE-BIN (5,20–5,52)` → `SHOE-RACK (5,82–7,12)` / `WHITEBOARD (5,72–7,17)` sát vùng mở cửa; 4 cửa sổ tường Đông phân bố lại theo chiều dài mới và 2 poster kẹp giữa cửa sổ 4–3 và 3–2 (`y` tường Đông).
- **Capsule và collider giữ nguyên:** lối đi dùng capsule bán kính `0,30 m`, cao `1,80 m`, mục tiêu thông thủy lối A–B và B–C tối thiểu `0,90 m` khi cả hai hàng kéo ra và có 34 collider người ngồi tổng hợp. Không giảm collider hay dùng teleport để vượt kiểm thử.
- **Tách biệt DEV và R4:** R5 chạy riêng ở Vite DEV loopback (`?mode=p507-visit&revision=r5` và `/p507-r5-review.html?revision=r5`). Mặc định visitor, Admin và Catalog tiếp tục đọc R4. Mọi vật liệu tạo mới dùng màu/texture procedural trung tính.

## Nâng cấp ánh sáng, vật liệu và chi tiết hình học

Các nâng cấp thực hiện trực tiếp trong [generate_blender.py](../../experiments/p507-r5/generate_blender.py), [prop_meshes.py](../../experiments/p507-r5/prop_meshes.py), [Visitor.tsx](../../apps/web/src/p507-m5/Visitor.tsx) và [p507-r5-review.ts](../../apps/web/src/p507-r5-review.ts), không thêm dependency ngoài hay tải texture ngoài:

- **Ánh sáng & bóng đổ (R5-only):** `ACESFilmicToneMapping` (`toneMappingExposure = 1.05`), `PCFSoftShadowMap` (`1024×1024`, manual `needsUpdate` và `ShadowSync` khi ghế di chuyển), nguồn sáng daylight chính từ phía cửa sổ Đông (`intensity = 1.65`, `0xfff6e8`) kết hợp `HemisphereLight` (`1.35`, trần/nền sáng tự nhiên tránh trần xám phẳng) và 2 fill light mềm từ phía Tây (`0.68`) và Nam (`0.48`). Bổ sung lớp gradient bóng tiếp xúc (`P507_R5_CONTACT_SHADOW`) dưới 34 ghế và các khối bàn/tủ/thiết bị sàn.
- **Vật liệu PBR & texture procedural:** sửa triệt để Z-fighting sàn R4 bằng texture gạch procedural 4×4 `512×512` pack sẵn trong GLB (`P507_SELF_GENERATED_NEUTRAL_TILE`, ron gạch và 2 ô điểm xám nhẹ mỗi chu kỳ `2,40 m`), tranh poster modernist procedural `128×192` (`P507_SELF_GENERATED_POSTER_ART`), kính cửa sổ/tủ hồ sơ/mặt đồng hồ dùng `BLEND` alpha hợp lý, bình nước xanh bán trong suốt (`alpha = 0,56`), bình thủy tinh máy cà phê (`alpha = 0,36`) có lớp cà phê bên trong, tinh chỉnh roughness/metallic cho nhựa ghế xanh than, thép sơn bàn, satin chrome và gỗ khung ảnh.
- **Hình học và chi tiết prop:** bo cạnh (`bevel`) cho khung máy tính/máy in/đồ nội thất, màn hình máy tính thêm đế oval, cần đứng, viền màn, đèn standby phát sáng nhẹ, bàn phím chi tiết phím và chuột có con lăn; máy in có khay nạp, nắp scanner và tờ giấy in; chậu lan có lá thon và cánh/nhị hai sắc; đồng hồ treo tường có kim giờ/phút và kính che; thanh song cửa sổ tường Đông thêm chi tiết uốn đầu thanh.

## So sánh phương án kích thước đã kiểm chứng

Đo trực tiếp bằng bộ giải hình học [layout_checks.py](../../experiments/p507-r5/layout_checks.py) (`capsule r = 0,30 m, h = 1,80 m`, `stored = 0,05 m`, `pulled = 0,295 m`, `stand = 0,585 m` cho các phương án compact):

| Phương án | Kích thước X × Y × Z (m) | Lối cất A–B / B–C | Lối kéo/ngồi A–B / B–C | Trạng thái / Kết quả kiểm |
| --- | --- | --- | --- | --- |
| R4 frozen | 6,90 × 9,315 × 3,50 | — | 0,20 / 0,15 m | Không đạt lối đi 0,90 m khi kéo ghế |
| R5 cũ (`80b5d6f`, bác bỏ) | 8,63 × 15,55 × 3,50 | 3,22 / 3,22 m | 0,94 / 0,94 m | Đạt lối đi nhưng phòng quá dài/rộng, mất tỷ lệ |
| Compact thử `too-small` | 7,15 × 9,75 × 3,50 | 0,887 / 0,892 m | 0,397 / 0,402 m | FAIL: 59 cấu hình không tiếp cận được; không mở tuyến occupied |
| Compact thử `tight-x` | 7,20 × 10,65 × 3,50 | 1,337 / 1,342 m | 0,847 / 0,852 m | FAIL: lối occupied < 0,90 m; 8 cấu hình không tiếp cận được |
| Compact thử `borderline` | 7,25 × 10,75 × 3,50 | 1,387 / 1,392 m | 0,897 / 0,902 m | FAIL: A–B đạt 0,897 m (< 0,90 m); 4 cấu hình bị chặn |
| **Compact chọn (`R5` mới)** | **7,26 × 10,76 × 3,50** | **1,392 / 1,397 m** | **0,902 / 0,907 m** | **PASS: 0 unreachable, 0 component errors; stored=36, pulled=36, occupied=2, mixed=36, end-occupied=30, individual-pull=34** |
| Compact dư lề `margin` | 7,30 × 10,80 × 3,50 | 1,412 / 1,417 m | 0,922 / 0,927 m | PASS hình học, nhưng lớn hơn phương án `7,26 × 10,76 m` |

## Mở demo sau khi chuẩn bị asset

Từ `D:\Code\DATN`, chuẩn bị R4 bằng quy trình owner-local, sau đó stage đúng bundle R5 đã khóa trong [asset-lock.json](../../experiments/p507-r5/asset-lock.json):

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

Các bộ kiểm thử và sinh bằng chứng Chrome (chạy tuần tự, chỉ 1 Vite server mỗi lượt):

```powershell
Set-Location D:\Code\DATN
node apps/web/tests/r5-review.mjs
node apps/web/tests/r5-browser.mjs
node .local/p507-r5/demo-video-mobile.mjs
```

- `P507_R5_PROPOSAL.glb`: `17,423,320` bytes, SHA-256 `0fab4225ea5b965798a4c345b5f78f0ca80e6da70be7bcf6f254119c62663c92` (`473,947` vertices / `281,664` triangles theo Khronos glTF Validator, `0` errors / `0` warnings).
- `asset-manifest.json`: `755,783` bytes, SHA-256 `290af961c496b7d100b607ffcc2c6a5f44729b5fbac6ca67b82c54815700b7fa`.
- Bộ ảnh `r5-review.mjs` chụp **22 ảnh R5** (Mặt bằng, Ba cụm bàn, Toàn cảnh từ cửa, Toàn cảnh từ cuối phòng, Cụm A/B/C, Máy tính & máy in, Hoa lan & bộ trà, TV/đồng hồ/poster, Kệ bốn tầng & bình nước, Khu tiện ích, Cửa/bảng trắng/kệ giày, Cửa sổ & rèm, Tường khung ảnh, Tường logo, Trần & ánh sáng, Lối A–B ghế kéo ra, Lối B–C ghế kéo ra, Góc nhìn khi ngồi, Cửa mở/đóng, Mobile 390×844) kèm `contact-sheet.png` đối chiếu 3 cột: **Frozen R4 (6,90 × 9,315) | R5 cũ `80b5d6f` (8,63 × 15,55) | R5 compact mới (7,26 × 10,76)**.
- Bộ E2E `r5-browser.mjs` giữ nguyên kiểm thử cũ (34/34 chu kỳ ghế, IWER VR/AR, fallback, hai chiều lối đi khi occupied) và bổ sung: đi bộ WASD thật từ spawn/cửa tới 5 ghế khó nhất (`A-07`, `B-11`, `B-06`, `B-09`, `C-01`), xoay ngắm chọn bằng `Enter` raycast thật, kéo-ngồi-đứng-cất từng ghế, và kiểm tra va chạm âm tính (`ROOM_BOUNDARY_OUTSIDE_UNSURVEYED`).
- Script `.local/p507-r5/demo-video-mobile.mjs` kiểm chạm mobile `390×844` và ghi video demo trung tính `p507-r5-compact-demo.mp4` chỉ trong viewport Chrome (không quay desktop/thông tin cá nhân).
- Số đo FPS Chrome SwiftShader/IWER **không** thay cho KPI phần cứng (Web3D 30 FPS / VR 72 FPS / Galaxy A17 / HMD thật). Số liệu exact-HEAD cuối cùng của bộ compact và so sánh trước/sau nằm trong report đính kèm Draft PR #34.

## Đối chiếu yêu cầu và bằng chứng

| Yêu cầu | Triển khai | Bằng chứng kiểm chứng |
| --- | --- | --- |
| Kích thước gọn gần R4 & 150 ID + 2 UNPLACED | `layout.py`, `props.py` | `test_layout.py`, `test_props.py`, `layout_checks.py`, bảng kích thước |
| Thiết bị, hoa, trà, poster, đồng hồ, tiện ích, TV `1,82 m` | `props.py`, `prop_meshes.py` | `verify_export.py`, `verify_props.py`, ảnh `r5-07`..`r5-12` |
| Ánh sáng, PBR, bóng tiếp xúc, sửa Z-fighting sàn | `generate_blender.py`, `Visitor.tsx`, `p507-r5-review.ts` | 22 ảnh `r5-review.mjs` + `contact-sheet.png` 3 cột |
| Tương tác 34 ghế + đi bộ WASD thật + raycast `Enter` + WebXR IWER | `apps/web/src/p507-r5/chairs.ts`, `Visitor.tsx` | `p507-r5-chairs.test.ts`, `r5-browser.mjs`, `p507-r5-compact-demo.mp4` |
| Tạo lại asset bằng Blender 4.5.9 LTS | `generate_blender.py`, `asset-lock.json` | `verify_export.py --verify`, `validate_glb.mjs` (0 errors / 0 warnings) |

## Tạo lại ứng viên để kiểm tra

Chạy Blender 4.5.9 LTS với R4 editable master đã xác minh từ archive ghim và thư mục đích mới trong `.local/p507-r5/`:

```powershell
Set-Location D:\Code\DATN
$blender = '.local/tools/blender-4.5.9-windows-x64/blender.exe'
$r5Export = '.local/p507-r5/kiem-tra-moi'
& $blender -b -t 2 --python-exit-code 1 --python experiments/p507-r5/generate_blender.py -- --output-dir $r5Export
python experiments/p507-r5/verify_export.py $r5Export --record
node experiments/p507-r5/validate_glb.mjs $r5Export
python experiments/p507-r5/verify_export.py $r5Export --verify
```
