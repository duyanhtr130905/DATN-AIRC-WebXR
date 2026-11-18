# Quy tắc làm việc — DATN AIRC WebXR

## Phạm vi và an toàn

- Root duy nhất: `D:\Code\DATN`. Remote duy nhất được phép ghi: `https://github.com/duyanhtr130905/DATN-AIRC-WebXR.git`.
- Không truy cập, đọc, chỉnh sửa, sao chép, fork hay dùng dữ liệu/mã/tài liệu của KLTN-Factory-Agentic-DT. Không dùng repository cũ làm template.
- Trước mọi thao tác ghi GitHub: kiểm tra `Get-Location`, `git rev-parse --show-toplevel`, `git remote -v`, `git branch --show-current`, `git status --short`, diff và secret. Sai root/remote thì dừng.
- Không force push, xóa nhánh/repo, thay visibility, deploy hoặc bắt đầu milestone/feature chưa được giao. **Codex không được tự merge PR.** ChatGPT chỉ được merge khi có ủy quyền cụ thể từ chủ dự án, review độc lập PASS, kiểm đúng HEAD/CI, không còn blocker và GitHub cho phép merge; ủy quyền của chủ dự án ngày 18/11/2026 áp dụng các PR đủ điều kiện trong lượt nghiệm thu hiện tại, không mặc nhiên cấp quyền vô thời hạn. Không sửa Git global config; không cài công cụ hệ thống nếu không cần.
- Lịch sử: M0-A chỉ tài liệu và checker; task M0-B1 ngày 14/11/2026 cho phép hai PoC cô lập trong experiments/ và test tooling dùng dữ liệu synthetic. Giới hạn lịch sử M0-B1; task M0-B2 ngày 14/11/2026 đã duyệt nền tảng chính thức apps/web, apps/api, infra. Stack/Modular Monolith/UI theo ADR-0001 ACCEPTED. Schema chi tiết/auth/hosting/retention/quyền dữ liệu/nghiệm thu VR vẫn chưa duyệt; không thay KPI hoặc tự triển khai feature chưa được giao/AI/RAG. Các giới hạn chưa M1 trong task cũ là lịch sử, không phủ nhận M1 đã merge.

## Nguồn thông tin và quyền tiếp tục hiện hành

