"""Survey-space geometry for the provisional P507 R5 layout."""

import copy
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
R4 = HERE.parent / "p507-g1-g2"
sys.path.insert(0, str(R4))
from geometry import occupancy

R5_LABEL = "R5 PROPOSAL / PROVISIONAL / SYNTHETIC / VIRTUAL ADAPTATION"
DIMENSIONS = (8.63, 15.55, 3.50)
CLUSTER_SHIFTS = {"A": (0, 5.80), "B": (0.80, 3.40), "C": (0.20, 0.95)}
PLAYER_RADIUS = 0.30
PLAYER_HEIGHT = 1.80
AISLE_TARGET = 0.90
SHELF_SURFACES = (0.0525, 0.77, 1.47, 2.175)
HISTORICAL_UNPLACED = {"P507-CHAIR-C-09", "P507-CHAIR-C-10"}

# Component boxes enclose the neutral chair parts authored in chair_module().
CHAIR_COMPONENTS = [
    {"name": "seat", "min": [-.22, -.215, .4375], "max": [.22, .215, .4925]},
    {"name": "back", "min": [-.215, -.257, .60], "max": [.215, -.16, 1.]},
    *[
        {"name": "sled", "min": [x-.022, -.248, 0], "max": [x+.022, .202, .432]}
        for x in (-.178, .178)
    ],
    *[
        {"name": "back_tube", "min": [x-.013, -.239, .43], "max": [x+.013, -.157, .844]}
        for x in (-.178, .178)
    ],
    {"name": "brace", "min": [-.19, .109, .410], "max": [.19, .131, .434]},
]
OCCUPIED_COMPONENTS = [
    {"name": "torso", "min": [-.22, -.155, .4925], "max": [.22, .13, 1.02]},
    {"name": "head", "min": [-.12, -.11, 1.02], "max": [.12, .13, 1.32]},
    {"name": "thighs", "min": [-.21, .035, .4925], "max": [.21, .40, .58]},
    {"name": "shins", "min": [-.19, .245, .04], "max": [.19, .42, .51]},
]


def shift_point(point, dx, dy):
    return [point[0] + dx, point[1] + dy, *point[2:]]


def shift_rect(rect, dx, dy):
    left, lower, right, upper = rect
    return [left + dx, lower + dy, right + dx, upper + dy]


def shift_door(door, dy):
    for key in ("from_y", "to_y"):
        door[key] += dy
    door["entry_rect"] = shift_rect(door["entry_rect"], 0, dy)
    door["swing_polygon"] = [shift_point(point, 0, dy) for point in door["swing_polygon"]]
    door["sweep_polygons"] = [
        [shift_point(point, 0, dy) for point in polygon] for polygon in door["sweep_polygons"]
    ]
    for leaf in door["leaves"]:
        for key in ("center", "hinge_survey"):
            leaf[key] = shift_point(leaf[key], 0, dy)


