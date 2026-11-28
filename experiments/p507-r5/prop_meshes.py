"""Blender mesh factories for neutral proposal assets."""

import math

import bpy
from generate_blender import cube, cylinder, lathe, material, pose_asset, tube


def palette():
    colors = {
        "black": ((0.025, 0.03, 0.038), 0.38, 0.08),
        "screen": ((0.009, 0.015, 0.023), 0.24, 0.03),
        "key": ((0.16, 0.18, 0.20), 0.63, 0.04),
        "silver": ((0.55, 0.58, 0.60), 0.29, 0.60),
        "white": ((0.88, 0.87, 0.81), 0.44, 0.02),
        "paper": ((0.77, 0.81, 0.77), 0.78, 0.00),
        "wood": ((0.32, 0.15, 0.068), 0.49, 0.00),
        "orchid": ((0.72, 0.38, 0.75), 0.51, 0.00),
        "green": ((0.08, 0.27, 0.08), 0.61, 0.00),
        "leaf_tip": ((0.36, 0.52, 0.13), 0.55, 0.00),
        "blue": ((0.045, 0.26, 0.46), 0.35, 0.08),
        "jug": ((0.20, 0.59, 0.74), 0.17, 0.00),
        "carafe": ((0.28, 0.38, 0.40), 0.14, 0.00),
        "coffee": ((0.13, 0.066, 0.026), 0.42, 0.00),
        "foam": ((0.27, 0.41, 0.30), 0.72, 0.00),
        "neutral": ((0.50, 0.44, 0.31), 0.48, 0.00),
    }
    mats = {
        name: material("P507_R5_" + name.upper(), rgb, roughness, metal)
        for name, (rgb, roughness, metal) in colors.items()
    }
    for name, alpha in (("jug", 0.60), ("carafe", 0.43)):
        bsdf = mats[name].node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mats[name], "surface_render_method"):
            mats[name].surface_render_method = "DITHERED"
        else:
            mats[name].blend_method = "BLEND"
    return mats


class Parts:
    def __init__(self, ident, col, mats):
        self.name = ident.replace("-", "_")
        self.col = col
        self.mats = mats
        self.objects = []

    def box(self, name, location, dimensions, mat, bevel=0.004):
        obj = cube(
            self.name + "_" + name,
            location,
            dimensions,
            self.mats[mat],
            self.col,
            bevel,
        )
        self.objects.append(obj)
        return obj

    def cyl(self, name, location, radius, depth, mat, axis="z"):
        obj = cylinder(
            self.name + "_" + name,
            location,
            radius,
            depth,
            self.mats[mat],
            self.col,
            24,
        )
        if axis == "y":
            obj.rotation_euler.x = math.pi / 2
        self.objects.append(obj)
        return obj

    def turned(self, name, center, profile, mat):
        obj = lathe(
            self.name + "_" + name, center, profile, self.mats[mat], self.col, 28
        )
        self.objects.append(obj)
        return obj

    def pipe(self, name, start, end, radius, mat):
        obj = tube(self.name + "_" + name, start, end, radius, self.mats[mat], self.col)
        self.objects.append(obj)
        return obj


def computer(p, _size):
    p.box("OVAL_BASE", (0, 0.112, 0.010), (0.22, 0.175, 0.02), "black", 0.009)
    p.box("RISER", (0, 0.132, 0.13), (0.046, 0.044, 0.244), "silver", 0.007)
    p.box("DISPLAY_BEZEL", (0, 0.125, 0.322), (0.508, 0.042, 0.312), "black", 0.009)
    p.box("INACTIVE_DISPLAY", (0, 0.100, 0.323), (0.484, 0.006, 0.284), "screen", 0.003)
    p.box("STANDBY_DOT", (0.22, 0.095, 0.176), (0.010, 0.003, 0.003), "key", 0.001)
    p.box("KEYBOARD", (-0.050, -0.100, 0.011), (0.360, 0.139, 0.022), "black", 0.007)
    for row in range(4):
        for col in range(12):
            p.box(
                "KEY",
                (-0.208 + col * 0.026, -0.143 + row * 0.023, 0.023),
                (0.018, 0.016, 0.006),
                "key",
                0,
            )
    p.box("SPACE", (-0.082, -0.081, 0.027), (0.092, 0.014, 0.006), "key", 0.001)
    p.box("MOUSE", (0.192, -0.120, 0.017), (0.063, 0.102, 0.034), "black", 0.015)
    p.box("MOUSE_SCROLL", (0.192, -0.130, 0.034), (0.009, 0.028, 0.005), "key", 0.002)


