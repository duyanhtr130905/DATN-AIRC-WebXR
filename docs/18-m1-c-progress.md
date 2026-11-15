# M1-C — Progress checkpoint

Cập nhật15/11/2026. Branch feat/m1-c-digital-twin-vertical-slice, HEAD ghi nhận khi bắt đầu:66e166626a63285e1c49925004ec10c286ab43f2. Chỉ một branch/PR; chưa tạo PR.

## C1 — IN PROGRESS

Workspace/Git sạch đã xác minh; main fast-forward có merge M1-B. Đang triển khai snapshot protocol2 opt-in (?protocol=2) với start/chunk/end, consistent PostgreSQL view và giới hạn512states/2MiB snapshot/32KiB frame. Protocol1 mặc định giữ compatibility M1-B cho<=32states. DB đóng trước network send; revalidate visibility và abort nếu queuepressure/permission thay đổi. Durable replay sau watermark.

Tests mới sẽ có0/1/32/33/41/80/120states, malformed chunks/atomic assembler, writer/visibility/disconnect/race/capacity vớiPG18/TCP thật. LocalPG vẫnBLOCKED nếu khôngDocker; khôngSQLite hoặc testPASS giả. Chưa kết quả C1 runtime; C2/C3 NOT STARTED.

Files dự kiến: apps/api/modules/state/read.py, realtime/router.py, snapshot protocol module vàtests, CI branch trigger/docs14. Không migration/schema mới hoặc sửa0001/0002.

Bước tiếp: hoàn thiện C1→lint/unit→push checkpoint C1→đợi actualPG/TCP/M1-BregressionCI PASS→commit evidence gate trước khi bắt đầu C2. Nếu quota dừng, giữ working tree/commits, đọc file này vàgitlog; không reset/main/PRriêng.


Checkpoint implementation C1: commit feed865 đã push.55unit tests PASS local; lint/compile/verifier/diff PASS.60PostgreSQL tests (12C1 mới) đang chờ CI, local BLOCKED thiếuPG. V2 wakeup queue coalesce và SQL durable replay authoritative. C2/C3 chưa bắt đầu.


C1 gate intermediate: commit404a862 CI [43671389080](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43671389080) PASS cả API PostgreSQL và web/browser. Fixture registration đã sửa;61PGtests gồm13C1 và48M1-A/B tests đã chạy, không skip. Review bổ sung receive READ_ONLY lúc chunking và safe-integer guard cho mọiv2message;58unitPASS local. Những bổ sung này cần finalC1CI trước chuyểnC2.


## C1 — PASS / C2 — IN PROGRESS

Final C1 source d62a935, [CI43671658702](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43671658702) PASS API/PG vàweb/typecheck/build/unit/browser.62unit và62PGtests, khôngskip. Source5a13cf2 JUnit đã tải kiểm tra62tests/0error/0failure/0skip, finald62 chỉ tăngoraclecoverage; finalCI cũngPASS.0/1/32/33/41/80/120states quaPG18+TCP,513capacityrejected; snapshot race/hide/overflow/disconnect/restart vàM1B regression. Protocol2 READ_ONLY vàJSsafeintegerreviewfixed. Không đổi schema/dependency. C2 bắt đầu sau gate này; C3 NOT STARTED.

Bước C2: typed runtimevalidated REST + UUID adapter + pure reducer + lifecycleWS +LiveScene/Panel; giữ offline foundationDEMO explicit, không fallbacklive giả. Tiếp theo seed20objects/41statesguarded và browserintegration.


C2 candidate: app defaultlive, explicitofflinefoundation; typedREST pagination/runtimevalidation/bounds/cancel; reducer atomic snapshot+sequence/version; boundedWS lifecycle; UUIDsceneadapter vàmeshcolorstates; guardedfixture20objects/41states vàsecondroom. Local typecheck/build PASS,21unitPASS,7Chrome foundation scenariosPASS (realChrome157WinsoftwareWebGL; backendwithoutDB). NewPGbrowserhappy path NOT RUN local, cần actualCI trướcC3. Files đang sửa: apps/web src/api/app/features/scene/styles/types/tests/vite, APIvertical_seed/test_vertical_slice, appCI/readmes/acceptance. Bước tiếp:pushC2candidate→actualPG/ChromeCI→sửalỗi→commitC2gate→C3.


C2 intermediate734c1e7 [CI43672507643](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43672507643) PASS cảjobs:62unit/63PG bao gồm actualChrome5scenarios. Đã tải report/screenshots và xem desktop/390px, actualmesh đỏmaintenance +Panelv2 hiện đúng. Sửa thêm deadline/cancel khi bodytransportignoreabort (testRED→GREEN), optionalmetadata empty/null hợp lệ theo backend;24frontendunitPASS local. Cần finalC2CI sau sửa trướcC3. C3 NOT STARTED.