def design_inventory():
    data = json.loads((R4 / "p507-provisional.json").read_text(encoding="utf-8"))
    width, length, height = DIMENSIONS
    dx_room = width - data["room"]["width_x"]
    dy_room = length - data["room"]["length_y"]
    for record in (data["room"], data["virtual_experience"]):
        record.update(width_x=width, length_y=length, height_z=height, source=R5_LABEL)
    data["virtual_experience"].pop("horizontal_expansion_factor", None)
    data["virtual_experience"].update(design_freeze="PROPOSAL", scope="R5_LOCAL_DEV_ONLY")
    data.update(label=R5_LABEL, layout_revision=5)
    shelf_y = 7.81
    utility = {
        "P507-CABINET-FILES": (6.01, 7.01),
        "P507-FRIDGE": (7.16, 7.76),
        "P507-UTILITY-SHELF": (shelf_y, shelf_y + 2.25),
        "P507-WASTE-BIN": (10.16, 10.48),
        "P507-SHOE-RACK": (10.58, 11.88),
        "P507-WHITEBOARD": (10.395, 11.845),
        "P507-TV-SMALL": (8.31, 9.11),
    }
    for item in data["objects"]:
        cluster = item.get("cluster")
        if cluster in CLUSTER_SHIFTS:
            item["rect"] = shift_rect(item["rect"], *CLUSTER_SHIFTS[cluster])
        if item["id"] in utility:
            item["rect"][1], item["rect"][3] = [y + dy_room - 5.60 for y in utility[item["id"]]]
        if item["id"] == "P507-UTILITY-SHELF":
            item["height"] = SHELF_SURFACES[-1]
        if item["id"] == "P507-TV-SMALL":
            item["bottom_z"] = SHELF_SURFACES[-1]
    shift_door(data["openings"]["door"], dy_room)
    data["handoff"]["starting_feet_survey"] = shift_point(
        data["handoff"]["starting_feet_survey"], 0, dy_room
    )
    data["handoff"]["nominal_avatar_radius_m"] = PLAYER_RADIUS
    for window in data["openings"]["windows"]:
        old_center = (window["from_y"] + window["to_y"]) / 2
        dy = old_center / (length - dy_room) * dy_room
        window["from_y"] += dy
        window["to_y"] += dy
        window["proxy_rect"] = shift_rect(window["proxy_rect"], dx_room, dy)
        window["blind"]["rect"] = shift_rect(window["blind"]["rect"], dx_room, dy)
    for key, item in data["hero"].items():
        dx = .55 if key == "tv" else 0
        item["center"] = shift_point(item["center"], dx, dy_room)
        if key == "tv":
            item["center"][2] += .04
            item["center_z"] += .04
            item["bottom_z"] += .04
        if "center_x" in item:
            item["center_x"] += dx
        if "occupancy_rect" in item:
            item["occupancy_rect"] = shift_rect(item["occupancy_rect"], dx, dy_room)
    for frame in data["photo_wall"]["frames"]:
        frame["center"] = shift_point(frame["center"], .75, dy_room)
    for item in data["ceiling"]["instances"]:
        x, y, _ = item["center"]
        item["center"] = shift_point(
            item["center"], x / (width - dx_room) * dx_room, y / (length - dy_room) * dy_room
        )
    return data


def facing(angle):
    rad = math.radians(angle)
    return (round(-math.sin(rad), 12), round(math.cos(rad), 12))


def local_to_room(point, center, angle):
    fx, fy = facing(angle)
    x, y, z = point
    return [center[0] + x*fy + y*fx, center[1] - x*fx + y*fy, center[2] + z]


def desk_binding(center, angle, desks):
    x, y = center
    fx, fy = facing(angle)
    matches = []
    for desk in desks:
        x0, y0, x1, y1 = desk["rect"]
        if fx and y0 < y < y1:
            distance = x0 - x if fx > 0 else x - x1
        elif fy and x0 < x < x1:
            distance = y0 - y if fy > 0 else y - y1
        else:
            continue
        if 0 <= distance < .45:
            matches.append((distance, desk["id"]))
    if len(matches) != 1:
        raise ValueError(f"Missing/ambiguous desk binding for {center}: {matches}")
    return matches[0][1]


def chair_spec(item, desks):
    x, y = shift_point(item["center"], *CLUSTER_SHIFTS[item["cluster"]])
    angle = item["orientation_deg"]
    y += {"P507-CHAIR-B-11": .06, "P507-CHAIR-B-12": -.06}.get(item["id"], 0)
    origin = [x, y, 0]
    desk_id = desk_binding((x, y), angle, desks)
    stored = local_to_room([0, .16, 0], origin, angle)
    pull_from_r4 = .66 if angle in (90, 270) else .98
    pulled = local_to_room([0, -pull_from_r4, 0], origin, angle)
    outer_row = (item["cluster"], angle) in (("C", 0), ("A", 180))
    pull_from = [0, -.59, 0]
    return {
        "id": item["id"], "desk_id": desk_id, "cluster": item["cluster"],
        "orientation_deg": angle, "stored": stored, "pulled": pulled,
        "seat_eye": local_to_room([0, .05, 1.20], pulled, angle),
        "stand": local_to_room([0, .545, 0], pulled, angle),
        "approach": local_to_room(pull_from, pulled, angle),
        "approach_alternatives": [
            local_to_room([x, y, 0], pulled, angle)
            for x in (-.55, .55) for y in (0, .55)
        ] if outer_row else [],
        "components": copy.deepcopy(CHAIR_COMPONENTS),
        "occupied_components": copy.deepcopy(OCCUPIED_COMPONENTS),
    }


