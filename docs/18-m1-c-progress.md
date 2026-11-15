# M1-C — Progress checkpoint

Cập nhật15/11/2026. Branch feat/m1-c-digital-twin-vertical-slice, HEAD ghi nhận khi bắt đầu:66e166626a63285e1c49925004ec10c286ab43f2. Chỉ một branch/PR; chưa tạo PR.

## C1 — IN PROGRESS

Workspace/Git sạch đã xác minh; main fast-forward có merge M1-B. Đang triển khai snapshot protocol2 opt-in (?protocol=2) với start/chunk/end, consistent PostgreSQL view và giới hạn512states/2MiB snapshot/32KiB frame. Protocol1 mặc định giữ compatibility M1-B cho<=32states. DB đóng trước network send; revalidate visibility và abort nếu queuepressure/permission thay đổi. Durable replay sau watermark.

Tests mới sẽ có0/1/32/33/41/80/120states, malformed chunks/atomic assembler, writer/visibility/disconnect/race/capacity vớiPG18/TCP thật. LocalPG vẫnBLOCKED nếu khôngDocker; khôngSQLite hoặc testPASS giả. Chưa kết quả C1 runtime; C2/C3 NOT STARTED.

Files dự kiến: apps/api/modules/state/read.py, realtime/router.py, snapshot protocol module vàtests, CI branch trigger/docs14. Không migration/schema mới hoặc sửa0001/0002.

Bước tiếp: hoàn thiện C1→lint/unit→push checkpoint C1→đợi actualPG/TCP/M1-BregressionCI PASS→commit evidence gate trước khi bắt đầu C2. Nếu quota dừng, giữ working tree/commits, đọc file này vàgitlog; không reset/main/PRriêng.
