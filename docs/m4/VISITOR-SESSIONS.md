# M4 — Phiên tham quan và báo cáo synthetic/local

[Issue #27](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/27) · [Quyết định phạm vi](../decisions/0002-m4-synthetic-visitor-scope.md) · [Roadmap](../ROADMAP.md)

## Chạy thử cục bộ

1. Dùng PostgreSQL 18 qua TCP loopback và tạo một database trống riêng tên `airc_visitor_local`. Thiết lập `DATABASE_URL` theo runbook [API](../../apps/api/README.md). Fixture CI tạo database riêng `airc_test_catalog_<32 hex>` dưới cụm thử nghiệm rồi xác minh tên trước khi chạy. Dùng bộ dữ liệu dựng sẵn của cảnh demo, gồm một phòng mô phỏng và hai khối mẫu.
2. Trong `apps/api`, chạy `python -m alembic -x confirm_catalog_database=airc_visitor_local upgrade head`. Lệnh yêu cầu xác nhận tên database. Migration 0005 tạo thêm hai bảng, constraint và index. Trước khi nâng một database có dữ liệu, xác minh backup và khôi phục ở database riêng. Khi xảy ra lỗi trong migration, transaction PostgreSQL rollback. Khi đã áp dụng, tắt tính năng và giữ bảng để giữ bằng chứng hoặc khôi phục backup sang database riêng sau khi kiểm chứng. Downgrade bị chặn.
3. Bật `VISITOR_SYNTHETIC_ENABLED=true` trong môi trường local của API. Nếu cần báo cáo, bật `ADMIN_ENABLED=true` và chạy `python -m app.modules.admin_bootstrap --confirm-database airc_visitor_local --username <ten>` theo quy trình mật khẩu tương tác trong runbook [M3](../m3/P507-M3-INTEGRATION.md). Đặt `ADMIN_ORIGIN=http://127.0.0.1:5173`. Khởi chạy API với `python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-proxy-headers`. Chạy Vite ở loopback cổng 5173. Giữ Vite và API trên máy kiểm thử, tránh tunnel hoặc reverse proxy công khai.
4. Mở `http://127.0.0.1:5173/?mode=offline` và chọn **Đồng ý ghi phiên mô phỏng**. Chọn khối mẫu, mở/ẩn thông tin, tải lại hoặc thử ngắt kết nối rồi đồng bộ. **Kết thúc phiên** ghi một sự kiện kết thúc. **Dừng ghi và xóa phiên** bỏ ngay dữ liệu tương tác và hàng đợi của phiên trong trình duyệt rồi đề nghị máy chủ xóa đúng phiên và các sự kiện con. Khi offline trình duyệt chỉ giữ ID cùng cờ chờ xóa để thử lại. Khi mã đã hết hạn, phiên đã mất hoặc cookie bị xóa, giao diện báo máy chủ không còn chấp nhận chứng minh và không xác nhận dữ liệu trên máy chủ đã bị xóa.
5. Mở `?mode=admin`, đăng nhập và chọn **Báo cáo phiên mô phỏng**. Lọc theo ngày bắt đầu phiên (UTC), phân trang danh sách và tải CSV/JSON.

## Thiết kế phục hồi và quyền truy cập

- Cookie host-only theo đường dẫn API visitor, HttpOnly, SameSite Strict, Secure khi chạy HTTPS. Máy chủ tạo ID phiên và 256 bit ngẫu nhiên cho chứng minh, chỉ giữ SHA-256. Tuổi thọ tuyệt đối 8 giờ phục vụ kiểm thử, độc lập với thời gian giữ dữ liệu. Cookie và ID phiên đều phải khớp. Xóa phiên thu hồi chứng minh. Cookie bị sao chép vẫn có thể phát lại trước thời điểm hết hạn hoặc thu hồi.
- Kiểm tra loopback peer, Host và scheme tường minh theo Admin origin, Origin trên mọi thao tác ghi, Fetch Metadata khi có, header riêng trên API phiên và từ chối header chuyển tiếp. Origin/CORS và CSRF của Admin kiểm soát xuất báo cáo. HttpOnly giảm nguy cơ đọc mã qua JavaScript. Mã tùy ý chạy trong cùng origin vẫn có thể thực hiện thao tác trong phiên, nên dùng origin local dành riêng và chỉ chạy mã tin cậy.
- Hàng đợi theo origin và chỉ lưu sau opt-in. Web Locks tuần tự hóa cập nhật qua tab và cho một luồng đồng bộ hoạt động tại một thời điểm. Mỗi event được gán UUID trước khi gửi, tối đa 128 event chờ, gửi 16 mỗi lần, timeout 3,5 giây và tối đa 3 lần retry tự động sau lần thử đầu. Tải lại, kết nối lại và nút thử lại có thể kích hoạt một lượt mới. Mất phản hồi sau commit giữ nguyên ID khi gửi lại. Nếu máy chủ từ chối batch, giao diện giữ hàng đợi và báo lỗi.
- Khi web shell còn truy cập được, có thể tải lại trang trong lúc API visitor mất kết nối. Khi mất cả web shell, cần kết nối lại để tải ứng dụng. Trình duyệt từ chối cookie, bộ nhớ hoặc Web Locks có thể dùng cảnh mẫu. Việc dọn dữ liệu site trong trình duyệt có thể làm mất chứng minh và dữ liệu chưa gửi.
- Bản ghi chỉ có nguồn mô phỏng, ID ngẫu nhiên, sự kiện allowlist và timestamp. Chế độ chạy mặc định tắt. Production bundle không hiển thị tính năng visitor hay Admin. API chỉ nhận PostgreSQL local riêng hoặc database kiểm thử UUID theo guard. Trong CI, PostgreSQL service dùng cổng được publish loopback, kiểm thử có guard tên và cờ riêng cho kết nối container.

## Kiểm chứng

```text
npm run build --prefix apps/web
npm test --prefix apps/web
npm run test:browser --prefix apps/web
python -m ruff check apps/api
python -m pytest -m 'not postgres'                  # cwd apps/api
python -m pytest -m postgres                        # cwd apps/api, disposable service
python tools/verify_repository.py
git diff --check
```

Bộ PostgreSQL yêu cầu `TEST_DATABASE_URL` trỏ vào `airc_foundation_test` trên loopback, `AIRC_ALLOW_TEST_DATABASES=1` và Chrome thật qua `CHROME_BIN`. Test migration nâng DB populated 0004, khôi phục bản sao logic vào DB riêng, so sánh dữ liệu M1–M3, thử rollback transaction và downgrade. Test Chrome chạy API thật, Vite và PostgreSQL, giữ bằng chứng tại `.local/m4-visitor-browser/`. CI tải thư mục và JUnit dưới artifact PostgreSQL của workflow application foundation.

Trình tạo oracle độc lập ở `apps/api/tests/visitor_oracle.py` sinh 1.000 UUID trước khi ghi. Bài test gán chúng vào 50 phiên riêng, gửi ngược thứ tự, phát lại và thử thay đổi nội dung. Đối chiếu DB, báo cáo, CSV và JSON. Artifact `.local/m4-visitor-evidence/` chứa manifest/binding, dữ liệu DB đã lọc, hai export và đối chiếu kèm SHA/môi trường. Snapshot tính thêm đúng một `session_start` do máy chủ sinh cho mỗi phiên. Chạy trên dịch vụ disposable và kiểm DSN trước mọi thử nghiệm sự cố.

## Điều kiện nghiệm thu

- Nghiệm thu kỹ thuật M4 qua review độc lập đúng HEAD Draft PR. Kiểm tra toàn bộ DoD, exact HEAD và bằng chứng tại [Draft PR #28](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28).
- Chủ dự án và người có thẩm quyền phê duyệt phạm vi thu thập, identity/consent, retention/xóa và quyền xem, xuất hoặc công bố trước khi bật ghi dữ liệu khách thật. Tài liệu này quy định cách thử với dữ liệu mô phỏng.
- M3 #2/#3 tiếp tục theo dõi riêng theo roadmap. Nghiệm thu MT1–MT3, gồm protocol và phiên người thật, theo M6.
