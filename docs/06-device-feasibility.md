# 06 — Device feasibility

Ngày kiểm tra nguồn: 14/11/2026. [Sổ nguồn](research/sources.md) ghi URL và cách kiểm tra lại. Source verification khác kiểm thử vật lý.

## Galaxy A17 5G

**VERIFIED ở cấp tài liệu:** [danh sách Google ARCore](https://developers.google.com/ar/devices) có dòng Samsung Galaxy A17 5G, kèm Supports Depth API. Đây không phải kết quả thử máy người dùng và không chứng minh Depth qua WebXR. Chưa biết model code/variant, OS, Chrome hoặc phiên bản Google Play Services for AR trên máy cụ thể: **NOT TESTED**.

[Google WebXR requirements](https://developers.google.com/ar/develop/webxr/requirements) yêu cầu secure context, trình duyệt WebXR tương thích và thiết bị ARCore có Google Play Services for AR cài/bật. Android Emulator không được nguồn này coi là nền tảng WebXR hỗ trợ. Truy cập trang HTTP bằng IP LAN không tương đương localhost của điện thoại.

## Quy trình thực tế

1. Ghi model code (không ghi IMEI/serial), Android/One UI, Chrome version và Play Services for AR version; đối chiếu danh sách Google lần nữa.
2. Dùng Chrome Android cập nhật, cài/bật Play Services for AR nếu thiết bị cho phép; không sideload để ép hỗ trợ.
3. Chạy [checker](../tools/webxr-capability-check/README.md) từ localhost điện thoại qua USB forwarding, hoặc HTTPS có chứng chỉ được thiết bị tin cậy. Không vô hiệu hóa bảo mật Chrome.
4. Bấm kiểm tra; ghi secure context, XR API và hai mode, ngày giờ, môi trường. Không có bước nào mở camera trong checker.
5. Nếu `immersive-ar=true`, chỉ ghi “API báo hỗ trợ”. Sau M0, với quyền người dùng, thử [WebXR sample chính thức](https://immersive-web.github.io/webxr-samples/) bằng nút vào session; test permission denied, tracking, hit-test nếu cần, thoát và resume. Sample có thể xin camera, là bước riêng và chưa thực hiện.
6. Nếu false/error, kiểm tra secure context/permission policy/Play Services/browser trước kết luận. Không suy ra lỗi phần cứng từ một lần false. Lưu ảnh đã che thông tin riêng tư; không đưa lịch sử duyệt web hoặc định danh máy lên Git.

## iPhone

Model và iOS/Safari chưa xác định: BLOCKED. Không khẳng định WebXR immersive-ar hỗ trợ hoặc không hỗ trợ toàn bộ iPhone chỉ từ tên hệ điều hành. Cần runtime detection và thử trên máy thật.

[Apple Quick Look](https://developer.apple.com/quick-look-gallery/) trình bày USDZ trên Safari/iPhone và đặt object trong AR. **PROPOSED:** Web 3D là luồng chung, Quick Look/USDZ là fallback xem một object nếu máy tương thích. Cần export riêng và kiểm tra scale/material; ranh giới session và event callback khác WebXR, không hứa lưu đầy đủ tương tác bên trong Quick Look. Không dùng fallback làm bằng chứng đạt hỗ trợ WebXR AR.

## VR emulator và kính thật

[React Three XR development setup](https://pmndrs.github.io/xr/docs/getting-started/development-setup) có emulator dựa IWER; [Meta IWSDK](https://developers.meta.com/vr/documentation/iwsdk/guides/overview/) cũng có emulation. Emulator hỗ trợ thử state/input/navigation trên desktop; không chứng minh binocular comfort, controller thật, tracking, passthrough, GPU/headset FPS hoặc refresh rate.

Không có kính: NOT TESTED toàn bộ VR vật lý và BLOCKED mục tiêu ≥72 FPS. Trao đổi giảng viên về việc mượn kính hoặc phương án nghiệm thu được ghi rõ; không tự hạ KPI hoặc thay bằng emulator.

## Ma trận thiết bị hiện tại

| Môi trường | Điều biết được | Chưa nghiệm thu |
| --- | --- | --- |
| Galaxy A17 5G | có tên trong danh sách ARCore chính thức | checker/session/tracking/FPS thật đều NOT TESTED |
| iPhone chưa rõ model | có hướng Quick Look ở cấp tài liệu | WebXR/Quick Look thực tế NOT TESTED |
| Kính VR chưa có | có thể phát triển bằng emulator | VR session, comfort, ≥72 FPS BLOCKED |
| Desktop của môi trường thực hiện | xem evidence M0 để biết browser thực được dùng | không đại diện Android/kính |