def prism(id_, name, min_, max_):
    x0, y0, z0 = min_
    x1, y1, z1 = max_
    return {
        "id": id_, "name": name, "polygon": [[x0,y0], [x1,y0], [x1,y1], [x0,y1]],
        "bottom_z": z0, "top_z": z1,
    }


def desk_components(desk):
    x0, y0, x1, y1 = desk["rect"]
    h = desk["height"]
    id_ = desk["id"]
    yield prism(id_, "top", (x0, y0, h-.05), (x1, y1, h))
    for x in (x0+.065, x1-.065):
        for y in (y0+.065, y1-.065):
            yield prism(id_, "leg", (x-.0195, y-.0195, .024), (x+.0195, y+.0195, h-.05))
            yield prism(id_, "foot", (x-.0225, y-.0225, 0), (x+.0225, y+.0225, .024))
    for y in (y0+.065, y1-.065):
        yield prism(id_, "long apron", (x0+.05, y-.0145, h-.1325), (x1-.05, y+.0145, h-.0675))
    for x in (x0+.065, x1-.065):
        yield prism(id_, "short apron", (x-.0145, y0+.05, h-.1325), (x+.0145, y1-.05, h-.0675))


def chair_colliders(chair, state, physical=False):
    position = chair["stored"] if state == "stored" else chair["pulled"]
    angle = chair["orientation_deg"]
    if physical:
        parts = chair["components"]
    else:
        parts = [{"name": "chair", "min": [-.23,-.27,0], "max": [.23,.23,1.02]}]
    if state == "occupied":
        parts = [*parts, *chair["occupied_components"]]
    for part in parts:
        box = prism(chair["id"], part["name"], part["min"], part["max"])
        box["polygon"] = [local_to_room([*point, 0], position, angle)[:2] for point in box["polygon"]]
        yield box


def build_layout():
    design = design_inventory()
    desks = [item for item in design["objects"] if item.get("cluster") in CLUSTER_SHIFTS]
    chairs = []
    for item in design["chairs"]["instances"]:
        if item["status"] == "PLACED_PROVISIONAL":
            chair = chair_spec(item, [d for d in desks if d["cluster"] == item["cluster"]])
            item["center"] = chair["stored"][:2]
            chairs.append(chair)
    proxies = occupancy(design)
    # The R4 TV mount helper uses a constant X; carry it with the TV in R5.
    for proxy in proxies:
        if proxy["id"] == "P507-TV-LARGE-MOUNT":
            proxy["polygon"] = [shift_point(point, .55, 0) for point in proxy["polygon"]]
            proxy["bottom_z"] += .04
            proxy["top_z"] += .04
    static = [proxy for proxy in proxies if proxy.get("kind") != "chair"]
    desk_ids = {desk["id"] for desk in desks}
    return {
        "design": design, "chairs": chairs, "shelf_surfaces_z": list(SHELF_SURFACES),
        "walkable_rect": [.05, .05, DIMENSIONS[0]-.05, DIMENSIONS[1]-.05],
        "spawn": design["handoff"]["starting_feet_survey"],
        "static_walk_colliders": static,
        "static_interaction_colliders": [
            *[proxy for proxy in static if proxy["id"] not in desk_ids],
            *[part for desk in desks for part in desk_components(desk)],
        ],
    }
