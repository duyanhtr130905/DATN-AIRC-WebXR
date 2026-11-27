# Thực hành demo M0–M5 trên Windows

Dùng checkout PR #32 tại D:\Code\DATN, Node 22.12–22.x, môi trường Python 3.13 đã cài theo runbook API và Chrome. Chạy từng khối trong PowerShell riêng theo thứ tự. Dừng và đọc lỗi nếu lệnh kiểm tra hoặc khởi động thất bại. [Runbook API](../../apps/api/README.md)

## Chuẩn bị R4 và chạy web

Nếu bản R4 gốc chưa có trên máy, chủ dự án dùng gh đã đăng nhập và chạy `python experiments/p507-webxr/prepare_asset.py --restore-vault` theo quyền hiện có. Lệnh từ chối ghi đè đích đã tồn tại. Với bundle gốc đã lưu, kiểm trực tiếp bằng các lệnh dưới. [Khôi phục và xác minh R4](../../experiments/p507-webxr/README.md)

```powershell
Set-Location D:\Code\DATN
python experiments/p507-webxr/validate_asset.py --prepare
python experiments/p507-webxr/verify_export_reference.py
npm ci --ignore-scripts --no-fund --prefix apps/web
$env:API_PROXY_TARGET = 'http://127.0.0.1:8000'
npm run dev --prefix apps/web -- --port 5173 --strictPort
```

Có thể mở cảnh mẫu offline ngay khi có Vite. Hai màn P507 Web 3D/XR và E1 cần R4 đã xác minh và chạy độc lập với API. Digital Twin cần API/PostgreSQL để xem Catalog và trạng thái. Admin và ghi phiên synthetic cũng cần API/PostgreSQL.

## Backend tùy chọn với PostgreSQL dùng riêng

Dùng PostgreSQL 18 dành riêng cho demo. Chọn cổng trống, chỉ bind 127.0.0.1, và xác minh đúng cụm PostgreSQL trước khi tạo database. Nếu cần tạo cụm mới, dùng `initdb -D <thư-mục-mới> -U airc_demo -A scram-sha-256 -W`, rồi `pg_ctl -D <thư-mục-mới> -l <log-riêng> -o "-h 127.0.0.1 -p 55497" -w start`. Ghi lại thư mục để dừng đúng tiến trình. Nhập mật khẩu demo tại prompt. Ví dụ dưới dùng `createdb` của cụm demo trên cổng 55497 và role `airc_demo`. `createdb` phải thành công trước migration hoặc seed.

```powershell
Set-Location D:\Code\DATN
$demoDb = 'airc_test_catalog_' + [Guid]::NewGuid().ToString('N')
createdb -h 127.0.0.1 -p 55497 -U airc_demo -W $demoDb
if ($LASTEXITCODE -ne 0) { throw 'Chưa tạo được database demo mới' }
$demoSecret = Read-Host 'Mật khẩu PostgreSQL demo' -AsSecureString
$demoEncoded = [Uri]::EscapeDataString([PSCredential]::new('airc_demo', $demoSecret).GetNetworkCredential().Password)
$env:DATABASE_URL = "postgresql+psycopg://airc_demo:${demoEncoded}@127.0.0.1:55497/$demoDb"
Remove-Variable demoSecret,demoEncoded
$env:ADMIN_ORIGIN = 'http://127.0.0.1:5173'
$env:CORS_ORIGINS = $env:ADMIN_ORIGIN
$env:VISITOR_SYNTHETIC_ENABLED = 'true'
$env:ADMIN_ENABLED = 'true'
$env:REALTIME_DISPATCHER_ENABLED = 'true'
$demoPython = (Resolve-Path .local/api-venv/Scripts/python.exe).Path
Set-Location apps/api
& $demoPython -m alembic -x "confirm_catalog_database=$demoDb" upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration demo thất bại' }
```

Chọn seed P507 để trình diễn Catalog và dữ liệu trạng thái. Dùng đúng manifest đã qua E0. Chạy bootstrap riêng nếu trình diễn Admin. Mật khẩu Admin được nhập tương tác, không ghi vào lệnh hay Git. [M3 Admin và dữ liệu mô phỏng](../m3/P507-M3-INTEGRATION.md) · [M4 phiên và báo cáo](../m4/VISITOR-SESSIONS.md)