def printer(p, _size):
    p.box("CARCASS", (0, 0.032, 0.113), (0.356, 0.285, 0.226), "white", 0.011)
    p.box("SCANNER_LID", (0, 0.043, 0.233), (0.349, 0.267, 0.025), "silver", 0.008)
    p.box("OUTPUT_MOUTH", (0, -0.112, 0.089), (0.270, 0.016, 0.048), "black", 0.005)
    p.box("OUTPUT_TRAY", (0, -0.150, 0.055), (0.224, 0.086, 0.015), "key", 0.006)
    p.box("PAPER_CASSETTE", (0, -0.112, 0.026), (0.303, 0.023, 0.033), "silver", 0.006)
    p.box(
        "FRONT_CONTROL", (0.118, -0.113, 0.184), (0.084, 0.018, 0.052), "black", 0.006
    )
    for i in range(3):
        p.box(
            "CONTROL",
            (0.093 + i * 0.023, -0.125, 0.188),
            (0.010, 0.007, 0.011),
            "paper",
            0.002,
        )


def tea(p, _size):
    p.cyl("ROUND_TRAY", (0, 0, 0.012), 0.179, 0.024, "wood")
    p.turned(
        "TEAPOT",
        (-0.035, 0.022),
        [(0.046, 0.024), (0.066, 0.068), (0.052, 0.137), (0.036, 0.152)],
        "white",
    )
    p.cyl("LID_KNOB", (-0.035, 0.022, 0.162), 0.012, 0.019, "white")
    p.pipe("SPOUT", (0.004, 0.020, 0.075), (0.075, 0.035, 0.132), 0.018, "white")
    p.pipe(
        "HANDLE_UPPER", (-0.087, 0.022, 0.115), (-0.119, 0.022, 0.107), 0.012, "white"
    )
    p.pipe(
        "HANDLE_OUTER", (-0.119, 0.022, 0.107), (-0.119, 0.022, 0.067), 0.012, "white"
    )
    p.pipe(
        "HANDLE_LOWER", (-0.119, 0.022, 0.067), (-0.087, 0.022, 0.056), 0.012, "white"
    )
    for [x, y] in ((0.075, -0.073), (-0.019, -0.106), (0.101, 0.021)):
        p.turned(
            "CUP_OUTER",
            (x, y),
            [(0.020, 0.024), (0.030, 0.058), (0.031, 0.064)],
            "white",
        )
        p.cyl("TEA_SURFACE", (x, y, 0.065), 0.024, 0.003, "coffee")


def orchid(p, _size):
    p.turned(
        "WEAVE_PLANTER",
        (0, 0),
        [(0.086, 0), (0.106, 0.036), (0.112, 0.067), (0.125, 0.135)],
        "wood",
    )
    for z in (0.039, 0.058, 0.079, 0.100, 0.122):
        p.cyl("WOVEN_RIM", (0, 0, z), 0.118 + (z - 0.06) * 0.08, 0.004, "neutral")
    p.cyl("POTTING_FILL", (0, 0, 0.135), 0.119, 0.007, "coffee")
    for i in range(5):
        a = i * math.tau / 5
        x, y = math.cos(a), math.sin(a)
        leaf = p.box(
            "TAPERED_LEAF",
            (x * 0.078, y * 0.078, 0.18),
            (0.156, 0.041, 0.012),
            "green",
            0.006,
        )
        leaf.rotation_euler = (0, -0.23, a)
    for sx, sy, height in (
        (-0.098, 0.055, 0.51),
        (0.072, -0.052, 0.57),
        (0.015, 0.10, 0.49),
    ):
        p.pipe("STEM", (0, 0, 0.14), (sx * 0.55, sy * 0.6, 0.37), 0.006, "green")
        p.pipe(
            "FLOWERING_STEM",
            (sx * 0.55, sy * 0.6, 0.37),
            (sx, sy, height),
            0.005,
            "green",
        )
        for b in range(2):
            cx, cy, cz = (
                sx * (0.8 + b * 0.19),
                sy * (0.8 + b * 0.19),
                height - 0.057 * b,
            )
            for i in range(5):
                a = i * math.tau / 5
                petal = p.box(
                    "PETAL",
                    (cx + 0.022 * math.cos(a), cy - 0.013, cz + 0.017 * math.sin(a)),
                    (0.034, 0.013, 0.028),
                    "white" if i % 3 else "orchid",
                    0.006,
                )
                petal.rotation_euler.y = -a
            p.box(
                "ORCHID_CENTER",
                (cx, cy - 0.020, cz),
                (0.018, 0.015, 0.019),
                "orchid",
                0.005,
            )


