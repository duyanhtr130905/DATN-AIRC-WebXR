# ADR-0001 — Renderer, kiến trúc và bố cục ứng dụng

- Trạng thái: **ACCEPTED** cho các quyết định liệt kê dưới đây.
- Ngày phê duyệt: **14/11/2026**.
- Người duyệt: **chủ dự án phê duyệt qua ChatGPT**, trong yêu cầu M0-B2. Đây là phê duyệt công nghệ/phạm vi foundation, không thay phê duyệt dữ liệu của AIRC hoặc điều chỉnh KPI từ giảng viên.
- Bằng chứng thực nghiệm: [PR #7 đã merge](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/7), merge `3ebd2ec780db80caacd5871ecda911236598f9be`, [báo cáo PoC](../11-renderer-poc-comparison.md).

## Quyết định đã duyệt

React + TypeScript + Vite; Three.js + React Three Fiber + React Three XR là renderer chính. FastAPI/Python và PostgreSQL là backend/database; SQLAlchemy phù hợp cho connection management. Modular Monolith, giao tiếp REST + WebSocket. Blender và glTF/GLB cho 3D assets. UI chính **Scene + Information Panel**, Guided Tour là chế độ phụ. Giữ Meta IWSDK trong experiments làm đối chứng, không xóa hoặc đổi nhãn PoC B.

M0-B2 giữ baseline frontend của M0-B1; tổ chức lại domain adapter, API client, scene và components trong apps/web. Không coi demo primitives là phòng 507. Không triển khai nghiệp vụ M1.

## Lịch sử nghiên cứu

Ở M0-A và M0-B1 ADR này là PROPOSED: A = R3F/XR, B = IWSDK; FastAPI/PostgreSQL/modular monolith là ứng viên. M0-B1 chạy thật cả hai và khuyến nghị A cho DOM/metadata; khuyến nghị lúc đó không phải phê duyệt. Nội dung và kết quả lịch sử trong [nghiên cứu](../07-technology-research.md), [phương án](../09-architecture-options.md), [PoC](../11-renderer-poc-comparison.md) được giữ nguyên. Yêu cầu M0-B2 ngày 14/11/2026 cung cấp phê duyệt mới.

## Hậu quả và điều kiện xem lại

R3F cần kiểm soát bundle/asset, lifecycle XR, phiên bản peer dependencies; IWSDK vẫn hữu ích khi cần đối chiếu ECS/XR. Chưa có bằng chứng phần cứng Android/kính, KPI FPS, tác vụ 15 người hoặc tracking sản phẩm. Nếu baseline không đáp ứng PoC có workload thực, lập ADR mới; không tự thay stack hoặc KPI.

## Chưa được phê duyệt — PROPOSED/BLOCKED

Schema chi tiết và migration nghiệp vụ; authentication provider; hosting/deployment; retention; chính sách quyền dữ liệu AIRC; KPI ≥3 phòng cuối cùng; phương pháp nghiệm thu VR không có kính. REST/WebSocket được duyệt làm phương thức giao tiếp, **chi tiết endpoint/message trong docs/14 vẫn PROPOSED**. SQLAlchemy dùng trong foundation; Alembic là công cụ dự kiến khi schema được duyệt, chưa có revision nghiệp vụ.
