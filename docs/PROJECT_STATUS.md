# Trạng thái dự án — nguồn tiếp tục hiện hành

## E0 diagnostic follow-up — 17/11/2026, IN REVIEW; E0 vẫn FAIL

[TV bounds investigation](3d-production/P507-E0-TV-BOUNDS-DIAGNOSTIC.md): ROOT_CAUSE_CONFIRMED bằng Blender4.0.2/exporter4.0.44, sáu controlled exports diagnostic-only, vertex/transform đối chiếu độc lập. Manifest đo evaluated bevel; export R4 bỏ export_apply nên dùng original mesh. xmin GLB từ rear casing, xmin evaluated từ bezel, chênh8.3055mm.402482POSITION samples/121IDs không vượt oriented proxy ở1mm. Evidence run44065711842 thuộc commit6ae02b0; finalHEAD/CI được cập nhật trong Draft PR15.

Không sửa R4/manifest/asset-lock/validator hoặc ngưỡng3mm; không chọn/áp dụng OptionA/B, không unlockE1. Chờ ChatGPT/chủ dự án nghiệm thu diagnostic và duyệt task correction riêng. G2_VISUAL PENDING, merge/deploy/E2/E3 không thực hiện.

---

## E0/E1 experiment — 17/11/2026, IN REVIEW / BLOCKED BY E0

Task owner đã duyệt E0 + desktop E1 ngày 17/11/2026; quyền này thay snapshot “chưa giao WebXR experiment” bên dưới, không phê duyệt roadmap/E2/E3/G3. Branch `feat/p507-webxr-e0-e1-experiment` từ PR #14 HEAD `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31`, Draft PR mới base `feat/p507-g1-g2-blockout-hero`; không sửa PR #13/#14 hoặc production.

**E0_FAIL:** artifact run44038653564/id14309207795 còn hạn, GLB10751036bytes/hash `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`, bundle/source/checkout/123records/121IDs/metres/axes/floor/windows/door đều kiểm được. Actual exported TV bounds khác manifest authored bounds tối đa8.3055mm; original browser report cũng có sai lệch. Zero oriented-proxy vertex violations ở1mm; không sửa R4 hoặc nới kiểm tra bounds3mm để PASS. Cần ChatGPT/owner nghiệm thu ý nghĩa authored-vs-exported bounds hoặc task sửa handoff riêng.

**E1 PARTIAL source / BLOCKED_BY_E0 runtime:** standalone DEV page, WASD/pointerlock lifecycle, conservative swept collision, selection và instrumentation đã viết. Pure logic xác minh tuyến ngắn Tây tới survey[.95,5.2,0], chặn tiếp vềB/khe hẹp/cửa ngoài; không walkthrough browser hoặc FPS PASS. Actual Chrome dừng ởE0 trước renderer E1. Frontend/unit/build và76Python regression PASS; exact finalHEAD/CI/artifact được bàn giao trong Draft PR. CI browser gate phải giữ đỏ khi finding còn mở.

Xem [báo cáo kỹ thuật E0/E1](3d-production/P507-WEBXR-E0-E1-EXPERIMENT.md) và [runbook](../experiments/p507-webxr/README.md). R4 không đổi, G1_CIRCULATION PARTIAL, G2_VISUAL PENDING, GPUthật/Galaxy/VR72 NOT TESTED. Dừng Draft PR, chờ ChatGPT/chủ dự án nghiệm thu; không merge/deploy/E2/E3.

---

## Bàn giao sang phiên chat mới — nghiệm thu kỹ thuật P507 R4 ngày 17/11/2026 (snapshot)

**Mục đích:** duy trì tiến độ qua các cuộc trò chuyện. Đây là snapshot nghiệm thu **trên bản asset commit**, không phải trạng thái GitHub tự cập nhật; phiên mới **phải fetch GitHub live** theo [AGENTS](../AGENTS.md), sau đó mới báo/triển khai.

