# M1-C — Checkpoint bàn giao

Cập nhật15/11/2026. Branch `feat/m1-c-digital-twin-vertical-slice`. HEAD tại checkpoint kiểm thử: `09f3e23ecde864e33763881a6ab2806d4564bbec`. Commit bàn giao tài liệu/định dạng theo sau; lấy HEAD hiện hành bằng git rev-parse HEAD, không reset/ghi main. Chỉ một PR cuối.

## Trạng thái

- C1 PASS → C2 PASS → C3 PASS trên source checkpoint, đang chốt final HEAD CI và PR review.
- M1-C IN REVIEW sau bàn giao; milestone sau NOT STARTED.
- Working tree trước commit bàn giao: định dạng source frontend (runtime token tương đương), acceptance/progress/status và raw evidence. Không thay schema/lockfile/stack.

## Commit và gate

| Giai đoạn | Commit/gate | Bằng chứng |
|---|---|---|
| C1 framing |feed865,404a862,5a13cf2; finald62a935|[43671658702](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43671658702),62unit/62PG PASS|
| C2 integration |734c1e7,f775fe3; checkpoint8372630|[43672737190](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43672737190), realPG/Chrome flow PASS|
| C3 E2E |94c5fe6,1e6e589,09f3e23|[43674376007](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376007),70unit/67PG/25frontend/16realbrowser +20samples PASS|
| Full M0/PoC/IWER |09f3e23|[M0](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376107), [PoC](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43674376051) PASS|

C1 CI lần đầufeed865 FAIL vì lint loại import fixture; explicit re-export sửa404a862, không xóa/skip assertions. Review C1 thêm READ_ONLY lúc snapshot và safe integers; C2 sửa stalled-body timeout/optional empty metadata, có RED→GREEN; C3 sửa partial fault restore, parent-owned timeout cleanup và clock drift bounds. Independent read-only review không còn finding P1/P2 mở. Không che kết quả lỗi trung gian.

## Đã triển khai

Bounded v2 snapshot, v1 compatibility; UUID Catalog adapter; atomic reducer; bounded reconnect lifecycle; live R3F/Panel/stale/fallback; explicit guarded20object/41state fixture; realPG/TCP/Chrome E2E/faults/metrics và artifacts. Xem [acceptance](18-m1-c-vertical-slice-acceptance.md), [raw JSON](evidence/m1-c-validation.json).

## Blocker và phần chưa làm

Local PostgreSQL BLOCKED; CI PG18 thật PASS. Real507/quyền dữ liệu, GalaxyAR và VR vật lý chưa có. Không multi-instance/publicwrites/sessiontracking/AI/deploy/KPI final validation. Không lỗi triển khai mở đã biết tại checkpoint; cần final HEAD CI trước bàn giao.

## Bước tiếp theo duy nhất

Commit/push các file bàn giao, kiểm tra root/remote/branch/secrets/diff; tạo một PR title M1-C: complete synthetic Digital Twin vertical slice; kiểm tra tất cả Checks trên HEAD mới, sửa nếu lỗi, báo PR/SHA/artifacts và dừng. Nếu phiên bị ngắt: đọc file này, gitlog/status và live PR/CI trước; không nghiên cứu lại từ đầu, không reset, không PR riêng/C1/C2 hoặc milestone mới.
