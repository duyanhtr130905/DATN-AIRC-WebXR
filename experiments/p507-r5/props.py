"""Neutral procedural props for the P507 R5 proposal.

Coordinates use survey metres, with a record's center at its support plane.
Local -Y is the front. Size describes the full, unscaled geometry envelope.
"""

from __future__ import annotations

import math
from itertools import pairwise


def horizontal_bounds(item):
    x, y, _ = item["center"]
    width, depth, _ = item["size"]
    orientation = round(item["orientation_deg"]) % 180
    if orientation == 90:
        width, depth = depth, width
    elif orientation != 0:
        angle = math.radians(item["orientation_deg"])
        a, b = abs(math.cos(angle)), abs(math.sin(angle))
        width, depth = width * a + depth * b, width * b + depth * a
    return [x - width / 2, y - depth / 2, x + width / 2, y + depth / 2]


def _part(ident, kind, center, size, angle=0, supports=(), **metadata):
    return {
        "id": f"P507-{ident}",
        "type": kind,
        "center": list(center),
        "size": list(size),
        "orientation_deg": angle,
        "support_ids": list(supports),
        "status": "PLACED_PROVISIONAL",
        "source_kind": "SYNTHETIC_NEUTRAL_PROCEDURAL_GEOMETRY",
        "rights": "NEUTRAL_GENERATED_GEOMETRY_ONLY",
        **metadata,
    }


def _desk_props(design, by_id):
    result = []
    chairs = {chair["id"]: chair for chair in design["chairs"]["instances"]}
    for index, desk, chair, angle in (
        (1, "A03", "A-06", 0),
        (2, "A06", "A-12", 180),
        (3, "B05", "B-09", 90),
        (4, "B05", "B-10", 90),
        (5, "C05", "C-11", 90),
        (6, "C05", "C-12", 90),
    ):
        desk_id, chair_id = f"P507-DESK-{desk}", f"P507-CHAIR-{chair}"
        x0, y0, x1, y1 = by_id[desk_id]["rect"]
        chair_x, chair_y = chairs[chair_id]["center"][:2]
        x, y = ((x0 + x1) / 2, chair_y) if angle == 90 else (chair_x, (y0 + y1) / 2)
        result.append(
            _part(
                f"COMPUTER-{index:02d}",
                "computer",
                (x, y, by_id[desk_id]["height"]),
                (0.54, 0.43, 0.48),
                angle,
                (desk_id,),
                chair_id=chair_id,
            )
        )

    a03 = by_id["P507-DESK-A03"]
    a06 = by_id["P507-DESK-A06"]
    x0, _, _, seam = a03["rect"]
    if abs(seam - a06["rect"][1]) > 1e-6 or abs(a03["height"] - a06["height"]) > 1e-6:
        raise ValueError(
            "A03 and A06 must give the printer one continuous level surface"
        )
    result.append(
        _part(
            "PRINTER-01",
            "printer",
            (x0 + 0.29, seam, a03["height"]),
            (0.38, 0.40, 0.265),
            270,
            (a03["id"], a06["id"]),
        )
    )
    for ident, kind, desk, offset, size in (
        ("TEA-SET-01", "tea", "A02", 0.23, (0.37, 0.37, 0.22)),
        ("ORCHID-01", "orchid", "A05", 1.10, (0.43, 0.42, 0.61)),
    ):
        desk = by_id[f"P507-DESK-{desk}"]
        x0, y0, _, y1 = desk["rect"]
        result.append(
            _part(
                ident,
                kind,
                (x0 + offset, (y0 + y1) / 2, desk["height"]),
                size,
                supports=(desk["id"],),
            )
        )
    return result


