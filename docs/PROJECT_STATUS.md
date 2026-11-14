# Trạng thái dự án — M0-A

Cập nhật 14/11/2026. Repo độc lập: DATN-AIRC-WebXR; local `D:\Code\DATN`; account `duyanhtr130905`; main bootstrap `b3c4f43`; nhánh `docs/m0-foundation`.

## Gate hiện tại

Bộ bàn giao Foundation & Feasibility sẵn sàng review. Scope M0-A do người dùng cho phép, framework/kiến trúc vẫn PROPOSED. Không có product frontend/backend/database/AI/RAG và không deploy.

## Đã có

Charter, requirements/KPI, risks, survey/data strategy, device/technology/UI research, architecture options, ADR template + proposed ADR, source/version index, checker độc lập, tests và PR template. Các tài liệu giữ nguyên MT1–MT3.

## Evidence và hạn chế

10 unit/DOM tests PASS; Chrome headless UI smoke PASS với native XR queries timeout và mock rejection/true riêng. Xem [evidence](evidence/m0-validation.md). Không có chứng cứ vật lý AR/VR, FPS hay KPI sản phẩm. Dữ liệu AIRC, ba phòng và quyền sử dụng chưa được xác minh.

## Handoff

[Acceptance](10-m0-acceptance.md) là checklist trạng thái; [backlog](backlog/README.md) chứa năm blocker issues #1–#5 đã tạo và đang OPEN. Validation được ghi trong evidence; commit/PR xác thực bằng GitHub và báo cáo cuối sau thao tác tạo PR. Không coi PR mở là phê duyệt của người dùng/giảng viên.

## Bước tiếp theo cần người dùng quyết định

Review PR; bổ sung đầu mối/quyền AIRC, số phòng/inventory, nguồn dữ liệu; thử Galaxy; trao đổi phương pháp nghiệm thu VR. Đề xuất M0-B gỡ blocker và duyệt PoC; chưa bắt đầu. M1 bị chặn đến khi có phê duyệt riêng và ADR được chấp nhận bằng phản hồi có thẩm quyền.
