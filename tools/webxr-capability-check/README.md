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

## Browser smoke portable và screenshot tái lập (review fixes P2/P3)

Cần Python 3.13 và Node >=22; không cần npm/pip dependencies cho runner. Windows/Linux được hỗ trợ: ưu tiên `CHROME_BIN`, sau đó Chrome/Chromium trong PATH và các vị trí hệ thống phổ biến. Không tự tải/cài browser. `CHROME_BIN` sai sẽ báo NOT RUN thay vì âm thầm dùng browser khác.

Windows PowerShell, tại root:

```powershell
$env:CHROME_BIN = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
python tools/webxr-capability-check/tests/run_browser_smoke.py
```

Có thể bỏ biến trên để tự tìm. Linux, tại clone của chính repository này (không thay workspace local Windows):

```sh
CHROME_BIN=/usr/bin/google-chrome python3 tools/webxr-capability-check/tests/run_browser_smoke.py
# hoặc tự tìm browser trong PATH
python3 tools/webxr-capability-check/tests/run_browser_smoke.py
```

Kết quả `.local/browser-smoke/result.json` chứa timestamp +07:00, OS/Python, Chrome product/version, từng scenario expected/actual/status và cleanup. `.local/browser-smoke/checker-390.png` là ảnh checker thật do Chrome chụp với viewport emulation 390×900 CSS px, không phải Galaxy. Không mở camera/requestSession. File `browser-driver.cjs` dùng CDP và WebSocket tích hợp Node, không cần package ngoài.

Exit code: **0 = utility scenarios PASS**, **1 = FAIL** (bao gồm browser startup/driver/cleanup), **2 = NOT RUN** (không tìm được browser hoặc Node). NOT RUN phải được hiển thị rõ; không đổi thành browser PASS. Native là quan sát runtime, mock chỉ kiểm tra nhánh lỗi/quyền; không trường hợp nào chứng minh phần cứng AR/VR.

Runner chỉ bind `127.0.0.1`, phục vụ thư mục checker; CDP cũng chỉ loopback. Tạo profile duy nhất trong `.local/browser-smoke/profile-*`, không dùng profile cá nhân. Có startup/driver deadline, đóng bằng Browser.close; finally đóng server/thread và chờ browser, fallback chỉ kết thúc process tree do runner tạo. Profile tạm được xóa; stderr/report ở vùng ignored. Không upload profile, cache hoặc stderr. Để tái lập trạng thái thiếu browser, đặt `CHROME_BIN` tới file không tồn tại và kiểm tra exit 2/report NOT RUN.

Test discovery/cleanup:

```sh
python -m unittest discover -s tools/webxr-capability-check/tests -p test_runner.py -v
```

CI có job `validation` bắt buộc và job `browser` riêng. Browser có sẵn thì lỗi test làm job FAIL; browser thiếu thì warning + report NOT RUN, không giả PASS. CI chỉ upload đúng JSON/screenshot qua allowlist; không ghi commit/deploy. [Ảnh review](../../docs/evidence/checker-390.png) và [report local mới](../../docs/evidence/browser-smoke.json) được lưu có chủ đích; artifact CI là kết quả lần chạy riêng, không ghi đè report local trong Git.