def _wall_props(design, by_id, tv_x):
    width, length = design["room"]["width_x"], design["room"]["length_y"]
    tv_left, tv_right = tv_x
    if tv_left < 0.49:
        raise ValueError("Insufficient TV-left wall span for neutral poster")
    posters = [
        _part(
            "POSTER-01",
            "poster",
            (tv_left - 0.27, length - 0.076, 1.56),
            (0.37, 0.052, 0.67),
            0,
            ("TV_WALL",),
            position="TV_LEFT",
        ),
        _part(
            "POSTER-02",
            "poster",
            (tv_right + 0.29, length - 0.076, 1.56),
            (0.37, 0.052, 0.67),
            0,
            ("TV_WALL",),
            position="TV_RIGHT",
        ),
    ]
    board_end = by_id["P507-WHITEBOARD"]["rect"][3]
    door_begin = design["openings"]["door"]["from_y"]
    if door_begin - board_end < 0.42 - 1e-6:
        raise ValueError("Insufficient wall span between whiteboard and entry")
    posters.append(
        _part(
            "POSTER-03",
            "poster",
            (0.076, (board_end + door_begin) / 2, 1.62),
            (0.35, 0.052, 0.63),
            90,
            ("WEST_WALL",),
            position="BOARD_DOOR",
        )
    )
    windows = sorted(
        design["openings"]["windows"], key=lambda row: row["from_y"], reverse=True
    )
    for n, (north, south) in enumerate(pairwise(windows[:3]), start=4):
        a, b = north["from_y"], south["to_y"]
        if a - b < 0.46:
            raise ValueError(
                f"Insufficient wall span between {north['id']} and {south['id']}"
            )
        posters.append(
            _part(
                f"POSTER-{n:02d}",
                "poster",
                (width - 0.076, (a + b) / 2, 1.61),
                (0.36, 0.052, 0.66),
                270,
                ("EAST_WALL",),
                adjacent_windows=[north["id"], south["id"]],
            )
        )
    cabinet = next(
        item for item in design["hero"].values() if item["id"] == "P507-CABINET-LOW"
    )
    clock_x = cabinet["center"][0] + 0.36
    posters.append(
        _part(
            "CLOCK-01",
            "clock",
            (clock_x, length - 0.077, 2.34),
            (0.35, 0.064, 0.35),
            0,
            ("TV_WALL",),
            above_id=cabinet["id"],
        )
    )
    return posters


def _shelf_props(shelf, levels):
    x0, y0, x1, y1 = shelf["rect"]
    x, y = (x0 + x1) / 2, (y0 + y1) / 2
    bottom, lower, upper, top = levels
    support = (shelf["id"],)
    layout = [
        ("COFFEE-MAKER-01", "coffee", y1 - 0.42, top, (0.35, 0.34, 0.42), 1),
        ("SPRAY-BOTTLE-01", "spray", y0 + 0.23, top, (0.10, 0.11, 0.26), 1),
        ("SHELF-CANISTER-01", "canister", y1 - 0.74, top, (0.13, 0.13, 0.15), 1),
        ("SHELF-BASKET-01", "basket", y0 + 0.40, upper, (0.39, 0.32, 0.22), 2),
        ("SHELF-DISHES-01", "dishes", y, upper, (0.34, 0.32, 0.16), 2),
        ("SHELF-BOX-01", "box", y1 - 0.41, upper, (0.37, 0.33, 0.25), 2),
        ("SHELF-DETERGENT-01", "bottle", y0 + 0.29, lower, (0.14, 0.13, 0.29), 3),
        ("SHELF-DETERGENT-02", "bottle", y0 + 0.55, lower, (0.13, 0.13, 0.25), 3),
        ("SHELF-UTENSILS-01", "utensils", y, lower, (0.43, 0.33, 0.32), 3),
        ("SHELF-BOTTLE-01", "bottle", y1 - 0.48, lower, (0.17, 0.15, 0.36), 3),
    ]
    for i, shift in enumerate((-0.70, -0.23, 0.23, 0.70), start=1):
        layout.append(
            (
                f"WATER-JUG-{i:02d}",
                "water_jug",
                y + shift,
                bottom,
                (0.285, 0.285, 0.487),
                4,
            )
        )
    return [
        _part(ident, kind, (x, location, z), dimensions, 90, support, tier=tier)
        for ident, kind, location, z, dimensions, tier in layout
    ]


def build_props(design, shelf_surfaces_z, tv_x):
    """Return the new positive inventory, separate from R4 records."""
    by_id = {item["id"]: item for item in design["objects"]}
    return (
        _desk_props(design, by_id)
        + _wall_props(design, by_id, tv_x)
        + _shelf_props(by_id["P507-UTILITY-SHELF"], shelf_surfaces_z)
    )
