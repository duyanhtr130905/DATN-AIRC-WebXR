# Current M2 preservation snapshot — 18/11/2026, PR21 IN_REVIEW

Owner explicitly approved private original-R4 archival and independent restore in [PR21 decision](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/21#issuecomment-6973024761). Source branch `integrate/m2-p507-issue-19`, starting HEAD `faa12d20a55a5d0dbf8e4b81cd0b1289d61f04bf`; ChatGPT's two-column M2 dependency fix retained. Main still `458569026edc917fa38d945ecd190bd4574b925f`; changes remain on Draft PR21, not merged.

PRIVATE owner-controlled [vault](https://github.com/duyanhtr130905/DATN-AIRC-WebXR-asset-vault) at `908a5cbb1f77b75b28666fd424cbd85f2aba4c1f`, Private verified before/after upload, owner-only collaborator list. Original ZIP11369216bytes/SHA256 `4255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8` matches GitHub digest; all28members preserved, six locks PASS, GLB10751036bytes/SHA256 `8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49`. No regeneration/Release/Pages/raw photos. [Preservation evidence/runbook](3d-production/P507-R4-PRESERVATION.md).

Independent clean remote restore and final HEAD regression pending. **CI_CROSS_REPO_RESTORE=BLOCKED**: source GITHUB_TOKEN not granted vault access; no PAT or secret added. Current CI still uses original expiring artifact; future automated CI restore needs separate owner decision. Issue20 DEFERRED; G1_CIRCULATION=PARTIAL; G2_VISUAL=PENDING_OWNER_APPROVAL; M2 IN_PROGRESS; M3–M7 unchanged. Next: remote restore proof → final tests/CI → ChatGPT review; Codex does not merge.

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
