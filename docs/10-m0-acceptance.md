# 10 — Nghiệm thu M0-A

Ngày 14/11/2026. Trạng thái: bộ bàn giao sẵn sàng review; không tự phê duyệt M0, không merge PR, không bắt đầu M1. [Evidence](evidence/m0-validation.md).

## Checklist deliverables

- [x] Workspace độc lập `D:\Code\DATN`, đã kiểm tra trống trước khởi tạo; không tạo thư mục con repo.
- [x] Repo PRIVATE AIRC mới trên account đã xác minh, bootstrap main; branch `docs/m0-foundation`.
- [x] README, AGENTS, .gitignore, PR template và bộ tài liệu 01–10.
- [x] KPI giữ nguyên, có cách đo và bằng chứng cần thu; không tuyên bố đạt KPI sản phẩm.
- [x] Checklist survey/phòng/20 object, data source/provenance/rights và stable ID đề xuất.
- [x] Nghiên cứu thiết bị, A/B công nghệ/version/license/maintenance, UI/UX và kiến trúc có nguồn.
- [x] ADR template và ADR công nghệ ở PROPOSED; chưa có ACCEPTED.
- [x] Checker tĩnh secure context/XR/modes, xử lý rejection/timeout, không tự camera hay network ngoài.
- [x] 10 unit/DOM tests + Chrome desktop smoke thật; giới hạn bằng chứng được nêu rõ.
- [x] Năm GitHub blocker issues #1–#5 đã tạo, đọc lại đúng nội dung và đều OPEN.
- [x] Link nội bộ/UTF-8, mẫu secret và diff whitespace đã kiểm tra; description PR đủ bảy phần đã chuẩn bị.

URL issues tại [backlog](backlog/README.md). Thao tác bàn giao cuối là commit/push nhánh và tạo PR mở vào main; URL PR/head SHA và kết quả đối chiếu live được cung cấp trong báo cáo cuối sau khi GitHub trả kết quả. Tài liệu không tự dự đoán số PR hoặc tự phê duyệt nghiệm thu.

## Chưa thể nghiệm thu

- BLOCKED: số phòng thực và quyền khảo sát/công bố; inventory và nguồn ba loại trạng thái chưa có.
- NOT TESTED: Galaxy thực; BLOCKED model iPhone; thiếu kính cho VR và mục tiêu 72 FPS.
- NOT RUN: latency/FPS/session recovery/99%/50 phiên/≥15 người; chưa có sản phẩm.
- PROPOSED: phương pháp đo chi tiết, renderer A/B, backend/DB/realtime, schema, UX, auth, hosting và retention.

Tài liệu hoặc checker không gỡ các blocker vật lý. Không chấp nhận dữ liệu mô phỏng như bằng chứng phòng/thiết bị thật.

## Đề nghị ChatGPT/chủ dự án nghiệm thu

1. Review traceability MT1–MT3, risk register, sources và test evidence; phân biệt source verification, mock, desktop runtime và physical evidence.
2. Kiểm tra PR diff chỉ chứa nền tảng M0 và utility, repo private/main/origin đúng, không có tài sản dự án cũ.
3. Xác nhận ưu tiên gỡ năm issues, người phụ trách và đầu mối AIRC; duyệt protocol/nguồn/quyền trước dữ liệu thật.
4. Chọn hướng UX để nghiên cứu tiếp và quyết định có cho phép PoC A/B sau M0 hay không. Việc review M0 không tự chốt framework/kiến trúc.
5. Giữ PR mở đến khi được nghiệm thu; Codex dừng sau bàn giao. M0-B/PoC chỉ là đề xuất, không thực hiện tự động.

## Bổ sung nghiệm thu review fixes P1–P4

- [x] Workflow read-only với PR main/push docs/m0-foundation; syntax/unit/verifier/Python/diff checks, browser job và artifact allowlist.
- [x] Runner portable Windows/Linux, CHROME_BIN/PATH, report expected/actual/status; local Chrome và missing-browser scenario đã chạy lại.
- [x] [Screenshot 390px thật](evidence/checker-390.png) review được; viewport emulation, không phải Galaxy vật lý.
- [x] Thông tin trao đổi người dùng về phòng 507, inventory và chưa có phần mềm thiết bị được ghi rõ provenance; KPI không thay đổi, admin manual PROPOSED.
- CI GitHub: kết luận phải lấy từ run thật sau push; trạng thái live và URL run ghi ở phần bàn giao/PR. Không tự tick PASS trước khi chạy.

PR hiện tại là [#6](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/6); sửa ngay trên docs/m0-foundation, không tạo PR mới. Các blocker thực địa chưa được gỡ.
