# Runbook thiết bị thật và preflight vault

## Thiết bị thật

**HARDWARE_BLOCKED** cho #4/#5. Trước lần thử, chủ dự án xác nhận model, môi trường, quyền dùng asset/media và thiết bị đại diện. Giảng viên duyệt workload, cách đo, task study và quy tắc dừng. Dùng route DEV loopback của M5, đã kiểm E0/hash trên chính checkout cần đo. [Runbook M5](../m5/P507-WEBXR.md)

### Galaxy A17 5G qua USB-localhost

1. Trên máy thử đã được phép, dùng Platform Tools/USB debugging, cắm cáp dữ liệu và xác nhận hộp thoại đúng máy. Chọn một thiết bị thật đã kết nối. Ghi model code, Android, Chrome và Google Play Services for AR; giữ số serial/IMEI ngoài bằng chứng.
2. Trên workstation chạy `npm run dev --prefix apps/web -- --port 5173 --strictPort`. Xác minh server lắng nghe loopback. Với một thiết bị được cấp quyền, chạy `adb -d reverse tcp:5173 tcp:5173` và kiểm mapping bằng `adb -d reverse --list` tại chỗ. Có thể dùng tính năng USB port forwarding của Chrome DevTools khi ADB trực tiếp không phù hợp. [Android ADB](https://developer.android.com/tools/adb) · [Chrome USB port forwarding](https://developer.chrome.com/docs/devtools/remote-debugging/local-server/)
3. Trong Chrome điện thoại mở `http://127.0.0.1:5173/?mode=p507-visit&evidence=1`. Qua remote console kiểm `window.isSecureContext`, `location.hostname` và ghi capability hai mode. Kiểm Web 3D tải đúng R4, responsive, chạm đúng ID, fallback khi thiếu hỗ trợ. Thử AR bằng nút từ thiết bị, kiểm từ chối/cho phép, hit-test có/không, chạm đặt trên mặt phẳng ngang, chọn ID sau đặt, system exit và re-entry. Ghi prompt/trạng thái thực tế và loại thiết bị; giữ media ở nơi đã được duyệt.
4. Nếu cần HTTPS, chỉ dùng TLS tin cậy qua đường thử riêng đã được duyệt, URL device-side vẫn thỏa loopback gate của ứng dụng. Xác minh chain/SAN trong trình duyệt. TLS với hostname khác không làm route DEV/loopback hợp lệ. Tránh cert bypass, chrome flags bỏ secure context, bind LAN, public tunnel và network bridge không được duyệt. Ghi BLOCKED nếu đường an toàn không tương thích.
5. Tháo đúng mapping bằng `adb -d reverse --remove tcp:5173`, thu hồi quyền USB debug của máy thử theo quy trình và dừng Vite. Ghi kết quả riêng cho mở phiên AR thật, hit-test, iOS/Android emulation nếu có, và cảnh tabletop. Kích thước ảo R4 và 1:1 thực địa là hai phạm vi khác nhau.

### Kính VR

- HMD tethered: ưu tiên browser hỗ trợ WebXR trên workstation kết nối kính theo runtime của nhà cung cấp, với cùng URL loopback. Kiểm `immersive-vr` và runtime compositor trước thao tác vào phiên trên thiết bị. Standalone: xác định browser/vendor có đường USB port forwarding hoặc private loopback đáng tin cho đúng máy. Nếu thiếu, xác nhận BLOCKED và ghi model/runtime thử, để owner duyệt phương án khác.
- Ghi model, firmware/runtime, browser, GPU driver (nếu có), resolution mỗi mắt, refresh rate đặt và đọc, render scale, reprojection, mức tải/nhiệt, nguồn điện, physical boundary và vùng di chuyển an toàn. Bắt đầu có người giám sát, dừng ngay nếu người thử khó chịu hoặc vượt vùng an toàn.
- Expected theo thứ tự: click để vào, đúng mode, ray/gaze khi runtime cung cấp, chọn logical ID và panel XR đọc được, thumbstick/va chạm, controller disconnect/reconnect, hệ thống tạm dừng, thoát và vào lại, trở về desktop và WebGL fallback. Ghi trường hợp unsupported/denied và expected/actual cùng artifact đã duyệt. Emulation kiểm hành vi, vật lý vẫn cần lần thử riêng. [WebXR Device API](https://www.w3.org/TR/webxr/)

### Raw frame timing

Chạy theo cửa sổ được phê duyệt sau warmup, cùng route/camera/scene settings ở mỗi lần. Có thể dùng 30 giây warmup và ba cửa sổ 120 giây làm đề xuất, chờ chủ dự án/giảng viên chốt. Ở URL `evidence=1`, sau khi canvas hoặc XR đã hoạt động, gọi trong console:

```js
window.__P507_M5__.startTiming("web", 120_000)
// Dùng "vr" hoặc "ar" trong phiên tương ứng. Lấy bản sao trước lần start tiếp theo.
copy(JSON.stringify({
  timing: window.__P507_M5__.timing,
  renderer: window.__P507_M5__.renderer,
  browser: navigator.userAgent,
  pixelRatio: window.devicePixelRatio,
}))
```

Nếu DevTools không có `copy`, in chuỗi JSON và lưu trong hồ sơ thử. Mỗi report có mode, duration, status, kích thước framebuffer, nominal XR Hz nếu runtime cung cấp và raw `intervalsMs` từ đồng hồ performance của callback. Ghi thêm code SHA, GLB SHA, workload, browser/GPU/runtime, test operator, UTC/timezone, hiển thị/thiết bị và profiler config vào metadata. Dữ liệu đo lưu thủ công ở máy thử. Tính `1000 * intervals.length / sum(intervals)`, p50/p95, số frame quá ngưỡng, lưu cả mẫu chậm. Capture bị gián đoạn vì pause/thoát/context loss phải có trạng thái riêng và ghi lý do trước khi chạy lại. Tách nominal refresh và cadence callback khỏi FPS compositor/app thật và dropped/reprojected frames. Đối chiếu VR72 bằng bộ đo runtime của kính trong protocol; giữ raw SwiftShader/IWER ở nhóm software regression.

### Hồi quy owner-local lặp lại

Từ checkout sạch, ghi SHA và chạy `validate_asset.py --prepare` rồi `verify_export_reference.py` theo [E0/E1 runbook](../../experiments/p507-webxr/README.md). Chạy `node apps/web/tests/m5-browser.mjs` cho fallback/mock, sau đó `node apps/web/tests/m5-browser.mjs --require-r4` cho Chrome WebGL/R4 và Chrome/IWER. Đặt `M5_BROWSER_OUT` riêng cho từng lượt để giữ report. Lưu exact SHA, hash GLB/manifest, scopes trong JSON, expected/actual, browser/OS/GPU, frame arrays và return code. R4 assets, screenshot hoặc media chưa có đủ quyền giữ cục bộ.

## Vault Issue #22

Đọc metadata source artifact 14309207795 ngày 20/11/2026: `expired=false`, 11.369.216 bytes, hết hạn **24/11/2026 14:46:36 ICT**. Bản lưu vault chủ sở hữu và bằng chứng owner-only clean restore tại commit vault đã pin `908a5cbb1f77b75b28666fd424cbd85f2aba4c1f` được ghi ở [R4 preservation](../3d-production/P507-R4-PRESERVATION.md). Hai check báo trạng thái trên main có thể SUCCESS trong lúc các job vault SKIPPED. [E0/E1 main run](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44659199187) · [TV diagnostic main run](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44659199182)

**Chạy được trên nhánh:** giữ phạm vi read-only và chạy `node --test experiments/p507-webxr/test_app_identity.mjs` và `python -m unittest discover -s experiments/p507-webxr -p "test_*.py" -v`. Nếu đã có copy R4 được phép, kiểm đúng ZIP hash, file/member locks, provenance, GLB và export reference theo runbook. Dùng `--prepare` cục bộ và đối chiếu report; chọn workspace riêng khi cần giữ báo cáo trước đó. Kết quả này không dùng thông tin xác thực App. [Security review và restore contract](../3d-production/P507-ISSUE22-SECURE-CI.md)

**Điều kiện chạy privileged, chủ dự án xét duyệt riêng:**

1. App riêng với **Contents Read**, Metadata Read ngầm định, tắt webhook không dùng, chỉ cài trên private vault đã pin. Xác minh toàn bộ danh sách repository được cài, App ID/client ID/installation ID và owner; token của workflow chỉ được thu hẹp tới vault.
2. Xác minh gói GitHub đủ quyền đặt environment `p507-vault-ci` với main-only, required reviewer, chặn tự duyệt và admin bypass, main được bảo vệ. Nếu điều kiện không khả dụng, giữ SECURITY_APPROVAL_REQUIRED.
3. Chỉ sau phê duyệt, owner điền trong environment ba biến `P507_VAULT_APP_CLIENT_ID`, `P507_VAULT_APP_ID`, `P507_VAULT_INSTALLATION_ID` và secret `P507_VAULT_APP_PRIVATE_KEY` qua UI bảo mật. Bật `P507_VAULT_CI_ENABLED=true` sau khi so check requirements và duyệt workflow main; không điền key ở repo/org scope.
4. Trên main đã review, chạy E0/E1 và TV diagnostic ở trusted jobs để chứng minh verify App identity, repository scope, token ngắn hạn, ZIP pin và 6 file, E0/E1/TV positives và negatives, không có original-Actions fallback. Chỉ chấp nhận bằng chứng gắn exact workflow SHA có kết quả thật. [GitHub protected environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