**GitHub đã xác minh (17/11/2026):**
- `main` tại `e9a72caa084d9f2cbc4af2656b73509ea57b6d4b`: M0-A/B1/B2 và M1-A/B/C đã **MERGED** (đây chỉ là prototype synthetic, không phải P507 thật hoặc nghiệm thu KPI).
- [PR #13 — G0](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13): **OPEN, chưa merge**, head `c0eff0755d2d058b38944de60f40fb17387f2a91`, base `main`.
- [PR #14 — P507 G1/G2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14): **OPEN/DRAFT, chưa merge**, base `docs/g0-p507-3d-production-spec`. **Asset R4 được nghiệm thu tại commit `3a11ec757168a59625a087ac83f28c433751a1f5`**, [CI run 44009648703](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44009648703) **SUCCESS, 2/2 jobs trên chính asset SHA**; [artifact](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44009648703/artifacts/14296828070) có `.blend`, `.glb`, `asset-manifest.json`, báo cáo và 17 ảnh Chrome (artifact GitHub chỉ lưu 7 ngày). **Nếu có commit tài liệu sau `3a11ec7`, CI ở trên không phải kết quả của HEAD mới; không được gán sai SHA.**

**Kết luận nghiệm thu kỹ thuật của ChatGPT sau khi kiểm tra mã, dữ liệu, logs, GLB/ảnh và 121 vùng hình học:**
- `G1_GEOMETRY = PASS` trong phạm vi provisional đã đặt; `G1_LAYOUT_34_CHAIRS = PASS`. Phòng khảo sát **6.00×8.10×3.50m** (`USER_REPORTED`); bản **trải nghiệm ảo** **6.90×9.315×3.50m** (chủ dự án phê duyệt mở rộng X/Y **15%**, tăng diện tích **32.25%**, **không còn tỷ lệ phòng 1:1**). Vật thể giữ kích thước gốc trừ kệ được phép tăng chiều ngang.
- **17 bàn** A6/B6/C5; **36 ID ghế lịch sử**, **34 ghế có mesh** A12/B12/C10; C09/C10 **UNPLACED/UNASSIGNED** (không tự xóa). Cửa hai cánh **mở ra ngoài**, tủ tài liệu **ba khoang kính**, kệ đồ rộng **1.50m** và TV nhỏ có support, tường **kem vani sRGB `#F5E6C8`**. Giữ TV chéo, rèm, trần và khu tiện ích.
- `G2_PIPELINE = PASS` trên asset SHA: **76 Python tests**, **25 frontend tests**, Blender `.blend`→GLB, Khronos glTF Validator **0 errors/0 warnings**, Chrome 17 ảnh/không ghi nhận lỗi console; GLB **10,751,036 bytes**. **Đây là nghiệm thu kỹ thuật, không phải G2 visual sign-off của chủ dự án**.
- `G1_CIRCULATION = PARTIAL`: lối Tây static/use **1.08/0.93m**, giữa cụm khi kéo ghế **0.20/0.15m**, hàng C tới tường **0.10m**; không gọi các khe hẹp là lối đi, không xác nhận ergonomics/PCCC/accessibility.
- `G2_VISUAL = PENDING OWNER APPROVAL`, `PHOTO_MATCH = PARTIAL` (kích thước phòng ảo không 1:1), `REAL_DEVICE_WEBXR = NOT RUN`, `REAL_AIRC_DATA = NOT VERIFIED`, `G3 = NOT STARTED`. Các số frame-time của SwiftShader CI **không phải FPS GPU/VR vật lý**. Chưa có bằng chứng về quyền công bố ảnh, logo/nội dung gốc hay nguồn trạng thái thiết bị thật.

**Quyết định/điểm dừng:** **đóng băng asset P507 R4 ở mức `READY FOR WEBXR EXPERIMENT`**, *không* phê duyệt độ chân thực cuối cùng; tạm dừng sửa hình 3D/G3. **WebXR experiment là bước tiếp theo dự kiến, chưa có nhiệm vụ Codex triển khai hoặc kết quả chạy headset**. Không tự merge PR #13/#14, retarget, deploy, sửa app M1-C production, KPI, API hoặc database. Đề xuất vòng sau: người dùng giao nhiệm vụ cụ thể → ChatGPT lập **một prompt** cho Codex → Codex mở nhánh/PR thí nghiệm WebXR riêng, tải đúng GLB/manifest và kiểm tra scale/trục/ID, camera/locomotion/collision/hiệu năng → ChatGPT nghiệm thu. Thử đi lại cần tránh vùng hẹp; mọi WebXR session phải do hành động người dùng kích hoạt. Không tự động bắt đầu code khi chỉ được yêu cầu báo tiến độ.

**Nguồn đọc bắt buộc cho chat mới:** [ROADMAP](ROADMAP.md) (sáu nhóm vẫn **PROPOSED**, không ngầm được duyệt), [R4 frozen layout](3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md), [WebXR asset handoff](3d-production/P507-WEBXR-ASSET-HANDOFF.md), [G0 production spec](3d-production/P507-G0-PRODUCTION-SPEC.md) và [PR #14/CI live](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14). **Quy trình đã chốt:** ChatGPT lập kế hoạch/viết prompt → **Codex triển khai** → ChatGPT đọc code/PR, chạy hoặc xem CI/ảnh để **nghiệm thu**; ChatGPT không tự ý viết code hoặc merge.

---

## Cập nhật R4 ngày17/11/2026 — đóng băng asset, chờ nghiệm thu trước thử WebXR

Theo quyết định mới của owner, [R4](3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md) tách survey6×8.1×3.5m USER_REPORTED khỏi virtual6.9×9.315×3.5m OWNER_APPROVED_VIRTUAL_ADAPTATION.17bàn giữ kích thước,36ID ghế lịch sử/34placed A12B12C10/C09C10UNPLACED. Cửa2cánh OUTWARD, tủ3khoang kính, kệ1.50m sâu.47m, sơnkemvani#F5E6C8.121placed vertex proxies; static/occupied-use report tách riêng, circulation PARTIAL; trụcTây1.08/.93m, centraluse.20/.15m. [WebXR asset handoff](3d-production/P507-WEBXR-ASSET-HANDOFF.md) READY FOR WEBXR EXPERIMENT sau technical gates/exactHEAD CI trong PRhandoff, không runtime mới. G2_VISUAL PENDING OWNER APPROVAL; REAL_DEVICE_WEBXR NOT RUN; không merge/deploy/G3. R3 bên dưới là lịch sử.

---

## Cập nhật ngày 17/11/2026 — R3 tổng hợp G1/G2, chờ review

Tiếp tục Draft PR #14/base G0, không merge/deploy/G3. Đã mở13 ảnh thực và3 sơ đồ local; không công bố nguồn. [Báo cáo R3](3d-production/P507-G1-G2-COMPREHENSIVE-REVIEW.md) và [đối chiếu nguồn](3d-production/P507-G1-G2-SURVEY-COMPARISON.md) thay trạng thái hiện hành của snapshot cũ bên dưới.17 bàn/36 ID ghế,24 đặt/12 UNPLACED; B/C dịch+X, TV chéo25°, máy nước xoay90°, AI wall27 frame, utility đầy đủ, trần8đèn/4quạt/2AC/projector/camera và4rèm.111 instance đã đặt có vertex proof,56unit tests; circulation PARTIAL (.26m sát tường phải/.53m chỗ kệ giày), usable walkway UNKNOWN. PHOTO_MATCH PARTIAL định tính, survey PROVISIONAL; G2_VISUAL PENDING OWNER APPROVAL, thiết bị thật NOT RUN. Final exact-HEAD CI/artifacts được ghi trong PR handoff sau khi chạy; không lấy green775 làm chứng cứ R3. Dừng sau bàn giao.

---

## Cập nhật 16/11/2026 — tiếp tục PR #14 sửa layout/hero G1/G2

Task hiện hành được chủ dự án giao: sửa A, ghế phải B/C, tủ/bình nước/cửa, inventory v2 và góc hero; **không merge/deploy/G3**. Root `D:\Code\DATN`, branch `feat/p507-g1-g2-blockout-hero`; [PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14) giữ Draft/base `docs/g0-p507-3d-production-spec`. PR #13 vẫn open lúc kiểm tra đầu task; không retarget/sửa G0.

Đã sửa 17 bàn/36 ghế explicit, SAT occupancy và mesh bounds độc lập trong Blender; không còn tủ–ghế/bình nước–entry overlap. A dịch +.60m X, cửa −.90m Y. Xem [revision với tọa độ và giới hạn](3d-production/P507-G1-G2-LAYOUT-LOOKDEV-REVISION.md) và [acceptance](3d-production/P507-G1-G2-ACCEPTANCE.md). Hero có ghế cong/khung ống, apron bàn, TV/tủ/máy nước nhiều chi tiết và vật liệu procedural; Three.js có lighting/camera/metrics riêng. Không thay Scene production, PostgreSQL/API/KPI.

**G1 geometry PASS cho occupancy provisional đã đặt; survey PROVISIONAL.** Clearance UNKNOWN: khoảng giữa envelope ghế chỉ .20/.40m, không chứng nhận sử dụng/PCCC. Tủ/kệ chưa có tọa độ và hướng/số cánh cửa UNKNOWN. **G2_VISUAL PENDING OWNER APPROVAL**; vẫn là scene procedural đơn giản, không photorealistic hoàn tất. PHOTO_MATCH BLOCKED; REAL_DEVICE_WEBXR NOT RUN; REAL_AIRC_DATA NOT VERIFIED; G3 NOT STARTED.

Local checks: 31 geometry tests, Blender4.5.9 export/evaluated bounds (cả thêm supported item), Khronos validator, frontend build/25 unit, checker10, repository verifier/diff/privacy scan. Final exact-HEAD CI và artifact links ghi trong PR handoff khi run hoàn tất; không lấy run cũ làm chứng cứ mới. Raw neutral artifacts nằm `.local/p507-g1-g2/` và CI artifact, không có ảnh khảo sát. Bước tiếp: exact-HEAD CI → ChatGPT/chủ dự án xem render → dừng chờ visual sign-off; không tự bắt đầu G3.

---


## Cập nhật ngày 16/11/2026 — G1/G2 đã khởi động, chưa nghiệm thu (snapshot, xác minh GitHub live)

**Task người dùng vừa duyệt:** bắt đầu **G1 room geometry + G2 hero lookdev**, theo [G0 production spec](3d-production/P507-G0-PRODUCTION-SPEC.md); **không triển khai G3**. [Draft PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14) trên `feat/p507-g1-g2-blockout-hero`, đang **IN PROGRESS / NOT MERGE READY** as-of 16/11/2026. Vì [G0 PR #13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13) chưa merge, PR #14 được xếp chồng lên branch G0; sau khi G0 được duyệt và merge, mới kiểm tra retarget PR #14 sang main. Không tự merge hai PR.

**Đã viết mã nguồn:** inventory tạm thời P507 có thể bổ sung với 17 bàn và 36 ghế placeholder, kiểm tra boundary/non-overlap/ID/provenance; Blender-Python source dựng shell có cửa/cửa sổ, nội thất/trần và góc hero TV–tủ–bình nước; trang preview Three.js dev-only. Các tọa độ là `PROPOSED_LAYOUT`, không chứng nhận lối đi hoặc dữ liệu AIRC. Chưa thay sản phẩm M1-C, schema, API hay quyền dữ liệu.

**Kết quả kỹ thuật đã chạy:** [CI G1/G2 run 43804659514](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43804659514) trên commit `e04427e739668e2414aae5acb4eb00c3da1c3f6b` đã xuất được Blender `.blend` + GLB, kiểm qua **Khronos glTF Validator 0 errors/0 warnings** (431 INFO unused UV), build frontend, mở bằng Chrome software WebGL và xuất ảnh 3 góc desktop + 390px mobile. Có khoảng 432 mesh và 7.200 triangles. Xem [báo cáo G1/G2](3d-production/P507-G1-G2-ACCEPTANCE.md). **G1: geometry/source technical PASS có giới hạn. G2: visual NOT ACCEPTED** sau khi ChatGPT trực tiếp xem ảnh; thiếu photo match P507, vật liệu và chi tiết kiểu game, hiệu năng GPU/thiết bị thật. Quyền ảnh/nhãn AIRC PENDING; ảnh gốc có người/nội dung nội bộ không commit. PR #14 phải giữ Draft trước khi user duyệt G2; không bắt đầu G3.

**KPI:** MT1–MT3 chưa nghiệm thu thực địa; ≥3 phòng vẫn nguyên; Issues #1–#5 chưa được đóng chỉ vì G1/G2 code có mặt.

---

## Cập nhật ngày 16/11/2026 — khảo sát P507 và chuẩn G0 (snapshot, kiểm GitHub live)

**Nguồn quyết định:** chủ dự án xác nhận trực tiếp ngày 16/11/2026 phương pháp dựng P507 **Hybrid Photorealistic Digital Twin** và yêu cầu chốt G0 một lần, tránh chuỗi G0-fix. Xem [P507 G0 Production Specification v1.0](3d-production/P507-G0-PRODUCTION-SPEC.md). Chỉ G0 art/production standard trong phạm vi này được đồng ý; sáu nhóm tương lai trong [ROADMAP](ROADMAP.md) vẫn **PROPOSED**, không mặc nhiên được triển khai.

**Khảo sát từ người dùng:** ngày 16/11/2026 đã nhận bảng inventory và nhiều ảnh P507, sơ đồ sàn/trần; người dùng xác nhận kích thước phòng 8.1×6×3.5m, 17 bàn (16 thường, 1 nhỏ), ba cụm A/B/C, cửa trái/bốn cửa sổ phải, bố trí trần và khu logo/TV/bảng. **USER_REPORTED/PROVISIONAL**, chưa có tài liệu xác nhận số đo/quyền AIRC, chưa được phép công bố ảnh có người, màn hình, bảng công tác hoặc nhãn hiệu. Không đóng Issues #1–#3, không gán P507 là real_verified. Khoảng cách/coords được tự cân chỉnh là PROPOSED_LAYOUT, không phải measurement/certified exit clearance. Inventory mở và được cập nhật bằng survey revisions.

**Task tài liệu G0:** [PR #13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13) **IN REVIEW as-of 16/11/2026** — verify live GitHub before reporting. Branch docs/g0-p507-3d-production-spec, base main at e9a72caa084d9f2cbc4af2656b73509ea57b6d4b. Task chỉ một tài liệu chuẩn + link README/AGENTS/STATUS; không có GLB, Blender export, web model, migration hay production write. PR #12 đã MERGED tại e9a72caa084d9f2cbc4af2656b73509ea57b6d4b; snapshot PR #12 IN REVIEW bên dưới đã hết hạn và chỉ có giá trị lịch sử.

**Bước tiếp theo (chưa triển khai):** nghiệm thu PR G0; sau đó chủ dự án có thể giao **một nhiệm vụ G1 geometry + G2 hero lookdev** theo tài liệu. G2 phải có browser preview, ảnh đối chiếu, performance evidence và chủ dự án duyệt trước G3. Chưa có lệnh cho Codex bắt đầu G1/G2/G3; KPI/AR/VR/visitor tracking giữ trạng thái chưa nghiệm thu.

---

Cập nhật 15/11/2026 bởi Codex trong task chuẩn hóa tài liệu. Root `D:\Code\DATN`; remote `https://github.com/duyanhtr130905/DATN-AIRC-WebXR.git`; base `main`. [ROADMAP](ROADMAP.md) là nguồn roadmap duy nhất, **PROPOSED — chờ chủ dự án duyệt**. [KPI](02-requirements-kpi.md) giữ nguyên; [ADR-0001](decisions/0001-technology-options.md) giữ nguyên các quyết định ACCEPTED.

**Snapshot as-of 15/11/2026, không tự bảo đảm là tiến độ mới nhất.** Mọi phiên kiểm tra tiến độ phải đọc default branch và đối chiếu GitHub live main HEAD, PR OPEN/MERGED, commit/CI/checks và issues/blockers theo quy trình trong [AGENTS](../AGENTS.md). Báo phần chưa xác minh nếu thiếu quyền truy cập. Sau PR #12 merge, snapshot này không tự chuyển thành phê duyệt roadmap hoặc task mới; cập nhật status khi task sau được chủ dự án duyệt.

## Milestone đã merge

| Milestone | Trạng thái | PR / merge commit |
| --- | --- | --- |
| M0-A | DONE | [#6](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/6) / `1a736d5` |
| M0-B1 | DONE | [#7](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/7) / `3ebd2ec` |
| M0-B2 | DONE | [#8](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/8) / `b4e4b91` |
| M1-A | DONE | [#9](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/9) / `99f6537` |
| M1-B | DONE | [#10](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/10) / `66e1666` |
| M1-C | DONE | [#11 merged](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/11) / `33ba38b00e2d6c218c1ab97ba1cc7201d1e92a58` |

Đã fetch và đối chiếu `origin/main` đúng merge trên; GitHub xác nhận PR #11 merged ngày 15/11/2026. Nhánh bàn giao M1-C có HEAD `4301be42773ea1fd83b9efb7e1d6fef655604967`. **M1 chỉ hoàn thành prototype synthetic**, PostgreSQL → FastAPI REST/WebSocket → Chrome/R3F primitives + Information Panel. Chưa hoàn thành sản phẩm P507; MT1–MT3 chưa được nghiệm thu trên sản phẩm thật.

## Bằng chứng và giới hạn

- [Acceptance M1-C](18-m1-c-vertical-slice-acceptance.md), [checkpoint lịch sử](18-m1-c-progress.md), [raw evidence](evidence/m1-c-validation.json) giữ nguyên; IN REVIEW trong snapshot cũ đã được thay bằng trạng thái merge ở đây.
- Snapshot source `09f3e23`: 70 backend unit, 67 PostgreSQL, 25 frontend unit, 16 browser groups/20 render samples được ghi PASS. PR #11 ghi final HEAD `4301be4` đã PASS CI; metrics/artifact từng SHA phải tách biệt, không gán vào merge commit.
- [CI final HEAD của M1-C](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43675175165) được dẫn từ PR #11; task tài liệu không chạy lại benchmark hoặc xác minh lại toàn bộ artifact sản phẩm. Local PostgreSQL BLOCKED là trạng thái môi trường trong bàn giao M1-C, không phải kết quả probe mới.
- Synthetic 20 objects/41 states không phải inventory/transform P507. CLI-start → afterRender không là source-to-render AIRC; software WebGL/viewport/IWER không là Galaxy/kính vật lý. State history/outbox/diagnostics không là visitor session/event persistence.

## Blocker và quyết định mở

Khảo sát P507 **chưa được xác nhận hoàn thành**. Lịch dự kiến 16/11/2026 chưa là bằng chứng thực hiện. Chưa có bộ survey/inventory/ảnh/kích thước/GLB/nguồn và quyền dữ liệu được xác nhận. Không mặc định AIRC có API quản lý thiết bị.

[Issues #1–#5](backlog/README.md) còn OPEN qua truy vấn GitHub ngày 15/11/2026: scope ≥3 phòng, survey/inventory, nguồn/quyền, Galaxy AR và phương án VR. Không đổi KPI, không chia P507 thành ba phòng. Galaxy/VR vật lý NOT TESTED; auth/quyền ghi, session identity/consent/retention, hosting và multi-instance chưa chốt.

Milestone tiếp theo **chưa được phê duyệt, NOT STARTED**. Sáu nhóm đề xuất và DoD/phụ thuộc/quyết định nằm trong ROADMAP; không tự bắt đầu M2/M3, visitor tracking, tích hợp thật hoặc deploy. Các mâu thuẫn charter/ADR/runbook và metadata `.techlead/project.yaml` lịch sử được liệt kê trong ROADMAP để chủ dự án review, không tự sửa quyết định hoặc mã nguồn.

## Snapshot task tài liệu đã bàn giao ngày 15/11/2026

**[PR #12](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/12) IN REVIEW as-of 15/11/2026 — verify GitHub live.** Đây là task tài liệu đã bàn giao tại thời điểm lập; không phải chỉ dẫn task hiện hành vĩnh viễn. Chủ dự án đã cho phép phạm vi: branch `docs/project-roadmap-source-of-truth`, một PR vào `main`; chỉ `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, `docs/PROJECT_STATUS.md`. Working tree ban đầu sạch trên nhánh M1-C; branch mới xuất phát `origin/main` tại merge `33ba38b`. Không thay acceptance/evidence lịch sử, schema/API/dependencies/assets/CI.

Kiểm tra của task tài liệu: `python tools/verify_repository.py` PASS (local Markdown links, UTF-8, secret patterns và checker resources); `git diff --check` PASS. Đây là quét mẫu giới hạn, không phải audit secrets toàn diện; external links không được crawl toàn bộ. Kết quả cuối/HEAD nằm trong PR bàn giao để tránh tự tham chiếu SHA. Tests runtime/KPI/thiết bị: NOT RUN trong task tài liệu vì không thay mã nguồn.

Follow-up theo [review ChatGPT](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/12#issuecomment-6890311024): bổ sung quy trình kiểm tra tiến độ chỉ đọc bằng GitHub live và bỏ cách diễn đạt task hiện hành vĩnh viễn. Phạm vi follow-up vẫn chỉ các Markdown của PR #12; không thay roadmap thành APPROVED.

Hành động tiếp tục, cần đối chiếu live trước mỗi phiên:

1. Nếu chủ dự án chỉ hỏi tiến độ, kiểm tra và báo cáo ngay theo AGENTS, không cần phê duyệt task triển khai. Phân biệt đã merge, đang review, đề xuất chờ duyệt và chưa triển khai; nêu rõ lệch docs-vs-GitHub và task tiếp theo đã duyệt nếu có bằng chứng.
2. Với snapshot PR #12 còn IN REVIEW: ChatGPT/chủ dự án nghiệm thu lại tài liệu và quyết định merge. Lệnh dừng sau bàn giao áp dụng cho lần thực hiện task tài liệu, không ngăn phiên sau đọc/báo cáo hoặc làm task mới đã được duyệt. Không tự merge.
3. Khi chủ dự án duyệt task sau, ghi người/ngày/tham chiếu, phạm vi/DoD và cập nhật status; chỉ triển khai đúng quyền đó. Sau mỗi PR đã nghiệm thu, cập nhật evidence, merge nếu có, blocker và bước tiếp. Merge PR tài liệu không đồng nghĩa roadmap được duyệt hoặc được phép bắt đầu M2/M3; review AI không thay phê duyệt của chủ dự án/giảng viên.
