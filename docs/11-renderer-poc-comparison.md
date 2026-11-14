# 11 — So sánh renderer PoC M0-B1

Ngày 14/11/2026. **PROPOSED — chưa chọn framework hoặc UI chính thức.** M0-A/PR #6 đã merge vào main `1a736d558f6b721921cd5f38de069d63a733721e`; task M0-B1 cho phép thực nghiệm A/B, không phải bắt đầu M1.

## Dataset và phương pháp công bằng

Cả hai dùng duy nhất [shared fixture/domain](../experiments/shared-fixtures/domain.ts): 1 phòng generic 12×3×9 đơn vị thử nghiệm, 5 cube tương tác trên bệ, ba nhóm lịch phòng/tình trạng thiết bị/thông tin trưng bày. Stable room ID `demo-room-001`, object IDs `demo-object-001`…`005`; vị trí, metadata, status/value/timestamp và provenance synthetic cố định, không liên quan phòng 507 hoặc thiết bị AIRC. Banner DEMO luôn hiện, không dùng 5 object để tuyên bố đạt MT1 ≥20 hoặc ≥3 phòng.

Hai renderer dùng chung [Shell/CSS](../experiments/shared-ui/Shell.tsx), camera (10,9,14), FOV 50, target (0,.4,0), ambient/directional light, material, tone mapping ACES, DPR 1; same box geometry, grid/floor/two walls. B dùng đúng World/ECS của IWSDK, không thay bằng Three.js thuần. A dùng Canvas/R3F/XR store thật.

Kịch bản: load → click cube bằng tọa độ chiếu từ camera thật → UI selection/metadata → đổi trạng thái → đối chiếu ECS B → kéo orbit → reset → Guided Tour/next → Scene + Panel → native AR unsupported. Mobile 390×844: touch canvas, tap danh mục, đổi trạng thái, focus và không overflow. Kiểm tra lỗi WebGL bằng nhánh forceNoWebGL có chủ đích. Emulator: user gesture vào VR, session active, inputSources >0, thoát qua UI IWER. Không mock navigator.xr để làm emulator PASS.

## Version, peer và lockfiles đã thử

| Thành phần | A | B |
| --- | --- | --- |
| React / React DOM | 19.3.1 / 19.3.1 | 19.3.1 / 19.3.1 cho DOM shell |
| Runtime | R3F 9.8.2 + React Three XR 6.6.32 | IWSDK core 1.1.0, plugin-dev 1.1.0 |
| Renderer | Three.js **stock 0.185.0** | `three: npm:super-three@0.185.0` theo SDK |
| Emulator | IWER 2.8.0 + DevUI 2.8.0 overrides; SEM 0.2.5 không bật environment | plugin emulator theo manifest, runtime bundle tự báo IWER 2.7.0; không gọi đó là 2.8 chỉ vì metadata dependency |
| Toolchain | Vite 7.3.8, plugin-react 5.1.1, TS 5.9.3 | cùng toolchain |
| Runtime máy thử | Node 22.16.0 / npm 11.10.1, Windows 11 | cùng máy |
| Lock | [A lock](../experiments/poc-a-r3f-xr/package-lock.json) | [B lock](../experiments/poc-b-iwsdk/package-lock.json) |

Latest được kiểm tra nhưng không mặc định dùng: Vite latest 8.3.8, plugin IWSDK peer ^7 nên chọn patch 7.3.8; TS latest 7.0.2 không cần cho PoC, pin 5.9.3 đã build. R3F 9 pair React 19 và peer >=19 <19.4; XR peer rộng không đủ chứng minh emulator transitive tương thích. Node 22.16 thỏa engine IWSDK/Vite >=22.12; không cài runtime hệ thống mới.

`npm ls three` xác nhận A Canvas/R3F/XR dùng cùng stock 0.185.0, B project/core/plugin dedupe cùng super-three 0.185.0. Không override alias B bằng stock Three. Tool browser-test riêng dùng Playwright 1.58.2 + Chrome có sẵn, không tải browser.

