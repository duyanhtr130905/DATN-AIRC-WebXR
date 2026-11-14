# WebXR capability check — công cụ M0 độc lập

Không dependency, React, backend hay database. Chỉ kiểm tra secure context, sự tồn tại `navigator.xr` và `isSessionSupported('immersive-ar'/'immersive-vr')`. Không gọi `requestSession`, `getUserMedia`, storage hoặc API mạng ngoài. Không tự mở camera; truy vấn chỉ chạy khi bấm nút. Trang tĩnh được server local cung cấp, kết quả nằm trong DOM và mất khi reload.

## Chạy trên máy tính

PowerShell:

```powershell
Set-Location -LiteralPath 'D:\Code\DATN'
python -m http.server 8000 --bind 127.0.0.1 --directory tools/webxr-capability-check
```

Mở `http://localhost:8000` rồi bấm **Kiểm tra API**. Dừng server bằng Ctrl+C. Server chỉ bind loopback; không phục vụ toàn bộ repository hoặc `.git`. Không khuyến nghị mở bằng file:// vì không đại diện luồng web/runtime. Python cần có sẵn; không cài hệ thống chỉ để chạy nếu chưa được phép.

## Galaxy A17 5G qua USB — phương án ưu tiên

1. Ghi model code, Android/Chrome/Google Play Services for AR version (không IMEI/serial); đối chiếu [danh sách ARCore](https://developers.google.com/ar/devices).
2. Chạy server ở máy tính như trên. Bật Developer options và USB debugging trên điện thoại nếu bạn đồng ý; chỉ xác nhận máy tính tin cậy của mình.
3. Kết nối USB, mở Chrome máy tính tại `chrome://inspect/#devices`, bật Discover USB devices, chấp thuận hộp thoại debugging trên điện thoại.
4. Chọn **Port forwarding**, đặt Device port `8000` → `localhost:8000`, bật forwarding. [Hướng dẫn Chrome chính thức](https://developer.chrome.com/docs/devtools/remote-debugging/local-server).
5. Chrome Android mở `http://localhost:8000`. Đây là localhost trên điện thoại qua USB, khác `http://<IP-máy-tính>:8000`. Kiểm tra secure context phải là Có; nếu Không thì dừng và kiểm tra cấu hình.
6. Bấm nút, ghi lại bốn kết quả, ngày giờ và versions; che thông tin riêng tư trước gửi. Tắt forwarding/USB debugging hoặc thu hồi quyền máy tính khi xong.

Cách khác: HTTPS có certificate chain được điện thoại tin cậy, phục vụ đúng thư mục này. Không bỏ qua lỗi certificate, không bật flag coi insecure origin là secure, không deploy lên hosting hay tunnel ngoài trong M0-A. Nếu chưa có USB/chứng chỉ hợp lệ thì ghi BLOCKED; không ép test HTTP LAN.

## Hiểu kết quả

- `secure context=false`: chưa truy vấn mode; dùng HTTPS hợp lệ/localhost.
- Không có `navigator.xr` hoặc thiếu method: trình duyệt/runtime hiện tại không cung cấp API đó; có thể vẫn xem Web 3D trong sản phẩm tương lai.
- `true`: trình duyệt báo hỗ trợ mode, **không chứng minh ARCore, tracking, hit-test, camera permission, model rendering hoặc FPS**.
- `false`: môi trường hiện tại không hỗ trợ mode; xem lại thiết bị, runtime và browser. Không kết luận vĩnh viễn về model.
- Promise rejection/SecurityError/NotAllowedError: hiển thị lỗi quyền/chính sách; hai mode độc lập. Pending quá 5 giây được ghi chưa xác định, có thể thử lại.
- Iframe có thể bị Permissions Policy chặn. Nên kiểm tra top-level; không dùng emulator/extension để kết luận máy có AR/VR thật.

## Kiểm thử và ghi nhận

```powershell
node --check tools/webxr-capability-check/checker.js
node --test tools/webxr-capability-check/tests/checker.test.cjs
```

Unit/DOM mock chỉ chứng minh logic lỗi và UI. Browser smoke (nếu chạy) ghi riêng tại [evidence](../../docs/evidence/m0-validation.md). Galaxy A17 5G, iPhone và kính VR thực tế: **NOT TESTED**. Công cụ không render AR, không đo FPS, không lưu session và không thay test MT1–MT3.

Ngày đối chiếu nguồn: 14/11/2026. [Google WebXR requirements](https://developers.google.com/ar/develop/webxr/requirements), [WebXR Device API](https://www.w3.org/TR/2026/CRD-webxr-20261109/).
