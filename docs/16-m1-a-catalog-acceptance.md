# Nghiệm thu M1-A — Database schema và Catalog API

Ngày14/11/2026, branch feat/m1-a-catalog; base merge M0-B2 b4e4b910c9ed8cd43feeafccff66bbf3d5b6e811. Chưa tự merge/deploy/M1-B/C. Bảng sẽ chốt theo actual CI sau push.

| Mục | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| Schema rooms/objects, ORM tách response | PASS | models + revision0001_catalog, UUID/FK/RESTRICT/unique/CHECK/JSONB/timestamptz/indexes; chưa runtime localPG |
| Alembic offlineSQL | PASS | unit sinh DDL2bảng, không seed; không thay migrationPG |
| Lint/compile/unit | PASS |26unit,ruff,compileall exit0; warninghttpxTestClient giữ nguyên |
| MigrationPG từdatabase trống/current/repeat/drift | NOT RUN | chờCI; khôngSELECT1-only claim |
| PG constraints/timezone/seed/API/pagination/privacy | NOT RUN | chờCI riêng, khôngSQLite |
| API read-only/validation/empty/no publicwrite | PASS | unittests + OpenAPI; PGreal queries chờCI |
| Seed dev/test guard/idempotency | NOT RUN | unit guardPASS, PGidempotency chờCI; khôngstartupseed |
| LocalPostgreSQL | BLOCKED | khôngDocker/PG, khôngtựcài |
| M0-A/PoC/app regressionCI | NOT RUN | chờCIHEADmới |
| Secret/link/whitespace/YAML | NOT RUN | chờcheckchốt |
| Dữ liệu thực/KPI/ARVRhardware | NOT RUN | thiếu survey/quyền/thiết bị |

## Thiết kế và bằng chứng cần kiểm

[Model](13-data-model.md), [contracts](14-api-contracts.md), [runbook](../apps/api/README.md). Initial revision0001_catalog không DMLseed, khôngcreate_all. DBCLI chỉloopbackprojectdev/test cóconfirmation/current_database. CI chỉbase airc_foundation_test đượcACK, tạodatabasenewUUID mỗiPGtest; khôngDROP/reset, serviceCI disposable. Downgrade bịchặn, NOTRUN.

Unit test mock táchPGthật: response schemas, cursor malformed/scope, 404/422/405, metadata filtering, noDB503, seedwrongDBguard và offlineDDL. PGsuite kiểm emptyschema/head/repeat/alembiccheck/constraints/index/FKRESTRICT, duplicateID/code,invalidsource/FK/metadata/transform/nulls, timezone,READONLY/sessionreturn, fixtures/idempotency/collision, multiple rooms/pagination/exclusion/privatefields. Chỉsyntheticfixture được côngbố; negativeprovenancelabels trongDBtest không dữliệuthật.

Independent review phát hiện parentvisibility race ở listobjects; sửa JOINRoom/source_kind trongcùngSQL vàthêmPGregression, khônggiảmtest. Chờ reviewclosure/CI.

## Giới hạn và quyết định tiếp

Catalog schema baseline đượcphéptriểnkhai, khôngtoànbộDigitalTwin schema. Transform/domainmetadata, state/session/event/outbox schema vẫnPROPOSED. Khôngsceneintegration/frontendredesign/publicwrites/authgiả/WebSocket/admin/AI. Không dữ liệuAIRC/507thật; không đạt≥20objects/≥3rooms hoặcKPI khác. Authprovider, retention, hosting, source/quyền, scopephòngcuối vàVRacceptance chờduyệt; Issues1–5 mở.

Đềxuất M1-B sauphêduyệt: state types/version/history vàstate read contracts, outbox/reconnect concurrency tests; chỉxemxétwrite khi operatorauthorization vàdata rightsđượcchốt. Sceneintegration riêngM1-C. Chưa tựtriểnkhai cácphầnđó.

## Lịch sử CI ban đầu

[Push run43579935413](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43579935413) trên8e603b5:21PGtests PASS,1testmigration FAIL vì assertion đọcstdout sai stream, trong khi Alembic thực tế in0001_catalog(head). Đã đổi sang Config(stdout=StringIO) để kiểm đúng output; không bỏ assertion/current/repeat/drift. Kết quả PGtoànbộ cầnCIrerun sau sửa. Review còn phát hiện queryparameter có thểghiđè host/dbname trong testURL; đãrejecturl.query vàcheckcurrent_database trướcCREATEDATABASE, thêm3unitnegative.
