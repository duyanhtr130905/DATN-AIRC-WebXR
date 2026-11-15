# Roadmap dự án DATN AIRC WebXR

Ngày lập: 15/11/2026. Chủ quyết định: chủ dự án; các quyết định phạm vi học thuật/KPI cần giảng viên xác nhận, quyền dữ liệu cần AIRC xác nhận.

**Trạng thái roadmap chính thức mới: PROPOSED — chờ chủ dự án phê duyệt.** Đây là nơi duy nhất quản lý roadmap hiện hành; chưa phải kế hoạch được phép triển khai. Không có bằng chứng phê duyệt một chuỗi M0–M8. PR tài liệu này không phê duyệt milestone tiếp theo, không bắt đầu M2/M3.

## Nguồn thông tin và cách tiếp tục qua các phiên

| Thông tin | Nguồn chịu trách nhiệm |
| --- | --- |
| Quy tắc làm việc và giới hạn quyền | [AGENTS](../AGENTS.md) và task được chủ dự án phê duyệt |
| Roadmap, phụ thuộc, DoD, đề xuất chờ duyệt | Tài liệu này |
| Trạng thái hiện tại, merge, blocker và bước tiếp | [PROJECT_STATUS](PROJECT_STATUS.md) |
| Phạm vi và KPI gốc | [Charter](01-project-charter.md), [requirements/KPI](02-requirements-kpi.md) |
| Quyết định kiến trúc và baseline | [ADR-0001](decisions/0001-technology-options.md), [kiến trúc](12-official-system-architecture.md), [model](13-data-model.md), [contracts](14-api-contracts.md) |
| Kết quả từng mốc và giới hạn bằng chứng | Acceptance và evidence tương ứng trong bảng bên dưới; PR/commit GitHub để xác minh merge |
| Vấn đề chưa giải quyết | [Backlog](backlog/README.md), Issues #1–#5; nội dung issue cần đọc lại trước task phụ thuộc |

Mỗi phiên phải đọc ROADMAP, PROJECT_STATUS, requirements/KPI và ADR liên quan trước khi làm; kiểm tra Git/PR hiện hành trước ghi. README chỉ dẫn đường, không chứa một roadmap thứ hai. Nếu nguồn mâu thuẫn mà không có cập nhật/phê duyệt rõ ràng, báo chủ dự án kèm nguồn và tác động; không tự chọn nguồn thuận tiện hoặc tự sửa quyết định.

## Roadmap lịch sử và milestone đã thực thi

Bảng M0-A/M0-B/M1/M2/M3/M4 trong charter là **đề xuất lịch sử** tại thời điểm nghiên cứu. M1 ở bảng đó nói về PoC/chọn stack, khác M1-A/B/C thực thi sau này. Không ánh xạ một-một, đổi tên hồi tố hoặc coi toàn bộ bảng lịch sử đã được duyệt. Acceptance và checkpoint cũ giữ nguyên trạng thái tại lúc bàn giao; các câu “chưa merge”, “chưa bắt đầu” không mô tả hiện tại. Xác nhận merge dưới đây dựa trên lịch sử `origin/main` và PR #11 ngày 15/11/2026.