License artifact đã đọc: React/Three/R3F/core/plugin là MIT; XR metadata SEE LICENSE nhưng LICENSE trong package có nội dung MIT; Havok transitive 1.3.14 có MIT trong package (physics tắt). Playwright Apache-2.0, TypeScript Apache-2.0. Lockfile lưu metadata license transitive; đây không phải xác nhận pháp lý hoặc security audit đầy đủ. npm audit production được chạy để ghi nhận snapshot, không phải chứng minh không có lỗ hổng chưa công bố. Snapshot audit production cuối của cả A/B báo 0 vấn đề ở các mức; không bao gồm audit đầy đủ mọi dev tool.

## Kết quả thực nghiệm

[Report local](evidence/m0-b1-local.json) ghi timestamp, OS/browser/node, expected/actual từng case và screenshot filenames. Máy local Chrome 157.0.8103.51, headless với SwiftShader, không GPU/mobile/kính thật. Hai mode desktop 1280×900 và mobile emulation 390×844; 250ms settle UI/ResizeObserver trước click không được diễn giải thành số liệu latency sản phẩm.

| Tiêu chí | A — R3F/XR | B — IWSDK |
| --- | --- | --- |
| Setup/build/TypeScript | build PASS, lock riêng | build PASS, lock/manifest riêng |
| Fixture/domain tests | 6/6 PASS | cùng 6/6 PASS, không đếm thành 12 test độc lập |
| Canvas mouse pick và orbit | PASS click thật, projection đổi sau drag | PASS click qua SDK RayInteractable, orbit |
| Metadata, lựa chọn, cập nhật/reset | PASS | PASS; test kiểm tra stateValue trong component ECS sau DOM command |
| Guided Tour và Scene + Panel | cả hai mode chạy | cùng layout/mode, không ưu ái thiết kế A |
| Touch/responsive/focus | PASS 390px không overflow | PASS 390px không overflow; ResizeObserver cần thiết |
| Loading/WebGL/native unsupported | có loading/error/fallback; controlled unsupported test PASS | tương đương, world startup catch lỗi |
| IWER lifecycle | enter/exit PASS, 2 input sources, không runtime exception trong case | enter/exit PASS, 2 input sources |
| Ray controller chọn đúng object | **NOT TESTED**, chỉ xác nhận sources/lifecycle | **NOT TESTED**, không giả lập click vào domain thay cho controller |
| Frame workload quan sát | 14 draw calls / 146 triangles ở lượt desktop ghi report | 14 draw calls / 146 triangles ở cùng cảnh |
| Main JS build gần nhất | khoảng 1.32 MB / 370 KB gzip | khoảng 2.66 MB / 736 KB gzip |
| Backend tương lai | domain/adapter không phụ thuộc Canvas; thêm provider sau khi được phép | bridge system nhận domain commands và map stable ID; adapter không phụ thuộc renderer |
| Chia module/bảo trì | scene declarative, ít glue với React DOM | thêm Identity component, system/controller mirror, World lifecycle và resize adapter |
| XR trên Galaxy/iPhone/kính thật | **NOT TESTED** | **NOT TESTED** |

Draw calls/triangles là một frame đọc từ renderer.info trong môi trường đã nêu, không benchmark FPS. Gzip từ output Vite, không phải tổng byte tải runtime hoặc so sánh tốc độ mạng. Các preset emulator chunks có trong dist nhưng không là scene AIRC; không tải preset vào fixture. Cả hai có cảnh báo bundle >500 KB; B thêm worker/chunks dependency dù physics/spatial UI tắt. Chưa profiling, LOD, cold/warm trials nhiều lượt, memory hay race/performance trace. `readyMs` trong JSON là một lần chạy harness (có settle), không đủ xếp hạng hiệu năng. **Không đo FPS**, không suy từ demo nhẹ ra KPI 30/72 FPS.

CI [PoC workflow](../.github/workflows/poc-validation.yml) build/test hai package bằng matrix fail-fast=false; browser job dựng lại preview, thử native/mobile/IWER và upload PNG/JSON. Không skip một PoC lỗi để lấy PASS. M0 workflow tiếp tục chạy checks cũ trên PR vào main. URL run và artifact GitHub thật được ghi ở PR/báo cáo bàn giao sau push, không coi local PASS là CI.

