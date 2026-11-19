# M5 — P507 Web 3D, WebXR AR/VR

Trạng thái nhánh M5 **IN_REVIEW / DEVICE_BLOCKED**. Baseline từ main đã fetch `87b8047c11308065fd6776e4dd44da4246ed0f1a`. Xem phạm vi do chủ dự án giao và điều kiện nghiệm thu. [Issue #29](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/29)

## Chạy tại máy chủ sở hữu asset

1. Dùng Node 22 và môi trường Python của repository. Chạy `npm ci --ignore-scripts --prefix apps/web`.
2. Dùng bundle R4 trung tính đã được chuẩn bị trên máy chủ sở hữu. Thực hiện bước restore có quyền theo [runbook E0/E1](../../experiments/p507-webxr/README.md) nếu file chưa có. Từ root chạy `python experiments/p507-webxr/validate_asset.py --prepare` rồi `python experiments/p507-webxr/verify_export_reference.py`.
3. Chạy `npm --prefix apps/web run dev`. Mở `http://127.0.0.1:5173/?mode=p507-visit` hoặc chọn **Tham quan P507** trong ứng dụng chính. Route cần Vite DEV và hostname loopback. Danh sách 121 ID từ chỉ mục R4 vẫn dùng được khi scene bị lỗi. Không cần backend hoặc tài khoản.
4. Trên desktop, chạm/chọn để xem chi tiết, kéo để nhìn quanh, WASD/← →/Enter khi canvas có focus. Có nút bước ngắn/xoay/reset và danh sách thao tác bằng bàn phím. Đi bộ sử dụng capsule và swept collision của E1. Khi WebGL lỗi, sử dụng danh sách.
5. Dùng nút **Vào VR** hoặc **Vào AR** khi runtime báo hỗ trợ. VR chọn bằng tia tracked-pointer hoặc select từ gaze/screen khi runtime cung cấp. Thumbstick xr-standard đi theo hướng nhìn, sử dụng cùng collision, không teleport. Khi người dùng thật bước ra khỏi đường đã kiểm proxy, cảnh VR ẩn cho tới khi trở lại vị trí hợp lệ. Đây là giới hạn điều hướng trong mô hình ảo. Dùng menu hệ thống và vùng an toàn của thiết bị trong buổi thử.
6. AR dùng pose mặt phẳng ngang gần, có hit-test do runtime cấp và một lần select rõ ràng để đặt mô hình để bàn ở tỷ lệ 0,08. Transform riêng thuộc nhóm trình bày AR. AR tạm ẩn trần và vỏ tường không có ID để tia từ phía trên chạm tới nội thất, rồi phục hồi hiển thị khi thoát XR. Geometry, logical ID và file R4 giữ nguyên. GLB gốc giữ mét, axes, local identity và kích thước ảo 6,90 × 9,315 × 3,50 m. Khảo sát 6,00 × 8,10 × 3,50 m vẫn USER_REPORTED. Khi không có mặt phẳng phù hợp hoặc tính năng bị từ chối, thoát XR để tiếp tục Web 3D. Thoát trong XR qua panel 3D hoặc menu hệ thống. Sau khi thoát, lựa chọn cũ được xóa và chuyển về điểm bắt đầu Web 3D.

Hash SHA-256 GLB là `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`. Manifest là `5240cb6674fb93b7ad46205d6788fa6bd0ad7a468a2bf1eb29e255ff7e28afd3`. Có 121 ID được bố trí và hai hồ sơ chưa bố trí P507-CHAIR-C-09/C-10. Mesh con truy lên ancestor theo extras của GLB. E0 đối chiếu bounds với reference độc lập đã khóa. Label provisional, USER_REPORTED và quyền đang chờ được giữ trên màn hình và panel XR.

## Kiểm chứng và bằng chứng

| Issue #29 | Bài kiểm tra / điều kiện xác nhận |
| --- | --- |
| 1. Ứng dụng chính | Chrome route loopback, WebGL R4, danh sách desktop/touch và fallback. Hồi quy LiveApp, standalone E1, Catalog/realtime P507, Admin và M4 chạy qua entry point cũ. |
| 2. R4 và định danh | E0 Python và Chrome đối chiếu hash, geometry, ID, proxy. Chrome M5 chọn từ geometry thực. Test tiêu cực cho ID/hierarchy sai và asset mất hoặc bị sửa. |
| 3. Vòng đời | Kiểm Chrome mock cho insecure, unsupported, devicechange, denied và user activation. IWER cho vào/thoát/vào lại, system end, visibility, disconnect, unmount. Chrome dùng WEBGL_lose_context kiểm context loss và restore. |
| 4. Tương tác | Chuột/touch/keyboard và collider sweep E1, controller tracked-pointer và panel 3D, AR đặt sau hành động người dùng. Kiểm thiết bị thực và độ thoải mái còn BLOCKED. |
| 5. Dữ liệu và M4 | Visitor đọc GLB/manifest cục bộ và dùng metadata provisional. Admin và public Catalog/WS đi theo route cũ. Visitor không gọi ghi API/WS, camera/media hoặc M4 sessions/events. |
| 6. Kiểm thử | Dùng lệnh bên dưới, phân biệt Chrome WebGL, Chrome + IWER với fixture mặt phẳng, mock API và thiết bị thật. Điều tra raycast Admin Windows cùng baseline và lưu kết quả trong bàn giao. |
| 7. Trạng thái | Draft PR duy nhất vào main. Branch IN_REVIEW, DEVICE_BLOCKED cho thiết bị thật. Issue #30 được thực hiện sau nghiệm thu độc lập. |

Từ root, chạy `npm --prefix apps/web run build`, `npm --prefix apps/web test`, `npm --prefix apps/web run test:browser` (Python có dependencies API), và lệnh kiểm PostgreSQL trong [runbook API](../../apps/api/README.md). Dùng PostgreSQL dùng một lần và test guards sẵn có. Chạy thêm:

```text
node --experimental-strip-types experiments/p507-webxr/navigation-check.mjs
node experiments/p507-webxr/e0-inspect.mjs
node experiments/p507-webxr/browser.mjs
node apps/web/tests/m5-browser.mjs
node apps/web/tests/m5-browser.mjs --require-r4
```

Lệnh M5 không cờ kiểm fallback không cần asset. `--require-r4` xác minh hash trước khi chạy toàn bộ kịch bản Chrome/IWER. IWER 2.8 chỉ được cài trong trang test opt-in. Fixture AR là mặt phẳng ngang tổng hợp qua IWER SEM, không phải ảnh camera, SLAM hay dữ liệu phòng. Bằng chứng ở `.local/p507-m5/` gồm report expected/actual, build SHA, hash, browser/OS/renderer, log lifecycle và raw frame intervals, PNG Chrome. WebGL chạy trên SwiftShader khi dùng cờ mặc định của runner. Giữ tệp media cục bộ theo quyền dữ liệu R4. Có thể bật `evidence=1` khi cần kiểm thử và lấy frame intervals từ bộ nhớ phiên. Evidence không lưu pose, camera, định danh người tham quan hay state Admin.

### Raycast Admin Windows

PR #28 ghi nhận lỗi gián đoạn của bài test Chrome Admin với R4 gốc. Baseline fetched đã PASS trong lượt chạy riêng. Lỗi lặp lại ở HEAD 1066025 khi Chrome chạy song song với kiểm R4. Probe với M5_ADMIN_RAY_PROBE=1 ghi năm lần click đúng phần tử CANVAS khi WebGL có 0 draw calls và canvas còn ở kích thước mặc định. Sau loạt draw đầu (218 lệnh trong lần đo), kích thước và tâm canvas thay đổi. Một click ở tâm canvas đã vẽ chọn đúng P507-CHAIR-C-08 (0ed3ab16-44a0-5c39-9421-d3cecda9ae3c). Bản sửa đồng bộ test theo WebGL draw đầu tiên, đo lại canvas và kiểm đúng UUID. Admin runtime, asset và ánh xạ không đổi. Chỉ chạy phép đo này với M3_REQUIRE_FROZEN=1, PostgreSQL dùng một lần và R4 đã kiểm hash. CI M3 vẫn dùng đường fallback. [Bàn giao PR #28](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28) · [Draft PR #31](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/31)

Tham chiếu runtime cho user activation, reference space và visibility. [W3C WebXR Device API](https://www.w3.org/TR/webxr/)

## Thiết bị thật — DEVICE_BLOCKED

| Thiết bị | Chuẩn bị | Expected / bằng chứng cần thu | Hiện trạng |
| --- | --- | --- | --- |
| Galaxy A17 5G · AR | Chủ dự án xác nhận model/OS, Chrome, AR runtime và quyền tại chỗ. Dùng máy thử loopback qua USB reverse và kiểm `isSecureContext`, hoặc cấu hình HTTPS được owner phê duyệt phù hợp gate cục bộ. Chọn bề mặt trống, có người hướng dẫn. | Từ Web 3D bấm AR, kiểm quyền cho phép/từ chối, bề mặt, đặt preview, tap chọn ID, thoát và vào lại. Ghi phiên bản, SHA build/asset, log, video đã lọc và frame intervals thực tế. Nếu thiếu AR/hit-test, ghi expected/actual và dùng fallback. | BLOCKED, chưa thử trên thiết bị. [#4](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/4) |
| HMD được chủ dự án chọn · VR | Xác nhận HMD/runtime/browser và controller. Thống nhất cách kết nối secure local, phạm vi di chuyển thật, người giám sát và thời lượng đo được phê duyệt. | Vào bằng cử chỉ, kiểm tia/chọn/đọc panel, thumbstick va chạm, dừng/khôi phục, disconnect controller, system end, exit/re-entry. Ghi SHA/kích thước/renderer, runtime, video và raw frame intervals đúng protocol. | BLOCKED, chưa có HMD/protocol đã xác nhận. [#5](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/5) |

Giữ KPI MT2-02 Web 3D ≥30 FPS và VR ≥72 FPS theo tài liệu KPI. Nhờ chủ dự án và giảng viên xác nhận protocol, kết quả phần cứng và bằng chứng trước nghiệm thu. [Requirements và KPI](../02-requirements-kpi.md)

## Các mục theo dõi trước nghiệm thu M6

- Quyền và nguồn khảo sát AIRC, inventory thực và dữ liệu đủ ba phòng. [#1](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/1) · [#2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/2) · [#3](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3)
- G2 visual, circulation/clearance và quyền hình ảnh tiếp tục chờ đánh giá. [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20)
- Privileged vault CI tiếp tục SKIPPED khi thiếu cấu hình được duyệt. Theo dõi hạn nguồn artifact 24/11/2026. [#22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22)
- Đề xuất cho lượt sau. Nếu cần ghi lượt tham quan P507, xem xét hợp đồng event có version, room scope P507, mapping logical ID đến Catalog UUID đóng version, kiểm 121 ID theo room ở server và loại hai hồ sơ unplaced. Yêu cầu opt-in và chốt purpose/retention/delete/export/access trước mọi ghi; khảo sát terminal event khi đạt trần 500 và quyền cleanup khi mất proof. Pose và media không thuộc hợp đồng đề xuất. Cả quyết định schema và đồng ý thu thập còn mở. [M4 runbook](../m4/VISITOR-SESSIONS.md)
- Tổng rà soát M0–M5 do chủ dự án yêu cầu là lượt bàn giao riêng sau nghiệm thu M5. [#30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30)
