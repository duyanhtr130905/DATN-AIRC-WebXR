# Sổ nguồn M0-A

Ngày truy cập/xác minh **14/11/2026** cho tất cả URL dưới đây. VERIFIED chỉ phạm vi nội dung đọc được; không phải thử runtime. Nghiên cứu độc lập từ nguồn công khai, không sử dụng repository cũ làm template.

| ID | Nguồn chính thức | Nội dung dùng và giới hạn |
| --- | --- | --- |
| S01 | [Google ARCore devices](https://developers.google.com/ar/devices) | VERIFIED có dòng Samsung Galaxy A17 5G / Depth API; chưa thử variant máy |
| S02 | [Google WebXR requirements](https://developers.google.com/ar/develop/webxr/requirements) | VERIFIED secure context, ARCore/Play Services và USB forwarding; trang ghi updated 31/10/2024, truy cập 2026 không biến nó thành release mới |
| S03 | [Google WebXR](https://developers.google.com/ar/develop/webxr) | VERIFIED điểm bắt đầu tài liệu WebXR AR; không suy ra mọi feature được mọi browser hỗ trợ |
| S04 | [React Three XR introduction](https://pmndrs.github.io/xr/docs/getting-started/introduction) | VERIFIED XR store + tích hợp R3F và ví dụ input |
| S05 | [XR development setup](https://pmndrs.github.io/xr/docs/getting-started/development-setup) | VERIFIED IWER/devui và cảnh báo experimental; không thử emulator ở M0 |
| S06 | [R3F introduction](https://r3f.docs.pmnd.rs/getting-started/introduction) | VERIFIED React renderer, pair major, v10 alpha; đường pmndrs.github.io cũ không truy cập được bằng công cụ nghiên cứu, dùng docs chính thức hiện hành |
| S07 | [Meta IWSDK overview](https://developers.meta.com/vr/documentation/iwsdk/guides/overview/) | VERIFIED ECS/Three.js, input, locomotion, IWER; updated 04/09/2026 |
| S08 | [Meta WebXR overview](https://developers.meta.com/vr/documentation/web/webxr-overview/) | VERIFIED runtime detection và đường phát triển Meta; updated 21/07/2026 |
| S09 | [Apple Quick Look gallery](https://developer.apple.com/quick-look-gallery/) | VERIFIED USDZ/AR xem object; không chứng minh WebXR hay callback toàn bộ tracking |
| S10 | [gh repo create](https://cli.github.com/manual/gh_repo_create) | VERIFIED tạo repo private/source/remote; dùng CLI theo yêu cầu |
| S11 | [W3C WebXR](https://www.w3.org/TR/2026/CRD-webxr-20261109/) | VERIFIED bản Candidate Recommendation Draft 09/11/2026, secure API/session support; không coi draft là final Recommendation |
| S12 | [Chrome USB forwarding](https://developer.chrome.com/docs/devtools/remote-debugging/local-server) | VERIFIED truy cập localhost Android qua máy tính bằng USB |
| S13 | [Khronos glTF](https://www.khronos.org/gltf/) | VERIFIED định dạng asset 3D trao đổi, không phải pipeline export đã test |
| S14 | [Blender LTS](https://www.blender.org/download/LTS/) | VERIFIED 5.2.4/4.5.16 còn maintained, chưa cài/chốt |
| S15 | [PostgreSQL version policy](https://www.postgresql.org/support/versioning/) | VERIFIED 18.7 stable và support đến 14/11/2030; không cài DB |
| S16 | [FastAPI PyPI JSON](https://pypi.org/pypi/fastapi/json) | VERIFIED 0.162.7, Python >=3.11; trang hướng dẫn WebSocket không tải được trong lần nghiên cứu, không tuyên bố đã đọc trang đó |
| S17 | [Smithsonian virtual tour](https://naturalhistory.si.edu/visit/virtual-tour) | VERIFIED mô tả tour, map/floor arrows/close-up, desktop/mobile; chưa trực tiếp usability test tour |
| S18 | [Museum Views](https://artsandculture.google.com/project/streetviews) | VERIFIED danh mục 360 panorama; chưa thao tác tour trên thiết bị |
| S19 | [Autodesk Tandem](https://www.autodesk.com/products/tandem/overview) | VERIFIED mô tả asset/data theo không gian; chưa dùng dashboard live, không dùng giá hiển thị placeholder |
| S20 | [Matterport editing features](https://support.matterport.com/s/article/Overview-of-Matterport-s-Editing-Features?language=en_US) | PARTIAL: chỉ search index chính thức đọc được tags/start location; trực tiếp trả CSS Error. Discover redirect tới trang không có text; chưa xác minh UI live |
| S21 | [WCAG 2.2 quickref](https://www.w3.org/WAI/WCAG22/quickref/) | VERIFIED nguồn tiêu chí accessibility; đề xuất áp dụng, chưa audit conformance |

## Registry và repo kiểm tra version/maintenance/license

[versions.json](versions.json) lưu metadata chọn lọc, không chứa auth/token. npm `latest` là dist-tag tại ngày kiểm tra, không phải version đã cài hoặc lockfile.

- [three npm](https://registry.npmjs.org/three/latest), [three releases](https://github.com/mrdoob/three.js/releases/tag/r187).
- [React npm](https://registry.npmjs.org/react/latest), [fiber npm](https://registry.npmjs.org/@react-three/fiber/latest), [fiber releases](https://github.com/pmndrs/react-three-fiber/releases/tag/v9.8.2).
- [XR npm](https://registry.npmjs.org/@react-three/xr/latest), [XR release](https://github.com/pmndrs/xr/releases/tag/v6.6.0), [XR license](https://raw.githubusercontent.com/pmndrs/xr/main/LICENSE).
- [IWSDK npm](https://registry.npmjs.org/@iwsdk/core/latest), [exact 1.1.0 metadata](https://registry.npmjs.org/@iwsdk/core/1.1.0), [repo](https://github.com/meta/immersive-web-sdk), [releases trống](https://github.com/meta/immersive-web-sdk/releases), [source package](https://github.com/meta/immersive-web-sdk/blob/65c0b138da51263b1f58ffe032e88a43e33b4e92/packages/core/package.json).

Chênh lệch npm stable/source main/release page được giữ nguyên và giải thích trong 07. License exact tarball/transitive audit còn phải làm khi PoC được phép. Không có kết quả đo FPS/AR/VR được tạo từ nghiên cứu tài liệu.

## Cách kiểm tra lại

Đọc lại trang chính thức, tìm đúng model/feature và ngày cập nhật; dùng `gh api repos/<owner>/<repo>` lấy archived/pushed_at/license và `releases/latest` (404 IWSDK nghĩa chưa có latest release, không tự suy ra SDK ngừng duy trì). GET registry endpoint trên để đối chiếu version/peer/engine. Không lưu header đăng nhập hoặc stdout token. Khi nguồn đổi, cập nhật ngày/snapshot và ghi rõ thay đổi trước chọn stack.

## Nguồn CI cho review fixes — kiểm tra 14/11/2026

Đọc README/action.yml và GitHub release/API chính thức trước chọn: [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1), [setup-node v7.1.0](https://github.com/actions/setup-node/releases/tag/v7.1.0), [setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0), [upload-artifact v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2). Workflow pin SHA full của từng tag thay vì nhánh main; không dùng action cài browser. Node 22/Python 3.13, cache không cần nên tắt, checkout không lưu credential.

[Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax): filter PR base main, push branch và contents: read; không pull_request_target/secrets/deploy/write. [upload-artifact](https://github.com/actions/upload-artifact) dùng allowlist chỉ report/screenshot với retention 14 ngày; include-hidden-files chỉ vì output ở `.local`, không glob profile. PyYAML [6.0.3](https://pypi.org/project/PyYAML/6.0.3/) chỉ cài vào `.local/validation-deps` để parse YAML local bằng BaseLoader (giữ key on), không là dependency sản phẩm/runner/CI. Kết quả GitHub chạy thật được bàn giao bằng URL run, không suy ra từ parse local.

## M0-B1 — recheck trước code ngày 14/11/2026

- [R3F introduction](https://r3f.docs.pmnd.rs/getting-started/introduction), [XR introduction](https://pmndrs.github.io/xr/docs/getting-started/introduction), [XR development setup](https://pmndrs.github.io/xr/docs/getting-started/development-setup): React major pairing, XR store và emulator workflow đã kiểm tra lại; artifact/types thực tế là nguồn để xác minh API version đã pin.
- [IWSDK overview](https://developers.meta.com/vr/documentation/iwsdk/guides/overview/), [project setup](https://developers.meta.com/vr/documentation/iwsdk/guides/01-project-setup/), [React/Preact UI](https://developers.meta.com/vr/documentation/iwsdk/guides/17-react-preact-2d-ui/), [minimal scene](https://developers.meta.com/vr/documentation/iwsdk/guides/01b-minimal-scene/), [repo chính thức](https://github.com/meta/immersive-web-sdk): đọc manifest/virtual module/World/ECS/DOM ownership, không dùng template dự án cũ. Đường minimal-scene thử ban đầu 02-minimal-scene không tồn tại, dùng link chính thức 01b; trang testing-experience có lần timeout nên runtime validation dựa artifact/types/source + test thật.
- [Google WebXR requirements](https://developers.google.com/ar/develop/webxr/requirements): recheck secure context/native device prerequisites; không suy emulator ra thiết bị thật.
- [npm metadata XR exact](https://registry.npmjs.org/@react-three/xr/6.6.32), [R3F exact](https://registry.npmjs.org/@react-three/fiber/9.8.2), [IWSDK exact](https://registry.npmjs.org/@iwsdk/core/1.1.0), [plugin exact](https://registry.npmjs.org/@iwsdk/vite-plugin-dev/1.1.0), [Vite 7.3.8](https://registry.npmjs.org/vite/7.3.8): version/peer/engine/license kiểm tra qua registry/npm CLI, lockfiles bảo toàn artifact đã thử. Vite major 8 latest không thỏa peer plugin ^7, không mặc định dùng latest.
- [IWER official repo](https://github.com/meta-quest/immersive-web-emulation-runtime), [IWER 2.8 metadata](https://registry.npmjs.org/iwer/2.8.0), [DevUI 2.8 metadata](https://registry.npmjs.org/@iwer/devui/2.8.0): override A được xác minh bằng dependency graph, declarations/source trong package và session emulation thật. Không sửa node_modules để làm giả SDK. installRuntime forceInstall chỉ cho URL opt-in emulation; không là claim native support.
- UI tham khảo recheck: [Smithsonian](https://naturalhistory.si.edu/visit/virtual-tour), [Autodesk Tandem](https://www.autodesk.com/products/tandem/overview), [model-viewer](https://modelviewer.dev/examples/scenegraph/). Đọc trang sản phẩm/examples thực tế, không sao chép code/model/ảnh; không gọi đó là usability research với người thật.

Các nhận định so sánh maintainability/UX là PROPOSED từ mã đã triển khai và các thử nghiệm có giới hạn tại docs/11. License MIT của XR/Havok đã đọc ở package đã cài thay vì chỉ tin npm label. Không có API/dữ liệu/ảnh AIRC được truy cập. Không cài công cụ toàn hệ thống; formatter 3.6.2 chỉ dùng qua npm exec cache local, không là runtime dependency.