## Lỗi đã gặp, cách xác minh và giới hạn còn lại

1. Tải dependency A ban đầu ECONNRESET; retry thành công, không reset/xóa source. Một số npm cleanup EPERM khi thay package đang có esbuild process, chỉ file node_modules local; không xóa/kill session người dùng. Lock hiện tại được dùng lại bằng npm ci trong CI.
2. IWSDK plugin từ chối emulator/workspace options đặt cùng project manifest. Chuyển dev.emulator sang iwsdk.config.json và giữ plugin https:false; build/typecheck sau sửa PASS. Không bật AI managed workspace hoặc cài certificate.
3. SDK renderer mặc định dùng window dimensions làm canvas phủ DOM panel. Sửa bằng CSS confinement + ResizeObserver/container aspect, dispose listeners. Browser click/touch DOM và kiểm tra canvas dimensions thật xác minh sửa; không dùng force click xuyên canvas.
4. XR dependency A mặc định ghép IWER 2.8 với DevUI 1.1.2/Three 0.165; có `onBuild is not a function` trong chunk emulator, không có inputs. Pin stock Three từ 0.187 về 0.185 **một mình không sửa được**, nên không quy lỗi chắc chắn cho Three 0.187. Override IWER/DevUI cùng 2.8 mới giải quyết render; SEM giữ cũ vì không dùng. Đã thử SEM 2.8 nhưng kéo Babel 8 cần Node >=22.18, loại override đó thay vì bỏ qua engine warning.
5. IWER 2.8 bảo vệ native navigator.xr kể cả khi Chrome không có XR device; chỉ URL `?emulate=1` mới gọi API chính thức forceInstall, không áp dụng native path. Không chỉnh Chrome flag insecure origin hoặc coi emulation là phần cứng.
6. XR overlay chặn nút DOM của trang (đúng ranh giới immersive); test dùng nút Exit của IWER thay vì force click. DevUI 1.x/2.x có title Exit khác nhau, harness nhận diện cả hai tên.
7. Canvas resize sau panel mount làm một lần click harness xảy ra quá sớm; chờ panel + settle render trước chiếu tọa độ. Vẫn click/touch canvas thật, không chọn qua store để làm PASS. B có warning annotation Rollup từ Zod và cả hai có warning bundle; không tắt cảnh báo.

8. CI PoC lần đầu [43568831269](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43568831269) build/domain A/B PASS nhưng browser setup FAIL: Chrome POSIX `SingletonSocket` vượt giới hạn độ dài vì temp path workspace sâu. Giữ temp trong workspace nhưng rút xuống `.local/t`; không chuyển sang profile cá nhân, không skip hoặc đổi FAIL thành PASS. Run mới phải xác minh sau push.

9. Một lần cold dev load B vượt timeout load-event 10s dù app đã hiện đầy đủ. Các luồng chính dùng DOMContentLoaded + đợi renderer readiness; emulator giữ navigation deadline 30s và đợi IWER readiness tường minh; không dùng load của mọi dev asset làm điều kiện nghiệp vụ và không bỏ kiểm tra runtime errors.

SDK dev tự sinh `.iwsdk/runtime` có metadata/credential tạm: ignore toàn thư mục, verifier báo lỗi nếu vô tình track, không push hoặc upload. Profile/cache Playwright cũng chỉ trong `.local`; server loopback, browser context đóng và dev/preview processes được kết thúc sau suite. Test failure làm exit 1; báo cáo/screenshot chỉ của lần chạy hiện tại. Screenshot local đã xem: desktop, Guided Tour, mobile và IWER; không ảnh AI.

## Hai hướng UX và nguồn tham khảo

