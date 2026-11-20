# Phiếu thực địa P507 và chuẩn bị nghiệm thu M6

Điền phiếu đã vệ sinh dữ liệu trong nơi lưu trữ được xác nhận quyền. Tra theo ID frozen hoặc Catalog UUID ở [M3 data source matrix](../m3/P507-DATA-SOURCE-MATRIX.md). Mỗi dòng có trạng thái `PENDING`, `CONFIRMED`, `MISMATCH` hoặc `NOT_FOUND` và tham chiếu bằng chứng riêng. Chỉ người có thẩm quyền ký xác minh sau khi đối chiếu.

## R4 và đề xuất R5

Đường thử dưới đây dùng manifest R4 đã khóa, tọa độ Three `[x,z]` mét, survey tương ứng `[x,-z]`. Vùng sàn dùng camera/player height 1,80 m, radius 0,30 m, kiểm full swept circle và union proxy tĩnh/có người dùng kéo ghế lùi 0,15 m. Các khoảng dưới đây là khoảng từ đường thử tới cạnh proxy tại điểm gần nhất, làm tròn theo manifest.

| Tuyến | Vị trí / proxy gây chặn | Kết quả mô hình và việc cần đo |
| --- | --- | --- |
| Lối Tây ngắn | Spawn `[1.25,-7.415]` → `[0.95,-7.415]` → `[0.95,-5.2]` | Các segment E1 thử qua được. Đo bề rộng theo từng mốc Y và trạng thái sử dụng. |
| Lối Tây tiếp nối | `[0.95,-5.2]` → `[0.95,-3.9]`, B11 `P507-CHAIR-B-11`, center survey `[1.40,3.85]`, 270°, cạnh X tĩnh 1,13 m | Mép proxy cách 0,18 m tĩnh, 0,03 m khi occupied. Cả hai nhỏ hơn radius 0,30 m. Đo vị trí/chân ghế và hành trình kéo thực dọc mép Tây. |
| Giữa A–B | `[1.2,-5.63]` → `[5.5,-5.63]`, A01 `P507-CHAIR-A-01`, center survey `[2.175,6.12]`, 0°, cạnh Y tĩnh 5,85 m | Khoảng 0,22 m tĩnh và 0,07 m occupied. Đối chiếu hàng A01–A06 và B05–B08 ở vị trí sử dụng, đo từng cổ chai. |
| Giữa B–C | `[1.2,-2.85]` → `[5.5,-2.85]`, B01 `P507-CHAIR-B-01`, center survey `[2.675,3.32]`, 0°, cạnh Y tĩnh 3,05 m | Khoảng 0,20 m tĩnh và 0,05 m occupied. Đối chiếu B01–B04 và C05–C08, ghế ở đầu cụm và vùng quay. |
| Tiếp cận tủ thấp | `[1.25,-8.49]` → `[1.25,-8.59]`, `P507-CABINET-LOW`, center survey `[2.25,9.035,0.525]`, proxy X [1.48,3.02], Y [8.775,9.245] | Proxy rộng 1,54 m và sâu 0,47 m, survey transform đồ mô hình 1,50 × 0,40 × 1,05 m. Đo mép, khoảng mở cửa và vị trí theo góc phòng. |

Chạy `node --experimental-strip-types experiments/p507-webxr/navigation-check.mjs` trên manifest R4 đã xác minh. Phép thử ghi ID cản đầu tiên theo thứ tự collider, hữu ích để tái hiện đường chủ dự án mô tả. Điểm bấm và hướng quan sát của lần thử thực địa cần chủ dự án xác nhận. Các vật sai kích thước/vị trí khác vẫn cần chủ dự án chỉ ID. P507 ảo 6,90 × 9,315 × 3,50 m, khảo sát user-reported 6,00 × 8,10 × 3,50 m.

Phiếu đo cho từng ID gồm revision/ngày/giờ/múi giờ, góc gốc và trục survey, điểm đầu/cuối và chiều cao đo, `width_m, depth_m, height_m, center_x/y/z, yaw_deg, tolerance_m`, khoảng hở tĩnh/occupied, thiết bị đo, người quan sát, nguồn và quyền. Ghi `UNKNOWN` khi chưa đo, lưu đính kèm raw theo quyền. R5 cần phê duyệt riêng scope, sai số, baseline survey và visual, ID mapping với R4, lock/reference mới tách biệt. Nghiệm thu riêng geometry, proxy sweep, real GLTFLoader, Blender/Khronos, E0/E1 Chrome và hình ảnh chủ dự án duyệt. [Freeze R4](../3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md) · [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20)

## Phiếu kiểm kê

