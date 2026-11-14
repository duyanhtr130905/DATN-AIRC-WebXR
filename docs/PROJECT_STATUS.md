# Trạng thái dự án — M0-B2

Cập nhật 14/11/2026, Codex. Root `D:\Code\DATN`, repo duyanhtr130905/DATN-AIRC-WebXR, branch `feat/m0-b2-app-foundation`. Không deploy hoặc merge PR; M1 NOT STARTED.

| Milestone | Trạng thái | Bằng chứng |
|---|---|---|
| M0-A | DONE | PR6 merge 1a736d558f6b721921cd5f38de069d63a733721e |
| M0-B1 | DONE | PR7 merge 3ebd2ec780db80caacd5871ecda911236598f9be; docs11 và hai PoC giữ nguyên |
| M0-B2 | IN REVIEW | apps/web, apps/api, infra, docs12–15 và app-validation CI |
| M1 | NOT STARTED | Chưa nghiệp vụ trạng thái/session/reports/realtime |

Chủ dự án phê duyệt qua ChatGPT ngày 14/11/2026: R3F/XR, FastAPI/PostgreSQL, REST/WebSocket, Modular Monolith, Scene + Information Panel chính và Guided Tour phụ. [ADR-0001 ACCEPTED](decisions/0001-technology-options.md). Giữ Meta IWSDK làm PoC đối chứng. Schema chi tiết/auth/hosting/retention/quyền dữ liệu/KPI ba phòng/VR acceptance vẫn chưa duyệt.

## Kết quả và bằng chứng

Frontend primitive synthetic, scene/panel, API client; backend factory/config/CORS/liveness/readiness/pool lifecycle. Design model và contracts PROPOSED, không migration/seed. [Run web](../apps/web/README.md), [API](../apps/api/README.md), [infra](../infra/README.md), [acceptance và CI](15-m0-b2-acceptance.md). Local build/7 frontend tests/14 backend tests/6 app browser scenarios đã PASS; M0-A và hai PoC build/tests/browser đã PASS lại. PostgreSQL local BLOCKED vì không Docker; kết quả PostgreSQL CI ghi riêng trong acceptance.

## Blocker thực địa giữ nguyên

Theo người dùng, thầy chỉ đạo “Cứ làm 1 phòng 507 trước”. Đây là thông tin trao đổi, chưa phải dữ liệu khảo sát chính thức. Dự kiến khảo sát 16/11/2026; chưa ảnh/sơ đồ/kích thước/inventory/nguồn/quyền dữ liệu, chưa phần mềm quản lý thiết bị. Không dựng mô hình 507 giả làm thật; DEMO không phải AIRC. KPI ≥3 phòng chưa điều chỉnh chính thức: giữ MT1–MT3 và Issues #1–#5 mở/BLOCKED. Galaxy A17 chưa thử AR session; iPhone chưa biết model; không kính VR. Chưa nghiệm thu FPS, latency, task completion hoặc tracking sản phẩm.

## Sau review

1. ChatGPT review PR M0-B2 và bằng chứng CI/browser, xử lý quyết định còn mở.
2. Khảo sát phòng 507, xác minh inventory/nguồn/quyền và phạm vi ≥3 phòng chính thức.
3. Chỉ sau phê duyệt M1: chốt schema/migration, catalog API + adapter có provenance; state/history/outbox và instrumentation latency. Không tự bắt đầu M1.

PR bàn giao [#8](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/8). Ba PR workflows PASS trên source commit4c6ad13, gồm PostgreSQL18.7 integration thật; latest HEAD checks được xác minh trước bàn giao. [Bản ghi CI](evidence/m0-b2-ci.json). PostgreSQL local vẫn BLOCKED; schema migration NOT RUN.
