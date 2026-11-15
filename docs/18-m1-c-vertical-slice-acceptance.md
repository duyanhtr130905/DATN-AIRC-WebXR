# Nghiệm thu M1-C — Digital Twin vertical slice synthetic

Ngày15/11/2026. Branch feat/m1-c-digital-twin-vertical-slice, mộtPR cuối. Không có dữ liệu/phòng507thật. MT1–MT3 và KPI≥3phòng chưa nghiệm thu.

| Giai đoạn | Trạng thái | Bằng chứng |
|---|---|---|
| C1 snapshot | PASS | d62a935; [CI43671658702](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43671658702);62unit/62PG, no skip |
| C2 integration | PASS | f775fe3; [CI43672737190](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/43672737190);62unit/63PG +24frontendunit,7foundationbrowser +5realPGbrowser scenarios. Bổ sungFSM unit local25PASS |
| C3 E2E/metrics/regression | NOT RUN | Chưa bắt đầu; không dùng kết quả M1-B để thay bằng chứng |

## C1

Protocol1 giữ <=32states compatibility. Protocol2 opt-in start/chunk/end, consistent RR view, releaseDB trước send, bounded512states/2MiB/32KiB frame/16states perchunk. Atomic staging, watermark vàdurable replay, source visibility từngchunk vàtrướcend. [Contract](14-api-contracts.md). Test0/1/32/33/41/80/120states TCP thật,513capacity reject, malformed framing, writer race, hide, overflow/disconnect/restart/READ_ONLY và regression cũ. Guard safeinteger v2. Thông tin quyền được kiểm tại thời điểm gửi, không thu hồi bytes đãtruyền.

## C2 đã kiểm chứng

Defaultlive REST Catalog UUID→deterministic synthetic primitive layout→authoritative WS snapshot/reducer→Canvas/Panel. Max100renderobjects,512states. Không publicwrites; guarded seed/CLI duy nhất. Scope theo room, cancellation của REST, boundedpagination vàsocket cleanup. Duplicate/old bỏ, gap/versionmismatch resync; retry12attempts rồi cần manualreload. Không fallbackhardcoded; offlinefoundationDEMO riêng explicit.

## Giới hạn

Singleprocess, chưa multiinstance; không survey507/GLB/ARVRphysical/sessiontracking/AI/deploy. LocalPG BLOCKED do thiếuDocker/PostgreSQL, không tựcài/SQLite. Metrics source-to-render chưa đo, C3 chưaPASS.390px chỉviewportemulation. Không bắt đầu milestone sau.
