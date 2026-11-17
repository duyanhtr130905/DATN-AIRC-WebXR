"""P507 provisional occupancy checks. Geometry PASS never certifies egress/survey accuracy."""

from __future__ import annotations

import argparse
import copy
import itertools
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
    if version not in (1, 2, 3):
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
    if version in (1, 2):
        data["schema_migration"] = {
            "from": version,
            "to": 3,
            "policy": "Preserve historical dimensions and IDs; no virtual approval or missing placement inferred",
            "historical_metadata": data.get("schema_migration"),
        }
        data["schema_version"] = 3
        data.setdefault("survey_baseline", copy.deepcopy(data["room"]))
        data.setdefault(
            "layout_mode", "HISTORICAL_PROVISIONAL_NO_VIRTUAL_APPROVAL_INFERRED"
        )
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


def footprint_center(item):
    """Offset belongs to local furniture axes, not global axes."""
    center = item["center"][:2]
    offset = item.get("footprint_offset", [0, 0])
    angle = math.radians(item.get("orientation_deg", 0))
    return [
        center[0] + offset[0] * math.cos(angle) - offset[1] * math.sin(angle),
        center[1] + offset[0] * math.sin(angle) + offset[1] * math.cos(angle),
    ]


def box_proxy(item, kind=None):
    center = item["center"]
    size = item.get("footprint_size", item.get("size"))
    polygon = oriented_rectangle(
        footprint_center(item), size[:2], item.get("orientation_deg", 0)
    )
    bottom = item.get(
        "bottom_z", center[2] - item["size"][2] / 2 if "size" in item else 0
    )
    top = item.get(
        "top_z",
        bottom
        + item.get(
            "occupancy_height",
            item.get("height", item["size"][2] if "size" in item else 1.02),
        ),
    )
    return {
        "id": item["id"],
        "kind": kind or item.get("type"),
        "cluster": item.get("cluster"),
        "polygon": polygon,
        "bottom_z": bottom,
        "top_z": top,
        "height": top - bottom,
        "orientation_deg": item.get("orientation_deg", 0),
        "support_id": item.get("support_id"),
        "wall_mount": item.get("wall_mount"),
        "source_refs": item.get("source_refs", []),
    }


