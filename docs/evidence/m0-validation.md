# Bằng chứng kiểm tra M0-A

Ngày thực hiện: 14/11/2026 (Asia/Saigon). Workspace `D:\Code\DATN`; Windows, Git 2.54.0.windows.1, Node 22.16.0, Python 3.13.2, Chrome 157.0.8103.51. Chỉ kiểm tra tài liệu và utility độc lập, không có benchmark sản phẩm.

## An toàn và GitHub

- VERIFIED: resolve root đúng, 0 mục kể cả ẩn trước bootstrap, không có `.git` tại root hoặc D:/Code hay D:/; thư mục ban đầu ĐATN không có `.git`. Không truy cập repository KLTN.
- VERIFIED: `gh auth status` trong môi trường có mạng và `gh api user` xác nhận `duyanhtr130905`. Lần chạy bị hạn chế mạng ban đầu báo token invalid/connection error; sau dùng kết nối được cho phép, keyring auth hợp lệ. Không đổi auth/config hoặc lưu token vào repo.
- VERIFIED trước tạo: exact API trả 404; danh sách toàn bộ owner repos phân trang không có tên trùng không phân biệt hoa/thường.
- VERIFIED sau tạo: repo private, default main, origin đúng AIRC. Bootstrap SHA `b3c4f43`; làm M0 trên `docs/m0-foundation`.

## Kiểm thử utility thực sự đã chạy

| Kiểm tra | Kết quả | Phạm vi |
| --- | --- | --- |
| `node --check tools/webxr-capability-check/checker.js` | PASS | cú pháp checker trên Node 22.16 |
| `node --check tools/webxr-capability-check/tests/browser-smoke.js` | PASS | cú pháp browser test |
| `node --test tools/webxr-capability-check/tests/checker.test.cjs` | PASS: 10/10 | insecure chặn query; navigator/XR/method thiếu; đúng this + true/false độc lập; permission rejection; sync throw/generic reject; getter lỗi; non-boolean; timeout; UI disable/retry |
| `python tools/webxr-capability-check/tests/run_browser_smoke.py` | PASS sau sửa harness | Chrome headless trên localhost, GPU disabled; native desktop + XR mock tách biệt |
| Kiểm thử Galaxy A17 5G/iPhone | NOT RUN; thiết bị vật lý NOT TESTED | không điều khiển hoặc tiếp cận điện thoại trong task |
| VR emulator / kính thật | NOT RUN / NOT TESTED | không cài emulator, không có kính; không có evidence 72 FPS |
| MT1–MT3 sản phẩm | NOT RUN | chưa triển khai, chưa có dữ liệu thật, người thử hoặc session dataset |

[Browser result JSON](browser-smoke.json) ghi kết quả runtime: secure context Có, navigator.xr Có, **native immersive-ar và immersive-vr đều timeout/chưa xác định**. Mock cố tình AR reject NotAllowedError, VR true và UI hiển thị độc lập. Browser smoke PASS nghĩa utility xử lý được các trạng thái này; không nghĩa thiết bị hỗ trợ AR/VR.

Hai lỗi của harness đã được tìm và sửa: chạy lúc iframe còn about:blank làm null button; stdout Python Windows không xuất được Unicode. Chạy lại hoàn tất sau sửa. Không xóa lịch sử thất bại khỏi báo cáo để giả PASS ngay từ đầu. Favicon test page trả 404 local, không ảnh hưởng checker logic. Không có camera hoặc requestSession được gọi.

## Repository verification

`python tools/verify_repository.py` kiểm tra UTF-8, local Markdown links, resource nội bộ và mẫu secret phổ biến; static scan checker không có network/session/camera/storage API. Không phải audit bảo mật đầy đủ. Lần kiểm tra giữa quá trình dựng tài liệu phát hiện 4 link đến tài liệu chưa tạo; các tài liệu đó được hoàn thiện trước lần xác minh cuối.

PASS: repository verifier đã chạy trên bộ tài liệu hoàn chỉnh, không còn link nội bộ hỏng và không phát hiện mẫu secret đã cấu hình. `git diff --check` và `git diff --cached --check` đã chạy sạch; chạy lại trên nội dung cuối trước commit/push. Diff được đọc để kiểm tra nhất quán scope/KPI/status, không có raw survey, ảnh/PII, credentials hoặc frontend/backend sản phẩm.

## Kiểm tra bố cục và issues

Chrome headless qua CDP đặt viewport mobile 390 × 900 CSS px: `innerWidth=390`, `documentElement.scrollWidth=390`, nút rộng khoảng 134px; ảnh chụp toàn trang đã xem, chữ không tràn ngang. Đây là emulated viewport, không phải Galaxy vật lý. Ảnh và profile tạm giữ trong `.local/`, không push. Lần chụp bằng window-size đơn thuần không đủ mô phỏng mobile nên đã dùng device metrics override để kiểm tra đúng viewport.

Năm issues #1–#5 đã tạo, đọc lại body/state từ GitHub CLI và xác nhận đều OPEN; không issue nào có bằng chứng được gỡ. Browser smoke sử dụng virtual-time-budget 15000ms; timeout native không dùng để kết luận support phần cứng hay đo thời gian thực/FPS.

## Research verification

Nguồn URL/ngày và giới hạn truy cập tại [sổ nguồn](../research/sources.md); metadata registry/repo tại [versions.json](../research/versions.json). Các URL quan trọng đã mở trực tiếp hoặc GET registry bằng mạng thật. Matterport live CSS Error và FastAPI WebSocket docs không đọc được được ghi rõ; không ghi mọi external URL đều HTTP PASS. Không cài runtime/dependency sản phẩm.

## Cách tái lập

Từ root chạy syntax, node tests, repository verifier và diff check như trên. Browser runner cần Chrome tại đường Windows hiện có, mở server loopback tạm, đóng server khi xong; log/profile trong `.local/` bị Git ignore. Browser runner khác kiểm thử điện thoại; theo README checker để người dùng tự thực hiện secure-context preflight. Metadata nguồn có thể thay đổi theo ngày.
