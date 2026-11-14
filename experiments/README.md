# M0-B1 — hai PoC độc lập

Chỉ synthetic, không phải phòng 507 hoặc sản phẩm chính thức. [PoC A](poc-a-r3f-xr/README.md), [PoC B](poc-b-iwsdk/README.md), [comparison](../docs/11-renderer-poc-comparison.md).

- shared-fixtures/domain.ts: contract, 1 room/5 objects, validation, adapter và domain state.
- shared-ui/: cùng Shell hai chế độ Guided Tour và Scene + Information Panel; không asset bên ngoài.
- poc-a-r3f-xr/: package/lockfile, R3F/XR renderer.
- poc-b-iwsdk/: package/lockfile, IWSDK World/ECS renderer + project manifest.
- browser-tests/: package/lockfile Playwright, Chrome có sẵn; real mouse/touch/WebGL/IWER tests và screenshot.

Không có nested Git repo, backend, database, auth hoặc admin. Điều kiện secure context/thiết bị thật vẫn chưa được nghiệm thu. Mỗi package build/test độc lập; browser suite so sánh hai preview cùng fixture/camera/material/light/viewport và một lượt emulation.
