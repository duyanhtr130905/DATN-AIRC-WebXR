# DATN AIRC WebXR

Xây dựng bản sao số không gian AIRC trên nền tảng WebXR hỗ trợ tham quan tương tác và lưu vết trải nghiệm.

**Nguồn tiếp tục qua các phiên:** [ROADMAP 2.0 — kế hoạch chính thức APPROVED 18/11/2026](docs/ROADMAP.md) và [PROJECT_STATUS — trạng thái hiện hành](docs/PROJECT_STATUS.md). Roadmap chỉ được quản lý tại ROADMAP; README không duy trì một kế hoạch riêng.

M0-A/B1/B2 và M1-A/B/C đã DONE/merge. [PR #11](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/11) merged tại `33ba38b00e2d6c218c1ab97ba1cc7201d1e92a58`. **M1 chỉ hoàn thành prototype synthetic** nối PostgreSQL → FastAPI REST/WebSocket → React/R3F primitives + Information Panel. Hiện M2 IN_PROGRESS: prototype một phòng P507 trên frozen R4 provisional; E0 FAIL, E1 runtime BLOCKED. Survey USER_REPORTED, virtual adaptation X/Y +15% không 1:1; G2 visual pending. MT1–MT3 chưa nghiệm thu; ≥3 phòng vẫn thuộc M6. Xem PROJECT_STATUS để phân biệt branch/main và PR chưa merge.

Trước task mới, đọc [AGENTS](AGENTS.md), ROADMAP, PROJECT_STATUS, [requirements/KPI](docs/02-requirements-kpi.md) và [ADR liên quan](docs/decisions/0001-technology-options.md). AGENTS là quy tắc thực thi và chống lệch roadmap; PROJECT_STATUS là snapshot/nghiệm thu. Không suy ra quyền tự triển khai feature từ kế hoạch APPROVED hoặc PR đã merge. Giữ KPI gốc; không chia P507 thành ba phòng.

## Đặc tả 3D P507 — G0 (16/11/2026)

Chủ dự án đã chốt **hướng Hybrid Photorealistic Digital Twin** và quy chuẩn G0 để tránh sửa đi sửa lại: [P507 Art Direction & Production Specification v1.0](docs/3d-production/P507-G0-PRODUCTION-SPEC.md). Đây là chuẩn kỹ thuật cho blockout G1, hero lookdev G2 và đánh giá trên Three.js. **Đặc tả không chứng minh đã dựng GLB hoặc P507 đạt KPI; dữ liệu khảo sát/ảnh AIRC còn provisional và quyền chưa xác minh.**

Đã nhận khảo sát P507 từ người dùng ngày 16/11/2026 (ảnh, sơ đồ sàn/trần và danh mục có thể bổ sung); chưa có AIRC sign-off. G0 là task chuẩn hóa thiết kế được chủ dự án yêu cầu, **không phê duyệt toàn bộ roadmap M2/M3**. Theo GitHub live, trạng thái G0 PR mới nhất cần xem tại PROJECT_STATUS và PR.

## Kiểm tra tiến độ trong chat mới

Có thể chỉ yêu cầu: `Kiểm tra tiến độ mới nhất của dự án tại repo duyanhtr130905/DATN-AIRC-WebXR`.

AI cần đọc tài liệu trên default branch và truy vấn GitHub live theo [AGENTS](AGENTS.md), báo main HEAD, PR OPEN/MERGED mới nhất, milestone, CI đúng SHA, blockers, lệch tài liệu và task tiếp theo đã được duyệt nếu có. PROJECT_STATUS là snapshot theo ngày, kể cả sau merge; không lấy cache hoặc kế hoạch làm tiến độ mới nhất. Chỉ đọc/báo cáo không cần duyệt task triển khai. Thiếu quyền private repo/connector thì báo giới hạn và yêu cầu cấp quyền, không nhận đã kiểm tra.

## Chạy và tìm tài liệu

| Nội dung | Nguồn |
| --- | --- |
| Web frontend | [apps/web](apps/web/README.md) |
| API, migration/seed có guard, CLI synthetic | [apps/api](apps/api/README.md) |
| PostgreSQL local | [infra](infra/README.md); lưu ý câu migration chưa có revision là lịch sử foundation, đối chiếu API runbook/model trước thao tác DB |
| Charter và KPI gốc | [Charter](docs/01-project-charter.md), [requirements/KPI](docs/02-requirements-kpi.md) |
| Kiến trúc và quyết định | [Kiến trúc](docs/12-official-system-architecture.md), [ADR-0001](docs/decisions/0001-technology-options.md) |
| Model và contracts | [Data model](docs/13-data-model.md), [API contracts](docs/14-api-contracts.md) |
| Survey, nguồn và quyền dữ liệu | [Checklist](docs/04-airc-survey-checklist.md), [nguồn dữ liệu](docs/05-data-source-strategy.md), [blocker issues](docs/backlog/README.md) |
| Kết quả M1-C | [Acceptance](docs/18-m1-c-vertical-slice-acceptance.md), [checkpoint lịch sử](docs/18-m1-c-progress.md), [evidence](docs/evidence/m1-c-validation.json) |
| Nghiên cứu và PoC lịch sử | [Sources](docs/research/sources.md), [technology](docs/07-technology-research.md), [UX](docs/08-ui-ux-research.md), [PoC A/B](experiments/README.md) |
| Công cụ M0-A | [WebXR capability checker](tools/webxr-capability-check/README.md) |

Acceptance, research và checkpoint cũ được giữ nguyên; các phát biểu “đang review/chưa triển khai” trong snapshot mô tả thời điểm bàn giao đó. Đối chiếu trạng thái mới trong PROJECT_STATUS và phần lịch sử/merge của ROADMAP; nếu còn mâu thuẫn thì báo chủ dự án.

Default live không âm thầm fallback dữ liệu hardcode; DEMO offline chỉ khi chọn riêng. Dữ liệu synthetic, viewport emulation, software WebGL và IWER không chứng minh dữ liệu thật P507, AR/VR vật lý hoặc KPI. Chưa có visitor session/event persistence, public write hoặc deployment sản phẩm. Hướng dẫn chạy chi tiết nằm trong runbook tương ứng.
