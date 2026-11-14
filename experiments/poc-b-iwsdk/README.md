# PoC B — Meta IWSDK

**DEMO – DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI PHÒNG 507.** Một phòng generic 12×3×9 đơn vị thử nghiệm, 5 primitive, không có số đo/inventory AIRC. Không phải sản phẩm chính thức và không chứng minh KPI MT1/MT2/MT3.

## Setup và chạy riêng

Node 22.12+ trong major 22; npm. Tại `D:\Code\DATN\experiments\poc-b-iwsdk`:

```sh
npm ci --ignore-scripts
npm run dev
npm run build
npm test
npm run preview
```

Dùng URL loopback Vite in ra. `build` chạy TypeScript noEmit trước bundling; `test` chạy 6 domain tests dùng chung. Linux dùng clone của chính repository và cùng lệnh; Windows workspace chính vẫn D:\Code\DATN. Không tự tải browser, không bật public host hoặc deploy. `--ignore-scripts` đã được thử; binaries Vite/esbuild đến từ optional packages phù hợp platform.

## Luồng thử

Chọn object bằng click/touch canvas hoặc danh mục → đọc metadata/source/timestamp → Đổi trạng thái DEMO → chọn Tour dẫn đường/Điểm tiếp theo → kéo orbit/chụm zoom → Đặt lại cảnh. Hai chế độ chia sẻ layout/domain cùng PoC còn lại. `?forceNoWebGL=1` cố tình đi nhánh lỗi dễ đọc; không phải bằng chứng thiếu WebGL trên thiết bị.

Các nút Vào AR/VR chỉ request khi bấm; không tự camera/session/offer. Native unsupported/permission error được giải thích, Web 3D vẫn là fallback. Không giả định DOM panel xuất hiện trong kính. Thoát bằng nút của runtime/emulator khi overlay đang chiếm màn hình; không force click xuyên overlay.

## Ranh giới dữ liệu

[Fixture/contract](../shared-fixtures/domain.ts) và [UI dùng chung](../shared-ui/Shell.tsx) nằm ngoài renderer. Stable ID không phụ thuộc mesh name/entity index. Adapter loader mẫu chỉ validate dữ liệu được caller cung cấp; không gọi API/backend. Chỉ record synthetic được đổi trạng thái. Không có persistence/auth/admin/DB/WebSocket.

## Browser evidence

Tại root, sau build cả A/B, `npm ci --ignore-scripts --prefix experiments/browser-tests` rồi `npm test --prefix experiments/browser-tests`. Cần Chrome có sẵn, có thể đặt CHROME_BIN; Playwright 1.58.2 chỉ là test dependency, không cài browser. Ảnh/report trong `.local/poc-browser`; CI upload allowlist artifact 14 ngày. Test dùng SwiftShader/software WebGL, không suy ra hiệu năng Galaxy/Quest. [So sánh và giới hạn](../../docs/11-renderer-poc-comparison.md).

## Dependency, ECS và emulator B

IWSDK core/plugin-dev 1.1.0; `three: npm:super-three@0.185.0` ở project, core và plugin dedupe cùng alias; không ép Three stock khác vào SDK. React/DOM 19.3.1 chỉ quản lý DOM shell, không reconcile scene. `virtual:iwsdk-project` + iwsdk.config.json là authority, empty scene manifest hợp lệ rồi tạo primitive bằng World/ECS.

DemoBridgeSystem sở hữu domain controller trong lifecycle world; DemoIdentity component giữ stable ID và projection trạng thái. React gửi command qua Bridge; component mirror được đồng bộ trước UI listeners. Entity index chỉ là runtime identity, không là object ID. Bật RayInteractable và click listener SDK cho mouse/touch/XR ray; OrbitControls chỉ điều khiển camera desktop. ResizeObserver căn renderer/camera theo container vì SDK mặc định lấy kích thước window; dispose observer/listeners/World khi unmount.

`npm run dev` bật IWER localhost theo dev.emulator trong manifest, không auto-enter XR. `npm run preview` là browser-first/native vì injectOnBuild=false. Bấm Vào VR để thử emulation trong dev; exit qua nút IWER. Plugin chỉ `{https:false}` vì localhost hợp lệ; không AI/MCP managed workspace hoặc tự mở browser. Không dùng self-signed certificate bypass để thử điện thoại. Muốn native AR trên Galaxy dùng HTTPS tin cậy hoặc USB localhost như checker, chưa được thử trong task.
