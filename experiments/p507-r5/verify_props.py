"""Check R5 prop counts, locations and supports using independently checked bounds."""

from collections import Counter
from itertools import combinations
from math import dist, isclose

EPSILON = .004


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def near(a, b):
    return isclose(a, b, abs_tol=EPSILON, rel_tol=0)


def within(rect, item):
    return (rect[0] - EPSILON <= item[0] and rect[1] - EPSILON <= item[1]
            and item[3] <= rect[2] + EPSILON and item[4] <= rect[3] + EPSILON)


def overlaps(bounds, other):
    return all(min(bounds[i + 3], other[i + 3]) - max(bounds[i], other[i]) > EPSILON for i in range(3))


def adjacent_platform(surfaces):
    first, second = surfaces
    a, b = first["rect"], second["rect"]
    require(near(first["z"], second["z"]), "Printer platforms have different heights")
    same_x = near(a[0], b[0]) and near(a[2], b[2])
    adjacent_y = near(a[3], b[1]) or near(a[1], b[3])
    require(same_x and adjacent_y, "Printer platform crosses a gap")
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def verify_props(manifest):
    placed = {item["id"]: item for item in manifest["instances"] if item["status"] != "UNPLACED"}
    bounds = {ident: item["authored_bounds_survey"] for ident, item in placed.items()}
    support = manifest["supports"]
    desks = support["desk_surfaces"]
    chair_bindings = {chair["id"]: chair for chair in manifest["layout"]["chairs"]}
    prefixes = ("COMPUTER", "PRINTER", "TEA-SET", "ORCHID", "POSTER", "CLOCK", "WATER-JUG")
    expected = dict(zip(prefixes, (6, 1, 1, 1, 5, 1, 4), strict=True))
    counts = {kind: sum(i.startswith("P507-" + kind + "-") for i in placed) for kind in prefixes}
    require(counts == expected, "R5 required prop count differs")
    stations = Counter()
    desk_props = [ident for ident in placed if ident.startswith(("P507-COMPUTER-", "P507-PRINTER-",
                                                                "P507-TEA-SET-", "P507-ORCHID-"))]
    for ident in desk_props:
        info = placed[ident]["survey_transform"]
        ids = info["support_ids"]
        surfaces = [desks[entry] for entry in ids]
        rect = surfaces[0]["rect"] if len(surfaces) == 1 else adjacent_platform(surfaces)
        require(near(bounds[ident][2], surfaces[0]["z"]) and within(rect, bounds[ident]),
                f"Desk support outside the top: {ident}")
        if ident.startswith("P507-COMPUTER-"):
            desk, = ids
            chair = chair_bindings[info["chair_id"]]
            require(chair["desk_id"] == desk
                    and (info["orientation_deg"] - chair["orientation_deg"]) % 360 == 0,
                    f"Workstation faces an incorrect chair: {ident}")
            stations[desk] += 1
        if ident.startswith("P507-PRINTER-"):
            require(set(ids) == {"P507-DESK-A03", "P507-DESK-A06"}
                    and info["orientation_deg"] == 270, "Printer must face entry on A03/A06")
    require(stations == Counter({"P507-DESK-A03": 1, "P507-DESK-A06": 1,
                                 "P507-DESK-B05": 2, "P507-DESK-C05": 2}), "Workstation allocation differs")
    for a, b in combinations(desk_props, 2):
        require(not overlaps(bounds[a], bounds[b]), f"Desk props overlap: {a} / {b}")
    door = support["door_interval"]
    entry = (0, (door["from_y"] + door["to_y"]) / 2)
    tea = placed["P507-TEA-SET-01"]["survey_transform"]["center"][:2]
    orchid = placed["P507-ORCHID-01"]["survey_transform"]["center"][:2]
    require(dist(entry, tea) < dist(entry, orchid), "Tea is expected closer to the doorway than the orchid")

    shelf = support["shelf_surfaces"]
    shelf_id = shelf["id"]
    rect, levels = shelf["rect"], shelf["surface_z"]
    require(len(levels) == 4 and all(a < b for a, b in zip(levels, levels[1:])), "Shelf tier count or order differs")
    require(near(rect[2] - rect[0], .47) and near(rect[3] - rect[1], 2.25) and near(levels[-1], 2.175),
            "Shelf dimensions differ")
    require(near(bounds[shelf_id][5], levels[-1]) and bounds[shelf_id][5] > bounds["P507-FRIDGE"][5],
            "Shelf top height does not match rendered bounds")
    shelf_props = {"P507-TV-SMALL": 1}
    for ident, item in placed.items():
        info = item["survey_transform"]
        if "tier" in info:
            shelf_props[ident] = info["tier"]
    for ident, tier in shelf_props.items():
        level_index = 4 - tier
        require(0 <= level_index < 4, f"Invalid shelf tier for {ident}")
        ceiling = levels[level_index + 1] if level_index < 3 else manifest["virtual_dimensions"]["height_z"]
        require(near(bounds[ident][2], levels[level_index]) and within(rect, bounds[ident])
                and bounds[ident][5] < ceiling, f"Shelf tier support invalid: {ident}")
    for a, b in combinations(shelf_props, 2):
        require(not overlaps(bounds[a], bounds[b]), f"Shelf props overlap: {a} / {b}")
    require(sum(tier == 4 for tier in shelf_props.values()) == 4
            and all(shelf_props.get(f"P507-WATER-JUG-{i:02}") == 4 for i in range(1, 5)),
            "Shelf bottom needs four standing jugs")
    utility = ["P507-CABINET-FILES", "P507-FRIDGE", shelf_id, "P507-WASTE-BIN", "P507-SHOE-RACK"]
    require(all(bounds[a][4] <= bounds[b][1] + EPSILON for a, b in zip(utility, utility[1:])),
            "Utility layout order or overlaps differ")
    require(bounds[utility[-1]][4] <= support["door_interval"]["from_y"] + EPSILON,
            "Shoe rack blocks door")

    poster_ids = [f"P507-POSTER-{i:02}" for i in range(1, 6)]
    clock, tv = bounds["P507-CLOCK-01"], bounds["P507-TV-LARGE"]
    require(bounds[poster_ids[0]][3] < tv[0] and tv[3] < bounds[poster_ids[1]][0], "TV poster placement differs")
    require(bounds[poster_ids[2]][1] >= support["whiteboard_rect"][3] - EPSILON
            and bounds[poster_ids[2]][4] < support["door_interval"]["from_y"], "Entry poster does not fit span")
    windows = sorted(support["window_intervals"], key=lambda window: window["from_y"], reverse=True)
    for ident, (north, south) in zip(poster_ids[3:], zip(windows[:2], windows[1:3]), strict=True):
        info = placed[ident]["survey_transform"]
        require(info["adjacent_windows"] == [north["id"], south["id"]]
                and south["to_y"] < bounds[ident][1] < bounds[ident][4] < north["from_y"],
                f"Window poster blocks an opening: {ident}")
    cabinet = bounds["P507-CABINET-LOW"]
    cabinet_top = [cabinet[i] for i in (0, 1, 3, 4)]
    for ident, item in placed.items():
        if item["survey_transform"].get("support_id") == "P507-CABINET-LOW":
            require(within(cabinet_top, bounds[ident]) and near(cabinet[5], bounds[ident][2]),
                    f"Display item is unsupported: {ident}")
    mount = bounds["P507-TV-LARGE-MOUNT"]
    require(overlaps(mount, tv) and near(mount[4], manifest["virtual_dimensions"]["length_y"] - .05),
            "Large TV mount does not connect the wall and television")
    require(cabinet[0] < (clock[0] + clock[3]) / 2 < cabinet[3] and cabinet[5] < clock[2],
            "Clock not above low display cabinet")
    for ident in [*poster_ids[:2], "P507-CLOCK-01"]:
        for frame, frame_bounds in bounds.items():
            if frame.startswith("P507-FRAME-"):
                shared_projection = all(
                    min(bounds[ident][axis + 3], frame_bounds[axis + 3])
                    - max(bounds[ident][axis], frame_bounds[axis]) > EPSILON
                    for axis in (0, 2)
                )
                require(not shared_projection, f"TV wall fixtures overlap in elevation: {ident} / {frame}")
    for a, b in combinations([*poster_ids, "P507-CLOCK-01", "P507-TV-LARGE"], 2):
        require(not overlaps(bounds[a], bounds[b]), f"Wall assets overlap: {a} / {b}")
    return {"counts": counts, "workstations": dict(stations), "shelf_tiers": shelf_props}
