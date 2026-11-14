# M1-B — State management và realtime synchronization

Ngày14/11/2026, branch feat/m1-b-state-realtime từ M1-A merge99f65377746a0eb7c924b6493db3a8e4680a444d. Chỉ dữ liệu SYNTHETIC, không mô hình/dữ liệu507 hoặc KPI đạt. M1-C NOT STARTED.

## Quyết định triển khai

Bốn bảng mới: current_states, state_history, room_state_cursors, outbox; revision0002_state_realtime sau0001_catalog (0001 giữ nguyên). Current target_room_id/object_id dùng CHECK one-target vàmappingstate_type; composite FK(object_id,room_id) yêu cầu UNIQUE objects(id,room_id) bổ sung trong0002 để enforce room scope. Không thay Catalog columns hoặc dữ liệu. History append-only trigger, unique(state_id,version), RESTRICT; JSONB/value size bounds, timestamptz, indexes.

State service chỉsynthetic, khóaRoom→Object→State→Cursor và kiểm expected_version (0create), tăngversion/roomsequence trong cùng transaction với current/history/outbox. CAS UPDATE expectedversion là hàng rào thêm. Caller sở hữu transaction; không commit/publish trong service; rollback đồng thời4thayđổi. Không Python lock làm concurrency guard. Không dùng ORM version_id_col vì service dùng explicit transactional compare+locks, SQLAlchemy cảnh báo ORM version counter không bảo vệ bulkSQL.

Outbox claim FOR UPDATE SKIP LOCKED +lease5s vàcommit claim trướcnotify; khônggiữDBconnection khichờclient. Finish theoowner, attempts tốiđa5, exponentialbackoff2–30s, exhausted giữrecord đểđiềutra/resync, khônginfinitepublishretry. Crash đểleaseexpire, reclaims cóthểtrùng; đây là at-least-once notification processing, không exactlyonce hoặcclientACK. published_at nghĩa xửlý notificationhint, không chứngminh mọi browser nhận/render. Durable rows đượcgiữđểreplay, chưaretentionpurge.

MộtAPIprocess/broker RAM; brokerchỉwake room, khônggiữrawpayload. WSregister trước REPEATABLE READ snapshot; watermark từcursor cùngsnapshot. Tail đọc durable published outbox sauwatermark, luôncheck target/parent visibility. Gap/backpressure hoặcpendingpublication>2s →resync.required vàclose1013, reconnectsnapshot lấycurrentstate; khônggiữstatecũvôhạn khi exhausted. Dedupe incomingsequence<=currentignore, +1apply, gapresync. Freshsnapshotkhi reconnect làbaseline, chưaresume-token/cursorretentioncontract.

## Endpoints/giới hạn

GET /api/v1/rooms/{room_id}/states; GET /api/v1/objects/{object_id}/states; GET /api/v1/objects/{object_id}/states/{state_type}/history. UUID+boundedpagination, typedresponse, source/parentfilters, safeerrors. room_schedule thuộcRoom, equipment_status/exhibit_info thuộcObject. ChỉbaselineJSON schemas activity/status, equipmentstatus, exhibit title/text, khôngsensorAPI hoặcnguồnthật.

WS /ws/v1/state?room_id=UUID, Origin phải thuộc explicitCORS origins, thiếuOriginbịchặn. snapshot/state.updated/resync.required/error/heartbeat cóschema_version,message_id,room_id,sequence,timestamp, statecóversion/source timestamps. Client gửi messagebịREAD_ONLY/close1008, khôngwrite. Max32connections,8wakequeuedtokens/client,32states/snapshot,32deltas/replay,256KiBoutgoing,sendtimeout1s. Uvicorn runbook/test đặtincoming8KiB/queue1. KhôngsyncSQL trêneventloop: to_thread vớishortDBscopes. Shutdown dừngdispatchertrướcpooldispose vàtry/finallydispose khilỗi. Multiinstance/multipleAPIworkers NOT TESTED/NOT SUPPORTED; two claimworkers đượctestDBclaims khôngđồngnghĩa multiinstancebroadcast.

## Checklist tạm thời trướcCI

| Mục | Trạng thái | Bằng chứng |
|---|---|---|
| Unit/lint/compile | PASS |37unit local,ruff/compileall exit0; warninghttpx đãbiết |
| PostgreSQL0001→0002/constraints/concurrency | NOT RUN | chờCI PG18; localkhôngDocker/PG |
| State readAPI/history/visibility | NOT RUN | chờPGintegration |
| Outbox failure/retry/crash/claims | NOT RUN | chờPGintegration |
| ActualTCP WebSocket/snapshot/race/reconnect/resync | NOT RUN | chờPG+Uvicorn+websockets17.4 |
| Metrics20samples | NOT RUN | chỉghiNUMkhiCI thựcsựchạy, artifact.local/m1-b-metrics.json |
| Catalog/frontend/M0/PoCregression | NOT RUN | chờCIHEADmới |
| Secrets/links/whitespace | NOT RUN | kiểmchốt trướcpush |
| LocalPostgreSQL/hardware | BLOCKED/NOT RUN | khôngtựcàiPG, khôngGalaxy/kính hoặcsource-to-render |

Reviewđộclập đãtìm2lỗiP2: latestexhausted gâyWSstalevôhạn vàstopfailure làmngăndispose. Đãsửa stallresync vàtry/finally, cótests. KếtquảPG/TCPcuối sẽbổsung sauactualCI, khôngmockthaybằngchứng.

## Nguồn và điều còn mở

Kiểm14/11/2026: [SQLAlchemy versioning](https://docs.sqlalchemy.org/en/21/orm/versioning.html), [PG locking](https://www.postgresql.org/docs/18/explicit-locking.html), [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/), [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html). Giữdependencybaseline; thêmwebsockets17.4 release30/10/2026/Python>=3.11/BSD3 để actualTCP vàUvicorn SansIO, hashlock. Compatibility sẽkiểmactualCI.

Chưa dữliệu/quyền507, authprovider/writeauthorization, retention/hosting, scope≥3phòng/VRacceptance. Không publicmutation/admin/session-eventvisitor/AI/sceneintegration. Issues1–5khôngđóng, KPIgiữnguyên. M1-C sauphêduyệt: clientadapter/reducer/version-resync vàsceneintegration, đo render timestampthật; không dùngmetricsbackendđểtuyênbố≤5s source-to-render.
