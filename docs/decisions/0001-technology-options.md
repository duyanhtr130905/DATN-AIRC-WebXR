# ADR-0001 — Lựa chọn framework và kiến trúc

- Trạng thái: **PROPOSED**
- Ngày: 14/11/2026
- Người có thẩm quyền duyệt: chủ dự án/giảng viên, chưa có phê duyệt
- Liên quan: MT1–MT3, R03/R04/R06/R08/R11

## Bối cảnh

Chưa có survey, chưa thử điện thoại, không có kính. M0-A nghiên cứu, không chọn framework hoặc triển khai sản phẩm.

## Các lựa chọn

A: Three.js + React Three Fiber + @react-three/xr. B: Meta IWSDK. Backend FastAPI/PostgreSQL/WebSocket và modular monolith là ứng viên, chưa chốt. [So sánh và version](../07-technology-research.md), [kiến trúc](../09-architecture-options.md).

## Đề xuất có điều kiện

Sau khi được phép, PoC A trước cho panel dữ liệu, B làm đối chứng XR; ưu tiên khảo sát P1 modular monolith. Dùng cùng asset/workload và thiết bị; pin version. Không triển khai PoC trong M0-A.

## Hậu quả và trigger xem lại

A cần kiểm tra peer/dependency và license exact XR package. B cần đo bridge React/ECS, renderer alias và license transitive. Cả hai cần bằng chứng Android/kính, FPS và tracking riêng. Nếu PoC hoặc quyền dữ liệu không đáp ứng, quay lại lựa chọn, không sửa KPI.

## Phê duyệt

Chưa có; không có quyết định ACCEPTED. Bổ sung bằng chứng PoC và link phản hồi người duyệt trước thay trạng thái.
