"""P507 provisional occupancy checks. Geometry PASS never certifies egress/survey accuracy."""

from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "p507-provisional.json"
EPS = 1e-8
DESK_TYPES = ("table_standard", "table_small")


def migrate_inventory(data):
    """v1 had a chair count, no trusted instances. Preserve IDs, leave positions unknown."""
    data = copy.deepcopy(data)
    version = data.get("schema_version")
    if version not in (1, 2):
        raise ValueError("Unsupported inventory schema_version")
    if version == 1:
        data["schema_version"] = 2
        data["migrated_from"] = 1
        data["chairs"]["instances"] = [
            {
                "id": f"P507-CHAIR-{g}-{i:02d}",
                "type": "chair",
                "cluster": g,
                "status": "UNPLACED",
                "source_kind": "UNKNOWN",
                "position_source": "UNKNOWN",
                "orientation_deg": None,
            }
            for g in "ABC"
            for i in range(
                1,
                1
                + data["chairs"]["count"] // 3
                + (1 if "ABC".index(g) < data["chairs"]["count"] % 3 else 0),
            )
        ]
        for key, ident in [
            ("cabinet", "P507-CABINET-LOW"),
            ("water_dispenser", "P507-WATER-DISPENSER"),
        ]:
            data["hero"][key].setdefault("id", ident)
    return data


def read_inventory(path: Path = DEFAULT) -> dict[str, Any]:
    return migrate_inventory(json.loads(path.read_text(encoding="utf-8")))


def survey_to_three(point):
    return [point[0], point[2], -point[1]]