def occupancy(data):
    """Placed 3D prisms. Touching/support is classified, never globally ignored."""
    out = []
    for o in data["objects"]:
        if o.get("status") != "UNPLACED" and valid_rect(o.get("rect")):
            bottom = o.get("bottom_z", 0)
            top = bottom + o.get("height", 0)
            out.append(
                {
                    "id": o["id"],
                    "kind": o.get("type"),
                    "cluster": o.get("cluster"),
                    "polygon": rect_polygon(o["rect"]),
                    "support_id": o.get("support_id"),
                    "bottom_z": bottom,
                    "top_z": top,
                    "height": o.get("height", 0),
                    "orientation_deg": o.get("orientation_deg", 0),
                    "wall_mount": o.get("wall_mount"),
                    "attachment_id": o.get("attachment_id"),
                    "source_refs": o.get("source_refs", []),
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
            out.append(box_proxy(c, "chair"))
    for key in ("cabinet", "water_dispenser", "tv"):
        item = data["hero"][key]
        if item.get("status") == "UNPLACED":
            continue
        if "footprint_size" in item:
            proxy = box_proxy(item, key)
            if valid_rect(item.get("occupancy_rect")):
                proxy["polygon"] = rect_polygon(item["occupancy_rect"])
            out.append(proxy)
        elif key != "tv":
            b = item.get("occupancy_rect")
            if not b:
                x, y, _ = item["center"]
                sx, sy = (
                    item["size"][:2] if key == "cabinet" else [item["radius"] * 2] * 2
                )
                b = [x - sx / 2, y - sy / 2, x + sx / 2, y + sy / 2]
            if valid_rect(b):
                bottom = item.get("bottom_z", 0)
                h = item.get(
                    "occupancy_height",
                    item["size"][2] if key == "cabinet" else item.get("height", 1.52),
                )
                out.append(
                    {
                        "id": item["id"],
                        "kind": key,
                        "polygon": rect_polygon(b),
                        "bottom_z": bottom,
                        "top_z": bottom + h,
                        "height": h,
                        "orientation_deg": item.get("orientation_deg", 0),
                    }
                )
    for item in data.get("ceiling", {}).get("instances", []):
        if item.get("status") == "PLACED_PROVISIONAL":
            out.append(box_proxy(item))
    for item in data.get("photo_wall", {}).get("frames", []):
        if item.get("status") == "PLACED_PROVISIONAL":
            out.append(box_proxy(item, "photo_frame"))
    for item in data.get("openings", {}).get("door", {}).get("leaves", []):
        out.append(box_proxy(item, "door_leaf"))
    for win in data.get("openings", {}).get("windows", []):
        if valid_rect(win.get("proxy_rect")):
            bottom = win["sill_z"] - 0.04
            top = win["top_z"] + 0.04
            out.append(
                {
                    "id": win["id"],
                    "kind": "window_glazing",
                    "polygon": rect_polygon(win["proxy_rect"]),
                    "bottom_z": bottom,
                    "top_z": top,
                    "height": top - bottom,
                    "wall_mount": "east",
                }
            )
        blind = win.get("blind", {})
        if blind.get("status") == "PLACED_PROVISIONAL" and valid_rect(
            blind.get("rect")
        ):
            bottom = blind["bottom_z"]
            top = bottom + blind["height"]
            out.append(
                {
                    "id": blind["id"],
                    "kind": "roller_blind",
                    "polygon": rect_polygon(blind["rect"]),
                    "bottom_z": bottom,
                    "top_z": top,
                    "height": blind["height"],
                    "wall_mount": "east",
                }
            )
    return out


def point_in_polygon(point, polygon):
    """Inclusive convex containment, independent of polygon winding."""
    signs = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        signs.append(
            (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
        )
    return all(s >= -EPS for s in signs) or all(s <= EPS for s in signs)


def vertical_overlap(a, b):
    return min(a.get("top_z", 1.02), b.get("top_z", 1.02)) - max(
        a.get("bottom_z", 0), b.get("bottom_z", 0)
    )


def is_supported(child, parent):
    return (
        child.get("support_id") == parent["id"]
        and abs(child.get("bottom_z", 0) - parent.get("top_z", parent.get("height", 0)))
        <= EPS
        and all(point_in_polygon(p, parent["polygon"]) for p in child["polygon"])
    )


def by_leaf(data, ident):
    return next(
        (
            leaf
            for leaf in data["openings"]["door"].get("leaves", [])
            if leaf.get("id") == ident
        ),
        None,
    )


def outward_leaf_valid(leaf, door):
    if not leaf or door.get("swing") != "OUTWARD" or leaf.get("swing") != "OUTWARD":
        return False
    ids = ["P507-DOOR-LEAF-01", "P507-DOOR-LEAF-02"]
    if (
        leaf.get("id") not in ids
        or leaf.get("type") != "door_leaf"
        or leaf.get("mount_support") != "P507-ARCH-WEST-DOOR-FRAME"
    ):
        return False
    i = ids.index(leaf["id"])
    sign = 1 if i == 0 else -1
    angle = door.get("opening_angle_deg")
    if (
        not finite(angle)
        or not 0 < angle <= 90
        or leaf.get("orientation_deg") != sign * angle
    ):
        return False
    half = (door["to_y"] - door["from_y"]) / 2
    hinge = [-0.05, door["from_y"] if i == 0 else door["to_y"], 0]
    if leaf.get("hinge_survey") != hinge or (
        not isinstance(leaf.get("size"), list)
        or len(leaf["size"]) != 3
        or any(
            abs(a - b) > EPS
            for a, b in zip(leaf["size"], [0.035, half, door["height"]])
        )
    ):
        return False
    fp = leaf.get("footprint_size")
    if (
        not isinstance(fp, list)
        or len(fp) != 2
        or any(not finite(a) or abs(a - b) > EPS for a, b in zip(fp, [0.07, half]))
    ):
        return False
    theta = math.radians(sign * angle)
    center = [
        hinge[0] - sign * half / 2 * math.sin(theta),
        hinge[1] + sign * half / 2 * math.cos(theta),
        door["height"] / 2,
    ]
    if (
        not isinstance(leaf.get("center"), list)
        or len(leaf["center"]) != 3
        or any(
            not finite(v) or abs(v - w) > 1e-6 for v, w in zip(leaf["center"], center)
        )
    ):
        return False
    return all(
        -half - 0.10 <= v[0] <= EPS
        and door["from_y"] - 0.04 <= v[1] <= door["to_y"] + 0.04
        for v in box_proxy(leaf)["polygon"]
    )


def validate_outward_door(door):
    errors = []
    if door.get("swing") != "OUTWARD" or not all(
        outward_leaf_valid(l, door) for l in door.get("leaves", [])
    ):
        errors.append(
            "Outward door requires two bounded outward leaf poses and hinge mechanics"
        )
    sweep = door.get("swing_polygon", [])
    expected = [
        [-0.85, door["from_y"]],
        [0, door["from_y"]],
        [0, door["to_y"]],
        [-0.85, door["to_y"]],
    ]
    if sweep != expected or len(door.get("sweep_polygons", [])) != 2:
        errors.append("Outward door sweep must remain bounded outside only")
    else:
        for leaf, sector in zip(door["leaves"], door["sweep_polygons"]):
            if (
                not sector
                or sector[0] != leaf["hinge_survey"][:2]
                or any(v[0] > EPS or not point_in_polygon(v, sweep) for v in sector)
            ):
                errors.append("Invalid outward leaf sweep sector")
            i = 0 if leaf["id"].endswith("01") else 1
            sign = 1 if i == 0 else -1
            hinge = leaf["hinge_survey"]
            half = (door["to_y"] - door["from_y"]) / 2
            expected_sector = [hinge[:2]] + [
                [
                    hinge[0]
                    - sign
                    * half
                    * math.sin(math.radians(leaf["orientation_deg"] * j / 12)),
                    hinge[1]
                    + sign
                    * half
                    * math.cos(math.radians(leaf["orientation_deg"] * j / 12)),
                ]
                for j in range(13)
            ]
            if len(sector) != len(expected_sector) or any(
                len(a) != 2
                or any(not finite(x) or abs(x - y) > 1e-6 for x, y in zip(a, b))
                for a, b in zip(sector, expected_sector)
            ):
                errors.append(
                    "Outward sweep sector must cover the entire hinged demo arc"
                )
    return errors


def validate_owner_chair_allocation(data):
    errors = []
    chairs = {c["id"]: c for c in data["chairs"]["instances"]}
    if data["chairs"].get("approved_layout_count") != 34:
        errors.append("Owner-approved layout count must remain 34")
    for g, n in (("A", 12), ("B", 12), ("C", 12)):
        for i in range(1, n + 1):
            ident = f"P507-CHAIR-{g}-{i:02d}"
            c = chairs.get(ident, {})
            if g == "C" and i in (9, 10):
                if (
                    c.get("status") != "UNPLACED"
                    or c.get("placement_allocation") is not None
                    or "center" in c
                ):
                    errors.append("C09/C10 must remain historical UNPLACED/UNASSIGNED")
                continue
            role = (
                ("row_lower" if i <= 6 else "row_upper")
                if g == "A"
                else (
                    "row_lower"
                    if i <= 4
                    else "row_upper"
                    if i <= 8
                    else "left_end"
                    if g == "B" and i >= 11
                    else "right_end"
                )
            )
            angle = {
                "row_lower": 0,
                "row_upper": 180,
                "right_end": 90,
                "left_end": 270,
            }[role]
            if (
                c.get("status") != "PLACED_PROVISIONAL"
                or c.get("placement_role") != role
                or c.get("orientation_deg") != angle
                or c.get("placement_allocation") != g
            ):
                errors.append("Owner chair allocation/pose mismatch: " + ident)
            center = c.get("center")
            if (
                isinstance(center, list)
                and len(center) == 2
                and all(finite(v) for v in center)
            ):
                desks = [
                    o
                    for o in data["objects"]
                    if o.get("type") in DESK_TYPES and o.get("cluster") == g
                ]
                core = [
                    o
                    for o in desks
                    if g == "A" or o["id"][-2:] in ("01", "02", "03", "04")
                ]
                if core and all(valid_rect(o.get("rect")) for o in core):
                    b = group_bbox(core)
                    x, y = center
                    valid_side = (
                        (b[0] < x < b[2] and b[1] - 0.6 < y < b[1])
                        if role == "row_lower"
                        else (b[0] < x < b[2] and b[3] < y < b[3] + 0.6)
                        if role == "row_upper"
                        else True
                    )
                    if role == "left_end":
                        desk = next(o for o in desks if o["id"] == "P507-DESK-B06")
                        r = desk["rect"]
                        valid_side = (
                            r[0] - 0.6 < x < r[0]
                            and r[1] < y < r[3]
                            and c.get("desk_id") == desk["id"]
                        )
                    if not valid_side:
                        errors.append(
                            "Actual chair side must match owner row/end allocation: "
                            + ident
                        )
            if c.get("footprint_size") != [0.46, 0.5] or c.get("height") != 1.02:
                errors.append(
                    "Historical full-size chair dimensions must not be scaled: " + ident
                )
    return errors


def occupied_use_report(data, proxies):
    pull = data.get("occupied_use", {}).get("chair_pullback_m", 0.15)
    posed = copy.deepcopy(proxies)
    for p in posed:
        if p.get("kind") == "chair":
            a = math.radians(p["orientation_deg"])
            dx = pull * math.sin(a)
            dy = -pull * math.cos(a)
            p["polygon"] = [[x + dx, y + dy] for x, y in p["polygon"]]
    collisions = []
    for i, a in enumerate(posed):
        for b in posed[i + 1 :]:
            if (
                "chair" in (a.get("kind"), b.get("kind"))
                and overlaps(a["polygon"], b["polygon"])
                and vertical_overlap(a, b) > EPS
            ):
                collisions.append([a["id"], b["id"]])

    def gap_between(ps, upper, lower):
        a = [p for p in ps if p.get("cluster") == upper]
        b = [p for p in ps if p.get("cluster") == lower]
        return (
            round(
                min(v[1] for p in a for v in p["polygon"])
                - max(v[1] for p in b for v in p["polygon"]),
                3,
            )
            if a and b
            else None
        )

    def west_route(ps):
        cluster = [p for p in ps if p.get("kind") in (*DESK_TYPES, "chair")]
        utility = [
            p
            for p in ps
            if p.get("kind")
            in ("file_cabinet", "fridge", "storage_shelf", "shoe_rack", "waste_bin")
        ]
        levels = sorted({v[1] for p in cluster + utility for v in p["polygon"]})
        widths = []
        for lo, hi in itertools.pairwise(levels):
            y = (lo + hi) / 2
            active = [
                p
                for p in cluster
                if min(v[1] for v in p["polygon"]) < y < max(v[1] for v in p["polygon"])
            ]
            if not active:
                continue
            left = max(
                [0.05]
                + [
                    max(v[0] for v in p["polygon"])
                    for p in utility
                    if min(v[1] for v in p["polygon"])
                    < y
                    < max(v[1] for v in p["polygon"])
                ]
            )
            widths.append(min(v[0] for p in active for v in p["polygon"]) - left)
        return round(min(widths), 3) if widths else None

    w, l = [data["room"][k] for k in ("width_x", "length_y")]
    occupied_chairs = [p for p in posed if p.get("kind") == "chair"]
    bounds_errors = [
        p["id"]
        for p in occupied_chairs
        if any(
            not (
                0.08 - EPS <= v[0] <= w - 0.05 + EPS
                and 0.05 - EPS <= v[1] <= l - 0.05 + EPS
            )
            for v in p["polygon"]
        )
    ]
    minimum_wall_gap = min(
        (
            min(
                min(v[0] - 0.05, w - 0.05 - v[0], v[1] - 0.05, l - 0.05 - v[1])
                for v in p["polygon"]
            )
            for p in occupied_chairs
        ),
        default=None,
    )
    return {
        "out_of_room_chairs": bounds_errors,
        "room_bounds_status": "FAIL" if bounds_errors else "PASS",
        "minimum_chair_to_inner_wall_m": round(minimum_wall_gap, 3)
        if minimum_wall_gap is not None
        else None,
        "chair_pullback_m": pull,
        "basis": data.get("occupied_use", {}).get(
            "basis", "PROPOSED occupied pose, not measured ergonomics"
        ),
        "collision_count": len(collisions),
        "collisions": collisions,
        "intercluster_clearance_m": {
            a + "-" + b: gap_between(posed, a, b) for a, b in [("A", "B"), ("B", "C")]
        },
        "west_main_route_static_min_m": west_route(proxies),
        "west_main_route_occupied_min_m": west_route(posed),
        "route_target_m": data.get("occupied_use", {}).get("main_route_target_m"),
        "status": "PARTIAL",
        "limitations": "Central gaps/right chair backs are not through-routes; no person/leg/door operation or legal egress certification.",
    }


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
    if data.get("schema_version") != 3:
        errors.append("Inventory must be migrated to schema v3")
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
        if c.get("status") == "PLACED_PROVISIONAL" and not (
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
                    "OWNER_APPROVED_VIRTUAL_ADAPTATION",
                ):
                    errors.append(f"Unsupported verified source claim: {key}={item}")
                if (
                    key in ("source", "size_source", "verification_level")
                    and isinstance(item, str)
                    and item.lower() in ("measured", "verified", "real_verified")
                ):
                    errors.append(f"Unsupported verified source claim: {key}={item}")
                claims(item)
        elif isinstance(value, list):
            for item in value:
                claims(item)

    if data.get("layout_revision", 0) >= 3:
        if data.get("layout_revision", 0) >= 4:
            baseline = data.get("survey_baseline", {})
            if [baseline.get(k) for k in ("width_x", "length_y", "height_z")] != [
                6,
                8.1,
                3.5,
            ] or baseline.get("source") != "USER_REPORTED":
                errors.append("Survey baseline must remain USER_REPORTED 6 x 8.1 x 3.5")
            virtual = data.get("virtual_experience", {})
            if (
                [width, length, height] != [6.9, 9.315, 3.5]
                or [virtual.get(k) for k in ("width_x", "length_y", "height_z")]
                != [width, length, height]
                or room.get("source") != "OWNER_APPROVED_VIRTUAL_ADAPTATION"
                or virtual.get("source") != room.get("source")
                or virtual.get("horizontal_expansion_factor") != 1.15
            ):
                errors.append(
                    "Virtual room dimensions must be owner-approved 6.9 x 9.315 x 3.5"
                )
            if data.get("migrated_from") != 1:
                errors.extend(validate_owner_chair_allocation(data))
            errors.extend(validate_outward_door(data["openings"]["door"]))
            file_cab = next(
                (o for o in objects if o.get("id") == "P507-CABINET-FILES"), {}
            )
            if (
                file_cab.get("compartment_count") != 3
                or file_cab.get("front_material") != "clear_glass"
            ):
                errors.append("File cabinet requires three clear-glass compartments")
        elif [width, length, height] != [6, 8.1, 3.5]:
            errors.append("Survey room dimensions must remain 6 x 8.1 x 3.5")
        for o in objects:
            if (
                o.get("type") == "table_standard"
                and abs(o.get("height", 0) - 0.9) > EPS
            ):
                errors.append(
                    f"Standard table height must remain surveyed .9m: {o.get('id')}"
                )
        tv = data["hero"]["tv"]
        if (
            not finite(tv.get("orientation_deg"))
            or abs(math.sin(math.radians(tv.get("orientation_deg", 0)))) < 0.01
        ):
            errors.append("TV must remain diagonal in the northwest corner")
        baseline_chair_ids = {
            f"P507-CHAIR-{g}-{i:02d}" for g in "ABC" for i in range(1, 13)
        }
        if not baseline_chair_ids.issubset({c.get("id") for c in chairs}):
            errors.append("Missing stable baseline chair IDs")
        if data["hero"]["water_dispenser"].get("orientation_deg") != 90:
            errors.append("Water front must rotate +90 degrees")
        door = data["openings"]["door"]
        if door.get("leaf_count") != 2 or len(door.get("leaves", [])) != 2:
            errors.append("Photo-observed door must have two leaves")
        for c in chairs:
            if (
                c.get("status") == "UNPLACED"
                and not c.get("placement_reason")
                and data.get("migrated_from") != 1
            ):
                errors.append(f"Unplaced chair needs reason: {c.get('id')}")
        instances = data.get("ceiling", {}).get("instances", [])
        for kind, count in data.get("ceiling", {}).get("required_counts", {}).items():
            if sum(i.get("type") == kind for i in instances) != count:
                errors.append(f"Ceiling {kind} count does not match survey inventory")
        if (
            len(data["openings"]["windows"]) != 4
            or sum(
                bool(w.get("blind", {}).get("id")) for w in data["openings"]["windows"]
            )
            != 4
        ):
            errors.append(
                "Four surveyed windows require four independent roller blinds"
            )
        for win in data["openings"]["windows"]:
            if (
                not finite(win.get("blind", {}).get("drop_m"))
                or not 0 < win["blind"]["drop_m"] < win["top_z"] - win["sill_z"]
            ):
                errors.append("Invalid roller blind drop")
            blind = win.get("blind", {})
            b = blind.get("rect")
            if (
                not valid_rect(b)
                or abs(b[1] - win["from_y"]) > EPS
                or abs(b[3] - win["to_y"]) > EPS
                or b[0] < width - 0.20
                or b[2] > width - 0.05 + EPS
                or blind.get("wall_mount") != "east"
            ):
                errors.append(
                    "Roller blind must attach to its own east window interval"
                )
        for group, count in (
            data.get("photo_wall", {}).get("required_groups", {}).items()
        ):
            if (
                sum(f.get("group") == group for f in data["photo_wall"]["frames"])
                != count
            ):
                errors.append(
                    f"Photo wall {group} frame count differs from observed layout"
                )
    if data.get("layout_revision", 0) >= 3 and data.get("photo_wall"):
        for group, expected_rows in (("A", [2, 3, 2, 2, 1]), ("I", [3, 1, 1, 1, 3])):
            frames = [
                f for f in data["photo_wall"]["frames"] if f.get("group") == group
            ]
            if all(
                isinstance(f.get("center"), list) and len(f["center"]) == 3
                for f in frames
            ):
                levels = sorted({round(f["center"][2], 3) for f in frames})
                rows = [
                    [f for f in frames if round(f["center"][2], 3) == z] for z in levels
                ]
                if [len(r) for r in rows] != expected_rows:
                    errors.append(
                        f"Photo wall {group} must preserve observed letter row structure"
                    )
                elif (
                    group == "I"
                    and max(r[0]["center"][0] for r in rows[1:4])
                    - min(r[0]["center"][0] for r in rows[1:4])
                    > 0.01
                ):
                    errors.append("Photo wall I stem must remain aligned")
    claims(data)
    records = (
        objects
        + chairs
        + [
            data["hero"][k]
            for k in ("cabinet", "water_dispenser", "tv")
            if data["hero"][k].get("id")
        ]
        + data.get("ceiling", {}).get("instances", [])
        + data.get("photo_wall", {}).get("frames", [])
        + data["openings"]["door"].get("leaves", [])
        + [w for w in data["openings"]["windows"] if w.get("id")]
        + [
            w["blind"]
            for w in data["openings"]["windows"]
            if w.get("blind", {}).get("id")
        ]
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
            "OWNER_APPROVED_VIRTUAL_ADAPTATION",
        ):
            errors.append(f"Unverified source claim: {ident}")
        if o.get("position_source") in ("MEASURED", "real_verified", "VERIFIED"):
            errors.append(f"Unverified position claim: {ident}")
    for o in objects:
        ident = o["id"]
        b = o.get("rect")
        if o.get("status") == "UNPLACED":
            continue
        if not valid_rect(b):
            errors.append(f"Invalid rectangle: {ident}")
            continue
        if not finite(o.get("height")) or not 0 < o["height"] <= height:
            errors.append(f"Invalid height: {ident}")
        bottom = o.get("bottom_z", 0)
        if (
            not finite(bottom)
            or bottom < 0
            or (finite(o.get("height")) and bottom + o["height"] > height)
        ):
            errors.append(f"Invalid vertical bounds: {ident}")
        if not o.get("position_source"):
            errors.append(f"Missing provenance for position: {ident}")
        if o.get("type") == "table_standard" and sorted(
            [round(b[2] - b[0], 3), round(b[3] - b[1], 3)]
        ) != [0.6, 1.5]:
            errors.append(f"Standard table dimensions do not match source: {ident}")
    for key in ("cabinet", "water_dispenser", "tv"):
        item = data["hero"][key]
        if key == "tv" and "center" not in item:
            continue
        center = item.get("center")
        if (
            not isinstance(center, list)
            or len(center) != 3
            or not all(finite(v) for v in center)
        ):
            errors.append(f"Invalid hero center: {key}")
            continue
        if "occupancy_rect" in item:
            b = item["occupancy_rect"]
            if not valid_rect(b):
                errors.append(f"Invalid hero occupancy rectangle: {key}")
            elif "footprint_size" in item:
                actual = box_proxy(item, key)["polygon"]
                if not all(point_in_polygon(p, rect_polygon(b)) for p in actual):
                    errors.append(f"Hero occupancy does not contain actual body: {key}")
            else:
                x, y, _ = center
                sx, sy = item["size"][:2] if key == "cabinet" else [0.39, 0.49]
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
        if (
            not finite(p.get("bottom_z"))
            or not finite(p.get("top_z"))
            or p["bottom_z"] < -EPS
            or p["top_z"] > height + EPS
            or p["bottom_z"] >= p["top_z"]
        ):
            errors.append(f"Invalid vertical bounds: {p['id']}")
        xmin = (
            0
            if p.get("kind") == "door_leaf"
            else 0.05
            if p.get("wall_mount") == "west"
            else 0.08
        )
        if outward_leaf_valid(by_leaf(data, p["id"]), data["openings"]["door"]):
            allowed.append(
                [p["id"], "OUTWARD_DOOR_ONLY", "bounded exterior leaf exception"]
            )
            continue
        if any(
            not (
                xmin - EPS
                <= v[0]
                <= (width + 0.05 if p.get("kind") == "window_glazing" else width - 0.05)
                + EPS
                and 0.05 - EPS <= v[1] <= length - 0.05 + EPS
            )
            for v in p["polygon"]
        ):
            errors.append(f"Out of room or wall collision: {p['id']}")
    by_proxy = {p["id"]: p for p in proxies}
    by_record = {o["id"]: o for o in records if o.get("id")}

    def valid_structural_support(record, support, proxy):
        if (
            proxy is None
            or not finite(proxy.get("bottom_z"))
            or not finite(proxy.get("top_z"))
        ):
            return False
        points = proxy["polygon"]
        if support == "P507-ARCH-CEILING":
            return (
                record.get("type")
                in ("light_panel", "ceiling_fan", "cassette_ac", "projector", "camera")
                and abs(proxy["top_z"] - height) < 1e-5
            )
        walls = {
            "P507-ARCH-WALL-WEST": "west",
            "P507-ARCH-WALL-EAST": "east",
            "P507-ARCH-WALL-NORTH": "north",
            "P507-ARCH-WALL-SOUTH": "south",
        }
        if support in walls:
            wall = walls[support]
            if record.get("wall_mount") != wall:
                return False
            if wall == "west":
                return (
                    0.05 - EPS <= min(v[0] for v in points)
                    and max(v[0] for v in points) <= 0.20 + EPS
                )
            if wall == "east":
                return (
                    width - 0.20 - EPS <= min(v[0] for v in points)
                    and max(v[0] for v in points) <= width - 0.05 + EPS
                )
            if wall == "south":
                return (
                    0.05 - EPS <= min(v[1] for v in points)
                    and max(v[1] for v in points) <= 0.20 + EPS
                )
            return (
                length - 0.20 - EPS <= min(v[1] for v in points)
                and max(v[1] for v in points) <= length - 0.05 + EPS
            )
        if support == "P507-ARCH-WEST-DOOR-FRAME":
            door = data["openings"]["door"]
            hinge_x = -0.05 if door.get("swing") == "OUTWARD" else 0.05
            hinges = [(hinge_x, door["from_y"]), (hinge_x, door["to_y"])]
            return (
                record.get("type") == "door_leaf"
                and abs(proxy["bottom_z"]) < EPS
                and abs(proxy["top_z"] - door["height"]) < EPS
                and any(
                    math.hypot(v[0] - x, v[1] - y) < 0.04
                    for v in points
                    for x, y in hinges
                )
            )
        if support == "north_west_wall_bracket":
            mount = by_record.get("P507-TV-LARGE-MOUNT", {})
            return (
                record.get("id") == "P507-TV-LARGE"
                and mount.get("attachment_id") == record["id"]
                and mount.get("wall_mount") == "north"
            )
        return False

    for record in records:
        mount = record.get("mount_support")
        if mount and not valid_structural_support(
            record, mount, by_proxy.get(record["id"])
        ):
            errors.append(f"Invalid structural support/mount: {record['id']} / {mount}")
    for p in proxies:
        support = p.get("support_id")
        if support and support.startswith("P507-ARCH-"):
            if not valid_structural_support(by_record[p["id"]], support, p):
                errors.append(f"Invalid structural support: {p['id']} / {support}")
            else:
                allowed.append([p["id"], support, "structural support"])
        elif support:
            parent = by_proxy.get(support)
            if not parent or not is_supported(p, parent):
                errors.append(f"Invalid support relation/height: {p['id']}")
            else:
                allowed.append([p["id"], parent["id"], "support relation"])

    def attachment(child, parent):
        return (
            child.get("kind") == "tv_mount"
            and child.get("attachment_id") == parent["id"]
            and parent.get("kind") == "tv"
            and child.get("wall_mount") == "north"
            and abs(max(p[1] for p in child["polygon"]) - (length - 0.05)) <= EPS
            and vertical_overlap(child, parent) > EPS
            and overlaps(child["polygon"], parent["polygon"])
        )

    for p in proxies:
        if p.get("attachment_id"):
            parent = by_proxy.get(p["attachment_id"])
            if not parent or not attachment(p, parent):
                errors.append(f"Invalid anchored attachment: {p['id']}")
            else:
                allowed.append([p["id"], parent["id"], "anchored TV mount attachment"])
    for i, a in enumerate(proxies):
        for b in proxies[i + 1 :]:
            if overlaps(a["polygon"], b["polygon"]):
                if (
                    is_supported(a, b)
                    or is_supported(b, a)
                    or attachment(a, b)
                    or attachment(b, a)
                ):
                    continue
                if vertical_overlap(a, b) > EPS:
                    collisions.append([a["id"], b["id"]])
                    errors.append(f"Footprint collision: {a['id']} / {b['id']}")
                else:
                    allowed.append([a["id"], b["id"], "vertical separation"])
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
            if (
                p.get("kind") != "door_leaf"
                and p.get("bottom_z", 0) < h
                and overlaps(p["polygon"], rect_polygon(entry))
            ):
                errors.append(f"Door entry collision: {p['id']}")
    else:
        unknown.append("DOOR_ENTRY_ZONE")
    swing = door.get("swing_polygon")
    if swing:
        if len(swing) < 3 or any(
            not isinstance(v, list) or len(v) != 2 or not all(finite(n) for n in v)
            for v in swing
        ):
            errors.append("Invalid door swing polygon")
        else:
            for p in proxies:
                if (
                    p.get("kind") != "door_leaf"
                    and p.get("bottom_z", 0) < h
                    and overlaps(p["polygon"], swing)
                ):
                    errors.append(f"Door swing collision: {p['id']}")
    if door.get("opening_angle_source") == "PROPOSED_LAYOUT":
        unknown.append("DOOR_SWING_ANGLE_PROVISIONAL")
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
    if data.get("layout_revision", 0) >= 3:
        for group in "BC":
            anchor = byid.get(f"P507-DESK-{group}01")
            if anchor and valid_rect(anchor.get("rect")) and anchor["rect"][0] <= 1.5:
                errors.append(
                    f"Cluster {group} must move towards windows relative to prior layout"
                )
    expected_ids = {
        f"P507-DESK-{g}{i:02d}"
        for g, n in (("A", 6), ("B", 6), ("C", 5))
        for i in range(1, n + 1)
    }
    if not expected_ids.issubset(byid):
        errors.append("Missing stable baseline desk IDs")
    if data.get("layout_revision", 0) >= 3:
        for ident in expected_ids:
            if ident in byid and byid[ident].get("status") != "PLACED_PROVISIONAL":
                errors.append(f"Baseline desk must remain placed: {ident}")
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
                geometric_right = [
                    c
                    for c in chairs
                    if c.get("cluster") == g
                    and c.get("status") == "PLACED_PROVISIONAL"
                    and isinstance(c.get("center"), list)
                    and len(c["center"]) == 2
                    and all(finite(v) for v in c["center"])
                    and c["center"][0] > r[2]
                    and r[1] < c["center"][1] < r[3]
                ]
                if {c["id"] for c in geometric_right} != {c["id"] for c in right}:
                    errors.append(
                        f"{g} must have exactly two geometrically right-end chairs matching their roles"
                    )
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
    static_clearances = {}
    for group in "BC":
        right = [
            p
            for p in proxies
            if p.get("kind") == "chair"
            and p.get("cluster") == group
            and any(
                c["id"] == p["id"] and c.get("placement_role") == "right_end"
                for c in chairs
            )
        ]
        if right:
            maxx = max(v[0] for p in right for v in p["polygon"])
            static_clearances[f"{group}_right_chair_to_window_wall"] = {
                "outer_boundary_gap_m": round(width - maxx, 3),
                "inner_wall_gap_m": round(width - 0.05 - maxx, 3),
                "usable_status": "UNKNOWN",
                "note": "Not enough evidence for chair pull-out or a route behind these chairs.",
            }
    cab = by_proxy.get("P507-CABINET-LOW")
    if cab and boxes.get("A"):
        static_clearances["cabinet_front_to_A_desk"] = {
            "static_gap_m": round(min(v[1] for v in cab["polygon"]) - boxes["A"][3], 3),
            "usable_status": "UNKNOWN",
        }
    utilities = [
        p
        for p in proxies
        if p.get("kind")
        in ("file_cabinet", "fridge", "storage_shelf", "shoe_rack", "waste_bin")
    ]
    low_desks = [p for p in proxies if p.get("kind") in DESK_TYPES]
    gaps_by_utility = {}
    for u in utilities:
        uy0 = min(v[1] for v in u["polygon"])
        uy1 = max(v[1] for v in u["polygon"])
        ux1 = max(v[0] for v in u["polygon"])
        candidates = [
            min(v[0] for v in p["polygon"]) - ux1
            for p in low_desks
            if min(uy1, max(v[1] for v in p["polygon"]))
            - max(uy0, min(v[1] for v in p["polygon"]))
            > EPS
            and min(v[0] for v in p["polygon"]) >= ux1
        ]
        if candidates:
            gaps_by_utility[u["id"]] = round(min(candidates), 3)
    static_clearances["west_utility_to_desks"] = {
        "static_gaps_m": gaps_by_utility,
        "usable_status": "UNKNOWN",
        "note": "Static gaps only; inspect occupied_use separately. No accessibility/egress claim.",
    }
    chair_aware_gaps = {}
    floor_groups = [p for p in proxies if p.get("kind") in (*DESK_TYPES, "chair")]
    for u in utilities:
        uy0 = min(v[1] for v in u["polygon"])
        uy1 = max(v[1] for v in u["polygon"])
        ux1 = max(v[0] for v in u["polygon"])
        candidates = [
            min(v[0] for v in p["polygon"]) - ux1
            for p in floor_groups
            if min(uy1, max(v[1] for v in p["polygon"]))
            - max(uy0, min(v[1] for v in p["polygon"]))
            > EPS
            and min(v[0] for v in p["polygon"]) >= ux1
        ]
        if candidates:
            chair_aware_gaps[u["id"]] = round(min(candidates), 3)
    static_clearances["west_utility_to_desks"]["chair_aware_static_gaps_m"] = (
        chair_aware_gaps
    )
    if data.get("layout_revision", 0) >= 3:
        unknown.extend(
            [
                "CAMERA_PLACEMENT_NOT_PHOTO_CONFIRMED",
                "CHAIR_PULL_OUT_CLEARANCE",
                "DOOR_CLEAR_OPERABLE_WIDTH",
            ]
        )
    occupied = occupied_use_report(data, proxies)
    if data.get("layout_revision", 0) >= 4:
        if data.get("occupied_use", {}).get("chair_pullback_m") != 0.15:
            errors.append("Occupied-use proxy must retain proposed .15m pullback")
        if occupied["collision_count"]:
            errors.append(
                "Occupied-use chair collision: " + str(occupied["collisions"])
            )
    if data.get("layout_revision", 0) >= 4 and occupied["out_of_room_chairs"]:
        errors.append(
            "Occupied-use chair wall/bounds collision: "
            + str(occupied["out_of_room_chairs"])
        )
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
        "occupied_use": occupied,
        "survey_baseline": data.get("survey_baseline", room),
        "virtual_experience": data.get("virtual_experience"),
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
        "ceiling_counts": {
            kind: sum(
                i.get("type") == kind
                for i in data.get("ceiling", {}).get("instances", [])
            )
            for kind in data.get("ceiling", {}).get("required_counts", {})
        },
        "frame_groups": {
            g: sum(
                f.get("group") == g
                for f in data.get("photo_wall", {}).get("frames", [])
            )
            for g in data.get("photo_wall", {}).get("required_groups", {})
        },
        "window_count": len(data["openings"]["windows"]),
        "blind_count": sum(
            bool(w.get("blind", {}).get("id")) for w in data["openings"]["windows"]
        ),
        "static_clearances": static_clearances,
        "circulation_status": "PARTIAL"
        if data.get("layout_revision", 0) >= 3
        else "UNKNOWN",
        "unplaced_chairs": [
            {"id": c["id"], "reason": c.get("placement_reason", "UNKNOWN")}
            for c in chairs
            if c.get("status") == "UNPLACED"
        ],
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
