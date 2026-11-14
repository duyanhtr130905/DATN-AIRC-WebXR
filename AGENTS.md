# Quy tắc làm việc — DATN AIRC WebXR

## Phạm vi và an toàn

- Root duy nhất: `D:\Code\DATN`. Remote duy nhất được phép ghi: `https://github.com/duyanhtr130905/DATN-AIRC-WebXR.git`.
- Không truy cập, đọc, chỉnh sửa, sao chép, fork hay dùng dữ liệu/mã/tài liệu của KLTN-Factory-Agentic-DT. Không dùng repository cũ làm template.
- Trước mọi thao tác ghi GitHub: kiểm tra `Get-Location`, `git rev-parse --show-toplevel`, `git remote -v`, `git branch --show-current`, `git status --short`, diff và secret. Sai root/remote thì dừng.
- Không force push, merge PR, xóa nhánh/repo, thay visibility, deploy hoặc bắt đầu M1 nếu chưa được yêu cầu. Không sửa Git global config; không cài công cụ hệ thống nếu không cần.
- M0 chỉ tài liệu nghiên cứu và công cụ capability check độc lập; không scaffold sản phẩm, database, AI/RAG. Không tự chốt framework, schema, kiến trúc hoặc thay KPI.

## Quy trình

1. Đọc README, `docs/PROJECT_STATUS.md`, task hiện hành và ADR liên quan; giữ thay đổi người dùng.
2. Branch theo task; M0 dùng `docs/m0-foundation`, PR vào `main`. Commit nhỏ, mô tả đúng nội dung.
3. Ưu tiên nguồn chính thức; ghi URL, ngày truy cập, phiên bản và giới hạn. Ghi VERIFIED/PROPOSED/BLOCKED/NOT TESTED đúng nghĩa.
4. Chỉ sửa trong phạm vi task. Thay đổi kiến trúc đã duyệt cần ADR và phê duyệt mới; không ghi ACCEPTED khi chưa có người duyệt.
5. Test tương xứng; `node --check tools/webxr-capability-check/checker.js`, `node --test tools/webxr-capability-check/tests/checker.test.cjs`, `python tools/verify_repository.py`, `git diff --check`. Chạy browser smoke khi có môi trường.
6. Không giả mạo kết quả: test mock khác browser thật, emulator khác kính, capability khác AR session. Test không chạy ghi NOT RUN và lý do; thiết bị không có ghi NOT TESTED.
7. Không commit ảnh/người/serial, token, `.env`, raw survey hoặc session có định danh. Cất dữ liệu thực hạn chế quyền ở nơi được AIRC chấp thuận, ngoài Git.
8. Cập nhật status, acceptance, evidence; kiểm tra link, diff và secret trước commit/push. Tạo PR có summary, files, findings, tests, limitations, questions và next milestone proposal. Không tự coi review AI là phê duyệt của giảng viên/người dùng.
