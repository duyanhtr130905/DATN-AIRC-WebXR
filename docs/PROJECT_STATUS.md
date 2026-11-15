# Trạng thái dự án — M1-C

Cập nhật15/11/2026. Root D:\Code\DATN; repository duyanhtr130905/DATN-AIRC-WebXR. Branch feat/m1-c-digital-twin-vertical-slice. M1-B merge66e166626a63285e1c49925004ec10c286ab43f2 đã xác minh.

| Milestone | Trạng thái |
|---|---|
| M0-A / M0-B1 / M0-B2 / M1-A | DONE |
| M1-B | DONE — PR#10 merged |
| M1-C | IN REVIEW — C1/C2/C3 PASS, chờ ChatGPT nghiệm thu PR |

Một branch và một PR cuối sau C1→C2→C3. [Checkpoint](18-m1-c-progress.md) ghi bằng chứng và bước tiếp; không mở PR riêng mỗi giai đoạn. Các kết quả lịch sử M1-B giữ trong [acceptance M1-B](17-m1-b-state-realtime-acceptance.md), không dùng làm PASS cho code M1-C mới.

Dữ liệu khảo sát507/inventory/ảnh/kích thước/nguồn/quyền vẫn BLOCKED; chưa có phần mềm quản lý thiết bị. Mọi fixture M1-C là synthetic, không phải507 và không nghiệm thu KPI. Giữ MT1–MT3, KPI≥3phòng và Issues1–5 mở. LocalPG BLOCKED; CI dùngPG18 riêng. Galaxy/VR physical NOT TESTED. Multi-instance/auth/retention/hosting/quyền dữ liệu chưa phê duyệt. Không visitor tracking/AI/deploy/milestone sau.


M1-C source09f3e23 đã PASS full CI:70backend unit,67PostgreSQL tests,25frontend unit,16realbrowser groups/20render samples; M0/PoC/IWER đềuPASS. [Acceptance M1-C](18-m1-c-vertical-slice-acceptance.md) và [raw evidence](evidence/m1-c-validation.json). Final HEAD checks ở PR là nguồn bàn giao hiện hành. Milestone sau M1-C NOT STARTED. Đây là synthetic vertical slice, không nghiệm thu MT1–MT3.
