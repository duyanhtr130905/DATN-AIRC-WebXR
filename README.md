# DATN AIRC WebXR

Xây dựng bản sao số không gian AIRC trên nền tảng WebXR hỗ trợ tham quan tương tác và lưu vết trải nghiệm.

**Nguồn tiếp tục qua các phiên:** [ROADMAP — PROPOSED, chờ chủ dự án phê duyệt](docs/ROADMAP.md) và [PROJECT_STATUS — trạng thái hiện hành](docs/PROJECT_STATUS.md). Roadmap chỉ được quản lý tại ROADMAP; README không duy trì một kế hoạch riêng.

M0-A/B1/B2 và M1-A/B/C đã DONE/merge. [PR #11](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/11) merged tại `33ba38b00e2d6c218c1ab97ba1cc7201d1e92a58`. **M1 chỉ hoàn thành prototype synthetic** nối PostgreSQL → FastAPI REST/WebSocket → React/R3F primitives + Information Panel. Khảo sát P507 chưa được xác nhận hoàn thành; MT1–MT3 chưa được nghiệm thu trên sản phẩm thật; milestone tiếp theo chưa được phê duyệt.

Trước task mới, đọc [AGENTS](AGENTS.md), ROADMAP, PROJECT_STATUS, [requirements/KPI](docs/02-requirements-kpi.md) và [ADR liên quan](docs/decisions/0001-technology-options.md). Không suy ra quyền triển khai từ roadmap PROPOSED hoặc PR đã merge. Giữ KPI gốc; không chia P507 thành ba phòng.

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
