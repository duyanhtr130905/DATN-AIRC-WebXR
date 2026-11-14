# PoC A — React Three Fiber + React Three XR

**DEMO – DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI PHÒNG 507.** Một phòng generic 12×3×9 đơn vị thử nghiệm, 5 primitive, không có số đo/inventory AIRC. Không phải sản phẩm chính thức và không chứng minh KPI MT1/MT2/MT3.

## Setup và chạy riêng

Node 22.12+ trong major 22; npm. Tại `D:\Code\DATN\experiments\poc-a-r3f-xr`:

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

## Dependency và emulator A

React/DOM 19.3.1, R3F 9.8.2, React Three XR 6.6.32, **Three.js stock 0.185.0**; Vite 7.3.8, TS 5.9.3. Lockfile riêng; không dùng super-three cho A. Vite major 7 được chọn vì plugin IWSDK yêu cầu ^7, cùng toolchain cho phép so sánh công bằng.

Thử IWER bằng URL `?emulate=1` trên localhost (preview cũng hỗ trợ). Store tắt offerSession và enterGrantedSession; chỉ query này bật injection, không auto-enter. Override IWER và DevUI về cùng **2.8.0** vì dependency XR mặc định ghép DevUI 1.1.2/Three 0.165 với IWER mới dẫn tới lỗi render. SEM giữ bản gốc 0.2.5, `syntheticEnvironment:false`, không tải preset room. IWER 2.8 bảo vệ native navigator.xr dù Chrome không có thiết bị; chỉ trong URL opt-in mới gọi `installRuntime({forceInstall:true})`, đây là JavaScript emulation chứ không ép Chrome/hardware thành hỗ trợ AR.

Override đã được thử runtime, chưa phải upstream compatibility guarantee. Ba preset chunks vẫn có trong build do import động của dependency, dù không dùng trong cảnh. Cần tối ưu tree-shaking/splitting sau PoC; không giấu cảnh báo bundle lớn.
