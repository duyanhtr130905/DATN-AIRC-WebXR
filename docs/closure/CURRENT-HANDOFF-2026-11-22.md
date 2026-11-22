# HỒ SƠ TIẾP NỐI ĐATN — trạng thái mới nhất ngày 22/11/2026

> **Điểm vào ưu tiên cho cuộc chat mới.** Đây là snapshot trạng thái của repo tại ngày 22/11/2026, không thay thế GitHub live. Trước khi code/merge, phải kiểm tra HEAD và issue/PR thực tế. Tài liệu này chỉ lưu yêu cầu và bằng chứng đã có; **không phải lệnh tự động triển khai R5**.

## 1. Một câu tóm tắt

DATN-AIRC-WebXR đã có demo P507 Web 3D/XR synthetic trên Windows; người dùng đã tự chạy và nêu 7 nhóm yêu cầu sửa bố trí/collider/ghế. **Prompt cập nhật P507 đã được soạn trong chat nhưng người dùng xác nhận CHƯA gửi Codex; chưa có code, PR hay kết quả test cho thay đổi này.** [Issue #33](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/33) là hồ sơ yêu cầu đang **chờ 7 xác nhận**. Đồng thời [PR #32](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/32) đóng backlog tổng hợp M0–M5 còn **DRAFT/chưa merge** vì thiếu ZIP Windows exact-HEAD cho final acceptance, dù sửa lỗi M4 P1 đã được reviewer xác nhận về mã/CI.

## 2. Trạng thái code/PR ở thời điểm ghi

- Repository: `duyanhtr130905/DATN-AIRC-WebXR`; local owner `D:\Code\DATN`. Baseline main trước các commit tài liệu 22/11: `735eebc0925a851e04f9bd1821c94bca46930597`.
- [PR #31](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/31) M5 synthetic DEV Web3D + Chrome/IWER XR đã **MERGED**, chỉ **TECHNICAL_ACCEPTED**, hardware AR Galaxy A17 #4 và VR HMD #5 vẫn BLOCKED.
- [PR #32](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/32), branch `feat/post-m5-m0-m5-gap-closure`, HEAD được kiểm tra `f96df72d50c3f05796a6bc528f0f0ef77abbf892`, **DRAFT/OPEN/NOT MERGED**. Reviewer [#5987391250](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/32#pullrequestreview-5987391250) xác nhận code/CI PASS cho queue M4 legacy 128 event + đúng 1 terminal và migration 0007 ordinal 501; 56 web, 75 API, 89 PG trên GitHub CI, 13 checks SUCCESS (bao gồm 2 status-only), 2 privileged vault SKIPPED. Đã đối chiếu artifact Linux PG 3 phiên/143 sự kiện, oracle 50 phiên/1.050 server+client, không thừa/thiếu/trùng; Windows 88/89 dưới tải trên head cũ vẫn lưu lịch sử.
- **Gate trước merge PR #32:** thiếu quyền truy cập thực tế vào `PR32-FINAL-f96df72-evidence.zip` tại đường dẫn máy Windows do Codex báo. Owner cần tải **ZIP sanitized thực sự lên chat** để reviewer kiểm SHA, R4 E0/E1 15/15, Admin/P507 2/2, Chrome/IWER R4 9/9 và báo cáo Windows exact-HEAD. Không báo kỹ thuật M2/M5 full/hardware PASS thay vì điều này. CI M5 thường chỉ có 2 fallback/mock.
- [Issue #30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30) tổng hợp G0–G12 vẫn OPEN; code chính ở PR #32 chưa được hợp nhất. Các blocker thật: M3 dữ liệu và rights #2/#3, P507 fidelity/circulation #20, private vault App #22, AR #4/VR #5, chính sách khách thật, M6 3 phòng và KPI MT1–MT3.
- [Issue #20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) là backlog M2 cũ về lối đi/sai kích thước/sai vị trí; sau demo 22/11 được owner yêu cầu xem lại, liên kết mới #33. Frozen R4 và hashes là **immutable history**; R5 hoặc overlay cần version/owner visual review, không thay đổi tài liệu khảo sát hay claims đã nghiệm thu.

## 3. Yêu cầu chỉnh sửa P507 do chủ dự án vừa đưa ra — CHƯA TRIỂN KHAI

| Nhóm | Chỉ dẫn của chủ dự án |
| --- | --- |
| Bàn cụm 1 | Thêm 1 lẵng hoa, 1 bộ ấm chén; cuối dãy gần cửa sổ đặt 1 máy in + 2 máy tính, hướng phù hợp người ngồi |
| Bàn cụm 2 và 3 | Mỗi cụm thêm 2 máy tính trên bàn phía trong gần cửa sổ, hướng người ngồi. Tổng cộng 6 máy tính mới |
| Lối đi | Mở lối giữa hai hàng ghế ở các cụm bàn; ghế hiện cản đường, collider/navigation phải theo trạng thái thật của ghế |
| Poster | Các poster hình chữ nhật dọc quanh tường, lúc đầu dùng khung rỗng được |
| Góc kệ | Dời thùng rác, bảng tin trắng, kệ giày về gần kệ đựng đồ; tăng chiều cao và chiều dài kệ 50%, giữ chiều rộng. Tầng #3 chứa 4 bình nước, tầng #2 có đồ |
| Đồng hồ | Treo đồng hồ trên tường phía trên tủ trưng bày |
| Ghế | Tương tác kéo ghế ra → ngồi → đứng dậy → cất vào bàn; khi cất mở lối đi, đồng bộ mesh/collider và UI |

Mức độ đã biết: mô tả định tính từ người dùng sau khi chạy demo. **Chưa có ID ứng với các cụm bàn, tọa độ/số đo thực địa, thiết kế tương tác đầy đủ, phạm vi bản phát hành hoặc quyền công bố.** Chưa được tự thay yêu cầu bằng bố trí suy luận.

### 7 câu hỏi phải chốt trước khi gửi Codex

1. Cụm bàn **#1, #2, #3** ứng với những cụm hàng/ID nào? Gửi ảnh/sơ đồ đánh số.
2. “Bàn phía trong gần cửa sổ” thuộc bàn/ID nào ở cụm 2/3? Hướng máy tính và vị trí màn hình đúng theo hướng người sử dụng cần gì?
3. Bao nhiêu poster, trên các tường nào, kích thước/khoảng cách? Có tránh bề mặt nào?
4. Tầng 2/3 kệ đếm dưới lên hay trên xuống? Đồ tầng 2 là đồ cụ thể hay placeholder?
5. Bố cục/thứ tự thùng rác–bảng tin trắng–kệ giày khi dồn sát kệ? Xác nhận logical ID kệ đựng đồ và tủ trưng bày.
6. Ghế được tương tác **tất cả hay một số**; click đổi trạng thái hay menu Lấy ra/Ngồi/Đứng/Cất? Mặc định các ghế được cất chưa?
7. Đây chỉ là **demo/provisional override** hay **bản revision mô hình chính thức** (cần đo, nguồn khảo sát, visual signoff riêng)?

## 4. Quy tắc làm việc tiếp

1. **Ưu tiên trả lời 7 câu hỏi** bằng ảnh/sơ đồ và định danh thật trong mô hình; đừng gửi prompt nháp cũ cho Codex như đã chốt.
2. Cũng cần đóng bước nghiệm thu còn thiếu của PR #32 bằng artifact sanitized (hoặc đánh dấu rõ không có và quyết định phạm vi kỹ thuật), review HEAD live/CI lần cuối, không auto merge khi thiếu gate.
3. Khi yêu cầu #33 đủ rõ và owner chủ động giao Codex, soạn **prompt chính thức cập nhật** dựa trên answers + layout/IDs của repo. Triển khai **trên nhánh mới sau khi ổn định PR #32**, một Draft PR, không làm trên main hoặc bản R4 frozen; versioned `R5 proposal` hoặc scene overlay rõ ràng.
4. Khi thử P507, chạy demo DEV loopback: `apps/web/index.html` nằm trong `apps/web`; từ repo root `npm run dev --prefix apps/web -- --port 5173 --strictPort` có thể gây 404 nếu Vite dùng cwd sai. Cách chắc chắn đã hướng dẫn: `Set-Location D:\Code\DATN\apps\web` rồi `npm run dev -- --port 5173 --strictPort`. URL `http://127.0.0.1:5173/?mode=p507-visit`; R4 phải validate/verify qua `experiments/p507-webxr/validate_asset.py --prepare` và `verify_export_reference.py`. M4 offline demo `?mode=offline`, M3 Digital Twin `?mode=p507`, Admin `?mode=admin`; các màn có backend cần DB và config riêng theo [Windows demo runbook trong PR #32](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/blob/f96df72d50c3f05796a6bc528f0f0ef77abbf892/docs/closure/WINDOWS-DEMO.md).
5. Đừng lẫn P507/demo với 3 phòng AIRC thực hay dữ liệu thật. Không đụng private vault credentials, không công khai GLB/survey, không bật visitor tracking, không khai hardware FPS đạt KPI chỉ từ IWER/SwiftShader.

## 5. Gợi ý yêu cầu cho cuộc chat mới

> Đọc `docs/closure/CURRENT-HANDOFF-2026-11-22.md`, [Issue #33](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/33), [Issue #20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20), [Issue #30](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/30), PR #32 và trạng thái `main` live. Tôi muốn tiếp tục chốt 7 chi tiết bố trí và tương tác ghế P507 trước khi giao Codex, đồng thời bảo toàn gate nghiệm thu PR #32. **Chưa triển khai yêu cầu R5; không tự đoán hay sửa frozen R4.**

---

**Lưu ý đồng bộ:** Tài liệu này là checkpoint có ngày/giờ. Những nhận xét “chưa merge” hoặc SHA cụ thể cần được kiểm tra lại từ GitHub trong cuộc chat mới. Tài liệu lịch sử `ROADMAP.md` và `PROJECT_STATUS.md` chứa nhiều đoạn **AS-OF**; khi có PR mới merge cần cập nhật kết luận hiện hành chứ không sửa/bóp méo nội dung nghiệm thu trước đó.
