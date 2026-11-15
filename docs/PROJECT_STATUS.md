# Trạng thái dự án — nguồn tiếp tục hiện hành

Cập nhật 15/11/2026 bởi Codex trong task chuẩn hóa tài liệu. Root `D:\Code\DATN`; remote `https://github.com/duyanhtr130905/DATN-AIRC-WebXR.git`; base `main`. [ROADMAP](ROADMAP.md) là nguồn roadmap duy nhất, **PROPOSED — chờ chủ dự án duyệt**. [KPI](02-requirements-kpi.md) giữ nguyên; [ADR-0001](decisions/0001-technology-options.md) giữ nguyên các quyết định ACCEPTED.

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

## Task hiện tại và checkpoint bàn giao

Chủ dự án đã cho phép đúng task tài liệu: branch `docs/project-roadmap-source-of-truth`, một PR vào `main`; chỉ `AGENTS.md`, `README.md`, `docs/ROADMAP.md`, `docs/PROJECT_STATUS.md`. Working tree ban đầu sạch trên nhánh M1-C; branch mới xuất phát `origin/main` tại merge `33ba38b`. Không thay acceptance/evidence lịch sử, schema/API/dependencies/assets/CI.

Kiểm tra của task tài liệu: `python tools/verify_repository.py` PASS (local Markdown links, UTF-8, secret patterns và checker resources); `git diff --check` PASS. Đây là quét mẫu giới hạn, không phải audit secrets toàn diện; external links không được crawl toàn bộ. Kết quả cuối/HEAD nằm trong PR bàn giao để tránh tự tham chiếu SHA. Tests runtime/KPI/thiết bị: NOT RUN trong task tài liệu vì không thay mã nguồn.

Bước tiếp theo theo thứ tự:

1. ChatGPT/chủ dự án review PR tài liệu, đối chiếu merge và các mâu thuẫn đã nêu; Codex dừng sau bàn giao, không tự merge.
2. Chủ dự án chấp nhận/sửa roadmap, ghi người/ngày/tham chiếu duyệt và chốt task tiếp theo với phạm vi/DoD cụ thể.
3. Chỉ thực hiện task đã duyệt sau khi đọc ROADMAP/status/KPI/ADR và kiểm tra Git/PR mới nhất. Sau mỗi PR đã được nghiệm thu, cập nhật status với evidence, merge nếu có, blocker và quyền tiếp tục; review AI không tự thay phê duyệt của chủ dự án/giảng viên.