| Mốc thực thi | Mục tiêu và phạm vi đã làm | Phụ thuộc thực tế | Definition of Done / bằng chứng bàn giao | Trạng thái merge |
| --- | --- | --- | --- | --- |
| M0-A | Foundation, nghiên cứu, checklist và capability checker | Repo độc lập và đề bài | Tài liệu/checker/test/PR theo [acceptance](10-m0-acceptance.md); không gỡ blocker thực địa | DONE — [PR #6](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/6), `1a736d5` |
| M0-B1 | Hai PoC renderer synthetic cô lập | M0-A; task cho phép PoC | So sánh A/B, browser/IWER và giới hạn thiết bị theo [acceptance](m0-b1-acceptance.md) | DONE — [PR #7](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/7), `3ebd2ec` |
| M0-B2 | Foundation React XR/FastAPI/PostgreSQL | M0-B1; ADR-0001 ACCEPTED | Nền tảng chính thức, runbooks và regression theo [acceptance](15-m0-b2-acceptance.md) | DONE — [PR #8](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/8), `b4e4b91` |
| M1-A | Catalog rooms/objects, Alembic, read-only API synthetic | M0-B2; task Catalog riêng | Migration/constraints/API trên PostgreSQL và guarded seed theo [acceptance](16-m1-a-catalog-acceptance.md) | DONE — [PR #9](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/9), `99f6537` |
| M1-B | State/history/outbox/cursor, REST/WebSocket synthetic | M1-A; task state/realtime riêng | Transaction/concurrency/replay/guards và PostgreSQL/TCP theo [acceptance](17-m1-b-state-realtime-acceptance.md) | DONE — [PR #10](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/10), `66e1666` |
| M1-C | Synthetic vertical slice PostgreSQL → API → Chrome/R3F/Panel | M1-B; gates C1 → C2 → C3 | Snapshot/adapter/reducer/scene và real PG/TCP/Chrome evidence theo [acceptance](18-m1-c-vertical-slice-acceptance.md) | DONE — [PR #11](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/11), `33ba38b00e2d6c218c1ab97ba1cc7201d1e92a58` |

**M1 chỉ hoàn thành prototype synthetic.** DONE/merge không đồng nghĩa hoàn thành Digital Twin P507 hoặc nghiệm thu MT1–MT3. Primitive layout/20 objects/41 states không là inventory hoặc transform thực địa; history/outbox không là lưu vết khách tham quan. Khảo sát dự kiến 16/11/2026 là thông tin kế hoạch lịch sử, chưa xác nhận đã thực hiện.

## Roadmap mới đề xuất

Các mã ĐX dưới đây chỉ để review, chưa phải tên/mã milestone được phê duyệt. Không đổi tên hoặc nội dung milestone sau duyệt nếu chưa có quyết định mới. Tất cả **PROPOSED / NOT STARTED**; không có deadline hay owner ngoài chủ dự án được mặc định cam kết. Mỗi mốc chỉ chuyển APPROVED khi có người/ngày/tham chiếu phê duyệt và task rõ phạm vi; IN PROGRESS khi được phép bắt đầu; DONE sau nghiệm thu PR và cập nhật status. BLOCKED ghi rõ điều kiện còn thiếu, không thay thế phê duyệt.

### ĐX-UX — UI/UX tham quan

- **Mục tiêu:** hoàn thiện luồng tham quan desktop/mobile dễ hiểu, theo Scene + Information Panel đã duyệt; Guided Tour là chế độ phụ.
- **Phạm vi:** review UI hiện có; wireframe và task flows chọn phòng/object, đọc ba loại trạng thái, loading/error/stale, keyboard/touch và WebGL fallback; đề xuất budget/asset loading. Không tự thay stack/UI direction hoặc tuyên bố usability đạt.
- **Phụ thuộc:** M1-C; [nghiên cứu UX](08-ui-ux-research.md); chủ dự án duyệt người dùng/tác vụ và phạm vi UI. Nội dung/định vị P507 cần ĐX-P507.
- **Definition of Done:** thiết kế và task script được chủ dự án chấp nhận; phần UI được phép triển khai có regression desktop/mobile/keyboard và evidence loading/error/stale; giới hạn accessibility ghi rõ. MT2-05 chỉ kết luận ở ĐX-KPI.
- **Trạng thái:** PROPOSED / NOT STARTED — chờ duyệt thiết kế và task triển khai.

### ĐX-P507 — Khảo sát và tích hợp P507

- **Mục tiêu:** chuyển từ generic synthetic sang không gian P507 có căn cứ, provenance và quyền sử dụng.
- **Phạm vi:** khảo sát theo [checklist](04-airc-survey-checklist.md), inventory/stable IDs, nguồn ba loại trạng thái; đề xuất tọa độ/đơn vị/độ chính xác, Blender → GLB/manifest và mapping Catalog; tích hợp dữ liệu thực chỉ theo task/schema/contract được duyệt. Có thể tách gate khảo sát → duyệt mapping/quyền → tích hợp; không tự coi có API thiết bị hoặc quyền ghi.
- **Phụ thuộc:** [Issues #1–#3](backlog/README.md); lịch/đầu mối/quyền AIRC; quyết định của giảng viên về phạm vi ≥3 phòng; ĐX-UX cho luồng hiển thị. Khảo sát P507 trước không đóng Issue #1.
- **Definition of Done:** gói survey/inventory được người có thẩm quyền xác nhận, provenance và quyền lưu/demo/báo cáo rõ; dữ liệu nhạy cảm ở nơi được phép ngoài Git; mapping asset/ID/transform và budget được duyệt, kiểm tra trên build; ba loại trạng thái có owner/cadence/timestamps và quy trình cập nhật đã duyệt. Phần thiếu ghi blocker; P507 không được đếm thành ba phòng hoặc dùng một mình để nghiệm thu MT1-01.
- **Trạng thái:** PROPOSED / NOT STARTED — dữ liệu, quyền, scope còn BLOCKED; chưa xác nhận khảo sát hoàn thành.

### ĐX-XR — WebXR trên thiết bị tương thích

- **Mục tiêu:** AR/VR có tương tác, vào/thoát/khôi phục an toàn và bằng chứng thiết bị thực.
- **Phạm vi:** preflight, user gesture/permission, input/navigation và nội dung trong XR; unsupported/denied fallback; asset/performance review. Emulator chỉ phục vụ phát triển; không dùng Quick Look thay chứng cứ WebXR.
- **Phụ thuộc:** ĐX-UX, asset đại diện từ ĐX-P507; [Issues #4–#5](backlog/README.md), model/OS/browser cụ thể, kính/lịch mượn và protocol VR được duyệt.
- **Definition of Done:** test scripts được duyệt, chạy AR/VR session thật và tương tác/thoát trên thiết bị đã chọn, ghi build/versions/log và lỗi; blocker thiết bị ghi trung thực. Kết luận 30/72 FPS và MT2 phải dựa ĐX-KPI, không từ emulator/capability.
- **Trạng thái:** PROPOSED / NOT STARTED — Galaxy AR và kính VR vật lý NOT TESTED, phương án VR chờ quyết định.

### ĐX-TRACE — Lưu vết trải nghiệm và báo cáo phiên

- **Mục tiêu:** persistence phiên/sự kiện, recovery sau reload và xuất báo cáo đối chiếu được cho MT3.
- **Phạm vi:** đề xuất schema/contracts session/event, identity/consent, durable queue/ACK/dedupe, recovery, export và xử lý offline/storage bị chặn. Không coi state_history hoặc diagnostics M1-C là visitor tracking.
- **Phụ thuộc:** M1-C, task flows ĐX-UX; chủ dự án duyệt schema/API, quyền truy cập, consent/retention/xóa, lưu trữ và phạm vi báo cáo trước thu thập dữ liệu hoặc migration.
- **Definition of Done:** thiết kế được duyệt, review migration/guards; tests với oracle event ID độc lập cho retry/duplicate/offline/reload, persistence và recovery; xuất ≥50 phiên mẫu có nhãn synthetic nếu mô phỏng và tái tính được. Chỉ nghiệm thu ≥99% theo protocol đã duyệt ở ĐX-KPI; không gọi 50 phiên là 50 người.
- **Trạng thái:** PROPOSED / NOT STARTED — schema/session policy chưa duyệt, visitor persistence chưa triển khai.

### ĐX-KPI — Kiểm thử và nghiệm thu MT1–MT3

- **Mục tiêu:** tạo evidence pack sản phẩm thật theo nguyên các yêu cầu trong [requirements/KPI](02-requirements-kpi.md).
- **Phạm vi:** traceability từng KPI, workload/thiết bị/build, source → render gồm clock uncertainty; Web 3D ≥30 FPS, VR ≥72 FPS trên kính chọn; ≥90% tác vụ với ≥15 người; recovery, ≥99% event và ≥50 phiên. Kiểm tra ≥3 phòng, ≥20 đối tượng, ≥3 loại trạng thái bằng dữ liệu/nguồn có quyền.
- **Phụ thuộc:** các mốc liên quan ở trên; giải quyết scope phòng; giảng viên duyệt protocol và ranh giới nguồn/timestamps, tuyển người/consent, thiết bị, môi trường chạy và quyền dữ liệu. Hosting/deploy nếu cần phải được duyệt riêng.
- **Definition of Done:** báo cáo từng KPI PASS/FAIL/BLOCKED với raw evidence có sanitize, oracle/cấu hình/build SHA và phương pháp tái lập; người có thẩm quyền nghiệm thu, các thiếu hụt công khai và có quyết định xử lý. Không dùng p95 thay ngưỡng mọi mẫu ≤5 giây, không dùng CI synthetic làm sản phẩm thật.
- **Trạng thái:** PROPOSED / NOT STARTED — MT1–MT3 chưa được nghiệm thu trên sản phẩm thật; protocol còn chờ duyệt.

### ĐX-REPORT — Báo cáo và bảo vệ

- **Mục tiêu:** bàn giao luận văn, demo và tài liệu bảo vệ có căn cứ, phân biệt kết quả đạt và hạn chế.
- **Phạm vi:** cấu trúc báo cáo/slide/demo script, kiến trúc, phương pháp/metrics, kết quả và giới hạn; hướng dẫn tái lập, provenance/license, kế hoạch demo dự phòng và bàn giao.
- **Phụ thuộc:** yêu cầu biểu mẫu/lịch của giảng viên; kết quả ĐX-KPI và evidence các mốc; quyền đưa dữ liệu/hình vào báo cáo. Có thể chuẩn bị dàn ý sớm nếu được giao riêng.
- **Definition of Done:** bộ tài liệu đúng yêu cầu được chủ dự án review, số liệu truy ngược evidence/build; demo rehearsal và giới hạn ghi rõ; chủ dự án/giảng viên quyết định nghiệm thu/nộp. Không tự nộp hoặc công bố.
- **Trạng thái:** PROPOSED / NOT STARTED — lịch/biểu mẫu/nghiệm thu chưa xác nhận; tháng 4/2027 trong charter chỉ là dự kiến.

Thứ tự đề xuất: duyệt task UI/UX và chuẩn bị survey P507; survey/quyền → mapping/asset tích hợp; XR và TRACE có thể lập kế hoạch theo phụ thuộc; kết quả hội tụ tại KPI → báo cáo/bảo vệ. Đây không phải quyền thực hiện song song hoặc giao việc tự động.

## Quyết định cần chủ dự án phê duyệt

| Quyết định | Người cần xác nhận / điều kiện |
| --- | --- |
| Chấp nhận/sửa roadmap; tên/mã, thứ tự, owner, phạm vi và task tiếp theo | Chủ dự án; ghi ngày và tham chiếu phê duyệt vào ROADMAP/status trước triển khai |
| P507 trước và cách giải quyết KPI ≥3 phòng | Chủ dự án + giảng viên/AIRC; giữ nguyên KPI đến quyết định chính thức, không chia P507 thành ba phòng |
| Lịch/đầu mối survey, độ chính xác, inventory, quyền đo/chụp/lưu/demo/báo cáo | Chủ dự án + AIRC/giảng viên; kế hoạch khảo sát không phải bằng chứng đã xong |
| Nguồn/owner/cadence ba loại trạng thái; thủ công hay tích hợp; t_source để đo ≤5s | AIRC + giảng viên/chủ dự án; không giả định có phần mềm/API thiết bị |
| Phạm vi UI/UX, asset budget, metadata/transform và thay đổi schema/contracts nếu cần | Chủ dự án; giữ ADR-0001, thay đổi kiến trúc cần ADR mới |
| Thiết bị AR/VR, lịch mượn kính và protocol nghiệm thu, phương án khi thiếu kính | Chủ dự án + giảng viên; emulator không thay 72 FPS thực |
| Session identity, auth/quyền ghi/export, consent, retention/xóa, hosting | Chủ dự án/người chịu trách nhiệm dữ liệu; chưa có phê duyệt production hoặc thu thập visitor |
| Protocol KPI, ≥15 người, ≥50 phiên, biểu mẫu và lịch bảo vệ | Chủ dự án + giảng viên; không tự cam kết thời gian của bên khác |

## Mâu thuẫn và giới hạn đã ghi nhận

- Charter M1 lịch sử khác M1-A/B/C thực thi; giữ cả hai với ngữ cảnh, không đổi milestone hồi tố.
- Acceptance/checkpoint M1-C còn IN REVIEW tại lúc bàn giao; trạng thái hiện tại đã DONE/merge theo PR #11. Không sửa snapshot hoặc gán metrics source `09f3e23` sang HEAD `4301be4` hay merge `33ba38b`.
- ADR-0001 có phần schema/contracts chưa duyệt từ foundation và bổ sung Catalog M1-A; state/realtime M1-B và slice M1-C được cho phép theo task riêng, ghi tại docs13/14 và acceptance. Không diễn giải thành phê duyệt toàn bộ schema/session/production. Nếu task mới cần mở rộng, báo chủ dự án để chốt phạm vi/ADR.
- `.techlead/project.yaml` còn milestone M0-B1/stack PROPOSED/ready-for-review; đây là metadata lịch sử chưa được đồng bộ, không dùng làm hiện trạng hoặc quyền tiếp tục. Task này chỉ sửa bốn tài liệu; cập nhật metadata cần task được chủ dự án duyệt.
- Infra runbook còn câu migration chưa có revision của M0-B2; revision 0001/0002 thực tế được ghi ở model/API runbook. Không chạy migration từ câu lịch sử; task có DB phải báo và đối chiếu hướng dẫn trước thao tác. PR này không sửa runbook lịch sử hoặc DB.
- Chưa có bằng chứng P507 hoàn tất survey, inventory/quyền/GLB thật hoặc nghiệm thu MT1–MT3. Issues #1–#5 còn mở qua truy vấn GitHub ngày 15/11/2026. Không đóng issue chỉ vì roadmap được lập.