```powershell
$demoManifest = (Resolve-Path ../../.local/p507-e0-e1/served/asset-manifest.json).Path
& $demoPython -m app.modules.p507_cli --confirm-database $demoDb --authorize-synthetic p507-r4-synthetic-v1 --seed-manifest $demoManifest
& $demoPython -m app.modules.admin_bootstrap --confirm-database $demoDb --username demo_operator
& $demoPython -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-proxy-headers
```

Có thể bỏ hai lệnh seed/bootstrap nếu chỉ chạy cảnh offline. Chỉ nhập fixture synthetic trong Admin. Mở http://127.0.0.1:8000/api/ready để kiểm PostgreSQL sẵn sàng.

## Trình tự trình diễn

| Màn hình | Thao tác |
| --- | --- |
| http://127.0.0.1:5173/?mode=offline | Xoay cảnh, chọn khối mẫu. Khi bật M4, bấm đồng ý, chọn khối, mở/ẩn thông tin. Dừng API trong lúc trang vẫn mở, thực hiện thêm thao tác và kết thúc. Khởi động lại API, bấm thử đồng bộ nếu cần, kiểm trạng thái đã kết thúc rồi mở lượt mới. |
| http://127.0.0.1:5173/?mode=p507 | Chọn phòng và vật thể, đối chiếu stable ID và nhãn nguồn synthetic. Xem một quan sát do Admin nhập và trạng thái cập nhật khi kết nối hoạt động. |
| http://127.0.0.1:5173/?mode=p507-visit | Chọn từ canvas hoặc danh sách, kéo để nhìn, WASD khi canvas có focus, thử reset và lối đi ngắn phía tây. Nút vào AR/VR phụ thuộc runtime có hỗ trợ. |
| http://127.0.0.1:5173/?mode=admin | Đăng nhập bằng tài khoản vừa bootstrap, chọn bản ghi synthetic và nhập quan sát có nguồn và timestamp. Vào báo cáo phiên, lọc theo ngày UTC, kiểm số sự kiện và tải CSV/JSON. |
| http://127.0.0.1:5173/p507-webxr-e1.html | Đợi LOADED, bấm Start để khóa chuột, đi bằng WASD, click chọn vật thể, Esc để thả chuột rồi thử Reset. |

Khi API mất kết nối nhưng Vite còn chạy, vẫn có thể reload để kiểm hàng đợi M4. Khi Vite cũng tắt, mở lại Vite cùng origin trước khi reload. Nếu mất mã phiên, giữ dữ liệu đang chờ đến khi quyết định xử lý. Trạng thái 413 cho biết batch bị từ chối và dữ liệu chưa ACK vẫn còn trên trình duyệt. Tại cổng sai hoặc thiếu /api/ready, kiểm port, DATABASE_URL và Vite proxy. Lỗi Admin/visitor 403 cần kiểm loopback và đúng origin 127.0.0.1:5173. Khi E0 fail, kiểm lại bundle và hash theo runbook, rồi mới mở lại. Khi WebGL không khả dụng, dùng danh sách.

Kết thúc buổi demo, đăng xuất Admin và Ctrl+C ở cửa sổ Vite/API. Nếu đã tạo cụm riêng, dùng `pg_ctl -D <đúng-thư-mục-cụm-demo> -m fast -w stop`. Đóng cửa sổ PowerShell chứa cấu hình DB. Dùng profile Chrome demo riêng nếu cần dọn dữ liệu site, và chỉ dọn khi đã xác nhận các phiên cần giữ hoặc đã xuất báo cáo. Giữ database dùng riêng để đối chiếu, hoặc xóa thủ công sau khi chủ dự án xác nhận đúng cụm/thư mục và không còn cần dữ liệu. Không xóa R4 đã xác minh.

Chrome/IWER kiểm kỹ thuật qua XR mô phỏng. SwiftShader là render phần mềm. Phép thử Galaxy A17/HMD và KPI Web3D 30 FPS/VR 72 FPS cần thiết bị và protocol riêng. [Thiết bị và phạm vi R4](SECURE-DEVICE-AND-VAULT.md)
