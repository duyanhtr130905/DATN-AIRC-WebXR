# Trạng thái dự án — M1-A Catalog

Cập nhật14/11/2026. D:\Code\DATN; repo duyanhtr130905/DATN-AIRC-WebXR; branch feat/m1-a-catalog. Main đã có M0-B2 merge b4e4b910c9ed8cd43feeafccff66bbf3d5b6e811.

M0-A DONE, M0-B1 DONE, M0-B2 DONE. M1 chính thức bắt đầu theo yêu cầu chủ dự án; M1-A IN PROGRESS (IN REVIEW khi bàn giao PR). M1-B/M1-C NOT STARTED.

Được phép: schema Catalog rooms/objects, Alembic0001_catalog,3GET API chỉ synthetic, seed tường minh và PG tests. State/session/event/outbox, auth/retention/hosting và real data policy vẫn PROPOSED/chưa duyệt. ADR0001 ACCEPTED giữ nguyên. Không CRUD write/WebSocket/scene integration/admin.

26unit tests và lint đã PASS local; SQL offline được sinh, không thay PG migration thật. PostgreSQL local BLOCKED vì khôngDocker, không tự cài. CI sẽ kiểm migration từDBtrống/current/repeat/schema drift, constraints/READONLY/API/privacy/pagination/timezone/seed. Kết quả chốt ở [acceptance](16-m1-a-catalog-acceptance.md). Giữ hồi quy M0-A, haiPoC và app browser.

Thầy yêu cầu làm phòng507 trước; chưa khảo sát/inventory/ảnh/sơđồ/kíchthước/nguồn/quyền dữ liệu, AIRC chưa phần mềm thiết bị. KPI≥3phòng chưa đổi; không KPI MT1–MT3 được nghiệm thu từfixture1room/4objects. Galaxy ARsession chưa test, khôngkínhVR. Issues1–5 không đóng. Dữ liệu synthetic không phải507.

Sau review: ChatGPT nghiệm thu M1-A, khảo sát và quyền dữ liệu, chốt phạm vi M1-B riêng. Không tự bắt đầu M1-B/C hoặc merge/deploy.