Đọc lại nguồn chính thức ngày 14/11/2026 trước dựng UI: [Smithsonian tour](https://naturalhistory.si.edu/visit/virtual-tour) — điều hướng phòng/điểm và close-up; [Tandem](https://www.autodesk.com/products/tandem/overview) — thông tin asset theo không gian; [model-viewer scene graph examples](https://modelviewer.dev/examples/scenegraph/) — kiểm tra object/material với controls DOM; [IWSDK React UI](https://developers.meta.com/vr/documentation/iwsdk/guides/17-react-preact-2d-ui/) — DOM không mặc định hiện trong kính. Đây là desk research trang sản phẩm/tài liệu, không tuyên bố usability test hoặc sao chép asset/code của họ.

- **Guided Tour:** chọn mode → điểm đầu → tiếp theo; giảm lựa chọn ban đầu, có đường tự khám phá. Prototype chọn/highlight và thông tin điểm; chưa tự đưa camera tới waypoint, chưa route qua phòng khác.
- **3D Scene + Information Panel:** canvas trung tâm, danh mục để chọn bằng keyboard/touch, panel trạng thái/nguồn/timestamp. Trên mobile panel xuống dưới canvas, không chồng controls. Màu nền ấm, chữ serif ở tiêu đề, accent teal, ít chuyển động; không dùng dashboard metric cards hoặc postprocessing nặng.

Đề xuất hướng Scene + Panel trước cho một phòng và metadata sau survey; Guided Tour là mode thay thế cho khách mới. Focus rõ, button đủ chạm, không hover-only, banner synthetic luôn có; chưa audit đầy đủ WCAG hoặc thử ≥15 người nên chưa chọn UI chính thức. DOM controls không là spatial UI trong kính; phần đó cần PoC riêng nếu framework được duyệt.

## Contract và chuẩn bị dữ liệu sau survey

DataAdapter/adapterFromLoader + validateScene là seam thay fixture bằng loader được ủy quyền sau này, không có network/database implementation. Validator kiểm tra duplicate IDs, room relation, finite vector, timestamp, enum trạng thái và provenance. real_verified cần evidenceRef ở object; unknown không được giả synthetic để mutation. DemoController giữ snapshot ổn định giữa commands, update immutable và có unsubscribe; tests xác minh reset và chỉ một object đổi.

Trong B, system sở hữu domain controller theo lifecycle world; ECS component giữ stable ID và projection state, React chỉ subscribe immutable snapshot và gửi commands. Không copy Object3D vào React state hoặc để React reconcile canvas do IWSDK sở hữu. Entity index/generation không là durable ID. Contract là **PoC/PROPOSED**, chưa schema chính thức, auth/validation backend hoặc source-of-record AIRC.

## Phòng 507 và khuyến nghị cần phê duyệt

Theo brief mới do người dùng cung cấp 14/11/2026: giảng viên chỉ đạo **“Cứ làm 1 phòng 507 trước.”** Đây là phạm vi triển khai đầu tiên; KPI ≥3 phòng chưa bị hủy. Dự kiến khảo sát khoảng **16/11/2026**, chưa có ảnh/kích thước/inventory/quyền. Không chia một phòng thành ba phòng giả, không gọi fixture là phòng 507. Chưa có phần mềm quản lý thiết bị; nhập tay qua admin chỉ là phương án tương lai PROPOSED, không có admin/DB trong PoC này.

**Khuyến nghị PROPOSED: A thuận lợi hơn cho bước tích hợp DOM/metadata tiếp theo** nhờ mô hình declarative ít glue và main chunk nhỏ hơn trong build thử; nhưng phải quản lý override emulator và thử AR thật. B đã chứng minh chạy được và có giá trị nếu ưu tiên ECS/XR systems; chi phí bridge/lifecycle/resize lớn hơn ở scene nhỏ này. Không có bằng chứng A nhanh hơn trên Galaxy/Quest; chưa đủ dữ liệu để chọn framework sản phẩm chính thức.

Cần chủ dự án/giảng viên duyệt: scope cuối/KPI ≥3 phòng, dữ liệu/quyền survey, hướng UX, renderer ứng viên sau PoC, phương pháp XR/VR khi không có kính và bước tích hợp dữ liệu kế tiếp. [ADR-0001](decisions/0001-technology-options.md) vẫn **PROPOSED**. Dừng sau PR, không tự bắt đầu M1.