def area_intersection(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(
        0, min(a[3], b[3]) - max(a[1], b[1])
    )


def group_bbox(objects):
    return [
        min(o["rect"][0] for o in objects),
        min(o["rect"][1] for o in objects),
        max(o["rect"][2] for o in objects),
        max(o["rect"][3] for o in objects),
    ]


def oriented_rectangle(center, size, orientation_deg):
    x, y = center
    w, d = size
    a = math.radians(orientation_deg)
    c, s = math.cos(a), math.sin(a)
    return [
        [x + u * c - v * s, y + u * s + v * c]
        for u, v in [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    ]


def rect_polygon(rect):
    x0, y0, x1, y1 = rect
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def overlaps(a, b):
    """Strict positive-area convex SAT; edge contact is allowed, penetration fails."""
    for poly in (a, b):
        for p, q in zip(poly, poly[1:] + poly[:1]):
            axis = (-(q[1] - p[1]), q[0] - p[0])
            pa = [v[0] * axis[0] + v[1] * axis[1] for v in a]
            pb = [v[0] * axis[0] + v[1] * axis[1] for v in b]
            if min(max(pa), max(pb)) - max(min(pa), min(pb)) <= EPS:
                return False
    return True


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def valid_rect(b):
    return (
        isinstance(b, list)
        and len(b) == 4
        and all(finite(v) for v in b)
        and b[0] < b[2]
        and b[1] < b[3]
    )


def close_rect(a, b):
    return all(abs(x - y) < EPS for x, y in zip(a, b))


def occupancy(data):
    out = []
    for o in data["objects"]:
        if valid_rect(o.get("rect")):
            out.append(
                {
                    "id": o["id"],
                    "kind": o.get("type"),
                    "cluster": o.get("cluster"),
                    "polygon": rect_polygon(o["rect"]),
                    "support_id": o.get("support_id"),
                    "height": o.get("height", 0),
                    "bottom_z": o.get("bottom_z", 0),
                }
            )
    for c in data["chairs"].get("instances", []):
        if (
            c.get("status") == "PLACED_PROVISIONAL"
            and isinstance(c.get("center"), list)
            and len(c["center"]) == 2
            and all(finite(v) for v in c["center"])
            and finite(c.get("orientation_deg"))
            and isinstance(c.get("footprint_size"), list)
            and len(c["footprint_size"]) == 2
            and all(finite(v) and v > 0 for v in c["footprint_size"])
        ):
            out.append(
                {
                    "id": c["id"],
                    "kind": "chair",
                    "cluster": c.get("cluster"),
                    "polygon": oriented_rectangle(
                        c["center"], c["footprint_size"], c["orientation_deg"]
                    ),
                }
            )
    for key in ("cabinet", "water_dispenser"):
        item = data["hero"][key]
        b = item.get("occupancy_rect")
        if not b:
            x, y, _ = item["center"]
            sx, sy = item["size"][:2] if key == "cabinet" else [item["radius"] * 2] * 2
            b = [x - sx / 2, y - sy / 2, x + sx / 2, y + sy / 2]
        if valid_rect(b):
            out.append({"id": item["id"], "kind": key, "polygon": rect_polygon(b)})
    return out


def verify(data):
    data = migrate_inventory(data)
    errors = []
    warnings = []
    unknown = []
    room = data["room"]
    width, length, height = [room[k] for k in ("width_x", "length_y", "height_z")]
    if not all(finite(v) and v > 0 for v in [width, length, height]):
        raise ValueError("Invalid room dimensions")
    objects = data["objects"]
    chairs = data["chairs"].get("instances", [])
    ids = set()
    if data.get("schema_version") != 2:
        errors.append("Inventory must be migrated to schema v2")
    chairs = data["chairs"].get("instances", [])
    if data["chairs"].get("count") != len(chairs):
        errors.append("Chair inventory count does not match instance records")
    for c in chairs:
        if c.get("cluster") not in ("A", "B", "C"):
            errors.append(f"Invalid chair cluster: {c.get('id')}")
        if c.get("status") not in ("PLACED_PROVISIONAL", "UNPLACED"):
            errors.append(f"Invalid chair status: {c.get('id')}")
        if not c.get("source_kind") or not c.get("position_source"):
            errors.append(f"Missing chair provenance: {c.get('id')}")
        if c.get("status") == "PLACED_PROVISIONAL":
            if not (
                isinstance(c.get("center"), list)
                and len(c["center"]) == 2
                and all(finite(v) for v in c["center"])
                and finite(c.get("orientation_deg"))
                and isinstance(c.get("footprint_size"), list)
                and len(c["footprint_size"]) == 2
                and all(finite(v) and v > 0 for v in c["footprint_size"])
            ):
                errors.append(f"Invalid chair pose: {c.get('id')}")

    def claims(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ("source_kind", "position_source") and item not in (
                    "PROPOSED_LAYOUT",
                    "UNKNOWN",
                    "SYNTHETIC",
                ):
                    errors.append(f"Unsupported verified source claim: {key}={item}")
                if key in ("source", "size_source") and isinstance(item, str) and item.lower() in ("measured", "verified", "real_verified"):
                    errors.append(f"Unsupported verified source claim: {key}={item}")
                claims(item)
        elif isinstance(value, list):
            for item in value:
                claims(item)

    claims(data)
    records = (
        objects
        + chairs
        + [data["hero"][k] for k in ("cabinet", "water_dispenser")]
        + data.get("unknown_inventory", [])
    )
    for o in records:
        ident = o.get("id")
        if not isinstance(ident, str) or not ident:
            errors.append("Empty or invalid survey ID")
        if ident in ids:
            errors.append(f"Duplicate survey ID: {ident}")
        ids.add(ident)
        if o.get("status") == "UNPLACED":
            unknown.append(ident)
        if o.get("source_kind", "PROPOSED_LAYOUT") not in (
            "PROPOSED_LAYOUT",
            "UNKNOWN",
            "SYNTHETIC",
        ):
            errors.append(f"Unverified source claim: {ident}")
        if o.get("position_source") in ("MEASURED", "real_verified", "VERIFIED"):
            errors.append(f"Unverified position claim: {ident}")
    for o in objects:
        ident = o["id"]
        b = o.get("rect")
        if not valid_rect(b):
            errors.append(f"Invalid rectangle: {ident}")
            continue
        if not finite(o.get("height")) or not 0 < o["height"] <= height:
            errors.append(f"Invalid height: {ident}")
        bottom=o.get("bottom_z",0)
        if not finite(bottom) or bottom < 0 or (finite(o.get("height")) and bottom+o["height"]>height):
            errors.append(f"Invalid vertical bounds: {ident}")
        if not o.get("position_source"):
            errors.append(f"Missing provenance for position: {ident}")
        if o.get("type") == "table_standard" and sorted(
            [round(b[2] - b[0], 3), round(b[3] - b[1], 3)]
        ) != [0.6, 1.5]:
            errors.append(f"Standard table dimensions do not match source: {ident}")
    for key in ("cabinet", "water_dispenser"):
        item = data["hero"][key]
        center = item.get("center")
        if (
            not isinstance(center, list)
            or len(center) != 3
            or not all(finite(v) for v in center)
        ):
            raise ValueError(f"Invalid hero center: {key}")
        if "occupancy_rect" in item and not valid_rect(item["occupancy_rect"]):
            errors.append(f"Invalid hero occupancy rectangle: {key}")
        elif "occupancy_rect" in item:
            x, y, _ = center
            sx, sy = item["size"][:2] if key == "cabinet" else [0.39, 0.49]
            b = item["occupancy_rect"]
            if (
                b[0] > x - sx / 2 + EPS
                or b[1] > y - sy / 2 + EPS
                or b[2] < x + sx / 2 - EPS
                or b[3] < y + sy / 2 - EPS
            ):
                errors.append(f"Hero occupancy does not contain actual body: {key}")
    proxies = occupancy(data)
    collisions = []
    allowed = []
    for p in proxies:
        if any(
            not (
                0.08 - EPS <= v[0] <= width - 0.08 + EPS
                and 0.05 - EPS <= v[1] <= length - 0.05 + EPS
            )
            for v in p["polygon"]
        ):
            errors.append(f"Out of room or wall collision: {p['id']}")
    for i, a in enumerate(proxies):
        for b in proxies[i + 1 :]:
            if overlaps(a["polygon"], b["polygon"]):
                if (
                    a.get("support_id") == b["id"]
                    and abs(a.get("bottom_z", 0) - b.get("height", 0)) < EPS
                ) or (
                    b.get("support_id") == a["id"]
                    and abs(b.get("bottom_z", 0) - a.get("height", 0)) < EPS
                ):
                    allowed.append([a["id"], b["id"], "support relation"])
                else:
                    collisions.append([a["id"], b["id"]])
                    errors.append(f"Footprint collision: {a['id']} / {b['id']}")
    door = data["openings"]["door"]
    start, end, h = [door[k] for k in ("from_y", "to_y", "height")]
    if (
        door.get("wall") != "west"
        or not all(finite(v) for v in [start, end, h])
        or not (0 < start < end < length and 0 < h < height)
    ):
        errors.append("Invalid door opening")
    entry = door.get("entry_rect")
    if valid_rect(entry):
        if (
            abs(entry[1] - start) > EPS
            or abs(entry[3] - end) > EPS
            or entry[0] < 0
            or entry[2] > width
        ):
            errors.append("Entry zone does not match door opening")
        for p in proxies:
            if overlaps(p["polygon"], rect_polygon(entry)):
                errors.append(f"Door entry collision: {p['id']}")
    else:
        unknown.append("DOOR_ENTRY_ZONE")
    if door.get("swing", "UNKNOWN") == "UNKNOWN":
        unknown.append("DOOR_SWING_AND_LEAF_COUNT")
    cursor = 0
    for win in data["openings"]["windows"]:
        if win["wall"] != "east" or not (
            cursor <= win["from_y"] < win["to_y"] <= length
            and 0 < win["sill_z"] < win["top_z"] < height
        ):
            errors.append("Invalid window opening")
        cursor = win["to_y"]
    desks = [o for o in objects if o.get("type") in DESK_TYPES]
    groups = {
        g: [o for o in desks if o.get("cluster") == g and valid_rect(o.get("rect"))]
        for g in "ABC"
    }
    boxes = {g: group_bbox(v) if v else None for g, v in groups.items()}
    byid = {o["id"]: o for o in desks}
    expected_ids = {
        f"P507-DESK-{g}{i:02d}"
        for g, n in (("A", 6), ("B", 6), ("C", 5))
        for i in range(1, n + 1)
    }
    if not expected_ids.issubset(byid):
        errors.append("Missing stable baseline desk IDs")
    a = [byid.get(f"P507-DESK-A{i:02d}") for i in range(1, 7)]
    if all(o and valid_rect(o.get("rect")) for o in a):
        ax, ay = a[0]["rect"][:2]
        for index, o in enumerate(a):
            x, y = ax + (index % 3) * 1.5, ay + (index // 3) * 0.6
            if not close_rect(o["rect"], [x, y, x + 1.5, y + 0.6]):
                errors.append("A must preserve three desks by two rows")
    for g in "BC":
        core = [byid.get(f"P507-DESK-{g}{i:02d}") for i in range(1, 5)]
        if all(o and valid_rect(o.get("rect")) for o in core):
            x, y = core[0]["rect"][:2]
            expected = [
                [x, y, x + 1.5, y + 0.6],
                [x + 1.5, y, x + 3, y + 0.6],
                [x, y + 0.6, x + 1.5, y + 1.2],
                [x + 1.5, y + 0.6, x + 3, y + 1.2],
            ]
            if not all(close_rect(o["rect"], e) for o, e in zip(core, expected)):
                errors.append(f"{g} core must be 2x2")
            enddesk = byid.get(f"P507-DESK-{g}05")
            if (
                not enddesk
                or not valid_rect(enddesk.get("rect"))
                or not close_rect(enddesk["rect"], [x + 3, y - 0.15, x + 3.6, y + 1.35])
            ):
                errors.append(f"{g}05 must be right longitudinal desk")
            if g == "B":
                small = byid.get("P507-DESK-B06")
                if (
                    not small
                    or not valid_rect(small.get("rect"))
                    or not close_rect(small["rect"], [x - 0.6, y, x, y + 1.2])
                ):
                    errors.append("B06 must be small desk on left")
            right = [
                c
                for c in chairs
                if c.get("cluster") == g
                and c.get("placement_role") == "right_end"
                and c.get("status") == "PLACED_PROVISIONAL"
            ]
            if data.get("migrated_from") == 1:
                unknown.append(f"{g}_RIGHT_CHAIRS")
            elif len(right) != 2:
                errors.append(f"{g} must have exactly two right-end chairs")
            elif enddesk and valid_rect(enddesk.get("rect")):
                r = enddesk["rect"]
                geometric_right = [c for c in chairs
                    if c.get("cluster") == g and c.get("status") == "PLACED_PROVISIONAL"
                    and isinstance(c.get("center"), list) and len(c["center"]) == 2
                    and all(finite(v) for v in c["center"])
                    and c["center"][0] > r[2] and r[1] < c["center"][1] < r[3]]
                if {c["id"] for c in geometric_right} != {c["id"] for c in right}:
                    errors.append(f"{g} must have exactly two geometrically right-end chairs matching their roles")
                for c in right:
                    if (
                        not isinstance(c.get("center"), list)
                        or len(c["center"]) != 2
                        or not all(finite(v) for v in c["center"])
                        or not finite(c.get("orientation_deg"))
                    ):
                        continue
                    if (
                        c.get("desk_id") != enddesk["id"]
                        or c.get("orientation_deg", 0) % 360 != 90
                        or not (c["center"][0] > r[2] and r[1] < c["center"][1] < r[3])
                    ):
                        errors.append(f"Incorrect right-end chair pose: {c['id']}")
    gaps = {}
    walkways = {}
    for upper, lower in [("A", "B"), ("B", "C")]:
        if boxes[upper] and boxes[lower]:
            key = upper + "-" + lower
            gaps[key] = round(boxes[upper][1] - boxes[lower][3], 3)
            up = [p for p in proxies if p.get("cluster") == upper]
            lo = [p for p in proxies if p.get("cluster") == lower]
            walkways[key] = {
                "provisional_envelope_gap_m": round(
                    min(v[1] for p in up for v in p["polygon"])
                    - max(v[1] for p in lo for v in p["polygon"]),
                    3,
                ),
                "clearance_status": "UNKNOWN",
                "reason": "fixed proposed chair envelopes only; no pullout, swing or accessibility survey",
            }
    warnings.extend(
        [
            "PROPOSED_LAYOUT only: these checks do not certify aisle width, accessibility or egress.",
            "P507 source measurements, rights and photo permissions are NOT AIRC-verified.",
        ]
    )
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "object_count": len(objects),
        "unique_ids": len(ids),
        "desk_count": len(desks),
        "clusters": {g: {"count": len(groups[g]), "bbox": boxes[g]} for g in "ABC"},
        "desk_edge_gaps_m": gaps,
        "usable_walkways": walkways,
        "chair_inventory": {
            "total": data["chairs"]["count"],
            "placed": sum(c.get("status") == "PLACED_PROVISIONAL" for c in chairs),
            "unplaced": sum(c.get("status") == "UNPLACED" for c in chairs),
        },
        "collision_count": len(collisions),
        "collisions": collisions,
        "allowed_relations": allowed,
        "unknown": unknown,
        "occupancy": proxies,
        "door": door,
        "hero": data["hero"],
        "rights": data.get("rights", {}),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, default=DEFAULT)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    report = verify(read_inventory(args.inventory))
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
