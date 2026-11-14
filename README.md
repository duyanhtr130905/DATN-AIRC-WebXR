# DATN AIRC WebXR

**Xây dựng bản sao số không gian AIRC trên nền tảng WebXR hỗ trợ tham quan tương tác và lưu vết trải nghiệm.**

AIRC là Trung tâm Nghiên cứu tiên tiến quốc tế về Trí tuệ nhân tạo ứng dụng, thuộc Viện Công nghệ thông tin – ĐHQGHN (bối cảnh do chủ đề cung cấp).

## Trạng thái hiện tại — M0-B1

PR #6 (M0-A) đã merge; đang thử hai PoC synthetic, chưa triển khai sản phẩm. Xem [prototype và lệnh chạy](experiments/README.md) và [so sánh A/B](docs/11-renderer-poc-comparison.md). Một phòng DEMO/năm object không phải phòng 507, không chứng minh KPI sản phẩm. Chỉ đạo mới: làm phòng 507 trước, survey dự kiến 16/11/2026; KPI ≥3 phòng vẫn chờ giải quyết chính thức.

## Mốc nền tảng trước đó

M0-A — Foundation & Feasibility, ngày 14/11/2026. Chưa khảo sát chi tiết, chưa có dữ liệu thực AIRC, chưa xác nhận đủ ba phòng. Theo trao đổi mới do người dùng cung cấp, giảng viên cho biết hiện chỉ có phòng 507; đang chờ xác nhận phạm vi chính thức để xử lý mâu thuẫn KPI ≥3 phòng, không tự điều chỉnh KPI. Chưa có frontend/backend sản phẩm, cơ sở dữ liệu, AR scene hoặc VR trải nghiệm. Framework và kiến trúc chưa được phê duyệt. Dự án độc lập hoàn toàn với KLTN-Factory-Agentic-DT, không sử dụng tài sản của dự án đó.

## Mục tiêu và phân hệ dự kiến

- MT1: ≥3 phòng, ≥20 đối tượng tương tác, ≥3 loại trạng thái (lịch phòng, tình trạng thiết bị, thông tin trưng bày), cập nhật hiển thị ≤5 giây.
- MT2: Web 3D ≥30 FPS; AR/VR trên thiết bị tương thích; mục tiêu VR ≥72 FPS trên kính được lựa chọn; ≥90% tác vụ hoàn thành với ≥15 người.
- MT3: lưu phiên/sự kiện, khôi phục sau reload, ghi nhận ≥99% sự kiện trong bộ kiểm thử, báo cáo ≥50 phiên mẫu.

Các phân hệ chỉ là đề xuất: không gian/3D assets, tương tác & XR, dữ liệu trạng thái, lưu vết & báo cáo, quản trị quyền. AI/RAG là mở rộng, không triển khai M0. Hạn dự kiến tháng 4/2027; quản lý theo milestone.

## Đọc tài liệu

| Nội dung | Tài liệu |
| --- | --- |
| Charter, phạm vi | [01](docs/01-project-charter.md) |
| KPI và cách đo | [02](docs/02-requirements-kpi.md) |
| Rủi ro | [03](docs/03-risk-register.md) |
| Khảo sát thực địa | [04](docs/04-airc-survey-checklist.md) |
| Nguồn dữ liệu | [05](docs/05-data-source-strategy.md) |
| Thiết bị | [06](docs/06-device-feasibility.md) |
| Công nghệ | [07](docs/07-technology-research.md) |
| UI/UX | [08](docs/08-ui-ux-research.md) |
| Kiến trúc PROPOSED | [09](docs/09-architecture-options.md) |
| Nghiệm thu và bằng chứng | [10](docs/10-m0-acceptance.md) |
| Sổ nguồn và phiên bản | [Sources](docs/research/sources.md) |
| Quyết định chưa duyệt | [ADR](docs/decisions/0001-technology-options.md) |
| Danh sách toàn bộ file | [Inventory](docs/file-inventory.md) |
| Tiếp tục công việc | [Project status](docs/PROJECT_STATUS.md) |

## Công cụ nền tảng M0-A

[WebXR capability check](tools/webxr-capability-check/README.md): HTML/JS tĩnh, không dependency, không camera, không telemetry. Chỉ kiểm tra API; kết quả `true` không chứng minh ARCore, hit-test, tracking, FPS hoặc trải nghiệm AR/VR hoạt động đầy đủ.

Chạy tại PowerShell ở `D:\Code\DATN`:

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory tools/webxr-capability-check
```

Mở `http://localhost:8000` trên máy tính. Hướng dẫn USB forwarding để điện thoại có secure context nằm trong README của công cụ. Không có website được deploy.

## Quy ước bằng chứng

`VERIFIED`: có nguồn hoặc kiểm tra cụ thể, không vượt phạm vi bằng chứng. `PROPOSED`: chờ duyệt. `BLOCKED`: cần dữ liệu/quyền/thiết bị. `NOT TESTED`: chưa thử thực tế. Kết quả test dùng `PASS`, `FAIL`, `NOT RUN` và ghi môi trường. Không suy ra nghiệm thu MT1–MT3 từ kiểm tra M0.
