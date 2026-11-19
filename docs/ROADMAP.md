# Roadmap 2.0 — DATN-AIRC-WebXR

**Nghiệm thu độc lập PR #28 — 19/11/2026 (PARTIAL / CORRECTION REQUIRED):** [Review #5974447677](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28#pullrequestreview-5974447677) đúng HEAD `3621e5bca9b6de5242e995837bf1c73638df1df3`: 49 web + 75 API unit + 83 PostgreSQL PASS và oracle 50 phiên/1.000 sự kiện synthetic đối chiếu DB/CSV/JSON; **lỗi chặn merge**: kết thúc phiên không cho mở phiên mới mà giữ lịch sử (UI chỉ còn thao tác xóa). PR #28 vẫn Draft, M4 `IN_REVIEW/PARTIAL`; Codex sửa và thêm API/Chrome E2E vào **cùng PR**, ChatGPT kiểm SHA và CI mới trước mọi merge. Consent/retention/real visitor policy vẫn BLOCKED, M6 KPI chưa PASS, M5 PLANNED.

**M4 (19/11/2026, nhánh triển khai):** Chủ dự án đã giao phần kỹ thuật synthetic/local-only qua [Issue #27](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/27). M4 IN_REVIEW trên nhánh triển khai, policy người tham quan thật BLOCKED. Xem [runbook và bằng chứng](m4/VISITOR-SESSIONS.md). M3 #2/#3 vẫn mở. Xem [quyết định phạm vi](decisions/0002-m4-synthetic-visitor-scope.md).

- Roadmap version: `2.0`.
- `plan_status: APPROVED`.
- Ngày phê duyệt: `2026-11-18`.
- Người phê duyệt: **chủ dự án, qua trao đổi ChatGPT** trong yêu cầu Roadmap 2.0 ngày 18/11/2026. Không có URL quyết định chat được cung cấp; không dựng permalink.
- Phạm vi phê duyệt: kế hoạch tám milestone M0–M7 và quy tắc quản lý tiến độ. **Không cấp quyền tự triển khai tất cả feature hoặc tự bắt đầu milestone.**
- GitHub live **19/11/2026**: [PR #26 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/26), baseline main cho M4 `ae21efd2359779aa5bc6a889624a4705cd830ee1`. Snapshot nghiệm thu PR #25: M3 candidate head `a7acadc951ab554360606d324cc427da354ec090` được ChatGPT nghiệm thu kỹ thuật độc lập ([review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#pullrequestreview-5971384295)), GitHub 13 SUCCESS (2 status-only) + 2 privileged SKIPPED + 0 FAIL, PostgreSQL 76/76 và Chrome synthetic DOM fallback CI. [PR #25 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) vào main merge `ba5139d34de1454029d9b71958123f2d5aec1375`. **M3 technical Admin/manual-first ACCEPTED nhưng full milestone IN_PROGRESS / BLOCKED #2/#3** vì thiếu dữ liệu thật và quyền công bố; M4 IN_REVIEW trên nhánh được giao qua #27, M5–M7 PLANNED. #20 visual deferred, #22 vault App privileged CI chưa chạy. Lịch sử M2/PR cũ là AS-OF.
- Roadmap 2.0 đã được nghiệm thu/merge qua [PR #16](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/16) tại `0efaf50a845091d3e6ac14bb0d7cf5f7963d701c`; G0 specification đã merge qua [PR #13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13) tại `cce30c06baa3dd2254a8b75c5c982f0900ef29f2`. Trạng thái branch/main vẫn phải xác minh GitHub live trước mỗi nhiệm vụ.

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
| M2 | Prototype 3D tương tác phòng P507 | APPROVED | DONE | NONE_IN_APPROVED_DOD | M0 → M1; frozen R4; E0 trước E1 | 7/7 DoD prototype chức năng đã được ChatGPT review ở đúng HEAD và merge; không chứng nhận fidelity/hardware/XR | [PR #24 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) head `b0a4e0f6`, merge `0b727a06`; [M2 final matrix](3d-production/P507-M2-FINAL-ACCEPTANCE.md); [PR #21](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21), [PR #23](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/23) | #22 OPEN: App CI chưa chạy/thực hiện quyền; #20 DEFERRED: lối ghế, kích thước/vị trí, G1_CIRCULATION PARTIAL, G2_VISUAL PENDING; physical-mobile/GPU30/VR72 và AIRC real data chưa nghiệm thu | M3 technical slice đã MERGED qua PR #25 (full field DoD còn BLOCKED #2/#3); #22 giữ OPEN, không tự mở M4 | 2026-11-19 |
| M3 | Tích hợp Digital Twin và dữ liệu P507 | APPROVED | IN_PROGRESS | BLOCKED | M1/M2 DONE; manual-first Admin được owner duyệt; quyền/nguồn thực #2/#3 | Stable mapping, 3 trạng thái có nguồn thật, realtime/freshness, source → UI và evidence/quyền | [PR #25 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) head `a7acadc9`, merge `ba5139d3`; [independent review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#pullrequestreview-5971384295); [M3 acceptance](m3/P507-M3-INTEGRATION.md) | TECHNICAL_ACCEPTED 121/121 mapping, Admin auth/private Catalog/3 synthetic state types, populated 0002→0004 upgrade, private multi-tab sync; **FULL_DOD_BLOCKED #2/#3** (inventory nhỏ, ba quan sát thật, cadence và disclosure quyền chưa có) | Owner bổ sung field evidence/permission; nghiệm thu nguồn → UI thực trước M3 DONE. Phần kỹ thuật M4 đã được giao riêng qua #27 | 2026-11-19 |
| M4 | Lưu vết trải nghiệm và báo cáo phiên | APPROVED | IN_REVIEW | BLOCKED | M1, tương tác synthetic, chính sách dữ liệu thật | Persistence/recovery/dedupe/export và oracle | [Issue #27](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/27), [Draft PR #28](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28), [independent review PARTIAL](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28#pullrequestreview-5974447677) | Kỹ thuật: chưa thể mở phiên mới sau khi end mà giữ phiên cũ; người thật: consent/retention/quyền chưa duyệt | Codex sửa lifecycle + API/Chrome E2E trên cùng PR, cung cấp HEAD/CI mới để review; chưa merge/M5 | 2026-11-19 |
| M5 | Tích hợp WebXR AR/VR | APPROVED | PLANNED | BLOCKED | Asset/trải nghiệm M2; thiết bị và XR protocol | Lifecycle/interactions/fallback và evidence thiết bị thật | Chưa có PR triển khai M5 | DEVICE_BLOCKED: #4/#5; chưa có evidence kính/AR thật | Chốt thiết bị/protocol và task XR | 2026-11-18 |
| M6 | Mở rộng không gian và nghiệm thu MT1–MT3 | APPROVED | PLANNED | BLOCKED | M3/M4/M5; ≥3 phòng; protocol KPI | Toàn bộ MT1–MT3 có evidence và nghiệm thu | [KPI](02-requirements-kpi.md); chưa có PR M6 | SCOPE_BLOCKED: #1 và dependency dữ liệu/thiết bị/protocol | Xác nhận scope ≥3 phòng và protocol với người có thẩm quyền | 2026-11-18 |
| M7 | Hoàn thiện luận văn, demo và bảo vệ | APPROVED | PLANNED | PARTIAL | Kết quả/evidence các milestone; yêu cầu giảng viên | Luận văn, demo, hướng dẫn, rehearsal/bảo vệ có căn cứ | Chưa có deliverable nghiệm thu M7 | Biểu mẫu/lịch và kết quả M6 chưa sẵn sàng | Dàn ý có thể làm sớm khi được giao | 2026-11-18 |

## Definition of Done có thể kiểm chứng

### M0 — Nghiên cứu, lựa chọn công nghệ và nền tảng (DONE / MERGED)

Giữ nguyên M0-A/B1/B2 theo PR #6/#7/#8: nghiên cứu có nguồn, capability checker và regression; hai PoC renderer synthetic có evidence/browser và giới hạn; ADR-0001 ACCEPTED, foundation và runbooks. DoD/acceptance, commit/CI và quyết định lịch sử được dẫn trong bảng lịch sử bên dưới; không chạy lại hoặc gán metrics cũ sang SHA mới. DONE cho phạm vi M0, không phải KPI sản phẩm.

### M1 — Prototype hệ thống và luồng dữ liệu synthetic (DONE / MERGED)

Giữ M1-A/B/C theo PR #9/#10/#11: Catalog và constraints/migrations được phép, state/realtime/history/outbox, bounded atomic snapshots và vertical slice PostgreSQL → API → browser/scene/panel. Evidence/acceptance lịch sử bên dưới kiểm logic, PostgreSQL/TCP/Chrome theo SHA. **M1 không là real Digital Twin P507; state history không là visitor tracking.**

### M2 — Prototype 3D tương tác phòng P507 (DONE — FUNCTIONAL PROTOTYPE SCOPE, 2026-11-19)

**CURRENT — ACCEPTED (2026-11-19):** [PR #24](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) MERGED vào main tại `0b727a06aef0773063dd4427a066054a3a87cd7d` sau độc lập review HEAD `b0a4e0f6f8d48053a470cbf5f20f9f44e5bc7d45`. **7/7 M2 DoD đạt trong phạm vi một prototype P507 tương tác**, theo [M2 FINAL ACCEPTANCE MATRIX](3d-production/P507-M2-FINAL-ACCEPTANCE.md): vault owner-local original restore, E0 contract/121 IDs, E1 Chrome 15/15, selection/panel provisional, error/recovery, desktop/responsive/fallback evidence và ChatGPT nghiệm thu. CI tại HEAD: **13 SUCCESS (2 chỉ báo status) + 2 privileged App SKIPPED; 0 FAIL**; không gọi App token restore PASS. Ảnh/bộ bằng chứng Windows final HEAD được Codex lưu local và đưa báo cáo định lượng trong PR; reviewer không trực tiếp xem ảnh của gói local final. #22 vận hành CI vẫn OPEN, #20 owner-deferred; `G1_CIRCULATION=PARTIAL`, `G2_VISUAL=PENDING_OWNER_APPROVAL`; không ký nghiệm thu 1:1, physical phone/touch, GPU30/VR72 hay nguồn AIRC thực. **M3 chưa bắt đầu; #2/#3 vẫn blocked và cần giao task riêng.**

**AS-OF trước PR #24 (lịch sử):**

**CURRENT (sau PR #21):** P507 R4/E0/E1 đã nằm trên `main` ở `42a34979`. E0 reference và Chrome E1 15/15 smoke PASS trong phạm vi PR #21, owner-private vault remote restore đã được Codex xác minh bằng evidence và GitHub xác nhận object archive tồn tại trong PRIVATE repo. **Không** công nhận G2 visual/fidelity, full circulation, 30FPS/VR72/mobile/XR hay MT1–MT3. CI post-expiry [#22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) còn BLOCKED, R4 vẫn provisional; M2 chưa DONE.

**AS-OF trước nghiệm thu 19/11:** PR #24 từng là Draft closure candidate. Đã được đánh giá/merge; trạng thái hiện hành ở đoạn CURRENT phía trên. #22 App activation vẫn chưa hoàn thành, #20 vẫn hoãn.

**Definition of Done M2 bên dưới vẫn hiện hành.** Những đoạn mô tả PR #21 còn Draft/chưa có trên main trong phần giải trình cũ là **snapshot AS-OF trước merge**, không phải trạng thái hiện tại.

Từng tiêu chí cần expected/actual, build/asset SHA hoặc hash, môi trường và kết luận review:

1. Frozen GLB, manifest và source có hash/provenance tái lập được; ghi source SHA khác checkout merge SHA. Dùng R4 provisional đã được owner cho phép cho thử chức năng; không tự thay lock/baseline.
2. E0 validation contract được duyệt; actual geometry, stable ID/ancestor mapping, units/axes, identity transform, floor/room/openings và oriented proxy/spawn/navigation hard checks PASS. Báo pre/post export drift riêng; không tăng tolerance hoặc bỏ lỗi để tuyên bố PASS. Source PR #15 scoped TECHNICAL_PASS; integration E0 actual Chrome PASS on clean `69176aa`, final HEAD evidence linked below.
3. E1 thực thi trong Chrome/browser thật, tải asset và render không bị chặn ở E0; test WASD/mouse/reset, lifecycle và collision, ghi rõ tuyến đi được/không đi được. Source/unit PASS riêng không chứng minh walkthrough.
4. Chọn logical ID và Information Panel đúng dữ liệu có provenance; không đếm mesh thành object hoặc gọi metadata provisional là real_verified.
5. Loading/unsupported/error/retry/recovery được kiểm bằng kịch bản expected/actual, có ảnh/log lỗi và kết quả sau recovery.
6. Browser walkthrough có ảnh/video đã sanitize, logs và số đo hiệu năng cơ bản với browser/OS/GPU/viewport/build/asset, raw samples và giới hạn. Review desktop/mobile/fallback trong phạm vi prototype; viewport emulation phải ghi rõ.
7. ChatGPT nghiệm thu độc lập chức năng P507; owner quyết định tích hợp; cập nhật ROADMAP/PROJECT_STATUS cùng PR/HEAD/CI/evidence và trạng thái branch/main.

AS-OF trước PR #21, bằng chứng tại thời điểm đó: G0 đã merge; R4 và E0/E1 từng chỉ có trên PR chưa merge: [G0 tại c0eff075](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/c0eff0755d2d058b38944de60f40fb17387f2a91/docs/3d-production/P507-G0-PRODUCTION-SPEC.md), [R4 freeze tại acd21c62](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/acd21c62c24b94d7dda4bbf25c80fe0b4224cc31/docs/3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md), [asset handoff](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/acd21c62c24b94d7dda4bbf25c80fe0b4224cc31/docs/3d-production/P507-WEBXR-ASSET-HANDOFF.md), [E0/E1 report tại 43a38286](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/43a3828654ca90a8a1d1a05750c4f06e36f6bba6/docs/3d-production/P507-WEBXR-E0-E1-EXPERIMENT.md), [TV diagnostic](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/43a3828654ca90a8a1d1a05750c4f06e36f6bba6/docs/3d-production/P507-E0-TV-BOUNDS-DIAGNOSTIC.md). Các evidence chưa đủ nghiệm thu M2; CI hiện hành nằm trong STATUS. Evidence mới sau correction cần gắn đúng HEAD và quyết định nghiệm thu, không chỉ thêm mã.

**M2 không đòi đủ ba phòng, dữ liệu AIRC thật, visitor persistence, headset, VR72 hoặc G2 visual hoàn thiện.** Issue #1 không chặn E0/E1/nghiệm thu prototype chức năng. R4 không là photorealistic hay bản sao AIRC hoàn thiện. `G2_VISUAL=PENDING_OWNER_APPROVAL`; không cần G2 visual PASS trước desktop E1. Visual sign-off, quyền ảnh/nhãn và fidelity đánh giá riêng trước demo/nghiệm thu cuối; không tự mở G3.

#### AS-OF 18/11 trước merge — M2 integration work item #19 (historical)

Owner explicitly approved [Issue #19](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/19): integrate reviewed R4/E0/E1 into a new branch from main `458569026edc917fa38d945ecd190bd4574b925f`, fix diagnostic exit status, verify offline demo and update current progress in this same PR. Branch `integrate/m2-p507-issue-19`, history-preserving merge `3f06344`; [Draft PR #21](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21)/final HEAD/checks linked from [integration evidence](3d-production/P507-M2-INTEGRATION-19.md). Source #14 `acd21c62` and #15 `c3c8002` remain Draft and unchanged. Main does not yet contain this feature.

Integration IN_REVIEW; initial 76 G1/G2 +18 E0/diagnostic/reference Python and frozen six hashes PASS, clean `69176aa` local E0 Chrome PASS and E1 15/15 PASS; final HEAD/CI results are recorded in Draft PR #21 and the integration report. Reviewed #15 scoped E0/E1 technical acceptance remains historical source evidence, not final integration certification. Diagnostic negative regression rejects final ROOT_CAUSE_UNRESOLVED; real same-version CLI CI [44247798568](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44247798568) confirms exit0 for matching and exit1 for both Three mismatches on clean `69176aa`. Current [runbook](../experiments/p507-webxr/README.md) opens standalone Vite E1 without M1 backend. Original artifact expires 24/11/2026 14:46:36 Asia/Saigon; authorized permanent storage absent, durable reproducibility BLOCKED pending owner decision. See report for exact tests and M2 DoD assessment.

Owner-deferred [Issue #20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) retains chair-row circulation, dimensions and placement discrepancies. No frozen source/asset lock/survey/collision modification permitted. G1_CIRCULATION=PARTIAL; G2_VISUAL=PENDING_OWNER_APPROVAL; no physical-GPU30/VR72 acceptance. **M2 remains IN_PROGRESS**, Roadmap 2.0 APPROVED with exactly M0–M7; M3–M7 states/dependencies unchanged. Independent ChatGPT review is the next gate; Codex stops at Draft PR.

#### Owner-approved R4 preservation — 18/11/2026

[Decision](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21#issuecomment-6973024761) permits separate PRIVATE owner vault and clean independent restore within current M2/#19, same Draft PR21. Original ZIP11369216bytes/SHA256 `4255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8` preserved at [vault](https://github.com/duyanhtr130905/DATN-AIRC-WebXR-asset-vault) commit `908a5cbb1f77b75b28666fd424cbd85f2aba4c1f`; six frozen hashes unchanged, privacy checked before/after upload. [Restore evidence](3d-production/P507-R4-PRESERVATION.md) records runbook/tests and exact final HEAD via PR21. Earlier absent-storage statements are AS-OF before this approval; independent owner remote restore PASS at clean `193720b` (archive/all28members/six hashes/reference/E0/E1 15groups), numeric evidence in linked report. Final documentation HEAD repeats restore and CI, exact SHA/results in PR21. CI cross-repo remains BLOCKED without separately approved credential/access; no PAT/secret granted, original CI artifact expires24/11/2026. M2 IN_PROGRESS, #20 DEFERRED, circulation PARTIAL/visual PENDING; M3–M7 dependencies unchanged. Existing corrected M2 dependency row retained. Next independent ChatGPT review; no autonomous merge/M3.

#### AS-OF trước merge PR #24 — Issue22 secure private-vault CI, 18/11/2026

Owner authorized implementation/tests/runbook/Draft PR, not App/PAT/secrets/grants. New branch `feat/m2-secure-vault-ci-22` from main42a34979; reviewed PR23 snapshot0f63a671 preserved/reconciled while PR23 remains Draft, not merged. PR21 MERGED/#19 CLOSED; #22 current. [Security/functional report](3d-production/P507-ISSUE22-SECURE-CI.md) records separate App identity/selected installation/Contents-read token, main-only protected environment, immutable restore and no artifact fallback. **App CI actual proof BLOCKED / SECURITY_APPROVAL_REQUIRED**; credentials/protected environment not configured. Legacy actual Chrome checks do not close this gate. Exact final HEAD/checks/evidence in [Draft PR24](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24); owner-remote checkpoint6ed7c82 E0/E1 15/15 and responsive390/768 PASS (not App proof); precommit30Python+13Node security tests PASS, responsive emulation rendering PASS, full mobile navigation PARTIAL, no physical-device/GPU KPI certification. M2 stays IN_PROGRESS, #20 DEFERRED/circulation PARTIAL/visual PENDING, M3 PLANNED/DEPENDENCY_BLOCKED; M3–M7 states/dependencies and existing DoD unchanged. Next security review then owner-only configuration approval, no autonomous merge/M3.

### M3 — Tích hợp Digital Twin và dữ liệu P507 (IN_PROGRESS — technical accepted / field blocked)

Mapping stable survey IDs ↔ Catalog/API/Information Panel được kiểm không thiếu/trùng/sai room; nguồn/quyền và owner/cadence/timestamps của room_schedule, equipment_status, exhibit_info được xác nhận. Chạy end-to-end từng loại từ nguồn → API/realtime → UI với raw traces; kiểm freshness/stale/error/reconnect và recovery. Evidence pack gồm source matrix có quyền, mapping revision, test scripts/logs, build SHA và nghiệm thu. Synthetic tiếp tục mang nhãn synthetic, không chuyển thành `real_verified`. M1 generic slice và metadata chọn object của M2 không chứng minh M3 hoàn thành.

**Quyết định hiện hành của chủ dự án — 2026-11-19.** Ưu tiên hoàn thiện và nghiệm thu M3. Hoãn demo tham quan hoàn chỉnh sang M4/M5 theo phạm vi được duyệt riêng. M3 giữ IN_PROGRESS/BLOCKED cho đến khi đủ inventory thực, nguồn và quyền #2/#3, cùng trace nguồn → UI. DoD và KPI giữ nguyên.

**Current implementation decision (2026-11-19):** Owner-authorized [PR #25](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) has MERGED at `ba5139d34de1454029d9b71958123f2d5aec1375` after independent technical [review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#pullrequestreview-5971384295) of exact head `a7acadc951ab554360606d324cc427da354ec090`. Admin manual-first (protected login, private Catalog, provenance, three state types, State/History/Outbox/WS, two-tab invalidation) is **TECHNICAL_ACCEPTED in synthetic/provisional local scope**, not M3 full DoD. 121 placed R4 IDs stay mapped. Existing [source matrix](m3/P507-DATA-SOURCE-MATRIX.md) distinguishes fixture from owner-entered data. Inventory of small items, representative real entries for all three types, manual operating cadence, confirmed provenance/permission to use in demo/thesis or publish, and real source→UI traces are **PENDING (#2/#3)**. Not real_verified, no source-to-render KPI claim, no deployment in the PR #25 scope.

### M4 — Lưu vết trải nghiệm và báo cáo phiên (IN_REVIEW)

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
| M2 | M0 → M1 → M2; M2 DONE trong phạm vi prototype chức năng qua PR #24. #20 deferred và #22 OPEN riêng |
| M3 | M1 + prototype chức năng M2 + quyết định nguồn/quyền (#2/#3) |
| M4 | M1 + luồng tương tác đã có + event contract/chính sách dữ liệu; có thể chuẩn bị song song khi dependency liên quan sẵn sàng và được giao |
| M5 | Asset/trải nghiệm M2 + quyết định thiết bị/XR protocol (#4/#5) |
| M6 | Hội tụ M3/M4/M5 + scope ≥3 phòng (#1) + protocol KPI |
| M7 | Tổng hợp kết quả/evidence các milestone; dàn ý sớm khi được giao |

Không giả định M3/M4/M5 phải code tuần tự tuyệt đối; chuẩn bị song song không tự cấp quyền triển khai hoặc bỏ dependency.

## Ánh xạ kỹ thuật lịch sử G/R/E

| Checkpoint/work item lịch sử | Milestone chịu trách nhiệm | Quyền và giới hạn |
| --- | --- | --- |
| G0 Production specification | M2 | Phương pháp đã chốt; PR #13 MERGED, `cce30c06` (không phải G2_VISUAL PASS) |
| G1 Geometry; G2 Hero lookdev | M2 | Technical geometry/pipeline tách visual approval |
| R1–R4 revisions của G1/G2 | M2 | Giữ nguyên tên/lịch sử; R4 frozen provisional dùng thử chức năng |
| E0 Asset validation; E1 Desktop Web 3D walkthrough | M2 | TECHNICAL_PASS theo review ChatGPT trên PR #15 HEAD `c3c8002`: E0 PASS, E1 Chrome 15 nhóm smoke PASS, 5/5 CI PASS. PR Draft/chưa MERGED; không suy ra M2 DONE, KPI hoặc G2 visual PASS |
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
| 2026-11-18 | ChatGPT nghiệm thu và merge PR #16, PR #13, đồng bộ PR #17 | Roadmap 2.0 MERGED `0efaf50a`; G0 spec MERGED `cce30c06`; status sync MERGED `2deb9267`. Dòng E0_FAIL/E1_BLOCKED phản ánh **thời điểm trước correction**, không còn là kết quả mới nhất của PR #15; G2 visual vẫn pending, M2 chưa DONE |
| 2026-11-18 | ChatGPT nghiệm thu kỹ thuật E0/E1 trên PR #15 HEAD `c3c8002` | E0 reference frozen SHA-bound / 1mm proxy, 3mm bounds PASS; 15 nhóm Chrome smoke E1 PASS; 5/5 checks CI PASS. Draft PR #15 chưa merge, PR #14 vẫn Draft. Ghi lỗi phụ diagnostic runner có thể exit 0 khi Three mismatch, cần sửa/test trước khi chứng nhận pipeline toàn diện. Tiếp theo: review demo/visual và reconciliation không ghi đè roadmap |

| 2026-11-18 | ChatGPT review kỹ thuật PR #21 tại `a0b91a8` | 12/12 exact-head CI SUCCESS; R4 lock, G1/G2 source và E0/E1 runtime giữ nguyên; diagnostic exit lỗi âm tính đã sửa, Chrome E1 15/15 PASS. **Kết luận: TECHNICAL_PASS phạm vi tích hợp, PR tổng thể PARTIAL/IN_REVIEW, chưa MERGE_READY** do bảng phụ thuộc M2 đã cần chỉnh và durable asset archive chưa được owner quyết định. Issue #20 deferred, G2_VISUAL PENDING/G1_CIRCULATION PARTIAL, M2 IN_PROGRESS |
| 2026-11-18 | Chủ dự án cho phép kho PRIVATE và Codex bảo toàn bản original R4 | Vault commit `908a5cbb`: ZIP 11,369,216 bytes, SHA256 `4255b199…3249f8`, 28 members, sáu locks; owner remote restore/E0/E1 theo [evidence](3d-production/P507-R4-PRESERVATION.md). Không cấp token CI cross-repo |
| 2026-11-18 | ChatGPT nghiệm thu và MERGE PR #21 | HEAD đã review `27ab5838` 12/12 exact-head CI SUCCESS, E0 PASS, E1 15/15; merge main `42a34979d5f48b31f3e58f17f59b7b7f6010bfe8`. Nghiệm thu **phạm vi tích hợp chức năng và lưu trữ nguyên bản**; không phải M2 DONE. Theo dõi [#22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) vì nguồn CI vẫn dùng artifact gốc hết hạn 24/11 và 4 HIGH dependency cần triage; #20 giữ deferred; không mở M3 |
| 2026-11-18 | ChatGPT reviewed Draft PR #24 at `997c9303` and MERGED docs PR #23 | PR #23 exact-head 12/12 CI PASS and main `5b971f59`; PR #24 unprivileged tests/legacy E0/E1 PASS (14 SUCCESS including 2 readiness reports; 2 App jobs SKIPPED), overall PARTIAL/SECURITY_APPROVAL_REQUIRED. Real App proof missing; current PR checks still depend on artifact ending 24/11, readiness main fails before activation, branch conflict after #23. Must approve App/secret/environment separately, reconcile main and update exact CI before merging #24; M2 IN_PROGRESS, no M3 |

| 2026-11-19 | Owner ủy quyền merge, ChatGPT tích hợp M3 technical PR #25 | Review độc lập đúng head `a7acadc951ab554360606d324cc427da354ec090` [ACCEPTED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#pullrequestreview-5971384295); 13 SUCCESS (2 status-only) + 2 privileged SKIPPED, 76 PostgreSQL tests PASS, F1 provenance/F2 populated migration/F3 private multi-tab PASS. [PR #25 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) merge `ba5139d34de1454029d9b71958123f2d5aec1375`. **M3 kỹ thuật ACCEPTED**, tổng milestone IN_PROGRESS/BLOCKED vì #2/#3 thiếu bản ghi AIRC thật/cadence/quyền demo hoặc công bố. Không kích hoạt M4–M7; #20/#22 riêng. |
| 2026-11-19 | ChatGPT nghiệm thu cuối M2 và MERGE PR #24 | Độc lập review head `b0a4e0f6f8d48053a470cbf5f20f9f44e5bc7d45`: 13 SUCCESS + 2 privileged App SKIPPED (không phải 15 PASS), E0/E1 actual owner-local PASS và 15/15 Chrome evidence, vault Private nguyên gốc; PR24 MERGED main `0b727a06aef0773063dd4427a066054a3a87cd7d`. Đóng **M2 trong phạm vi prototype chức năng** 7/7 DoD, không phải G2 visual/real-world fidelity/mobile/XR/KPI; #22 vẫn OPEN operational security/CI App (chưa setup/trusted proof), #20 DEFERRED, M3 PLANNED/DEPENDENCY_BLOCKED #2/#3, chỉ code khi owner giao task riêng |

Điểm kiểm soát hiện hành (2026-11-19): M0/M1/M2 DONE. [PR #25](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) đã MERGED, M3 Admin manual-first/synthetic technical accepted, nhưng M3 vẫn IN_PROGRESS/BLOCKED về nguồn/quyền thực địa theo #2/#3; không báo M3 DONE. #20 visual/circulation owner hoãn; #22 GitHub App private-vault trusted CI chưa có live proof. M4 IN_REVIEW trên nhánh #27, M5–M7 PLANNED.


AS-OF trước merge #21: owner approved integration #19 and deferred #20; Draft PR #21 lúc đó pending review/archival decision. Lịch sử này đã được thay bởi dòng MERGED #21 trong decision log; current gate là quyền CI private-vault #22 và nghiệm thu chức năng M2 còn thiếu. Không có milestone mới.

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

### Demo-first priority decision — 2026-11-19

**AS-OF quyết định trước đó — 2026-11-19 (demo-first, inventory deferred, đã được thay thế):** Chủ dự án tạm dừng thu thập/bổ sung vật nhỏ trong inventory P507 để ưu tiên thử demo chức năng sớm. **Không thay đổi M3 execution_status=IN_PROGRESS/dependency_status=BLOCKED; M3 full DoD nguồn thật #2/#3 chưa đạt.** Được phép chuẩn bị/tự chạy thử local demo các phần đã merge: E1 standalone có đi bộ, M3 Admin private manual-first có 3 state types, và trang P507 public synthetic riêng (không coi là một trải nghiệm viewer tích hợp). **Admin private không tự publish sang public WS**; mọi phương án hợp nhất viewer/publication phải được đánh giá về quyền dữ liệu trước khi code. M4/M5/M6/M7 giữ PLANNED; kế hoạch và task code mới cần owner phê duyệt riêng.

### M3 owner authorization — 2026-11-19

Owner approved technical implementation of the P507 M3 slice in one branch and one Draft PR. AIRC source and rights dependency remains BLOCKED by #2/#3. See [source matrix](m3/P507-DATA-SOURCE-MATRIX.md). G3 and M4–M7 remain outside this task.

M3 manual-first Admin được chủ dự án duyệt 2026-11-19 trong PR #25. Xem [quyết định](m3/P507-ADMIN-DECISION.md). M3 IN_REVIEW / PARTIAL **(AS-OF trước merge)**, quyền công bố chưa xác nhận. Nghiệm thu phân biệt sẵn sàng merge kỹ thuật với đạt đầy đủ DoD, theo [ma trận ứng viên M3](m3/P507-M3-INTEGRATION.md#final-technical-and-field-gates).

**Quyết định cập nhật:** a7acadc9 đã được [review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#pullrequestreview-5971384295) và [merge PR #25](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) tại `ba5139d34de1454029d9b71958123f2d5aec1375`; M3 giữ IN_PROGRESS/BLOCKED thực địa. Chỉ chủ dự án/người có thẩm quyền mới xác nhận các bản ghi AIRC và phạm vi công bố; merge kỹ thuật không đóng #2/#3.