- [ROADMAP](docs/ROADMAP.md) là nguồn roadmap duy nhất; [PROJECT_STATUS](docs/PROJECT_STATUS.md) ghi hiện trạng và bằng chứng. Roadmap **2.0 APPROVED ngày 18/11/2026**, duy nhất tám milestone M0–M7. Phê duyệt kế hoạch không cấp quyền tự triển khai mọi feature. Current milestone M2 IN_PROGRESS; M0/M1 DONE/MERGED; xem STATUS để tách branch/main.
- Chỉ thực hiện task được chủ dự án phê duyệt, trong phạm vi và DoD đã chốt. **M2 đang IN_PROGRESS** nhưng không được tự bắt đầu work item M2/M3 mới hoặc milestone tiếp theo chỉ vì PR trước đã merge.
- Không tự đổi tên, thứ tự hoặc nội dung milestone đã duyệt. Đề xuất thay đổi phải ghi riêng và chờ phê duyệt, không sửa KPI hoặc chia P507 thành ba phòng.
- Sau mỗi lượt/review, áp dụng Post-Acceptance Synchronization bên dưới kể cả khi thất bại; chưa nghiệm thu ghi IN_REVIEW. Merge kỹ thuật không đồng nghĩa KPI đạt.
- Nếu tài liệu mâu thuẫn, báo chủ dự án kèm nguồn, thời điểm và tác động; không tự chọn một cách hiểu, sửa quyết định hoặc dùng kế hoạch lịch sử làm quyền triển khai. Giữ nguyên acceptance/evidence lịch sử và dẫn trạng thái hiện tại.
- Snapshot bàn giao task tài liệu ngày 15/11/2026: [PR #12](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/12) IN REVIEW as-of 15/11/2026 — verify GitHub live. Phạm vi và lệnh dừng của lần bàn giao này được lưu trong PR; không dùng chúng làm task hiện hành vĩnh viễn hoặc ngăn yêu cầu kiểm tra tiến độ chỉ đọc. Sau merge, status vẫn là snapshot theo ngày; cập nhật khi task sau được chủ dự án duyệt. Merge tài liệu không phê duyệt roadmap hoặc task M2/M3.

## Roadmap Deviation Guard — Mandatory

Trước khi nhận hoặc thực thi bất kỳ yêu cầu phát triển nào, ChatGPT/Codex phải xác định: yêu cầu thuộc M0–M7 nào; nằm trong phạm vi/DoD đã duyệt không; dependency đã đạt chưa; có đổi kiến trúc, dữ liệu, KPI, quyền, asset baseline, thứ tự ưu tiên hoặc milestone không; có mâu thuẫn quyết định đã duyệt không. Đối chiếu ROADMAP, PROJECT_STATUS, KPI, ADR và task có thẩm quyền trước phần triển khai.

Nếu yêu cầu mới từ chủ dự án khác/mâu thuẫn roadmap hiện hành:

1. **Báo ngay trước khi thực hiện phần sai lệch.**
2. Chỉ rõ milestone, tài liệu và quyết định liên quan.
3. Giải thích tác động kỹ thuật, tiến độ, phụ thuộc và KPI.
4. Đưa phương án giữ roadmap hoặc thay đổi có kiểm soát.
5. Chờ chủ dự án quyết định khi ảnh hưởng phạm vi, kiến trúc, điều kiện nghiệm thu hoặc an toàn dữ liệu; tiếp tục được phần độc lập đã được phép.
6. Nếu duyệt ngoại lệ/điều chỉnh, cập nhật decision log, ROADMAP và PROJECT_STATUS **trước** triển khai theo phạm vi mới, ghi người/ngày/phạm vi và evidence; không bịa chat URL.

Mẫu thông báo:

**ROADMAP DEVIATION DETECTED**

- Requested action:
- Current milestone / approved scope:
- Conflict:
- Impact / risks:
- Recommended action:
- Decision required:

Không suy diễn “cứ làm đi” chung chung thành quyền thay KPI, bỏ dependency hoặc thêm milestone. Không dùng roadmap để từ chối máy móc yêu cầu hợp lệ: nêu xung đột và phương án để owner quyết định. Không tạo roadmap thứ hai trong README/AGENTS/YAML; checkpoint/work item thuộc tám milestone, không đổi tên hồi tố.

## Post-Acceptance Synchronization — Mandatory

Sau mỗi lượt Codex:

1. Codex giao PR/HEAD/CI đúng SHA/evidence và giới hạn, không tự nghiệm thu.
2. ChatGPT nghiệm thu độc lập với kết luận **PASS/PARTIAL/FAIL/BLOCKED**.
3. Cập nhật **ROADMAP và PROJECT_STATUS ngay cả khi nghiệm thu thất bại**: kết luận/DoD, evidence, blocker, next action và quyền tiếp tục.
4. Commit tài liệu đồng bộ.
5. ChatGPT đọc lại diff và HEAD cập nhật; nếu còn sai, ghi và sửa theo phạm vi.
6. Nếu docs trên branch chưa merge, ghi rõ trạng thái branch so với main, PR/head/base và CI tương ứng; không tuyên bố đã đồng bộ main chỉ vì Draft PR xanh.
7. Chủ dự án quyết định merge/triển khai bước tiếp theo hoặc **ủy quyền có phạm vi cho ChatGPT merge các PR đủ điều kiện** sau review và kiểm tra live. Codex không được merge. Không coi review AI thay nghiệm thu học thuật/quyền AIRC.

Quy trình áp dụng sau mọi kết luận, không đợi PASS. Roadmap 2.0 được bàn giao qua [PR #16](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/16); trạng thái nghiệm thu/merge phải xác minh GitHub live, không suy từ lời bàn giao cũ. E0/E1 correction là task feature tiếp theo của M2, cần quyền riêng sau đồng bộ. Không tự bắt đầu M3–M7.

## Quy tắc M2 P507 hiện hành

- M2 chỉ prototype một phòng P507. Issue #1 OPEN: `DEFERRED_FOR_M2; REQUIRED_FOR_M6`; không chặn E0/E1/nghiệm thu chức năng M2. MT1-01 ≥3 phòng giữ nguyên tại M6; không chia phòng giả.
- Survey 6.00 × 8.10 × 3.50 m USER_REPORTED; virtual 6.90 × 9.315 × 3.50 m OWNER_APPROVED_VIRTUAL_ADAPTATION, X/Y +15%, không 1:1.
- Owner cho phép R4 provisional thử E0/E1; không cần G2 visual PASS trước desktop E1. `G2_VISUAL=PENDING_OWNER_APPROVAL`; E0 aggregate FAIL/E1 runtime BLOCKED vẫn giữ cho tới correction và evidence được nghiệm thu. Freeze không mở G3.
- Visual sign-off, quyền ảnh/nhãn và fidelity cần đánh giá riêng trước demo/nghiệm thu cuối. Không chạm frozen hash/asset/contract/runtime trong task tài liệu.
- Trước task asset/Blender/P507, đọc [G0 tại PR #13 HEAD](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/c0eff0755d2d058b38944de60f40fb17387f2a91/docs/3d-production/P507-G0-PRODUCTION-SPEC.md) và các report commit-linked trong ROADMAP/STATUS; chúng chưa có trên main. Không commit raw survey/photos/PII; dùng revision và stable IDs, không mở G0-fix chỉ vì bổ sung số đo.

## Kiểm tra tiến độ chỉ đọc trong cuộc chat mới

Repository `duyanhtr130905/DATN-AIRC-WebXR` là entry point để tiếp tục tìm thông tin dự án. Câu kích hoạt mẫu: `Kiểm tra tiến độ mới nhất của dự án tại repo duyanhtr130905/DATN-AIRC-WebXR`.

Yêu cầu chỉ đọc để báo cáo tiến độ không cần phê duyệt task triển khai. Thực hiện ngay các bước sau, không sửa file/GitHub hoặc bắt đầu milestone:

1. Xác minh đúng repository và default branch qua GitHub live; đọc `README.md`, `AGENTS.md`, `docs/ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/02-requirements-kpi.md` và ADR liên quan từ default branch. PR chưa merge chỉ là nội dung đang review, phải tách khỏi tài liệu trên default branch; nếu ROADMAP chưa có thì báo rõ và đọc bản đề xuất trong PR nếu truy cập được.
2. Truy vấn GitHub live main HEAD, PR mới nhất OPEN và MERGED, cùng HEAD/base/merge commit tương ứng; kiểm tra CI/checks theo đúng SHA, trạng thái run/job và các checks đang chờ/thất bại. Không coi synthetic merge SHA của PR là branch HEAD; ghi rõ SHA mà kết quả CI áp dụng, không gán kết quả cũ cho HEAD mới.
3. Truy vấn issues/blockers đang mở, đọc nội dung/thảo luận liên quan và đối chiếu PROJECT_STATUS/ROADMAP/ADR với commit/PR/CI vừa xác minh. Timestamp của tài liệu chỉ cho biết lúc lập snapshot, không chứng minh đó là tiến độ mới nhất. Không suy đoán “latest” từ cache, lịch sử chat, metadata cũ hoặc roadmap PROPOSED.
4. Báo thời điểm kiểm tra và nguồn/link: main HEAD; PR/HEAD/merge và CI; các nhóm **đã merge / đang review / đề xuất chờ duyệt / chưa được triển khai**; blocker; điểm lệch tài liệu so với GitHub; hành động kế tiếp và task đã được phê duyệt nếu có bằng chứng. Nếu chưa có task triển khai được duyệt, ghi rõ điều đó; không tự chọn milestone để làm.
5. Nếu không truy cập được private repository/connector, báo giới hạn và yêu cầu chủ dự án cấp/kết nối quyền truy cập phù hợp. Nếu chỉ kiểm được một phần, nêu rõ phần đã/chưa xác minh; không nhận đã kiểm tra live đầy đủ. Không yêu cầu gửi token/credentials vào chat hoặc Git.

Quy trình này áp dụng cả sau khi PR #12 merge. Một yêu cầu triển khai mới vẫn cần phạm vi được chủ dự án phê duyệt; việc đọc/báo cáo không tự cấp quyền ghi, merge, deploy, sửa KPI hoặc triển khai roadmap.

## Chuẩn sản xuất mô hình P507 sau khi chốt G0

- Với mọi nhiệm vụ liên quan dựng Blender, GLB, camera matching, material/lighting, WebXR asset hoặc survey P507: **phải đọc [P507 G0 Production Specification v1.0](docs/3d-production/P507-G0-PRODUCTION-SPEC.md)** trước khi đặt giả định/viết code. Đây là chuẩn art & quality đã được chủ dự án chốt ngày 16/11/2026; không lặp lại vòng G0-fix chỉ vì có thêm đồ vật hoặc số đo.
- Dữ liệu khảo sát P507 ngày 16/11/2026 do người dùng cung cấp vẫn ở mức USER_REPORTED/PROVISIONAL; **chưa có AIRC quyền lưu/công bố**. File G0 không cấp phép commit raw images chứa người, màn hình, bảng công tác, logo/ảnh bản quyền hoặc chuyển data sang real_verified.
- Inventory là mở. New measurements/objects update survey revision, preserve stable IDs; never rewrite art direction from scratch. Camera matches/Blender exports/software GLB tests don't by themselves satisfy MT1–MT3.
- Câu các nhóm ĐX-P507/ĐX-UX/ĐX-XR còn PROPOSED là **ngữ cảnh lịch sử G0 ngày 16/11/2026**, đã được thay bởi Roadmap 2.0 APPROVED M0–M7 ngày 18/11/2026. G0 riêng không cấp quyền triển khai G1/G2/G3; G2 phải có visual sign-off trước G3, không tự merge hoặc deploy.

## Quy trình

1. Trước mọi task, đọc `docs/ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/02-requirements-kpi.md`, task hiện hành và các ADR liên quan; đọc README để tìm runbook, giữ thay đổi người dùng.
2. Branch theo task; M0-A dùng `docs/m0-foundation`; M0-B1 dùng `feat/m0-b1-renderer-poc`, M0-B2 dùng `feat/m0-b2-app-foundation`; PR vào `main`. Commit nhỏ, mô tả đúng nội dung.
3. Ưu tiên nguồn chính thức; ghi URL, ngày truy cập, phiên bản và giới hạn. Ghi VERIFIED/PROPOSED/BLOCKED/NOT TESTED đúng nghĩa.
4. Chỉ sửa trong phạm vi task. Thay đổi kiến trúc đã duyệt cần ADR và phê duyệt mới; không ghi ACCEPTED khi chưa có người duyệt.
5. Test tương xứng; `node --check tools/webxr-capability-check/checker.js`, `node --test tools/webxr-capability-check/tests/checker.test.cjs`, `python tools/verify_repository.py`, `git diff --check`. Chạy browser smoke khi có môi trường.
6. Không giả mạo kết quả: test mock khác browser thật, emulator khác kính, capability khác AR session. Test không chạy ghi NOT RUN và lý do; thiết bị không có ghi NOT TESTED.
7. Không commit ảnh/người/serial, token, `.env`, raw survey hoặc session có định danh. Cất dữ liệu thực hạn chế quyền ở nơi được AIRC chấp thuận, ngoài Git.
8. Cập nhật status, acceptance, evidence; kiểm tra link, diff và secret trước commit/push. Tạo PR có summary, files, findings, tests, limitations, questions và next milestone proposal. Không tự coi review AI là phê duyệt của giảng viên/người dùng.

## Kiểm tra ứng dụng chính thức

Xem apps/web/README.md và apps/api/README.md. Build/typecheck/unit/browser frontend; ruff/compileall/pytest backend. Test PostgreSQL yêu cầu TEST_DATABASE_URL của database kiểm thử riêng; không dùng SQLite làm bằng chứng PostgreSQL. Không DDL/seed tự động. Khi chưa duyệt schema, migration NOT RUN, không gọi create_all. Giữ regression M0-A và hai PoC.

## Lịch sử quyền triển khai theo task — không cấp quyền tiếp tục

M0-A/B1/B2 và M1-A/B/C đã merge; các giới hạn theo giai đoạn dưới đây giữ ngữ cảnh task lịch sử. Các câu cấm/chưa triển khai M1 trong baseline ở trên không phủ nhận những task M1 đã được phê duyệt và hoàn thành. Phạm vi task mới phải được chủ dự án duyệt riêng; xem ROADMAP/status trước khi diễn giải lịch sử.

## M1-A được phê duyệt

Task M1-A cho phép Catalog rooms/objects, initial Alembic, read-only API và fixture synthetic riêng; branch feat/m1-a-catalog. Không M1-B/C, auth giả, write endpoints, state/session/event schema hoặc scene integration. User task mới thay giới hạn lịch sử chưa M1 ở trên. Không create_all/startup DDL/seed. Migration/seed phải xác nhận DB project dev/test loopback, không DROP/reset hoặc xóa volume. CI PostgreSQL riêng tạo database airc_test_catalog_UUID; TEST_DATABASE_URL chỉ base airc_foundation_test và AIRC_ALLOW_TEST_DATABASES=1. Chạy ruff/compileall/unit và toàn bộ PG migrations/constraints/API tests, giữ M0/PoC/frontend/browser regression.

## M1-B được phê duyệt

Task M1-B cho phép state/history/outbox/cursor, migration0002, internal synthetic service/CLI, readREST/WebSocket vàPG/TCP/concurrency tests. Branch feat/m1-b-state-realtime; không M1-C/publicwrites/authgiả/real507data. Giữ nguyên revision0001; assertion cũ vềhead/tables phải cập nhật đúng0002 nhưng giữ coverage Catalog. PGfaultinjection chỉunique disposable database đãguard, không đụng databasekhác. LocalPG khôngcó ghiBLOCKED, CIphảichạy thật.

## M1-C được phê duyệt

Task15/11/2026 cho phép C1 snapshot scalability →C2 frontend Catalog/state/3D integration →C3 realPG/TCP/Chrome render evidence, mộtbranch feat/m1-c-digital-twin-vertical-slice vàmộtPR cuối. Không chuyển giai đoạn khi gate trước chưaPASS. Mỗi giai đoạn commit/push vàcập nhật docs/18-m1-c-progress.md. Không visitor tracking/publicwrites/auth giả/GLB507/AI/multiinstance/deploy/milestone sau. Giữ protocol1 compatibility hoặc testpolicyđổiwire rõràng; protocol2 explicit opt-in. Synthetic chỉdev/test đãguard, khôngstartupseed/migrations destructive.
