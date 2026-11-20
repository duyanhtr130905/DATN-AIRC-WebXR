# CURRENT MAIN STATUS — post-M5 gap closure authorized, 20/11/2026

**CURRENT POST-M5 GAP CLOSURE AUTHORIZATION — 20/11/2026:** Chủ dự án đã yêu cầu **bắt đầu một lượt tổng hợp bổ sung các thiếu sót M0–M5**. [Issue #30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30) hiện `AUTHORIZED / EXECUTION REQUESTED`, được rà soát thành 13 nhóm G0–G12: M0/M1/M2 DONE trong phạm vi đã nghiệm thu; M3 nguồn dữ liệu và quyền #2/#3, M4 policy/capacity500/recovery, M5 thiết bị #4/#5, M2 fidelity #20 và bảo mật vault #22. **Tại thời điểm này Codex chưa bắt đầu mã/không có Draft PR #30**; đây là công việc một nhánh/một Draft PR tiếp theo, Codex phải fetch lại HEAD của main trước khi code, chờ ChatGPT nghiệm thu độc lập trước merge. Trước hết sửa M4 `visitor.py` terminal `session_end` tại ngưỡng 500, Chrome M4 Windows timeout, xác minh regressions và tạo field/rights/device/privacy evidence kits. **Không tự sửa frozen R4, không cấp vault App token/PAT/secrets, không mở public/thu thập người thật, không bịa 3 phòng/vật thật/KPI; thiếu quyền và thiết bị giữ BLOCKED.** Original R4 Actions artifact hết hạn 24/11/2026 14:46:36 ICT; bản owner-private vault tồn tại nhưng CI privileged #22 vẫn chưa được phép/proven. M6 formal KPI và M7 chưa triển khai. Trạng thái M3/M4/M5 đầy đủ không tự thành DONE bởi ủy quyền #30; các ghi chú M5/M4 cũ bên dưới là AS-OF.

**CURRENT M5 TECHNICAL ACCEPTANCE — 19/11/2026:** [PR #31 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/31) commit `aeffe01a8b3a2c807ed82968db870989cc2ecd8d` after [independent M5 final review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/31#pullrequestreview-5977083763) of candidate `fdfc9c58de39b21435041ce3a4509574dddd0149`. **M5_TECHNICAL_ACCEPTED / MERGED** for DEV/loopback, pinned original R4, synthetic/provisional Web3D + Chrome/IWER WebXR: 9/9 distinct owner-local Chrome/IWER R4 scenarios reviewed from user-supplied ZIP (SHA-256 `2ee4ffc50e1f31ccdad8bb0dff1bc1d7c27fef1815191dda64ce2ca28b2cbf5d`) with screenshots, VR/AR controller pick `P507-CHAIR-A-01`, gesture/permissions, VR lifecycle exit/re-entry, AR preview hit test/no-hit-test, listeners cleaned, context loss/recovery, mobile viewport; E1 original R4 Chrome 15/15; R4 121 placed/2 unplaced and GLB SHA `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49` verified. R4 Admin Windows raycast now PASS after waiting for true draw/canvas measurement, UUID `0ed3ab16-44a0-5c39-9421-d3cecda9ae3c`. Exact-head GitHub CI 52 web + 75 API non-PG + 86 PostgreSQL PASS; 13 SUCCESS checks including status-only, 2 privileged vault SKIPPED #22. **Important:** GitHub CI M5 runs only 2 fallback/mock scenarios; 9/9 positive XR evidence came from reviewed Windows ZIP, not CI. Windows concurrent PostgreSQL suite 85/86 due one M4 Chrome 500ms locator timeout; isolated 10/10 PASS; CI Linux 86/86 PASS. SwiftShader frame times and warnings cannot certify hardware performance. **M5 full milestone remains IN_PROGRESS / DEVICE_BLOCKED**: native physical AR Galaxy #4 and VR HMD #5, representative Web3D30/VR72, protocol and device-specific UX unverified. No real visitor tracking permission or AIRC data release; M3 #2/#3, M2 #20, private App CI #22, M4 consent/retention and 500-event terminal edge remain open. Per owner decision, [single post-M5 consolidated M0–M5 gap closure #30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30) is **NEXT / NOT YET CODED** before M6 formal KPI acceptance. Historical M5 IN_REVIEW notes below are AS-OF before merge.

**M5 IN_REVIEW / DEVICE_BLOCKED — nhánh feat/m5-webxr-ar-vr-integration, 19/11/2026.** Route tham quan Web 3D / WebXR cục bộ trong apps/web dùng R4 đã khóa hash và navigation E1. Main đã fetch ở 87b8047c11308065fd6776e4dd44da4246ed0f1a. Xem [runbook M5](m5/P507-WEBXR.md) và evidence theo HEAD [Draft PR #31](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/31). Windows Admin raycast đã tái hiện ở zero WebGL draw calls, regression nay chờ draw thật và kiểm đúng UUID. AR #4 / VR #5 còn chờ thiết bị và protocol, G2 #20 còn mở, privileged vault #22 SKIPPED. Chủ dự án yêu cầu [Issue #30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30) sau nghiệm thu độc lập M5. Các snapshot M4 và quyết định giao việc bên dưới ghi trạng thái vào thời điểm lập.


**QUYẾT ĐỊNH M5 VÀ LƯỢT TỔNG RÀ SOÁT SAU M5 — 19/11/2026:** Chủ dự án đã **giao triển khai M5 kỹ thuật** (một nhiệm vụ Codex, một nhánh và một Draft PR) qua [Issue #29](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/29) từ main `25331ad13dfe3d795cd44034b4a516474abed86d` (Codex phải xác minh SHA live). **M5 chưa có code/PR** tại thời điểm ghi; M5 `PLANNED / DEVICE_BLOCKED` cho đến khi Codex mở branch/PR, các thử nghiệm AR/VR trên thiết bị thật #4/#5 chưa được thực hiện. Tương tác P507 R4 phải kiểm đúng asset; mô phỏng IWER không thay bằng chứng AR/VR vật lý, không đụng M3 private hoặc bật tracking thật M4. **Sau khi ChatGPT nghiệm thu M5**, chủ dự án yêu cầu **một lượt duy nhất rà soát và bổ sung tất cả tồn đọng M0–M5**, trước khi chuyển sang nghiệm thu M6; xem [Issue #30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30) (hiện PLANNED, CHƯA TRIỂN KHAI). Đây là lượt hợp nhất/khắc phục trong chuẩn bị M6, **không phải milestone mới và không bỏ/đổi DoD/KPI M0–M7**. Các mục thiếu dữ liệu/pháp lý/thiết bị vẫn BLOCKED cho tới khi người có thẩm quyền cung cấp quyết định/bằng chứng; #2/#3/#4/#5/#20/#22, raycast R4 Windows, M4 consent/retention và trần 500 events vẫn cần theo dõi. Vấn đề #22 có rủi ro expiration nguồn artifact 24/11/2026; không tự tạo token/grant để vượt rào quyền.

**CURRENT M4 TECHNICAL ACCEPTANCE — 19/11/2026:** [PR #28 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28) at merge commit `05a60e8b5294ef3bb605723f4941f333eef7353f` after [independent final technical review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28#pullrequestreview-5975532440) of exact candidate `cb5bba49a4c6f58e7be597c074a3342590bcbe70`. **M4_TECHNICAL_ACCEPTED / MERGED** in gated synthetic/local scope: 49 web, 75 API unit, 86 PostgreSQL PASS (Chrome M4 E2E), 13 CI success (includes reporting-only) + 2 privileged vault SKIPPED; oracle 50 synthetic sessions/1,000 client IDs + 50 server starts matches DB/CSV/JSON; normal same-browser A→B visit preserves both sessions and 12 unique events, old proof 401, retry/rollback/cross-tab tested. Prior PARTIAL review is historical AS-OF and was fixed. **M4 FULL milestone stays IN_PROGRESS / BLOCKED** until authorized consent/identity/retention/deletion/report access for real visitor data; do not claim M6 MT3 KPI PASS. Disclosed technical limits: 500-event ceiling can prevent recording a terminal `session_end` at capacity; lost/expired proof limits authorized cleanup; address before real capture. Owner-local original frozen R4 Admin raycast reportedly fails on baseline and final candidate; CI synthetic fallback PASS does not clear actual raycast, vault privileged jobs #22 remain SKIPPED. M3 real inventory/source/rights #2/#3 still BLOCKED. M5 PLANNED and physical AR/VR device/protocol #4/#5 BLOCKED; no M5 code was created by this merge.

**Bàn giao sửa vòng đời phiên trên Draft PR #28 (IN_REVIEW):** Bản sửa tách kết thúc/giữ lịch sử, đồng ý cho lượt mới và rút đồng ý/xóa. Chuyển quyền và ghi bắt đầu trong một transaction PostgreSQL, có retry theo cùng ID thao tác. Kiểm thử Chrome và DB đối chiếu hai phiên trên cùng browser context cùng 12 sự kiện qua CSV/JSON. Oracle độc lập 50 phiên và 1.000 ID vẫn chạy trong workflow. Kết quả và artifact gắn đúng SHA tại [CI nhánh M4](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/workflows/app-validation.yml?query=branch%3Afeat%2Fm4-visitor-sessions-reporting) và [Draft PR #28](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28). Chờ ChatGPT review lại. Chính sách dữ liệu khách thật vẫn BLOCKED.


**Nghiệm thu độc lập PR #28 — 19/11/2026 (PARTIAL / CORRECTION REQUIRED):** Review đúng HEAD `3621e5bca9b6de5242e995837bf1c73638df1df3` tại [#5974447677](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28#pullrequestreview-5974447677). Bằng chứng synthetic/local từ CI: 49/49 web, 75/75 API non-PostgreSQL, 83/83 PostgreSQL PASS; 13 check SUCCESS (có check chỉ báo), 2 vault privileged SKIPPED (#22). Oracle độc lập 50 phiên synthetic, 1.000 client event IDs + 50 server starts: DB/CSV/JSON đối chiếu không thiếu/thừa/trùng. **Lỗi BLOCKING:** Sau `session_end`, cookie hợp lệ khiến POST /visitor/sessions trả chính phiên đã kết thúc; UI không cho bắt đầu phiên mới, chỉ còn chức năng xóa (làm mất phiên/sự kiện đã lưu). Phải tách **kết thúc và giữ lịch sử** với **rút đồng ý/xóa**, thêm E2E Chrome/API cho 2 lượt liên tiếp trong cùng browser, bảo đảm cả hai còn ở báo cáo và token cũ không thể sửa phiên cũ; sửa trên **cùng Draft PR #28** và nghiệm thu lại đúng HEAD/CI mới. **M4 vẫn IN_REVIEW / PARTIAL, chưa merge, chưa DONE**, policy dữ liệu khách thật BLOCKED; MT3 M6 chưa PASS; M5 chưa triển khai. M3 #2/#3 và #22 giữ nguyên.

**M4 (19/11/2026, nhánh triển khai):** Chủ dự án đã giao phần kỹ thuật synthetic/local-only qua [Issue #27](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/27). M4 IN_REVIEW trên nhánh triển khai, policy người tham quan thật BLOCKED. Xem [runbook và bằng chứng](m4/VISITOR-SESSIONS.md). M3 #2/#3 vẫn mở. Xem [quyết định phạm vi](decisions/0002-m4-synthetic-visitor-scope.md).

**Quyết định của chủ dự án về M3 — 2026-11-19.** Ưu tiên hoàn thiện và nghiệm thu M3. Hoãn demo tham quan hoàn chỉnh sang M4/M5 theo phạm vi được duyệt riêng. M3 giữ IN_PROGRESS/BLOCKED cho đến khi đủ inventory thực, nguồn và quyền #2/#3, cùng trace nguồn → UI. DoD và KPI giữ nguyên.

**AS-OF quyết định trước đó — 2026-11-19 (demo-first, inventory deferred, đã được thay thế):** Chủ dự án tạm dừng thu thập/bổ sung vật nhỏ trong inventory P507 để ưu tiên thử demo chức năng sớm. **Không thay đổi M3 execution_status=IN_PROGRESS/dependency_status=BLOCKED; M3 full DoD nguồn thật #2/#3 chưa đạt.** Được phép chuẩn bị/tự chạy thử local demo các phần đã merge: E1 standalone có đi bộ, M3 Admin private manual-first có 3 state types, và trang P507 public synthetic riêng (không coi là một trải nghiệm viewer tích hợp). **Admin private không tự publish sang public WS**; mọi phương án hợp nhất viewer/publication phải được đánh giá về quyền dữ liệu trước khi code. M4/M5/M6/M7 giữ PLANNED; kế hoạch và task code mới cần owner phê duyệt riêng.

**Roadmap 2.0 APPROVED** remains the only milestone source of truth. Chủ dự án đã ủy quyền merge M3 technical slice sau ChatGPT independent review; [PR #25](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25) được merge vào `main` bằng commit `ba5139d34de1454029d9b71958123f2d5aec1375` với candidate HEAD `a7acadc951ab554360606d324cc427da354ec090`. Đây là trạng thái **đã merge**, không còn Draft/IN_REVIEW của PR #25. Docs-only post-acceptance synchronization follows the merge; always verify latest live main SHA.

**Independent technical acceptance:** [Final review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/25#pullrequestreview-5971384295) gắn đúng candidate HEAD. Checks 13 SUCCESS (bao gồm 2 reporting-only), 2 privileged vault App SKIPPED (Issue #22), 0 FAILURE. [CI](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44477280736) chạy **76/76 selected PostgreSQL tests PASS**, Chrome synthetic DOM fallback, F1 provenance correction, F2 nonempty 0002→0003→0004 preservation, F3 two-tab private Catalog invalidation/reconnect, public/private WS isolation. Owner-local actual frozen R4/E0/E1 PASS do Codex báo cáo; ảnh/video owner-local cuối chưa được reviewer trực tiếp kiểm chứng, nên không coi CI DOM fallback là frozen raycast proof.

**Current milestones:** M0/M1/M2 **DONE** trong phạm vi đã phê duyệt. M3 **execution_status=IN_PROGRESS**, **dependency_status=BLOCKED** (#2/#3). Phần **M3_TECHNICAL_ACCEPTED / MERGED**: P507 121 placed provisional IDs; Admin loopback-only manual-first login, private Catalog CRUD (vật nhỏ mới NOT_MODELED/INFO_ONLY), provenance, three state types, State/History/Outbox/WS, authenticated preview and recovery. **M3_FULL_DOD=NOT_DONE**: không có đủ danh mục/đối tượng thực được xác nhận, ba bản ghi quan sát thật cho `room_schedule`/`equipment_status`/`exhibit_info`, cadence và bằng chứng nguồn/quyền sử dụng/bản ghi, giới hạn quyền demo/luận văn/công bố, và thực địa source→UI trace. Không được coi synthetic fixture hoặc OWNER_ENTERED/PENDING_VERIFICATION là AIRC-verified; MT1-04 physical-change→UI chưa nghiệm thu.

**Scope and next decision:** AIRC không có API; chủ dự án đã xác nhận quyền thống kê thiết bị phục vụ ĐATN và là Admin nhập thủ công. Tiếp theo cần chủ dự án cung cấp/đối chiếu ít nhất một thiết bị và một đối tượng trưng bày có định danh P507, các vật nhỏ còn thiếu, ba quan sát thật kèm timestamp/múi giờ/nguồn/cadence và phạm vi được phép xem riêng/demo/đưa vào luận văn/công khai. Chỉ sau khi có evidence mới có thể nghiệm thu phần field DoD của M3. M4 synthetic/local đã được giao riêng qua #27 sau khi PR #26 merge.

**Open tracked issues:** [#2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/2) survey/inventory confirmation; [#3](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3) source, cadence and usage/disclosure permissions; [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) deferred geometry/fidelity; [#22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) privileged vault GitHub App CI not proven. M4 **IN_REVIEW** trên nhánh `feat/m4-visitor-sessions-reporting` (base `ae21efd2359779aa5bc6a889624a4705cd830ee1`), M5–M7 **PLANNED**. Trạng thái M4 này áp dụng cho [Draft PR #28](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/28); main giữ baseline đã merge. [M3 acceptance/runbook](m3/P507-M3-INTEGRATION.md), [source matrix](m3/P507-DATA-SOURCE-MATRIX.md).


---

## AS-OF M2 closeout on main
# CURRENT PROJECT STATUS — M2 functional prototype accepted, 2026-11-19

**Source of truth:** [Roadmap 2.0](ROADMAP.md) APPROVED. Main merge baseline `0b727a06aef0773063dd4427a066054a3a87cd7d` after [PR #24](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) was independently reviewed at exact head `b0a4e0f6f8d48053a470cbf5f20f9f44e5bc7d45` and **MERGED**. A subsequent docs-only post-acceptance commit may advance main; always verify live GitHub SHA. [Final M2 7-DoD matrix](3d-production/P507-M2-FINAL-ACCEPTANCE.md) is authoritative over historical PENDING/Rerun notes.

**Milestones:** M0 DONE, M1 DONE, **M2 DONE in the single-room provisional P507 FUNCTIONAL PROTOTYPE scope**, M3–M7 PLANNED (M3 `DEPENDENCY_BLOCKED` by source/rights Issues #2/#3 and future owner task). PR #21/#23/#24 MERGED; R4 frozen GLB/lock and M1 backend unchanged. M2 completion does not authorize M3 coding.

**Functional acceptance:** DoD 1–7 closed by ChatGPT independent review/owner-delegated PR integration. Owner-private clean restore data, E0 actual 121 logical IDs / 402482 vertices / 3mm and 1mm bounds, E1 Chrome 15/15 scoped west route, logical ID panel with provisional provenance, loading/errors/retry/reload, desktop/responsive 390x844/768x1024 emulation and fallback evidence all documented. Candidate exact SHA GitHub CI: **13 SUCCESS including 2 status-only, 2 privileged SKIPPED, 0 FAIL**; App-token actual CI **NOT RUN**. Final-HEAD local image ZIP exists on owner's machine but was not uploaded/visually inspected by this reviewer; owner-provided raw JSON/report and previous CI browser artifacts were inspected. No physical mobile/touch, hardware FPS30, VR72, AR/VR or physical-realism signoff.

**Tracked open risks:** [#22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) owner-controlled private-vault CI App authorization/configuration and live trusted-main restore is **OPEN/NOT_PROVEN** (not M2 DoD); never claim a skipped job passed. Original Actions artifact expires 24/11/2026 14:46+07, but byte-preserved PRIVATE vault archive commit `908a5cbb` is present. [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) is DEFERRED_BY_OWNER (chair-row aisle, object sizes/positions), `G1_CIRCULATION=PARTIAL`, `G2_VISUAL=PENDING_OWNER_APPROVAL`. M3 #2/#3 (source and data rights) still BLOCKED, not green. Historical four HIGH npm advisories in dev chain returned zero on final Codex audit without lock change; re-check prior to deploy.

**Next approval gate:** only **plan M3 source/rights and catalog-to-P507 mapping** until owner separately authorizes implementation. No auto G3, visual corrections, App grants/secrets, main deployment or M3/M4/M5 development.

---

## AS-OF trước nghiệm thu M2 cuối — preserved historical snapshots
# Final M2 closure candidate (2026-11-19)

Draft PR #24 is based on main 5b971f591585124424e8393118b0911eb7c11110 after PR #21/#23. M2 IN_PROGRESS pending independent acceptance and owner decision. See [M2 final acceptance matrix](3d-production/P507-M2-FINAL-ACCEPTANCE.md). Exact candidate HEAD and evidence are recorded on PR #24.

## AS-OF trước lần hợp nhất cuối PR #24

# Independent review status — M2 Issue #22 (18/11/2026)

**Main:** `5b971f591585124424e8393118b0911eb7c11110` after [PR #23 MERGED](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/23) (docs-only, exact-head 12/12 CI SUCCESS). PR #21 MERGED P507/owner-private archive; Issue #19 CLOSED.

**PR #24:** reviewed implementation HEAD `997c93033ebd0716b85a910558686e4edd762b6e`; Draft, **PARTIAL / SECURITY_APPROVAL_REQUIRED**, NOT MERGED. Exact-head GitHub checks: **14 SUCCESS + 2 App SKIPPED**, 0 failed. Two of 14 are reporting-only readiness checks. Live installation-token restore was NOT RUN; mock negative tests and owner-local vault restore must not be mislabeled as App CI proof. [Review](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) and [Issue #22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) record these facts.

**Technical evidence scoped PASS:** 76 geometry Python, 30 E0/restore/security Python, 13 Node identity, 45 frontend tests; actual Chrome legacy E0 PASS and E1 15/15 PASS, responsive viewport emulation 390x844/768x1024 PASS for rendering and panel layout. No physical touch navigation, real mobile acceptance, GPU30/VR72, full circulation or G2 visual signoff. Owner-private R4 original asset remains frozen. Existing HIGH dev dependencies not remediated.

**Blockers:** (1) owner approval/configuration for vault-only Contents:read GitHub App and protected `p507-vault-ci` environment with private key as environment secret, not repo/org secret; (2) legacy PR browser/diagnostic checks still use expiring Actions artifact after **24/11/2026 14:46:36 +07**; (3) main `vault-access-readiness` fails if feature flag disabled, requiring owner-approved setup/transition; (4) PR #23 merged into main after PR #24 branch created, and GitHub reports PR24 mergeable=false until carefully reconciled; (5) exact-head live App proof and post-expiry required-check policy missing.

**Roadmap:** M0/M1 DONE, M2 IN_PROGRESS/PARTIAL, M3–M7 PLANNED; #20 deferred (G1_CIRCULATION=PARTIAL, G2_VISUAL=PENDING_OWNER_APPROVAL); no unapproved App grant/deployment/M3. This snapshot is on Draft PR24 branch only, NOT on main. Preserve previous history as AS-OF. New docs-only HEAD must be separately checked; CI of reviewed HEAD `997c9303` is not CI of the new docs commit.

---

## AS-OF before independent PR24 review (historical snapshot)
# Current Issue22 snapshot — 18/11/2026, implementation IN_REVIEW

Main `42a34979d5f48b31f3e58f17f59b7b7f6010bfe8`: PR21 MERGED, Issue19 CLOSED, P507 provisional + owner-private restore present. New branch `feat/m2-secure-vault-ci-22` implements authorized Issue22; App CI **BLOCKED / SECURITY_APPROVAL_REQUIRED** (no App/key/installation/environment/activation created). Exact final HEAD/checks/run/evidence are in the [Draft PR24](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) and [security/functional report](3d-production/P507-ISSUE22-SECURE-CI.md). Legacy original-artifact checks are separate from blocked App proof; skipped privileged jobs never count as E0/E1 PASS.

PR23 is OPEN/DRAFT at `0f63a671cbea5f3160330d7a954761ff780d18bb` at intake; preserved its reviewed five-file synchronization on this branch, with current Issue22 extension, without merging/modifying PR23 or claiming those docs already main. Correct two-column M2 dependency table retained. See AS-OF PR23 snapshot below.

Separate CI App/JWT identity/installation/read-only token scope and explicit pinned-vault restore implemented; owner restore_asset.py unchanged. Privileged main-only environment jobs never checkout PR SHA; secure setup runbook requires owner approval, environment-only key, protection entitlement and full installation selection audit. Current API found protected environment/activation absent. Frozen ZIP/GLB/lock/IDs/provenance/collision/tolerances unchanged. Precommit30Python+13Node security/identity and76geometry PASS; actual responsive emulation390/768 PASS. Clean checkpoint6ed7c82 owner remote restore/E0/E1 15/15/responsive390/768 PASS, explicitly LOCAL_OWNER_NOT_APP ([evidence](evidence/p507-issue22-functional-6ed7c82.json)). Final exact-HEAD rerun/CI results linked from Draft PR24; actual App proof still BLOCKED. Read-only npm triage:4HIGH from one picomatch ReDoS chain, all dev; production-only audit0; no dependency changes.

M0/M1 DONE,M2 IN_PROGRESS,M3 PLANNED/DEPENDENCY_BLOCKED. #20 DEFERRED,G1_CIRCULATION=PARTIAL,G2_VISUAL=PENDING_OWNER_APPROVAL; no mobile-device/touch navigation/KPI30/VR72 acceptance. Next: final checks and independent ChatGPT security review; owner separately approves App/protected environment/secrets and real trusted-main CI proof. No merge/deploy/M3.

---

## AS-OF PR23 documentation synchronization (unmerged source snapshot)

# Trạng thái hiện hành — M2 P507 đã tích hợp, 18/11/2026

**Main HEAD tại lần nghiệm thu:** [`42a34979d5f48b31f3e58f17f59b7b7f6010bfe8`](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/commit/42a34979d5f48b31f3e58f17f59b7b7f6010bfe8). Đây là snapshot đã kiểm tra live; lần tiếp theo phải fetch GitHub để xác nhận SHA mới. [PR #21](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21) **MERGED** sau independent ChatGPT review tại head `27ab5838db5f27c3a6694916b9bdbada4edb72ea`, **12/12 CI checks SUCCESS** (6 workflows) trên đúng head; GitHub xác nhận merge commit `42a34979`. PR #14/#15 là nhánh nguồn Draft lịch sử, **không cần và không được tự merge lại**.

**Accepted scope:** tích hợp P507 frozen R4 (provisional), E0 actual geometry/reference 121 IDs/402.482 vertices với tolerance 3mm/1mm, Chrome E1 15/15 smoke PASS, diagnostic root-cause exit0/negative exit1; 76 geometry, 23 E0/restore/diagnostic và 45 frontend unit tests theo evidence. Không gọi E1 smoke là 30FPS physical GPU, VR72, mobile/full-room circulation hay XR. Backend M1 synthetic không bị thay.

**Private archive:** [vault riêng](https://github.com/duyanhtr130905/DATN-AIRC-WebXR-asset-vault) đã được GitHub connector xác minh PRIVATE và owner admin. Commit `908a5cbb1f77b75b28666fd424cbd85f2aba4c1f` chứa Git blob ZIP 11.369.216 bytes, manifest và lock; SHA256 ZIP `4255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8`; GLB 10.751.036 bytes / SHA256 `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`. Clean remote owner restore PASS theo báo cáo Codex/committed numerical evidence `193720b`; reviewer không trực tiếp chạy local Windows restore hay tải lại binary ZIP để tự tính SHA256. Private visibility + Git object verified; danh sách collaborators owner-only là báo cáo Codex, không được kiểm chứng độc lập bằng API. [Runbook](3d-production/P507-R4-PRESERVATION.md).

**Open CI blocker:** [Issue #22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22) ghi lại `CI_CROSS_REPO_RESTORE=BLOCKED`: E0/E1 và TV diagnostic workflows còn gọi old Actions artifact ID 14309207795 (expires **2026-11-24 14:46:36 +07**). Current CI 12/12 PASS ở head trước hạn, nhưng **không chứng nhận CI sau hạn**; token/cross-repo quyền chưa được chủ dự án cấp, không tự phát hành PAT/secret. Cần owner chốt phương án đọc PRIVATE vault trong CI và kiểm thử không fallback trước hạn.

**Deferred/other risks:** [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) lưu lỗi giữa hàng ghế, sai kích thước/vị trí; `G1_CIRCULATION=PARTIAL`, `G2_VISUAL=PENDING_OWNER_APPROVAL`. Bốn HIGH npm audit từ frontend tooling hiện có cần triage riêng, chưa sửa trong PR #21; không có public deployment. M0/M1 DONE, **M2 IN_PROGRESS**, M3–M7 PLANNED, MT1–MT3 chưa nghiệm thu; ≥3 phòng thuộc M6. User approval of roadmap/merge not permission to begin M3 feature.

**Next action M2:** ưu tiên xử lý #22 trước 24/11 theo quyền owner, tiếp tục nghiệm thu phần desktop/mobile/fallback còn thiếu; giữ #20 deferred. Báo cáo khác biệt Roadmap nếu yêu cầu mới vượt phạm vi; không tự deploy, mở G3 hoặc M3.

---

## AS-OF trước merge PR #21 — lịch sử

# Snapshot M2 private preservation trước merge — 18/11/2026 (AS-OF)

Owner explicitly approved private original-R4 archival and independent restore in [PR21 decision](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21#issuecomment-6973024761). Source branch `integrate/m2-p507-issue-19`, starting HEAD `faa12d20a55a5d0dbf8e4b81cd0b1289d61f04bf`; ChatGPT's two-column M2 dependency fix retained. Main still `458569026edc917fa38d945ecd190bd4574b925f`; changes remain on Draft PR21, not merged.

PRIVATE owner-controlled [vault](https://github.com/duyanhtr130905/DATN-AIRC-WebXR-asset-vault) at `908a5cbb1f77b75b28666fd424cbd85f2aba4c1f`, Private verified before/after upload, owner-only collaborator list. Original ZIP11369216bytes/SHA256 `4255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8` matches GitHub digest; all28members preserved, six locks PASS, GLB10751036bytes/SHA256 `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`. No regeneration/Release/Pages/raw photos. [Preservation evidence/runbook](3d-production/P507-R4-PRESERVATION.md).

Independent clean owner remote restore PASS on `193720b1770de119d5f87e732d5594a0f10b8b62`,dirty=false: all28members/six hashes,Python reference,E0 actual Chrome and E1 15/15 PASS without M1 backend; [numeric evidence](evidence/p507-r4-owner-restore-193720b.json). No existing bundle/original Actions fallback. 76 geometry+23 E0/restore/diagnostic,45 frontend units/build/typecheck,repository checks PASS. Final documentation HEAD reruns remote restore/local checks and all CI; exact final HEAD/results in Draft PR21. npm audit flags4HIGH on unchanged frontend tooling; no dependency edits, separate triage remains. **CI_CROSS_REPO_RESTORE=BLOCKED**: source GITHUB_TOKEN not granted vault access; no PAT or secret added. Current CI still uses original expiring artifact; future automated CI restore needs separate owner decision. Issue20 DEFERRED; G1_CIRCULATION=PARTIAL; G2_VISUAL=PENDING_OWNER_APPROVAL; M2 IN_PROGRESS; M3–M7 unchanged. Next: final exact-HEAD tests/CI → ChatGPT review → owner decision on CI vault access; Codex does not merge.

---

## AS-OF before private preservation

# Current snapshot — M2 integration Issue #19, 18/11/2026

Main verified `458569026edc917fa38d945ecd190bd4574b925f`. Integration branch `integrate/m2-p507-issue-19` starts from that main; no-ff merge `3f06344` preserves reviewed #15 `c3c800227cfd07426b4504f38607bb864b0b12f8`, #14 `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31` and G0 history. Branch contains R4/E0/E1 source **not merged to main**. [Draft PR #21](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21); branch tested clean at `69176aa0a005cc7db5433c2b82e24ed68a7b356f`. Final branch HEAD and exact CI are recorded in [integration evidence](3d-production/P507-M2-INTEGRATION-19.md) and Draft PR to avoid circular SHA claims.

Owner-approved [#19](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/19) is an M2 integration task; Roadmap 2.0 APPROVED, M0/M1 DONE/MERGED, M2 IN_PROGRESS. Independent ChatGPT acceptance pending: integration IN_REVIEW / PARTIAL until final checks and review. Inherited scoped E0/E1 TECHNICAL_PASS applies only to #15 reviewed head, not automatically to this integration. Initial local 76 geometry +18 E0/reference/diagnostic tests and all six bundle hashes PASS. Diagnostic false-green fixed; injected Three manual/Box3 mismatches must conclude UNRESOLVED and exit 1. Original root-cause evidence retained.

[Runbook](../experiments/p507-webxr/README.md): Vite-only Chrome demo at http://127.0.0.1:5173/p507-webxr-e1.html, no M1 backend. Original asset still available; expiry 24/11/2026 14:46:36 Asia/Saigon. Durable fresh-machine reproducibility BLOCKED after expiry without approved original-bundle storage; verified same-machine copy is available, no permanent archive/Release published. Local clean `69176aa`: E0 actual Chrome PASS (402482 POSITION samples, 0 proxy violations), E1 15/15 groups PASS with no M1 backend, 45 frontend units/build/typecheck and 10 checker tests PASS. Same-version Blender4.0.2/exporter4.0.44 diagnostic CI [44247798568](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44247798568) SUCCESS at clean `69176aa`: matching CONFIRMED/exit0, injected manual and Box3 mismatch UNRESOLVED/exit1. Exact URL5173 Chrome smoke PASS, no API/WS requests. Final documentation HEAD CI reported separately in #21; no old CI reused as final verification.

Owner-deferred [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20): inaccessible chair-row passages, inaccurate object sizes and placements. Frozen R4 unchanged; G1_CIRCULATION=PARTIAL, G2_VISUAL=PENDING_OWNER_APPROVAL. Hardware KPI30/VR72, mobile/XR and final fidelity/rights remain unverified. M3–M7 stay planned with existing dependencies, no new milestone.

Next: final integration regression and Draft PR → independent ChatGPT review → owner archival decision and later #20 task if explicitly resumed. No autonomous merge/deploy/M3.

---

## Review bổ sung — PR #21, 18/11/2026 (snapshot theo HEAD trước chỉnh tài liệu)

- **Nguồn review độc lập:** [PR #21 review comment](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21#issuecomment-6972847975), HEAD được kiểm `a0b91a8ab61d47a88ff9eb991631a561a62f2a08`; **12/12 CI checks SUCCESS** tại HEAD đó, bao gồm E0 frozen-asset Chrome và E1 15/15 smoke, Blender/Khronos/Chrome, API/PostgreSQL, PoC và diagnostic. Không được gán CI này cho commit cập nhật tài liệu mới cho đến khi chạy lại.
- **Verdict:** `TECHNICAL_PASS` cho phạm vi mã tích hợp Issue #19; **PR #21 PARTIAL / IN_REVIEW, chưa merge**. `main` tại thời điểm review vẫn `458569026edc917fa38d945ecd190bd4574b925f`.
- **Đã sửa trong commit cập nhật tài liệu tiếp theo:** lỗi cấu trúc bảng hai cột `Ma trận phụ thuộc` tại hàng M2 (trước đó chứa cả dòng 11 cột), không thay DoD/KPI.
- **Blocker còn mở:** nguồn original artifact ID `14309207795` hết hạn **24/11/2026 07:46:36 UTC (14:46:36 ICT)**; chưa có kho lưu trữ byte-preserving độc lập được owner cấp quyền, nên durable fresh-machine restore/CI lâu dài là `BLOCKED`. Hiện artifact còn truy cập được, bản local được kiểm chứng nhưng không phải backup riêng.
- **Backlog owner hoãn:** [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) lối đi giữa hàng ghế, sai kích thước/vị trí vật thể. `G1_CIRCULATION=PARTIAL`, `G2_VISUAL=PENDING_OWNER_APPROVAL`; E1 smoke kỹ thuật không chứng nhận độ chân thực/đi lại toàn phòng, 30FPS, VR72, AR/VR hoặc KPI cuối.
- **Next action:** chủ dự án phê duyệt phương án lưu trữ riêng có hạn chế quyền + hash/restore; khi có đường dẫn hợp lệ, triển khai và kiểm chứng khôi phục; sau đó review chính xác HEAD mới và xét merge PR #21. Chưa bắt đầu M3; #14/#15 giữ Draft. Roadmap M0–M7 không đổi.

## AS-OF historical snapshots — retained main documentation before Issue #19

# Trạng thái dự án — snapshot hiện hành

## Snapshot M2 — E0/E1 được nghiệm thu kỹ thuật (18/11/2026)

- **Main trước commit đồng bộ lần này:** [`2deb9267c614bdef55741f9fa104b729960c79db`](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/commit/2deb9267c614bdef55741f9fa104b729960c79db). PR #13 (G0), #16 (Roadmap 2.0) và #17 (post-review sync) đã MERGED; M0/M1 DONE, **M2 IN_PROGRESS**.
- **[PR #15](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/15) HEAD `c3c800227cfd07426b4504f38607bb864b0b12f8`: OPEN/DRAFT, base PR #14.** ChatGPT độc lập đã nghiệm thu **E0 technical PASS và E1 desktop Chrome 15/15 scenario groups PASS** trong phạm vi smoke tại [review comment](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/15#issuecomment-6969123428); **PR tổng thể PARTIAL/IN_REVIEW, chưa merge, không phải M2 DONE**.
- **E0:** committed `export-bounds-v1.json` offline Python-derived, gắn frozen GLB SHA `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49` (10,751,036 bytes), 121 logical IDs / 402.482 POSITION samples, 0 oriented-proxy violations. Runtime Chrome đối chiếu reference độc lập, bounds tolerance **3 mm**, proxy containment **1 mm**, TV authoring-vs-export drift **8.3055 mm** vẫn báo rõ. Frozen asset/manifest/lock không thay.
- **E1:** 15 nhóm Chrome smoke PASS, gồm load/spawn, raycast ancestor ID/panel provisional, WASD/pointer lock/ESC/reset, blur, pagehide **event-injected**, reload, tuyến Tây và blocker `P507-CHAIR-B-11`, các lỗi missing/hash/schema/corrupt với retry và unsupported WebGL. Chỉ tuyến Tây, không chứng nhận toàn phòng an toàn/PCCC/accessibility. Local RTX 3050 short-smoke là lời bàn giao Codex, không trực tiếp kiểm được file `D:\\Code\\DATN\\.local\\...` qua GitHub; CI dùng SwiftShader 640×360, không đủ làm KPI Web3D 30FPS/VR72.
- **CI đúng head #15:** [E0/E1 44233764219](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44233764219), [G1/G2 44233764259](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44233764259), [TV diagnostic 44233764274](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44233764274) đều SUCCESS (**5/5 check jobs**). Asset artifacts chỉ giữ khoảng 7 ngày.
- **Còn mở:** [PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14) Draft R4, **G2_VISUAL PENDING_OWNER_APPROVAL**, **G1_CIRCULATION PARTIAL**, full-room navigation/mobile/device fidelity chưa nghiệm thu. Diagnostic `diagnose_tv_bounds.py` có nhánh ba chiều số sai nhưng exit 0 dù `ROOT_CAUSE_UNRESOLVED` (non-blocking với E0/E1, phải có negative test và sửa). #14/#15 cần reconcile với main trước khi có thể merge; không để status lịch sử ghi đè Roadmap 2.0.
- **Next action:** owner xem screenshot/demo chức năng P507 để quyết định acceptance thực tế và hướng tích hợp nhánh M2; sửa diagnostic runner defect trong correction nhỏ cùng phạm vi trước khi đóng pipeline. Không tự mở G3/M3/M5 hoặc thay KPI. ≥3 phòng vẫn thuộc M6; Issues #1–#5 vẫn OPEN.

**Snapshot này phản ánh lần nghiệm thu và branch HEAD, không phải lời khẳng định mã #15 đã merge vào main. Kiểm tra GitHub live sau commit tài liệu tiếp theo.**

---


## Lịch sử — snapshot hậu merge #16/#13, trước review #15 (18/11/2026)

- **Main HEAD:** [cce30c06baa3dd2254a8b75c5c982f0900ef29f2](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/commit/cce30c06baa3dd2254a8b75c5c982f0900ef29f2).
- **Roadmap 2.0 APPROVED / MERGED:** [PR #16](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/16), reviewed head `9117e452f6f691d3c0ebd5cbcb89a8521b91f36e`, merge commit `0efaf50a845091d3e6ac14bb0d7cf5f7963d701c`, final HEAD 7/7 CI PASS. Quy tắc deviation guard và review/sync đã có trên main; ủy quyền merge chỉ trong phạm vi owner cho phép.
- **G0 P507 đặc tả MERGED:** [PR #13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13), reviewed head `c0eff0755d2d058b38944de60f40fb17387f2a91`, merge commit `cce30c06baa3dd2254a8b75c5c982f0900ef29f2`, 7/7 CI PASS ở head. Không đồng nghĩa G2 visual được duyệt.
- **Còn OPEN/DRAFT:** [PR #14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14) head `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31` (G1/G2 R4; technical PASS nhưng G2_VISUAL PENDING, G1_CIRCULATION PARTIAL); [PR #15](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/15) head `43a3828654ca90a8a1d1a05750c4f06e36f6bba6` (root cause TV ACCEPTED, **E0 aggregate FAIL / E1 runtime BLOCKED**). Không merge hoặc tự retarget #14/#15.
- **Milestone:** M0/M1 DONE/MERGED; **M2 IN_PROGRESS**, P507-only provisional; M3–M7 PLANNED. ≥3 phòng là yêu cầu MT1-01 của M6, không chặn prototype M2. Issues #1–#5 vẫn chưa được xác nhận giải quyết.
- **Bước tiếp theo:** M2 E0 contract correction có kiểm soát trên frozen R4 theo task được duyệt riêng, tiếp đó Chrome E1 walkthrough và nghiệm thu. Giữ PR #14/#15 Draft đến khi đạt các gate riêng; bảo toàn Roadmap 2.0 khi reconcile nhánh M2.

**Snapshot này là bằng chứng tại thời điểm ghi; mọi lần tiếp tục phải kiểm tra GitHub live và không gán CI của head cũ cho commit mới.**

---


## Lịch sử — snapshot trước merge 2026-11-18 09:57 +07:00 (Asia/Saigon)

Repository `duyanhtr130905/DATN-AIRC-WebXR`; root `D:\Code\DATN`; default branch `main`; live main HEAD **`e9a72caa084d9f2cbc4af2656b73509ea57b6d4b`** ([commit](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/commit/e9a72caa084d9f2cbc4af2656b73509ea57b6d4b)). Snapshot GitHub khớp baseline yêu cầu 18/11/2026. [PR #12](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/12) đã MERGED tại main HEAD ngày 15/11/2026; câu IN REVIEW phía lịch sử không còn là trạng thái hiện hành.

**Roadmap 2.0 APPROVED ngày 18/11/2026 bởi chủ dự án qua ChatGPT. M0/M1 DONE / MERGED. Current milestone: M2 IN_PROGRESS, dependency_status PARTIAL.** [ROADMAP](ROADMAP.md) duy nhất quản lý DoD M0–M7; [AGENTS](../AGENTS.md) quản lý quyền và guard. Phê duyệt kế hoạch không cấp quyền tự làm mọi feature. MT1–MT3 chưa nghiệm thu trên sản phẩm thật.

**Branch vs main — snapshot tại 09:57 ngày 18/11/2026:** bản cập nhật được soạn trên `docs/approved-m0-m7-roadmap-v2` từ main HEAD nêu trên, lúc đó chưa merge. [PR #16](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/16) là nguồn để xác minh HEAD/checks/merge **mới nhất**; sau khi review và merge, không được dùng snapshot này để nói nội dung vẫn chưa có trên `main`. Chủ dự án đã ủy quyền trong lượt nghiệm thu này cho ChatGPT merge trực tiếp các PR đủ điều kiện sau review/CI/mergeability; Codex không được tự merge.

### PR hiện hành — truy vấn GitHub live

| PR | Phạm vi | HEAD | Base branch | Draft | State / merge |
| --- | --- | --- | --- | --- | --- |
| [#13](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/13) | G0 specification, work item M2 | `c0eff0755d2d058b38944de60f40fb17387f2a91` | `main` | false | OPEN / NOT MERGED |
| [#14](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/14) | G1/G2 R4 asset, work items M2 | `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31` | `docs/g0-p507-3d-production-spec` (#13) | true | OPEN / NOT MERGED |
| [#15](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/15) | E0/E1 + TV diagnostic, work items M2 | `43a3828654ca90a8a1d1a05750c4f06e36f6bba6` | `feat/p507-g1-g2-blockout-hero` (#14) | true | OPEN / NOT MERGED |

Base heads xác minh tương ứng: #13 base main `e9a72caa…`; #14 base #13 `c0eff075…`; #15 base #14 `acd21c62…`. Không chỉnh sửa/retarget/rebase/merge các PR này. File 3D/E0/E1 không có trên main; dùng GitHub commit links bên dưới, không relative link tới file vắng mặt.

### M2 — asset, nghiệm thu và giới hạn

| Thành phần | Trạng thái hiện hành / bằng chứng |
| --- | --- |
| Frozen R4 | Provisional functional trial được owner cho phép; [freeze tại acd21c62](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/acd21c62c24b94d7dda4bbf25c80fe0b4224cc31/docs/3d-production/P507-G1-G2-R4-VIRTUAL-FREEZE.md), [handoff](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/acd21c62c24b94d7dda4bbf25c80fe0b4224cc31/docs/3d-production/P507-WEBXR-ASSET-HANDOFF.md) |
| Survey / virtual | Survey **6.00 × 8.10 × 3.50 m USER_REPORTED**; virtual **6.90 × 9.315 × 3.50 m OWNER_APPROVED_VIRTUAL_ADAPTATION**; X/Y +15%, không 1:1, chưa AIRC xác nhận fidelity/quyền |
| G1 geometry | Technical PASS cho phạm vi provisional: 121 placed IDs / 123 records, 17 bàn, 34 ghế đặt / 36 ID lịch sử; circulation PARTIAL, không chứng nhận navigation/PCCC/accessibility |
| G2 | PIPELINE PASS theo CI dưới; **G2_VISUAL=PENDING_OWNER_APPROVAL**. Không photorealistic/final-art PASS; không cần visual PASS trước desktop E1 |
| TV diagnostic | ROOT_CAUSE_CONFIRMED; **ACCEPTED** theo nghiệm thu ChatGPT được chủ dự án xác nhận trong yêu cầu 18/11; không có URL quyết định chat được cung cấp |
| E0 | **Aggregate FAIL**; [report tại 43a38286](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/43a3828654ca90a8a1d1a05750c4f06e36f6bba6/docs/3d-production/P507-WEBXR-E0-E1-EXPERIMENT.md); chưa correction Option A/B |
| E1 | Source **PARTIAL**, runtime **BLOCKED_BY_E0**; chưa browser walkthrough/render/performance E1; unit/input/navigation logic không thay runtime acceptance |
| Sau M2 | G3 NOT STARTED; M3–M7 PLANNED/chưa triển khai trong phạm vi tương ứng. M1 synthetic không là M3 real P507; M1 state history không là M4 visitor persistence |

Frozen GLB 10,751,036 bytes, SHA-256 `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`; source `acd21c62c24b94d7dda4bbf25c80fe0b4224cc31`, original CI checkout merge `9764b90f86317446bb585bf668171f81e1c57edb`, R4 checkpoint `3a11ec757168a59625a087ac83f28c433751a1f5`. [Original run/artifact 14309207795](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44038653564/artifacts/14309207795) được ghi trong handoff là hết hạn 24/11/2026 07:46:36 UTC; lần này không tải lại binary hoặc kiểm lại hash/retention. Nếu mất artifact thì ghi BLOCKED, không tự thay bằng re-export. Quyền ảnh/nhãn và final fidelity/visual sign-off cần đánh giá riêng trước demo/nghiệm thu cuối.

### CI trên đúng HEAD PR #15

Ba run sau đều được truy vấn live với `headSha=43a3828654ca90a8a1d1a05750c4f06e36f6bba6`:

| Run | Conclusion | Ý nghĩa |
| --- | --- | --- |
| [G1/G2 44066707478](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44066707478) | SUCCESS | Regression geometry/Blender/Chrome pipeline; không dùng export mới thay frozen R4 hoặc suy E1 PASS |
| [TV diagnostic 44066707650](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44066707650) | SUCCESS | Chẩn đoán root cause; không đổi aggregate E0 |
| [E0/E1 44066707535](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44066707535) | FAILURE | Logic SUCCESS; browser FAILURE tại E0 gate TV, E1 chưa mở |

Khác biệt với phần thân PR #15 AS-OF 17/11: G1/G2 run trước ghi IN_PROGRESS, nay live SUCCESS; đây là cập nhật trạng thái run, không phê duyệt visual/E1. Không chạy lại các workflow trong task tài liệu.

**TV root cause:** Blender **4.0.2** / exporter **4.0.44**; `authored_bounds_survey` lấy evaluated bevel geometry, frozen GLB export có `export_apply=false` nên dùng original positions. Max union bounds delta khoảng **8.3055 mm**; các extremum owners khác nhau. Independent oriented proxy audit: **402,482 POSITION samples / 121 IDs, 0 violations vượt tolerance 1 mm**. Đây là containment evidence, không chứng nhận an toàn/tuyến đi/fidelity. [Báo cáo chẩn đoán tại HEAD #15](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/43a3828654ca90a8a1d1a05750c4f06e36f6bba6/docs/3d-production/P507-E0-TV-BOUNDS-DIAGNOSTIC.md) giữ numeric snapshot source `6ae02b0397c88970c46618bbe5b4ba3d501edfcf`; không gán snapshot cũ cho HEAD mới. **Option A/B chưa được triển khai**; diagnostic ACCEPTED không là E0 contract correction hoặc E0 PASS.

### Issues và milestone chịu trách nhiệm

Tất cả #1–#5 xác minh vẫn **OPEN**; bảng sau là phân công trách nhiệm trong roadmap, không phải thay GitHub Milestone metadata hoặc đóng issue.

| Issue | Phạm vi chịu trách nhiệm / ảnh hưởng |
| --- | --- |
| [#1 Phòng](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/1) | **DEFERRED_FOR_M2; REQUIRED_FOR_M6**. Không chặn E0/E1/nghiệm thu chức năng một phòng P507; MT1-01 ≥3 phòng vẫn bắt buộc M6 |
| [#2 Survey/inventory](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/2) | M3 mapping/xác thực, M6 inventory/KPI; đã có nguồn USER_REPORTED/provisional cho M2, chưa bộ survey AIRC verified hoàn chỉnh |
| [#3 Nguồn/quyền](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/3) | M3 nguồn ba trạng thái; M6 nghiệm thu; quyền ảnh/nhãn/demo vẫn riêng; neutral R4 không cấp quyền raw photos hoặc real_verified |
| [#4 Galaxy AR](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/4) | M5 thiết bị AR thực, M6 KPI; chưa có evidence vật lý |
| [#5 VR](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/5) | M5 kính/protocol và M6 VR72; emulator không thay thiết bị |

Scope ba phòng/KPI, quyền AIRC, nguồn trạng thái, consent/retention/auth/quyền ghi và protocol học thuật chưa được giải quyết chỉ bằng roadmap. Không giả định có AIRC API, không tự tạo dữ liệu thật.

### Quyết định gần nhất và next action

Owner đã duyệt 2.0/P507-only/defer ba phòng tới M6/R4 functional trial; xem decision log và DoD trong ROADMAP. Guard bắt buộc báo sai lệch trước phần ngoài phạm vi; sau mỗi review PASS/PARTIAL/FAIL/BLOCKED đều commit đồng bộ ROADMAP/STATUS, đọc lại diff/HEAD và phân biệt branch/main.

1. Bàn giao **một Draft PR tài liệu**, dừng cho ChatGPT nghiệm thu độc lập. Hiện bản cập nhật tài liệu chưa ACCEPTED/chưa MERGED; không tự ghi review PASS.
2. Sau nghiệm thu, cập nhật kết luận/evidence/HEAD vào ROADMAP/STATUS, commit và ChatGPT đọc lại; owner quyết định merge/bước tiếp. Không sửa hoặc merge PR #13–#15 trong lượt này.
3. Task phát triển tiếp theo vẫn **M2: quyết định/chốt E0 validation contract correction có kiểm soát, rồi browser walkthrough E1 trên frozen R4**. Không tự tuyên bố E0 PASS, không trộn correction/runtime vào PR tài liệu, không khởi tạo milestone mới.

### Kiểm tra task tài liệu và integration

Kiểm tra local lần này: `python tools/verify_repository.py` PASS (171 files/171 local Markdown links, UTF-8/limited secret patterns/resources); `git diff --check` PASS; checker syntax và 10 Node tests PASS; 8 Python runner tests và compileall tools PASS. Kiểm bổ sung tạm ngoài repository PASS: đúng 8 file được phép/8 milestone và DoD, M0/M1 links, M2/E0/E1/visual/guard, body KPI và history không đổi, cấu trúc bảng Markdown; PyYAML 6.0.3 safe_load, giữ nguyên key set/path; 6 GitHub commit-file links tồn tại tại đúng SHA qua Git tree API. PyYAML chỉ ở `.local` ignored, không đổi dependencies. Không phát hiện schema/enum/parser consumer của project.yaml trong source/config repository; consumer ngoài repo chưa xác minh. Final HEAD/clean status/CI được chốt trong PR bàn giao; pattern scan không là security audit toàn diện, không crawl mọi external URL. Phạm vi chỉ Markdown và metadata YAML; không thay feature/CI/dependencies/frozen asset. Không chạy ứng dụng E0/E1/KPI/thiết bị trong task này; checker regression là kiểm công cụ M0, không là evidence E1. Working tree ban đầu sạch trên branch E0/E1; sau switch main, GLB local vốn ignored ở branch #15 hiện untracked. Đã giữ nguyên file và thêm exclude **chỉ local `.git/info/exclude`**, không sửa asset/.gitignore hoặc đưa binary vào commit.

PR #13 sửa chung AGENTS/README/STATUS, #14/#15 bổ sung STATUS; nguy cơ conflict/khôi phục snapshot cũ. Branch Roadmap 2.0 này là nguồn thay đổi chính sách đã duyệt. Sau merge docs, reconcile #13 rồi #14 rồi #15, giữ guard, metadata M2 và snapshot mới; chỉ đưa nội dung lịch sử/gate-specific vào đúng phần, không khôi phục PROPOSED/M0-B1 current. Đây là đề xuất cho owner khi nghiệm thu, không tự rebase/retarget/merge.

## AS-OF / HISTORICAL — snapshot 15/11/2026

Phần nguyên văn dưới đây được giữ để bảo toàn kết luận/SHA/evidence cũ. Các câu PROPOSED/chưa phê duyệt/chưa survey/PR #12 IN REVIEW là **lịch sử**, không điều khiển task hiện hành; snapshot 18/11 và Roadmap 2.0 ở trên thay cho hiện trạng cũ.

### Bản lưu 15/11 — nguồn tiếp tục tại thời điểm đó

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