Điền 20 hàng ứng viên dưới đây. ID là gợi ý khớp trong mô hình, cả 20 hàng mở ở PENDING. Có thể đổi ứng viên sau khi xác nhận thực địa và quyền. Một thiết bị chỉ tính một lần theo identity đã đối chiếu. Giữ ghi nhận riêng khi thấy vật thật chưa có mesh.

| ID ứng viên | Identity thật và phòng | Vị trí, nhóm, bằng chứng | Tương tác đã thử | Người xác minh và quyền | Kết quả |
| --- | --- | --- | --- | --- | --- |
| P507-DESK-A01 | | | | | PENDING |
| P507-DESK-A03 | | | | | PENDING |
| P507-DESK-A04 | | | | | PENDING |
| P507-DESK-B01 | | | | | PENDING |
| P507-DESK-B06 | | | | | PENDING |
| P507-DESK-C01 | | | | | PENDING |
| P507-CHAIR-A-01 | | | | | PENDING |
| P507-CHAIR-A-07 | | | | | PENDING |
| P507-CHAIR-B-01 | | | | | PENDING |
| P507-CHAIR-B-11 | | | | | PENDING |
| P507-CHAIR-C-01 | | | | | PENDING |
| P507-CABINET-LOW | | | | | PENDING |
| P507-CABINET-FILES | | | | | PENDING |
| P507-FRIDGE | | | | | PENDING |
| P507-UTILITY-SHELF | | | | | PENDING |
| P507-WASTE-BIN | | | | | PENDING |
| P507-SHOE-RACK | | | | | PENDING |
| P507-WHITEBOARD | | | | | PENDING |
| P507-TV-SMALL | | | | | PENDING |
| P507-TV-LARGE | | | | | PENDING |

Mẫu inventory bổ sung cho vật nhỏ. Không sửa map chỉ vì có hàng mới. Trong Admin, tạo dữ liệu thử theo `INFO_ONLY` hoặc `NOT_MODELED`, kiểm không có PLACED binding, editor/preview đọc được và public Catalog/WS chỉ nhận synthetic được phép. Khi được phép nhập dữ liệu thực, kiểm scope private, nguồn và hành trình correction cùng audit.

```csv
inventory_revision,room_id,field_item_ref,sanitized_name,quantity,category,location,model_disposition,catalog_id_if_known,observed_at_with_offset,observer_role,evidence_ref,rights_decision_ref,verification_state
```

## Nguồn và quyền

| Loại | Định danh | Giá trị cần thu | Bằng chứng và cadence |
| --- | --- | --- | --- |
| `room_schedule` | Room UUID | Khung thời gian và trạng thái được phép ghi | Đầu mối lịch, giờ nguồn đổi có offset, người quan sát, ai cập nhật khi lịch đổi. |
| `equipment_status` | Room và object UUID | Trạng thái theo schema Admin, phạm vi sử dụng | Người phụ trách thiết bị, quan sát trực tiếp/nguồn được duyệt, trigger và nhịp xác minh. |
| `exhibit_info` | Room và object UUID | Mô tả đã lọc theo mục đích được duyệt | Người quản lý hiện vật, revision nội dung, thời điểm thay đổi, quy trình correction. |

Mẫu nhập vào form Admin theo contract hiện hành:

- `room_schedule` · room UUID `____`, `activity` `____` (1–160 ký tự), `status` chọn `free / occupied / closed`. Giữ khung giờ và nguồn lịch trong phiếu đối chứng.
- `equipment_status` · object UUID `____`, `status` chọn `available / maintenance / offline`.
- `exhibit_info` · object UUID `____`, `title` `____` (1–160 ký tự), `text` `____` (tối đa 800).
- Mỗi form điền `observed_at` và múi giờ tại máy nhập, `source_note`, provenance theo nguồn được phép và `expected_version` từ bản đang chỉnh. Khi conflict, đọc version mới rồi ghi correction theo quy trình có audit. Chờ source và quyền trước mọi nhập liệu thật.

Mỗi dòng cần `source_ref, source_observed_at+offset, observer_role, operator, capture_cadence, correction_owner, rights_ref, committed_at, version, event_id, rendered_at+offset`. Actor và source note lấy từ Admin audit. Không điền timestamps giả hoặc ghi hash/tên nhạy cảm vào PR. Mẫu phê duyệt quyền gồm asset/record IDs và revision, người phê duyệt & vai trò, ngày hiệu lực/hết hạn, điều kiện che dữ liệu, thu hồi và tham chiếu quyết định. Điền quyết định độc lập cho **Admin private**, **demo giảng viên/hội đồng**, **luận văn** và **website/GitHub**. Quyền khảo sát, ý định của chủ dự án và quyền công bố của AIRC cần bằng chứng riêng.