def poster(p, size):
    width, _, height = size
    p.box("WOOD_BACK", (0, 0.013, height / 2), (width, 0.026, height), "wood", 0.004)
    p.box(
        "NEUTRAL_CARD",
        (0, -0.006, height / 2),
        (width - 0.043, 0.009, height - 0.043),
        "paper",
        0.001,
    )
    for side in (-1, 1):
        p.box(
            "VERTICAL_FRAME",
            (side * (width - 0.021) / 2, -0.013, height / 2),
            (0.021, 0.026, height),
            "wood",
            0.002,
        )
        p.box(
            "HORIZONTAL_FRAME",
            (0, -0.013, height / 2 + side * (height - 0.021) / 2),
            (width - 0.042, 0.026, 0.021),
            "wood",
            0.002,
        )


def clock(p, size):
    radius = size[0] / 2
    z = radius
    p.cyl("SILVER_BEZEL", (0, 0.005, z), radius, 0.044, "silver", "y")
    p.cyl("LIGHT_DIAL", (0, -0.018, z), radius - 0.011, 0.010, "white", "y")
    for i in range(60):
        a = i * math.tau / 60
        r = radius - 0.025
        mark = p.box(
            "HOUR_TICK" if i % 5 == 0 else "MINUTE_TICK",
            (math.sin(a) * r, -0.024, z + math.cos(a) * r),
            (0.006 if i % 5 == 0 else 0.0025, 0.003, 0.017 if i % 5 == 0 else 0.007),
            "black",
            0,
        )
        mark.rotation_euler.y = a
    for x, y in ((-0.075, 0.056), (0.096, 0.08)):
        p.pipe("CLOCK_HAND", (0, -0.028, z), (x, -0.028, z + y), 0.004, "black")
    p.cyl("HAND_PIN", (0, -0.028, z), 0.011, 0.004, "silver", "y")


def coffee(p, _size):
    p.box("DRIP_BASE", (0, 0, 0.030), (0.318, 0.321, 0.06), "black", 0.012)
    p.box("HEAT_PLATE", (0, -0.036, 0.066), (0.235, 0.223, 0.013), "silver", 0.008)
    p.box("TANK_BACK", (0, 0.111, 0.235), (0.304, 0.103, 0.35), "black", 0.013)
    p.box("BREW_HEAD", (0, 0.017, 0.355), (0.306, 0.287, 0.105), "black", 0.014)
    p.box("FRONT_CONTROLS", (0, -0.129, 0.367), (0.295, 0.015, 0.062), "silver", 0.005)
    for i in range(3):
        p.box(
            "COFFEE_BUTTON",
            (-0.064 + i * 0.037, -0.140, 0.365),
            (0.021, 0.009, 0.012),
            "black",
            0.002,
        )
    p.turned(
        "GLASS_CARAFE",
        (0, -0.033),
        [(0.077, 0.073), (0.096, 0.11), (0.085, 0.215), (0.065, 0.247)],
        "carafe",
    )
    p.cyl("CARAFE_LID", (0, -0.033, 0.255), 0.067, 0.022, "black")
    p.pipe(
        "CARAFE_HANDLE", (0.063, -0.03, 0.228), (0.122, -0.030, 0.216), 0.012, "black"
    )
    p.pipe(
        "CARAFE_HANDLE", (0.122, -0.030, 0.216), (0.116, -0.034, 0.115), 0.011, "black"
    )
    p.pipe(
        "CARAFE_HANDLE", (0.116, -0.034, 0.115), (0.083, -0.037, 0.106), 0.010, "black"
    )


def vessel(p, size, kind):
    width, depth, height = size
    r = min(width, depth) / 2
    if kind == "water_jug":
        profile = [(0.80 * r, 0), (0.96 * r, 0.021), (0.97 * r, 0.046)]
        for z in (0.077, 0.14, 0.204, 0.267, 0.329):
            profile.extend(((0.94 * r, z - 0.008), (r, z), (0.94 * r, z + 0.008)))
        profile.extend(
            (
                (0.94 * r, 0.369),
                (0.81 * r, 0.408),
                (0.51 * r, 0.433),
                (0.24 * r, 0.441),
                (0.24 * r, 0.463),
            )
        )
        p.turned("RIBBED_PET_BODY", (0, 0), profile, "jug")
        p.cyl("WATER_JUG_CAP", (0, 0, 0.475), 0.25 * r, 0.024, "blue")
    else:
        p.turned(
            "CONTAINER_BODY",
            (0, 0),
            [
                (0.77 * r, 0),
                (0.94 * r, 0.025),
                (0.89 * r, height * 0.68),
                (0.52 * r, height * 0.85),
            ],
            "white" if kind == "spray" else "foam" if kind == "bottle" else "neutral",
        )
        p.cyl(
            "CAP",
            (0, 0, height * 0.89),
            0.40 * r,
            height * 0.105,
            "black" if kind == "canister" else "paper",
        )
        if kind == "spray":
            p.box(
                "SPRAY_NOZZLE",
                (0, -0.016, height - 0.017),
                (r * 1.25, 0.055, 0.034),
                "blue",
                0.004,
            )


