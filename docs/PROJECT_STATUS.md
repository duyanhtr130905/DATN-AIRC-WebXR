# Trạng thái dự án — nguồn tiếp tục hiện hành

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
