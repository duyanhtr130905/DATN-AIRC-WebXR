# M2 FINAL ACCEPTANCE MATRIX

Candidate on Draft PR #24, based on main 5b971f591585124424e8393118b0911eb7c11110.
The [PR](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) records the exact tested HEAD, CI and final rerun results. The evidence below is historical until the final candidate is rerun.

| DoD | Expected | Actual at reviewed 997c930 | Evidence | Candidate status |
| --- | --- | --- | --- | --- |
| 1 Frozen asset | Clean owner restore, archive/source/manifest and provenance | Private vault commit 908a5cbb1f77b75b28666fd424cbd85f2aba4c1f, 28 members and six locked files; checkout 997c930 | [Preservation](P507-R4-PRESERVATION.md) | Rerun pending |
| 2 E0 | Chrome hard gates including 121 logical IDs, identity, geometry and proxy/navigation | Actual Chrome PASS; TV authoring/export drift separately diagnosed; 3 mm bounds and 1 mm proxy | [E0/E1 report](P507-WEBXR-E0-E1-EXPERIMENT.md) | Rerun pending |
| 3 E1 | Real Chrome control, lifecycle, collision and route | 15/15 smoke groups; west route exercised; aisle between chair rows remains blocked | [PR24 historical run](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44279217509) | Rerun pending |
| 4 Selection | Logical ID via ancestor and matching panel provenance | Chrome selection/panel smoke; metadata provisional | [Historical checkpoint](../evidence/p507-issue22-functional-6ed7c82.json) | Rerun pending |
| 5 Recovery | Loading, unsupported, missing/hash/schema/corrupt, retry/reload | Historical Chrome smoke exercised failures/recovery; unsupported via injection | [Historical checkpoint](../evidence/p507-issue22-functional-6ed7c82.json) | Rerun pending |
| 6 Browser | Desktop, 390x844, 768x1024, fallback, raw samples and environment | Chrome software-rendered smoke and emulated layouts; performance samples scoped to recorded build/viewport | [Historical run](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/actions/runs/44279217509) | Rerun pending |
| 7 Independent acceptance | Candidate evidence, demo guide, limits, review and owner disposition | [Demo guide](../../experiments/p507-webxr/README.md), Roadmap/Status and Draft PR; independent candidate review and owner disposition pending | [PR24](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/pull/24) | Pending independent acceptance |

Original ZIP 11,369,216 bytes, SHA-256 4255b199c6892c53b6709b1c66ce873cbcb4088dfa8ecef679a8e3e4713249f8.
Original GLB 10,751,036 bytes, SHA-256 8662ff65af012f547b062c8e5121cdf3fc7269319e5ebce9daef9cd32cf11f49.

CI PR status is NOT_RUN_PRIVILEGED_REQUIRED. App activation is an operational item under [#22](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/22); owner vault restore is the reproducibility path for DoD 1.
G1 circulation is partial, G2 visual is pending, and real-world fidelity, physical mobile/XR and GPU KPI remain unverified. [#20](https://github.com/duyanhtr130905/DATN-AIRC-WebXR/issues/20) tracks deferred geometry and placement.
