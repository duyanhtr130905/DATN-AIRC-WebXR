"""G1 geometry checks for provisional P507 data; no external dependencies.

Layout is a proposed visualization, *not* a measured safety/egress drawing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "p507-provisional.json"
EPS = 1e-8


def read_inventory(path: Path = DEFAULT) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported inventory schema_version")
    return data


def area_intersection(a: list[float], b: list[float]) -> float:
    x = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    y = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return x * y


def group_bbox(objects: list[dict[str, Any]]) -> list[float]:
    return [min(o["rect"][0] for o in objects), min(o["rect"][1] for o in objects),
            max(o["rect"][2] for o in objects), max(o["rect"][3] for o in objects)]


def verify(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    room = data["room"]
    width, length, height = (float(room[k]) for k in ("width_x", "length_y", "height_z"))
    if min(width, length, height) <= 0:
        errors.append("Room dimensions must be positive")
    ids: set[str] = set()
    objects = data["objects"]
    for o in objects:
        ident = o.get("id", "")
        if not isinstance(ident, str) or not ident:
            errors.append("Empty or invalid survey ID")
        if ident in ids:
            errors.append(f"Duplicate survey ID: {ident}")
        ids.add(ident)
        b = o.get("rect")
        if not isinstance(b, list) or len(b) != 4 or any(not isinstance(v, (int, float)) or isinstance(v, bool) for v in b):
            errors.append(f"Invalid rectangle: {ident}")
            continue
        xmin, ymin, xmax, ymax = b
        if not (0 <= xmin < xmax <= width and 0 <= ymin < ymax <= length):
            errors.append(f"Out of room or invalid bounds: {ident}: {b}")
        z = o.get("height")
        if not isinstance(z, (int, float)) or not 0 < z <= height:
            errors.append(f"Invalid height: {ident}")
        if o.get("type") not in ("table_standard", "table_small", "furniture", "equipment"):
            warnings.append(f"Unknown object kind (allowed; renderer may use placeholder): {ident}")
        if not o.get("position_source"):
            errors.append(f"Missing provenance for position: {ident}")
        if o.get("type") == "table_standard":
            edges = sorted((round(xmax - xmin, 3), round(ymax - ymin, 3)))
            if edges != [0.6, 1.5]:
                errors.append(f"Standard table dimensions do not match source: {ident}: {edges}")
    valid_rects = [o for o in objects if isinstance(o.get("rect"), list) and len(o["rect"]) == 4]
    for i, obj in enumerate(valid_rects):
        for other in valid_rects[i+1:]:
            if area_intersection(obj["rect"], other["rect"]) > EPS:
                errors.append(f"Footprint collision: {obj['id']} / {other['id']}")
    groups = {c: [o for o in objects if o.get("cluster") == c] for c in ("A", "B", "C")}
    boxes = {k: group_bbox(v) if v else None for k, v in groups.items()}
    # NOTE: gaps exclude chairs, door swing, cabinets, and any later inventory items.
    gaps: dict[str, float] = {}
    if boxes["A"] and boxes["B"]:
        gaps["A-B"] = round(boxes["A"][1] - boxes["B"][3], 3)
    if boxes["B"] and boxes["C"]:
        gaps["B-C"] = round(boxes["B"][1] - boxes["C"][3], 3)
    for key, gap in gaps.items():
        if gap < 0:
            errors.append(f"Clusters overlap by Y: {key}")
    warnings.extend([
        "PROPOSED_LAYOUT only: these checks do not certify aisle width, accessibility or egress.",
        "36 chair locations, cabinets and door swing need separate occupancy survey before clearance certification.",
        "P507 source measurements, names, rights and photo permissions are NOT AIRC-verified.",
    ])
    return {
        "ok": not errors, "errors": errors, "warnings": warnings,
        "object_count": len(objects), "unique_ids": len(ids),
        "desk_count": sum(o["type"] in ("table_standard", "table_small") for o in objects),
        "clusters": {k: {"count": len(v), "bbox": boxes[k]} for k, v in groups.items()},
        "desk_edge_gaps_m": gaps, "rights": data.get("rights", {}),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, default=DEFAULT)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    report = verify(read_inventory(args.inventory))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