Chạy thử bằng dữ liệu synthetic với đúng ba loại qua Admin. Chạy lại với nguồn thật sau khi được phê duyệt. Đo clock offsets trước/sau giữa nguồn, API và browser, ghi uncertainty. Đánh dấu `t0` là lần thay đổi được ghi ở nguồn, `t1` lúc operator bắt đầu nhập, `t2` lúc API commit, `t3` lúc WS giao đúng event/version và `t4` là frame UI áp dụng đúng value/ID/version ở Admin preview. Đối chiếu bằng audit, network timeline và frame/UI trace cùng event/version. Lưu `t4−t0` đã hiệu chỉnh và tách `t1−t0`, `t2−t1`, `t4−t2`. Copy event cùng giá trị cũ, sai scope, correction, reconnect, mất sample và lỗi đồng hồ đều cần ghi expected/actual. Lưu cả mẫu fail. Thiếu clock alignment hoặc t0 thì ghi mẫu không đủ evidence. Giữ public và private tách biệt.

## Nghiệm thu M6

Hoàn thiện phiếu từng lượt với `protocol_revision, approval_refs, code_sha, environment, room/object_revision, UTC_start, local_timezone, operator_role, expected, actual, artifact_ref, result, deviation`. Chốt kịch bản, cỡ mẫu, thiết bị, cách chọn người/scene và xử lý dữ liệu trước thu. [Nguồn KPI đã duyệt](../02-requirements-kpi.md)

| KPI | Expected và oracle | Evidence cần lưu | Hiện trạng |
| --- | --- | --- | --- |
| MT1-01 | ≥3 phòng thật khác nhau và được phép sử dụng | Một phiếu cho mỗi phòng gồm AIRC room ref, scene ID, quyền và thao tác chuyển phòng, bằng chứng sơ đồ có quyền | BLOCKED #1 |
| MT1-02 | ≥20 identity tương tác thực duy nhất | Phiếu trên, ID map, bằng chứng tương tác và chữ ký xác minh mỗi ID | BLOCKED #2 |
| MT1-03 | ≥3 loại trạng thái có nguồn | Ba phiếu quan sát thực, source/provenance, quyền, UI và audit | BLOCKED #3 |
| MT1-04 | ≤5 giây cho từng mẫu hợp lệ theo protocol | Raw t0–t4, offsets, network, error và kết quả theo từng ID/version | NOT_RUN nguồn thật |
| MT2-01 | Tham quan Web 3D desktop/mobile | Thử mở/chuyển phòng, điều hướng, chọn và fallback, build SHA/video được phép | PARTIAL, một phòng P507 và emulation |
| MT2-02 | AR và VR thực trên cấu hình tương thích | Capability, request trên click, quyền, tương tác và thoát/khôi phục với mỗi thiết bị | HARDWARE_BLOCKED |
| MT2-03 | Web 3D ≥30 FPS trên thiết bị đại diện | ≥3 phòng và ≥20 ID trong workload đã duyệt, frame raw, elapsed/tỷ lệ, GPU, OS, browser, resolution, cache, network, cấu hình/nhiệt nếu có | NOT_RUN phần cứng đại diện |
| MT2-04 | VR ≥72 FPS trên kính đã chọn | Runtime/app/compositor frame timing và dropped/reprojected frames, Hz, thiết bị, raw windows | HARDWARE_BLOCKED |
| MT2-05 | ≥90% lượt tác vụ thành công, ≥15 người đồng thuận | ID nghiên cứu tách riêng consent, giao cố định task ID, success/fail/abandoned cùng bằng chứng; lấy toàn bộ lượt được giao làm mẫu số | BLOCKED protocol/consent |
| MT3-01/02 | Persistence và reload/retry đúng phiên, scope và ID | Oracle độc lập ghi session/event expected trước khi so DB; reload, retry, offline/fault, hết proof, dedupe/order | Synthetic regression; policy thật BLOCKED |
| MT3-03 | ≥99% expected unique valid IDs tồn tại đúng scope trong DB | Oracle unique IDs độc lập, count missing/unexpected/duplicates và sai canonical fields, tỷ lệ matched/expected ×100% | Oracle synthetic 50/1.000 là evidence kỹ thuật |
| MT3-04 | ≥50 session IDs phân biệt | CSV/JSON và DB match theo session/event IDs, count, aggregate, UTC/ordering, scope và labels | Oracle synthetic; mẫu M6 theo protocol chưa chạy |
