# 07 — Technology research

> Lịch sử M0-A/M0-B1 được giữ nguyên bên dưới. Cập nhật 14/11/2026: chủ dự án đã duyệt stack/kiến trúc/UI trong M0-B2; xem [ADR-0001 ACCEPTED](decisions/0001-technology-options.md) và [kiến trúc chính thức](12-official-system-architecture.md). Các phát biểu “chưa chọn/PROPOSED” về framework bên dưới mô tả thời điểm nghiên cứu, không phải trạng thái hiện tại. Schema chi tiết/auth/hosting/retention/quyền dữ liệu/KPI cuối/VR acceptance vẫn chưa duyệt.


> Ghi chú lịch sử: nội dung M0-A dưới đây là snapshot trước PoC. M0-B1 nay có cài/build/package được thử; xem [comparison](11-renderer-poc-comparison.md). Kiến trúc/framework/UI sản phẩm vẫn PROPOSED.

**PROPOSED, chưa chọn framework.** Nghiên cứu ngày 14/11/2026, chỉ đọc tài liệu/registry/metadata; chưa cài hay build hai stack. [Sổ nguồn](research/sources.md) và [snapshot](research/versions.json) ghi chi tiết kiểm chứng.

## Snapshot phiên bản và maintenance

| Thành phần | Kết quả nguồn chính thức tại ngày kiểm tra | Hệ quả |
| --- | --- | --- |
| Three.js | npm 0.187.0, GitHub release r187 (30/10/2026), MIT, repo không archived | cùng renderer nền; version mới không đảm bảo plugin tương thích |
| React / R3F | React 19.3.1; fiber 9.8.2 MIT; peer React >=19 <19.4, three >=0.156 | [R3F docs](https://r3f.docs.pmnd.rs/getting-started/introduction) yêu cầu major React tương ứng; v10 đang alpha, không mặc định dùng alpha |
| @react-three/xr | npm 6.6.32; GitHub latest release v6.6.0 (30/01/2025); repo không archived, push 15/10/2026 | npm khác release page; peer React >=18, fiber >=8, three * không phải kết quả integration test |
| XR license | npm ghi SEE LICENSE IN LICENSE, GitHub nhận diện NOASSERTION; [file LICENSE](https://raw.githubusercontent.com/pmndrs/xr/main/LICENSE) có văn bản kiểu MIT | kiểm tra license trong tarball/version khóa trước chọn, không coi metadata NOASSERTION là cấm sử dụng |
| @iwsdk/core | npm stable 1.1.0 MIT, repo không archived, push 13/11/2026; GitHub chưa có release | Node engine >=20.19 <21 hoặc >=22.12 <23 hoặc >=24; Node sẵn có 22.16 thỏa engine theo metadata, chưa build |
| IWSDK renderer | core 1.1.0 khai báo alias three → super-three 0.185.0 | không tự ép three 0.187.0 vào IWSDK; kiểm tra dependency graph/dedupe trong PoC |
| Blender | [LTS page](https://www.blender.org/download/LTS/) liệt kê 5.2.4 và 4.5.16 còn maintained | PROPOSED đánh giá LTS và pipeline export; chưa chọn/cài |
| FastAPI | PyPI 0.162.7, Python >=3.11 | chỉ ứng viên backend; không triển khai M0 |
| PostgreSQL | [version policy](https://www.postgresql.org/support/versioning/) liệt kê 18.7, support đến 14/11/2030 | ứng viên stable; không dùng RC làm mặc định; chưa chọn/cài DB |

Dấu hiệu release/push gần đây chứng minh có hoạt động ở thời điểm xem, không phải cam kết SLA, độ ổn định hoặc an toàn dependency. IWSDK source main ghi 1.1.0-rc.1 trong khi npm stable 1.1.0: dùng snapshot npm để mô tả package, không suy ra source main chính là artifact phát hành.

## So sánh trên cùng tiêu chí

Các nhận định phù hợp/độ khó là suy luận kỹ thuật **PROPOSED** từ cấu trúc SDK, chưa benchmark. Không chấm điểm hiệu năng khi chưa đo.

| Tiêu chí | A: Three.js + R3F + @react-three/xr | B: Meta Immersive Web SDK |
| --- | --- | --- |
| Digital Twin | React state/UI thuận lợi cho metadata, panel và dashboard; mapping object/asset vẫn tự xây | ECS phù hợp entity/object và state systems; metadata và nghiệp vụ vẫn tự xây |
| Web 3D | R3F render Three.js, DOM UI kề canvas | browser 3D dùng ECS/Three.js, có thể tắt XR |
| AR/VR | XR store, pointer/interactions, tùy runtime/feature | XR input/lifecycle và systems sẵn; cũng phụ thuộc runtime/feature |
| React/backend | React tự nhiên; REST/WebSocket cần adapter | runtime ECS không phải React renderer; React shell cần bridge rõ; backend độc lập |
| Tương tác/điều hướng | pointer, grab/touch theo thư viện; tour/floor routing cần thiết kế | locomotion/grab/spatial UI có sẵn; room routing và domain state vẫn cần làm |
| Giả lập | IWER/devui theo docs, experimental; kiểm tra version extension tránh xung đột | IWER và workflow desktop do SDK hỗ trợ |
| Hiệu năng/assets | LOD, culling, instancing và tối ưu GLB theo Three.js; tránh setState mỗi frame | chỉ bật system cần; đo overhead ECS/physics; kiểm tra alias renderer |
| Trưởng thành | Three/R3F có nhiều release, XR phát hành riêng; có rủi ro peer rộng | SDK 1.x, nhiều hệ thống tích hợp, release GitHub thiếu; cần đọc package docs khớp version |
| Tài liệu/community | docs R3F/XR và hệ sinh thái pmndrs; không suy ra support thương mại | docs Meta, examples và repo public; không lấy sponsor làm đảm bảo mọi browser |
| License | Three/R3F MIT; XR phải lưu license exact package | core MIT; Havok và dependency khác cần review license riêng nếu dùng |
| Codex triển khai | component/state dễ chia module, rủi ro code mẫu version cũ hoặc render loop lạm dụng | cần tuân thủ ECS/lifecycle, bridge UI và manifest; sample docs có thể khác npm |
| Lock-in/mở rộng | giảm phụ thuộc bằng domain ID + XR adapter; vẫn phụ thuộc pmndrs API | WebXR/Three giảm platform lock-in; ECS/scene composition tạo chi phí chuyển runtime |
| Thiết bị hiện tại | không có bằng chứng stack chạy Galaxy/iPhone/kính của dự án | tương tự; Meta SDK không tự cấp hỗ trợ Android AR |

Nguồn khả năng A: [XR introduction](https://pmndrs.github.io/xr/docs/getting-started/introduction), [development setup](https://pmndrs.github.io/xr/docs/getting-started/development-setup), [R3F introduction](https://r3f.docs.pmnd.rs/getting-started/introduction). Nguồn B: [IWSDK overview](https://developers.meta.com/vr/documentation/iwsdk/guides/overview/), [repository](https://github.com/meta/immersive-web-sdk), [Meta WebXR](https://developers.meta.com/vr/documentation/web/webxr-overview/). Truy cập tất cả ngày 14/11/2026.

## Đề xuất PoC sau phê duyệt

Ưu tiên khảo sát **A trước** vì sản phẩm có nhiều panel dữ liệu và báo cáo; dùng **B làm đối chứng** cho input/locomotion/spatial UI. Đây là thứ tự thử đề xuất, không phải lựa chọn framework. Nếu XR là trọng tâm và bridge UI của B đơn giản hơn sau thử, cân nhắc lại.

PoC cùng một asset generic gắn nhãn synthetic (hoặc asset thực được cấp quyền), cùng số object/camera/light/resolution và cùng tuyến. Thử desktop/mobile: load, room navigation, chọn object, panel; XR emulator: enter/exit/input; Galaxy: session thật khi có máy; kính: đo ≥72 FPS khi mượn được. Tách adapter nguồn/tracking mock khỏi renderer. Pin versions + lockfile riêng; kiểm tra peer/license/transitive deps; ghi setup time, LOC glue, memory/draw calls/frame time và lỗi. Không chạy PoC ở M0-A.

Điều kiện lựa chọn: dữ liệu thực/thiết bị được chốt, PoC tái lập, kết quả đáp ứng protocol, license rõ, chủ dự án/giảng viên duyệt ADR. Không framework nào bảo đảm sẵn KPI 30/72 FPS, 99% event hoặc ≤5 giây.

## Backend và asset vẫn mở

FastAPI/PostgreSQL/WebSocket là hướng ban đầu hợp lý cần PoC persist/ACK/reconnect/authorization, chưa quyết định. Blender → GLB/glTF theo [Khronos glTF](https://www.khronos.org/gltf/) giữ định dạng trao đổi; chưa có model AIRC. Hosting, auth provider, retention và schema đều chờ duyệt, không deploy.
