# Ứng dụng web — M1-C synthetic integration

Chế độ mặc định dùng Catalog REST + WebSocket protocol2 cùng origin. Không tự thay bằng fixture khi API/DB lỗi. `/?mode=offline` là DEMO foundation riêng được chọn tường minh, không có realtime data. Layout primitive deterministic theo UUID sorting, không phải tọa độ phòng507. Render tối đa100objects/phòng; snapshot tối đa512states. Chưa hỗ trợ catalog mutation khi đang subscribe; cần tải lại Catalog nếu inventory thay đổi.

Chạy `npm ci --ignore-scripts --prefix apps/web`, `npm run dev --prefix apps/web`. API mặc định127.0.0.1:8000; Vite proxy `/api` và `/ws` cho dev/preview. Nếu đổi API port, đặt API_PROXY_TARGET phía Node, không VITE secret. Origin thật của trang cần có trong CORS_ORIGINS backend, không wildcard/changeOrigin. Browser dùng ws/wss theo location.

Tests: `npm run build --prefix apps/web`, `npm test --prefix apps/web`, `npm run test:browser --prefix apps/web`. Browser smoke foundation dùng explicit offline và kiểm tra live mode khi DB unavailable. RealPG→API→WS→Chrome test chạy từ pytest PostgreSQL (xem apps/api/README.md). Không cài browser tự động; CHROME_BIN cho Chrome có sẵn.390px là viewport emulation, không Galaxy.

## Hướng dẫn foundation trước M1-C

# Ứng dụng web chính thức — foundation

Node 22 >=22.12 <23; dependency và lockfile riêng. React 19 / R3F 9 / XR 6 theo baseline M0-B1. Hai primitive dùng dữ liệu synthetic, không phải phòng 507. Chưa có tracking, Guided Tour nghiệp vụ hoặc AR/VR session; không tự mở camera.

Từ root `D:\Code\DATN`:

```powershell
npm ci --ignore-scripts --no-fund --prefix apps/web
npm run dev --prefix apps/web
npm run build --prefix apps/web
npm test --prefix apps/web
```

Mở http://127.0.0.1:5173; khởi động backend theo [API README](../api/README.md). Vite proxy `/api` đến http://127.0.0.1:8000 trong dev/preview. `API_PROXY_TARGET` là cấu hình Node-side nếu đổi cổng, không nhúng secret vào `VITE_`. Hosting/routing production chưa được chọn. UI phân biệt backend alive và PostgreSQL not ready; lỗi API không ngăn xem dữ liệu DEMO.

## Browser smoke thực tế

Build trước, dùng Chrome có sẵn, không tự tải browser:

```powershell
$env:API_PYTHON = 'D:/Code/DATN/.local/api-venv/Scripts/python.exe'
$env:CHROME_BIN = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
npm run test:browser --prefix apps/web
```

Linux: `API_PYTHON="$PWD/.local/api-venv/bin/python" CHROME_BIN=/usr/bin/google-chrome npm run test:browser --prefix apps/web`.

Runner mở Vite preview/FastAPI trên cổng loopback ngẫu nhiên, process/profile riêng và dọn khi kết thúc. API test không đọc `.env` root: cwd riêng trong `.local/t`, loại DATABASE_URL/CORS_ORIGINS khỏi environment kế thừa. Backend health 200 và DB not_configured 503 là expected trong suite này. PostgreSQL success được kiểm riêng ở backend CI.

Report và ảnh `desktop.png`, `mobile-390.png`, `unsupported.png` ở `.local/app-browser`, ignored; CI upload artifact 14 ngày. 390px là viewport emulation trên Chrome headless/software WebGL, không phải Galaxy thật. WebGL unsupported và network failure có injection rõ trong report; không mock XR hoặc khởi tạo camera. Browser không được tìm thấy trả NOT RUN và exit khác 0.

Các lớp: src/app, components, features/catalog, scene, api, shared, styles. Renderer không gọi backend trực tiếp; demo adapter tách khỏi mesh. Scene lazy nhưng SDK vẫn sinh emulator chunks lúc build dù không kích hoạt/load: cần budget bundle và asset ở M1. Dừng dev server bằng Ctrl+C.


## C3 diagnostics và bằng chứng

Bản chạy thông thường không thu thập test diagnostics. Để build phục vụ suite realbrowser: PowerShell `$env:VITE_TEST_DIAGNOSTICS='1'` rồi npm run build; Linux `VITE_TEST_DIAGNOSTICS=1 npm run build --prefix apps/web`. Đặtflag chỉ trongtest; không dữ liệu cá nhân. CI bậtflag, uploadartifact .local/m1-c-browser/report.json cùngảnhCanvas/desktop390px. Khôngcommit profiles/cache hoặc ảnhgiả. Report raw20samples vàclockbounds; khôngFPS thiếtbị/KPI AIRC.