def storage(p, size, kind):
    width, depth, height = size
    if kind == "dishes":
        for i in range(5):
            z = 0.011 + i * 0.020
            p.turned(
                "STACKED_PLATE",
                (0, 0),
                [(0.122, z - 0.011), (0.143, z), (0.151, z + 0.007)],
                "white",
            )
        p.turned(
            "CEREAL_BOWL",
            (0, 0),
            [(0.067, 0.11), (0.098, 0.152), (0.096, 0.158)],
            "paper",
        )
    else:
        p.box(
            "BOTTOM",
            (0, 0, 0.013),
            (width - 0.016, depth - 0.016, 0.026),
            "neutral",
            0.008,
        )
        top = height if kind == "box" else height * 0.68
        for side in (-1, 1):
            p.box(
                "SIDE",
                (side * (width - 0.032) / 2, 0, top / 2),
                (0.021, depth - 0.017, top),
                "neutral",
                0.005,
            )
            p.box(
                "SIDE",
                (0, side * (depth - 0.032) / 2, top / 2),
                (width - 0.023, 0.021, top),
                "neutral",
                0.005,
            )
        if kind == "basket":
            for i in range(5):
                p.box(
                    "BASKET_RIB",
                    (-width * 0.40 + i * width * 0.2, -depth / 2 + 0.005, top / 2),
                    (0.009, 0.009, top),
                    "wood",
                    0.001,
                )
        elif kind == "box":
            p.box(
                "STACKABLE_LID",
                (0, 0, height - 0.013),
                (width, depth, 0.026),
                "paper",
                0.008,
            )
        else:
            for i in range(6):
                x = -0.142 + i * 0.055
                p.pipe(
                    "UTENSIL_HANDLE",
                    (x, 0, 0.12),
                    (x, 0.051, height - 0.035),
                    0.009,
                    "silver",
                )
                p.box(
                    "UTENSIL_HEAD",
                    (x, 0.055, height - 0.027),
                    (0.023, 0.013, 0.045),
                    "silver",
                    0.007,
                )


def build_mesh(record, collection, mats):
    kind = record["type"]
    parts = Parts(record["id"], collection, mats)
    size = record["size"]
    factories = {
        "computer": computer,
        "printer": printer,
        "tea": tea,
        "orchid": orchid,
        "poster": poster,
        "clock": clock,
        "coffee": coffee,
    }
    if kind in factories:
        factories[kind](parts, size)
    elif kind in ("water_jug", "bottle", "canister", "spray"):
        vessel(parts, size, kind)
    elif kind in ("basket", "dishes", "box", "utensils"):
        storage(parts, size, kind)
    else:
        raise ValueError(f"Unknown procedural model: {kind}")
    return pose_asset(parts.objects, record, collection, center=record["center"])


def shelf_mesh(item, surfaces, collection):
    mats = {
        "gray": bpy.data.materials["P507_PBR_UTILITY_GRAY_STEEL"],
        "blue": bpy.data.materials["P507_PBR_SHELF_BLUE_ENAMEL"],
        "top": bpy.data.materials["P507_PBR_LAMINATE_WHITE"],
    }
    p = Parts(item["id"], collection, mats)
    x0, y0, x1, y1 = item["rect"]
    width, depth, height = y1 - y0, x1 - x0, item["height"]
    for x in (-width / 2 + 0.023, width / 2 - 0.023):
        for y in (-depth / 2 + 0.022, depth / 2 - 0.022):
            p.box("UPRIGHT", (x, y, height / 2), (0.036, 0.042, height), "gray", 0.006)
    for z in surfaces:
        p.box(
            "PAN",
            (0, 0, z - 0.0175),
            (width - 0.012, depth - 0.014, 0.035),
            "top",
            0.006,
        )
        for side in (-1, 1):
            p.box(
                "BLUE_EDGE",
                (0, side * (depth - 0.025) / 2, z - 0.025),
                (width, 0.025, 0.05),
                "blue",
                0.003,
            )
    return pose_asset(
        p.objects, item, collection, center=((x0 + x1) / 2, (y0 + y1) / 2, 0)
    )
