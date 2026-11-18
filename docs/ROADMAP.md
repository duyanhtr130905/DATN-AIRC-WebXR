# Roadmap 2.0 — DATN-AIRC-WebXR

- Roadmap version: `2.0`.
- `plan_status: APPROVED`.
- Ngày phê duyệt: `2026-11-18`.
- Người phê duyệt: **chủ dự án, qua trao đổi ChatGPT** trong yêu cầu Roadmap 2.0 ngày 18/11/2026. Không có URL quyết định chat được cung cấp; không dựng permalink.
- Phạm vi phê duyệt: kế hoạch tám milestone M0–M7 và quy tắc quản lý tiến độ. **Không cấp quyền tự triển khai tất cả feature hoặc tự bắt đầu milestone.**
- GitHub last verified: **2026-11-18 09:57 +07:00 (Asia/Saigon)**; main `e9a72caa084d9f2cbc4af2656b73509ea57b6d4b`; PR #13–#15 và Issues #1–#5 khớp baseline chủ dự án cung cấp.
- Bằng chứng đồng bộ Roadmap 2.0 được theo dõi tại [PR #16](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/16). Trạng thái merge/HEAD là dữ liệu thay đổi theo thời gian: phải kiểm tra GitHub live trước khi kết luận nội dung đã nằm trên `main`; không dùng snapshot trước merge làm trạng thái hiện hành.

## Source of truth và thứ tự ưu tiên

**Tài liệu này là nguồn chính thức, hiện hành và duy nhất của roadmap.** Chỉ có tám milestone cấp dự án M0–M7; không tạo milestone bổ sung hoặc biến work item/checkpoint thành milestone.

1. Quyết định có thẩm quyền mới nhất và task được chủ dự án phê duyệt xác định quyền/phạm vi; ghi thay đổi vào decision log trước triển khai. Quyền AIRC và nghiệm thu học thuật thuộc người có thẩm quyền tương ứng.
2. [Requirements/KPI](02-requirements-kpi.md) giữ các ngưỡng gốc; [ADR-0001 ACCEPTED](decisions/0001-technology-options.md) giữ stack/kiến trúc. Roadmap không tự thay KPI, quyền dữ liệu hay ADR.
3. ROADMAP quản lý milestone, DoD, phụ thuộc và quyết định kế hoạch; [PROJECT_STATUS](PROJECT_STATUS.md) quản lý snapshot, nghiệm thu và GitHub live theo SHA. [AGENTS](../AGENTS.md) quy định thực thi, deviation guard và đồng bộ. README chỉ dẫn đường.
4. Acceptance/evidence/PR/commit là nguồn truy xuất kết quả từng checkpoint; nguồn mới chỉ thay kết luận cũ trong phạm vi được duyệt. Nội dung trên PR chưa merge phải phân biệt với main; tài liệu lịch sử không cấp quyền tiếp tục.

Nếu có xung đột chưa có quyết định, nêu nguồn, thời điểm, tác động và chờ quyết định cần thiết theo AGENTS; không tự chọn cách hiểu hoặc hạ tiêu chí. Không dùng phần trăm tiến độ không có cơ sở.

## Ngữ nghĩa trạng thái

| Chiều | Giá trị và điều kiện |
| --- | --- |
| `plan_status` | `PROPOSED` hoặc `APPROVED`; kế hoạch M0–M7 hiện APPROVED |
| `execution_status` | `PLANNED`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`; phản ánh việc làm/đánh giá, không gộp blocker vào đây |
| `dependency_status` | `NONE`, `PARTIAL`, `BLOCKED`; ghi dependency cụ thể bên cạnh |
| Trạng thái công việc/PR | `IMPLEMENTED` = có source; `TECHNICAL_PASS` = checks xác định trên SHA đạt; `ACCEPTED` = có quyết định nghiệm thu trong phạm vi; `MERGED` = GitHub xác nhận tích hợp; `PARTIAL/FAIL` = thiếu/không đạt tiêu chí |

Draft/open/merged là trạng thái GitHub riêng. Green CI không thay ACCEPTED hoặc MERGED. DONE cần DoD đạt, quyết định nghiệm thu và trạng thái tích hợp rõ ràng; không kết luận chỉ vì có mã. Kết luận review PASS/PARTIAL/FAIL/BLOCKED không thay các enum ba chiều trên.

## Tổng quan tám milestone

Ngày last verified trong bảng là ngày đối chiếu kế hoạch/snapshot, không phải ngày hoàn thành KPI.

| Milestone | Mục tiêu | Plan approval | Execution status | Dependency flag | Dependencies | DoD summary | Evidence/PR | Blockers | Next action | Last verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M0 | Nghiên cứu, lựa chọn công nghệ và nền tảng | APPROVED | DONE | NONE | Đề bài và quyền task M0 | Nghiên cứu, PoC, ADR, foundation đã nghiệm thu/tích hợp | PR #6/#7/#8, acceptance bên dưới | Không còn blocker trong DoD M0; blocker thực địa chuyển tiếp | Bảo toàn lịch sử | 2026-11-18 |
| M1 | Prototype hệ thống và luồng dữ liệu synthetic | APPROVED | DONE | NONE | M0 | Catalog, state/realtime, vertical slice synthetic đã tích hợp | PR #9/#10/#11, acceptance bên dưới | Không phải real Digital Twin hoặc visitor tracking | Tái sử dụng baseline theo task được giao | 2026-11-18 |
| M2 | Prototype 3D tương tác phòng P507 | APPROVED | IN_PROGRESS | PARTIAL | M0 → M1; frozen R4; E0 contract trước E1 | E0 actual checks PASS và browser walkthrough chức năng được nghiệm thu | [#13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13), [#14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14), [#15](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/15); STATUS | E0 aggregate FAIL; E1 runtime BLOCKED | Nghiệm thu/đồng bộ PR tài liệu, rồi task M2 correction E0 → browser E1 | 2026-11-18 |
| M3 | Tích hợp Digital Twin và dữ liệu P507 | APPROVED | PLANNED | BLOCKED | M1, prototype chức năng M2, nguồn/quyền | Stable mapping, 3 trạng thái có nguồn, realtime/freshness, source → UI | Chưa có PR triển khai M3; DoD bên dưới | DEPENDENCY_BLOCKED: #2/#3, chưa đạt M2 | Chốt nguồn/quyền và task tích hợp khi được giao | 2026-11-18 |
| M4 | Lưu vết trải nghiệm và báo cáo phiên | APPROVED | PLANNED | PARTIAL | M1, tương tác, event contract, chính sách dữ liệu | Persistence/recovery/dedupe/export và oracle | Chưa có PR triển khai M4 | Contract/consent/retention chưa chốt | Chuẩn bị thiết kế theo dependency khi được giao | 2026-11-18 |
| M5 | Tích hợp WebXR AR/VR | APPROVED | PLANNED | BLOCKED | Asset/trải nghiệm M2; thiết bị và XR protocol | Lifecycle/interactions/fallback và evidence thiết bị thật | Chưa có PR triển khai M5 | DEVICE_BLOCKED: #4/#5; chưa có evidence kính/AR thật | Chốt thiết bị/protocol và task XR | 2026-11-18 |
| M6 | Mở rộng không gian và nghiệm thu MT1–MT3 | APPROVED | PLANNED | BLOCKED | M3/M4/M5; ≥3 phòng; protocol KPI | Toàn bộ MT1–MT3 có evidence và nghiệm thu | [KPI](02-requirements-kpi.md); chưa có PR M6 | SCOPE_BLOCKED: #1 và dependency dữ liệu/thiết bị/protocol | Xác nhận scope ≥3 phòng và protocol với người có thẩm quyền | 2026-11-18 |
| M7 | Hoàn thiện luận văn, demo và bảo vệ | APPROVED | PLANNED | PARTIAL | Kết quả/evidence các milestone; yêu cầu giảng viên | Luận văn, demo, hướng dẫn, rehearsal/bảo vệ có căn cứ | Chưa có deliverable nghiệm thu M7 | Biểu mẫu/lịch và kết quả M6 chưa sẵn sàng | Dàn ý có thể làm sớm khi được giao | 2026-11-18 |

## Definition of Done có thể kiểm chứng

### M0 — Nghiên cứu, lựa chọn công nghệ và nền tảng (DONE / MERGED)

Giữ nguyên M0-A/B1/B2 theo PR #6/#7/#8: nghiên cứu có nguồn, capability checker và regression; hai PoC renderer synthetic có evidence/browser và giới hạn; ADR-0001 ACCEPTED, foundation và runbooks. DoD/acceptance, commit/CI và quyết định lịch sử được dẫn trong bảng lịch sử bên dưới; không chạy lại hoặc gán metrics cũ sang SHA mới. DONE cho phạm vi M0, không phải KPI sản phẩm.

### M1 — Prototype hệ thống và luồng dữ liệu synthetic (DONE / MERGED)

Giữ M1-A/B/C theo PR #9/#10/#11: Catalog và constraints/migrations được phép, state/realtime/history/outbox, bounded atomic snapshots và vertical slice PostgreSQL → API → browser/scene/panel. Evidence/acceptance lịch sử bên dưới kiểm logic, PostgreSQL/TCP/Chrome theo SHA. **M1 không là real Digital Twin P507; state history không là visitor tracking.**

### M2 — Prototype 3D tương tác phòng P507 (IN_PROGRESS)

Từng tiêu chí cần expected/actual, build/asset SHA hoặc hash, môi trường và kết luận review:

1. Frozen GLB, manifest và source có hash/provenance tái lập được; ghi source SHA khác checkout merge SHA. Dùng R4 provisional đã được owner cho phép cho thử chức năng; không tự thay lock/baseline.
2. E0 validation contract được duyệt; actual geometry, stable ID/ancestor mapping, units/axes, identity transform, floor/room/openings và oriented proxy/spawn/navigation hard checks PASS. Báo pre/post export drift riêng; không tăng tolerance hoặc bỏ lỗi để tuyên bố PASS. Hiện aggregate **FAIL**.
3. E1 thực thi trong Chrome/browser thật, tải asset và render không bị chặn ở E0; test WASD/mouse/reset, lifecycle và collision, ghi rõ tuyến đi được/không đi được. Source/unit PASS riêng không chứng minh walkthrough.
4. Chọn logical ID và Information Panel đúng dữ liệu có provenance; không đếm mesh thành object hoặc gọi metadata provisional là real_verified.
5. Loading/unsupported/error/retry/recovery được kiểm bằng kịch bản expected/actual, có ảnh/log lỗi và kết quả sau recovery.
6. Browser walkthrough có ảnh/video đã sanitize, logs và số đo hiệu năng cơ bản với browser/OS/GPU/viewport/build/asset, raw samples và giới hạn. Review desktop/mobile/fallback trong phạm vi prototype; viewport emulation phải ghi rõ.
7. ChatGPT nghiệm thu độc lập chức năng P507; owner quyết định tích hợp; cập nhật ROADMAP/PROJECT_STATUS cùng PR/HEAD/CI/evidence và trạng thái branch/main.

Evidence hiện có (chỉ trên PR, không nằm trong main): [G0 tại c0eff075](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/c0eff0755d2d058b38944de60f40fb17387f2a91/docs/3d-production/P507-G0-PRODUCTION-SPEC.md), [R4 freeze tại acd21c62](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/acd21c62c24b94d7dda4bbf25c80fe0b4224cc31/docs/3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md), [asset handoff](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/acd21c62c24b94d7dda4bbf25c80fe0b4224cc31/docs/3d-production/P507-WEBXR-ASSET-HANDOFF.md), [E0/E1 report tại 43a38286](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/43a3828654ca90a8a1d1a05750c4f06e36f6bba6/docs/3d-production/P507-WEBXR-E0-E1-EXPERIMENT.md), [TV diagnostic](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/43a3828654ca90a8a1d1a05750c4f06e36f6bba6/docs/3d-production/P507-E0-TV-BOUNDS-DIAGNOSTIC.md). Các evidence chưa đủ nghiệm thu M2; CI hiện hành nằm trong STATUS. Evidence mới sau correction cần gắn đúng HEAD và quyết định nghiệm thu, không chỉ thêm mã.

**M2 không đòi đủ ba phòng, dữ liệu AIRC thật, visitor persistence, headset, VR72 hoặc G2 visual hoàn thiện.** Issue #1 không chặn E0/E1/nghiệm thu prototype chức năng. R4 không là photorealistic hay bản sao AIRC hoàn thiện. `G2_VISUAL=PENDING_OWNER_APPROVAL`; không cần G2 visual PASS trước desktop E1. Visual sign-off, quyền ảnh/nhãn và fidelity đánh giá riêng trước demo/nghiệm thu cuối; không tự mở G3.

### M3 — Tích hợp Digital Twin và dữ liệu P507 (PLANNED)

Mapping stable survey IDs ↔ Catalog/API/Information Panel được kiểm không thiếu/trùng/sai room; nguồn/quyền và owner/cadence/timestamps của room_schedule, equipment_status, exhibit_info được xác nhận. Chạy end-to-end từng loại từ nguồn → API/realtime → UI với raw traces; kiểm freshness/stale/error/reconnect và recovery. Evidence pack gồm source matrix có quyền, mapping revision, test scripts/logs, build SHA và nghiệm thu. Synthetic tiếp tục mang nhãn synthetic, không chuyển thành `real_verified`. M1 generic slice và metadata chọn object của M2 không chứng minh M3 hoàn thành.

### M4 — Lưu vết trải nghiệm và báo cáo phiên (PLANNED)

Visitor session/event contract, schema và quyền ghi/export được duyệt; chính sách consent/identity/retention/xóa rõ trước thu thập. Tests chứng minh persistent storage, retry/dedupe/order/offline/reload/recovery kể cả storage bị chặn/token hết hạn. Oracle event IDs độc lập đối chiếu expected/actual/missing/duplicate; CSV/JSON tái tính từ raw records được. Evidence gồm thiết kế đã duyệt, migration/guard review nếu có, test reports/database traces đã sanitize và mẫu export có nhãn. Không dùng state_history/outbox M1 thay visitor tracking; tỷ lệ ≥99% và ≥50 phiên nghiệm thu đầy đủ tại M6.

### M5 — Tích hợp WebXR AR/VR (PLANNED)

Protocol/thiết bị được duyệt; user gesture/permissions, requestSession, input/navigation/interactions, enter/exit/re-entry/cleanup và denied/unsupported fallback được thử có expected/actual. Chạy AR/VR trên thiết bị thật đã chọn; evidence pack ghi model/OS/browser/XR runtime/build/asset, video/log lifecycle và raw performance/frame timing. Emulator chỉ là evidence phát triển, không thay thiết bị thật hay VR72. Thiếu thiết bị ghi BLOCKED, không tự bỏ KPI.

### M6 — Mở rộng không gian và nghiệm thu MT1–MT3 (PLANNED)

Giảng viên/người có thẩm quyền duyệt scope/protocol; giữ nguyên [toàn bộ KPI và phương pháp](02-requirements-kpi.md). Evidence pack từng KPI phải truy xuất input/script/build/asset/source/device/raw output, kết luận PASS/FAIL/BLOCKED và quyết định nghiệm thu:

- ≥3 phòng thực được xác nhận có quyền và mapping; ≥20 đối tượng tương tác có căn cứ, không đếm mesh/nhân phòng; ≥3 loại trạng thái có nguồn.
- Source → UI latency ≤5s theo protocol/clock uncertainty; không thay ngưỡng mọi mẫu bằng p95 hoặc dùng synthetic CLI làm nguồn AIRC.
- Web3D ≥30 FPS trên workload đại diện; VR mục tiêu ≥72 FPS trên kính thật đã chọn; raw frame samples/thiết bị/môi trường, không lấy software/emulator làm bằng chứng hardware.
- ≥90% tác vụ với ≥15 người đồng thuận theo script/protocol đã duyệt, công khai thất bại/bỏ cuộc.
- MT3 đầy đủ: session/event persistence, recovery; ≥99% unique valid expected events theo oracle độc lập; export ≥50 phiên phân biệt, nhãn synthetic nếu có, không gọi 50 phiên là 50 người.

Không tự thay ngưỡng/phương pháp kiểm chứng trong task này; protocol còn PROPOSED phải được duyệt trước đo nghiệm thu. M6 hội tụ các phần M3/M4/M5; chưa có KPI sản phẩm PASS.

### M7 — Hoàn thiện luận văn, demo và bảo vệ (PLANNED)

Luận văn/sơ đồ/phương pháp/benchmark/phân tích kết quả truy ngược evidence các milestone, ghi giới hạn và phần chưa đạt. Demo script và phương án dự phòng rehearsal được; hướng dẫn chạy/tái lập rõ phiên bản/dữ liệu/quyền, không lộ bí mật. Chủ dự án/giảng viên review theo biểu mẫu/lịch thực được cung cấp và nghiệm thu/nộp/bảo vệ; không tự cam kết deadline hoặc công bố. Evidence: bản tài liệu/version, traceability số liệu, rehearsal logs và quyết định review. Dàn ý có thể làm sớm khi được giao.

## Ma trận phụ thuộc và khả năng chuẩn bị song song

| Đích | Phụ thuộc / điều kiện |
| --- | --- |
| M1 | M0 → M1 |
| M2 | M0 → M1 → M2; E0 đạt trước E1 runtime |
| M3 | M1 + prototype chức năng M2 + quyết định nguồn/quyền (#2/#3) |
| M4 | M1 + luồng tương tác đã có + event contract/chính sách dữ liệu; có thể chuẩn bị song song khi dependency liên quan sẵn sàng và được giao |
| M5 | Asset/trải nghiệm M2 + quyết định thiết bị/XR protocol (#4/#5) |
| M6 | Hội tụ M3/M4/M5 + scope ≥3 phòng (#1) + protocol KPI |
| M7 | Tổng hợp kết quả/evidence các milestone; dàn ý sớm khi được giao |

Không giả định M3/M4/M5 phải code tuần tự tuyệt đối; chuẩn bị song song không tự cấp quyền triển khai hoặc bỏ dependency.

## Ánh xạ kỹ thuật lịch sử G/R/E

| Checkpoint/work item lịch sử | Milestone chịu trách nhiệm | Quyền và giới hạn |
| --- | --- | --- |
| G0 Production specification | M2 | Phương pháp đã chốt; PR #13 OPEN, chưa merge |
| G1 Geometry; G2 Hero lookdev | M2 | Technical geometry/pipeline tách visual approval |
| R1–R4 revisions của G1/G2 | M2 | Giữ nguyên tên/lịch sử; R4 frozen provisional dùng thử chức năng |
| E0 Asset validation; E1 Desktop Web 3D walkthrough | M2 | E0 FAIL, E1 source PARTIAL/runtime BLOCKED; chờ correction task sau nghiệm thu tài liệu |
| G3 Full-room art production | M2 hoặc chuẩn bị fidelity cuối tại M6 | Chỉ khi owner cho phép; không bắt đầu chỉ vì R4 freeze; visual gate riêng |
| G4 WebXR runtime | M5 | Chưa triển khai trong phạm vi M5 |
| G5 Digital Twin mapping/state | M3 | Chưa tích hợp dữ liệu thật P507 |
| E2/E3 nếu được đề xuất | Tên thí nghiệm lịch sử, chưa được giao | Không tạo milestone mới, không mặc nhiên cấp quyền; ánh xạ theo phạm vi trước task |

## Phạm vi P507 và dependency mở

- M2 chỉ prototype **một phòng P507**. Issue #1 vẫn OPEN: **`DEFERRED_FOR_M2; REQUIRED_FOR_M6`**. MT1-01 ≥3 phòng không đổi; không chặn E0/E1 hoặc nghiệm thu chức năng M2, không chia P507 thành ba phòng giả và không tự công nhận MT1-01 PASS.
- Survey baseline **6.00 × 8.10 × 3.50 m**, `USER_REPORTED`; virtual experience **6.90 × 9.315 × 3.50 m**, `OWNER_APPROVED_VIRTUAL_ADAPTATION`; X/Y +15%, chiều cao giữ nguyên. Không phải phòng thật 1:1; R4 chưa được AIRC xác nhận fidelity/quyền.
- #2 survey/inventory: M3 xác thực mapping/dữ liệu và M6 inventory/KPI; M2 dùng provisional có provenance, chưa đóng #2. #3 nguồn/quyền: M3 và quyền dùng dữ liệu/ảnh/nhãn tại demo/nghiệm thu cuối; không có quyền công bố raw photos. #4 AR và #5 VR: M5, evidence KPI tại M6. Cả năm issue vẫn OPEN.
- G3/M3–M7 chưa triển khai trong phạm vi tương ứng. Auth/quyền ghi/consent/retention/hosting và protocol học thuật còn cần quyết định theo task; không mặc định có API AIRC.

## Decision / change log

| Ngày | Quyết định | Thẩm quyền / tác động |
| --- | --- | --- |
| 2026-11-18 | Roadmap 2.0 APPROVED, duy nhất M0–M7 | Chủ dự án qua yêu cầu ChatGPT; thay kế hoạch quản lý PROPOSED ngày 15/11, không đổi lịch sử M0/M1 hoặc tự giao feature |
| 2026-11-18 | M2 P507-only prototype | Owner xác nhận phạm vi; không dùng yêu cầu ba phòng chặn thử chức năng |
| 2026-11-18 | ≥3 rooms deferred tới M6; KPI unchanged | #1 `DEFERRED_FOR_M2; REQUIRED_FOR_M6`, vẫn OPEN |
| 2026-11-18 | R4 provisional được phép thử E0/E1; G2 visual vẫn pending | Xác nhận quyền thử đã có; không cần visual PASS trước E1, không mở G3 hoặc công nhận photorealism |
| 2026-11-18 | TV root cause ACCEPTED theo nghiệm thu ChatGPT được owner thuật lại | Diagnostic không thay E0 FAIL/E1 BLOCKED; Option A/B chưa triển khai, không có permalink chat được cung cấp |
| 2026-11-18 | Post-review progress synchronization bắt buộc | Kể cả PASS/PARTIAL/FAIL/BLOCKED đều cập nhật ROADMAP/STATUS, commit, đọc lại diff/HEAD; phân biệt branch/main |
| 2026-11-18 | Roadmap deviation warning trước phần lệch phạm vi | Theo guard và mẫu trong AGENTS; ngoại lệ được duyệt phải ghi decision log/ROADMAP/STATUS trước triển khai |
| 2026-11-18 | Ủy quyền merge trong lượt nghiệm thu PR hiện tại | Chủ dự án cho phép ChatGPT merge trực tiếp các PR **đủ điều kiện** sau review độc lập, xác minh CI/HEAD/mergeability và không còn blocker; quyền này không cấp cho Codex, không áp dụng vô hạn cho mọi PR tương lai |

Điểm kiểm soát: [PR #16](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/16) dành riêng cho đồng bộ roadmap; phải kiểm tra trạng thái merge thực tế trên GitHub. ChatGPT chỉ được merge PR khi chủ dự án ủy quyền rõ, đã review phạm vi/CI đúng HEAD, giải quyết blocker và xác nhận không làm mất governance; Codex không tự merge. Công việc phát triển tiếp theo vẫn thuộc **M2 — chốt E0 validation contract correction có kiểm soát, rồi browser walkthrough E1 trên frozen R4**, theo task feature được phê duyệt riêng; không tạo milestone mới.

## Lịch sử M0/M1 — giữ nguyên checkpoint và evidence

Bảng M0-A/M0-B/M1/M2/M3/M4 trong charter là **đề xuất lịch sử** tại thời điểm nghiên cứu. M1 ở bảng đó nói về PoC/chọn stack, khác M1-A/B/C thực thi sau này. Không ánh xạ một-một, đổi tên hồi tố hoặc coi toàn bộ bảng lịch sử đã được duyệt. Acceptance và checkpoint cũ giữ nguyên trạng thái tại lúc bàn giao; các câu “chưa merge”, “chưa bắt đầu” không mô tả hiện tại. Xác nhận merge dưới đây dựa trên lịch sử `origin/main` và PR #11 ngày 15/11/2026.

| Mốc thực thi | Mục tiêu và phạm vi đã làm | Phụ thuộc thực tế | Definition of Done / bằng chứng bàn giao | Trạng thái merge |
| --- | --- | --- | --- | --- |
| M0-A | Foundation, nghiên cứu, checklist và capability checker | Repo độc lập và đề bài | Tài liệu/checker/test/PR theo [acceptance](10-m0-acceptance.md); không gỡ blocker thực địa | DONE — [PR #6](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/6), `1a736d5` |
| M0-B1 | Hai PoC renderer synthetic cô lập | M0-A; task cho phép PoC | So sánh A/B, browser/IWER và giới hạn thiết bị theo [acceptance](m0-b1-acceptance.md) | DONE — [PR #7](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/7), `3ebd2ec` |
| M0-B2 | Foundation React XR/FastAPI/PostgreSQL | M0-B1; ADR-0001 ACCEPTED | Nền tảng chính thức, runbooks và regression theo [acceptance](15-m0-b2-acceptance.md) | DONE — [PR #8](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/8), `b4e4b91` |
| M1-A | Catalog rooms/objects, Alembic, read-only API synthetic | M0-B2; task Catalog riêng | Migration/constraints/API trên PostgreSQL và guarded seed theo [acceptance](16-m1-a-catalog-acceptance.md) | DONE — [PR #9](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/9), `99f6537` |
| M1-B | State/history/outbox/cursor, REST/WebSocket synthetic | M1-A; task state/realtime riêng | Transaction/concurrency/replay/guards và PostgreSQL/TCP theo [acceptance](17-m1-b-state-realtime-acceptance.md) | DONE — [PR #10](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/10), `66e1666` |
| M1-C | Synthetic vertical slice PostgreSQL → API → Chrome/R3F/Panel | M1-B; gates C1 → C2 → C3 | Snapshot/adapter/reducer/scene và real PG/TCP/Chrome evidence theo [acceptance](18-m1-c-vertical-slice-acceptance.md) | DONE — [PR #11](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/11), `33ba38b00e2d6c218c1ab97ba1cc7201d1e92a58` |

**M1 chỉ hoàn thành prototype synthetic.** DONE/merge không đồng nghĩa hoàn thành Digital Twin P507 hoặc nghiệm thu MT1–MT3. Primitive layout/20 objects/41 states không là inventory hoặc transform thực địa; history/outbox không là lưu vết khách tham quan. Thông tin chưa khảo sát trong acceptance cũ là AS-OF lúc bàn giao; nguồn P507 hiện có ở mức USER_REPORTED, chưa AIRC verified.


## Lịch sử kế hoạch và mâu thuẫn cố ý bảo lưu

- Bản roadmap ngày 15/11/2026 (PROPOSED) đã được thay bằng 2.0; bản nguyên văn và các nhóm ĐX-UX/P507/XR/TRACE/KPI/REPORT vẫn truy xuất tại [ROADMAP trên main baseline e9a72caa](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/e9a72caa084d9f2cbc4af2656b73509ea57b6d4b/docs/ROADMAP.md). Chúng là lịch sử đề xuất, không phải hệ milestone hiện hành thứ hai. Nội dung tương ứng nay thuộc DoD M2–M7 theo quyết định 18/11.
- Charter M0–M4 là lịch sử; không đổi tên hồi tố. Acceptance M0/M1 giữ nguyên các snapshot IN REVIEW/chưa merge và SHA/metrics; bảng merge lịch sử ở trên cùng STATUS giải thích hiện tại.
- ADR-0001 giữ ACCEPTED stack/kiến trúc/UI; các câu chưa duyệt schema ở foundation phải đọc cùng bổ sung M1-A và acceptance M1-B/C, không suy thành quyền session/production. Không sửa ADR hồi tố.
- Infra runbook còn câu chưa có migration ở foundation; revision 0001/0002 đã có theo API runbook/model. Đây là giới hạn lịch sử; task có DB phải đối chiếu trước thao tác, PR này không sửa runbook/DB.
- Metadata M0-B1/PROPOSED đã được đồng bộ về M2/ACCEPTED trong task này; YAML chỉ là index, không là roadmap hay quyền tự triển khai. Không phát hiện parser/schema/enum consumer trong repository khi quét tracked source/config; giữ nguyên bộ field.
- Các snapshot PR #13–#15 có câu chờ xác nhận/số ghế/layout/CI đang chạy theo thời điểm cũ. Giữ nguyên branch đó; snapshot hiện hành ở STATUS phân biệt owner cho thử chức năng, diagnostic ACCEPTED và visual pending. Mâu thuẫn về quyền AIRC/protocol chưa được quyết định không tự giải quyết bằng tài liệu.
