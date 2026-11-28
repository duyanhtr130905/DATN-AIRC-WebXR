"""Blender mesh factories for neutral proposal assets."""

import math

import bpy
from generate_blender import cube, cylinder, lathe, material, pose_asset, tube


def _poster_art_material():
    name = "P507_SELF_GENERATED_POSTER_ART"
    existing = bpy.data.images.get(name)
    if existing:
        bpy.data.images.remove(existing)
    w, h = 128, 192
    img = bpy.data.images.new(name, width=w, height=h, alpha=True)
    pixels = []
    for y in range(h):
        ny = y / h
        for x in range(w):
            nx = x / w
            # Neutral geometric modernist poster pattern (zero text or external assets).
            if abs(nx - 0.5) < 0.36 and 0.64 < ny < 0.86:
                rgb = (0.14, 0.33, 0.42)
            elif ((nx - 0.50) ** 2 + (ny - 0.40) ** 2) ** 0.5 < 0.22:
                rgb = (0.72, 0.43, 0.25)
            elif 0.14 < nx < 0.86 and (0.16 < ny < 0.19 or 0.10 < ny < 0.125):
                rgb = (0.20, 0.26, 0.31)
            else:
                rgb = (0.91, 0.89, 0.84)
            pixels.extend((*rgb, 1.0))
    img.pixels.foreach_set(pixels)
    img.pack()
    mat = material("P507_R5_POSTER_ART", (0.91, 0.89, 0.84), 0.72, 0.0)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "EXTEND"
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def palette():
    colors = {
        "black": ((0.032, 0.038, 0.046), 0.34, 0.10),
        "screen": ((0.015, 0.020, 0.028), 0.14, 0.05),
        "key": ((0.19, 0.21, 0.24), 0.56, 0.06),
        "silver": ((0.64, 0.67, 0.70), 0.25, 0.78),
        "white": ((0.92, 0.91, 0.86), 0.36, 0.02),
        "paper": ((0.92, 0.91, 0.87), 0.82, 0.00),
        "wood": ((0.38, 0.21, 0.095), 0.42, 0.00),
        "orchid": ((0.76, 0.36, 0.78), 0.45, 0.00),
        "orchid_lip": ((0.88, 0.72, 0.22), 0.48, 0.00),
        "green": ((0.09, 0.31, 0.09), 0.52, 0.00),
        "leaf_tip": ((0.36, 0.52, 0.13), 0.50, 0.00),
        "blue": ((0.05, 0.30, 0.54), 0.30, 0.10),
        "jug": ((0.22, 0.66, 0.84), 0.13, 0.00),
        "carafe": ((0.34, 0.46, 0.48), 0.10, 0.00),
        "coffee": ((0.12, 0.058, 0.022), 0.32, 0.00),
        "foam": ((0.26, 0.44, 0.32), 0.64, 0.00),
        "neutral": ((0.58, 0.50, 0.36), 0.46, 0.00),
        "clock_glass": ((0.84, 0.91, 0.94), 0.08, 0.00),
        "led_green": ((0.18, 0.68, 0.42), 0.30, 0.00),
    }
    mats = {
        name: material("P507_R5_" + name.upper(), rgb, roughness, metal)
        for name, (rgb, roughness, metal) in colors.items()
    }
    screen_bsdf = mats["screen"].node_tree.nodes.get("Principled BSDF")
    sk = "Specular IOR Level" if "Specular IOR Level" in screen_bsdf.inputs else "Specular"
    if sk in screen_bsdf.inputs:
        screen_bsdf.inputs[sk].default_value = 0.48
    led_bsdf = mats["led_green"].node_tree.nodes.get("Principled BSDF")
    if "Emission Color" in led_bsdf.inputs:
        led_bsdf.inputs["Emission Color"].default_value = (0.18, 0.78, 0.46, 1.0)
        led_bsdf.inputs["Emission Strength"].default_value = 0.85
    for name, alpha in (("jug", 0.54), ("carafe", 0.36), ("clock_glass", 0.14)):
        bsdf = mats[name].node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mats[name], "surface_render_method"):
            mats[name].surface_render_method = "BLENDED"
        if hasattr(mats[name], "blend_method"):
            mats[name].blend_method = "BLEND"
    mats["poster_art"] = _poster_art_material()
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
    p.box("OVAL_BASE", (0, 0.112, 0.009), (0.22, 0.175, 0.018), "silver", 0.008)
    p.box("RISER", (0, 0.134, 0.13), (0.044, 0.040, 0.244), "silver", 0.008)
    p.box("NECK_HINGE", (0, 0.126, 0.252), (0.072, 0.028, 0.036), "black", 0.006)
    p.box("DISPLAY_BEZEL", (0, 0.118, 0.322), (0.508, 0.032, 0.312), "black", 0.008)
    p.box("DISPLAY_CHIN", (0, 0.104, 0.173), (0.504, 0.014, 0.016), "silver", 0.003)
    p.box("INACTIVE_DISPLAY", (0, 0.100, 0.326), (0.486, 0.006, 0.284), "screen", 0.003)
    p.box("STANDBY_DOT", (0.22, 0.095, 0.173), (0.010, 0.004, 0.004), "led_green", 0.001)
    p.box("KEYBOARD", (-0.050, -0.100, 0.011), (0.360, 0.139, 0.020), "black", 0.007)
    for row in range(4):
        for col in range(12):
            p.box(
                "KEY",
                (-0.208 + col * 0.026, -0.143 + row * 0.023, 0.022),
                (0.018, 0.016, 0.006),
                "key",
                0.001,
            )
    p.box("SPACE", (-0.082, -0.081, 0.026), (0.092, 0.014, 0.006), "key", 0.001)
    p.box("MOUSE", (0.192, -0.120, 0.016), (0.062, 0.102, 0.032), "black", 0.014)
    p.box("MOUSE_SCROLL", (0.192, -0.134, 0.032), (0.009, 0.026, 0.005), "silver", 0.002)


def printer(p, _size):
    p.box("CARCASS", (0, 0.032, 0.110), (0.356, 0.285, 0.220), "white", 0.012)
    p.box("SCANNER_LID", (0, 0.043, 0.232), (0.349, 0.267, 0.026), "silver", 0.009)
    p.box("TOP_PAPER_TRAY", (0, 0.112, 0.250), (0.220, 0.040, 0.026), "black", 0.006)
    p.box("OUTPUT_MOUTH", (0, -0.112, 0.089), (0.270, 0.016, 0.048), "black", 0.005)
    p.box("OUTPUT_TRAY", (0, -0.150, 0.055), (0.224, 0.086, 0.015), "key", 0.006)
    p.box("PRINTED_SHEET", (0, -0.145, 0.065), (0.190, 0.095, 0.004), "paper", 0.001)
    p.box("PAPER_CASSETTE", (0, -0.112, 0.026), (0.303, 0.023, 0.033), "silver", 0.006)
    p.box(
        "FRONT_CONTROL", (0.118, -0.113, 0.184), (0.084, 0.018, 0.052), "black", 0.006
    )
    p.box("PRINTER_STATUS_LED", (0.142, -0.123, 0.198), (0.016, 0.004, 0.006), "led_green", 0.001)
    for i in range(3):
        p.box(
            "CONTROL",
            (0.093 + i * 0.023, -0.124, 0.178),
            (0.010, 0.007, 0.011),
            "paper",
            0.002,
        )


def tea(p, _size):
    p.turned(
        "ROUND_TRAY",
        (0, 0),
        [(0.165, 0.0), (0.176, 0.008), (0.178, 0.028), (0.168, 0.028), (0.163, 0.014), (0.001, 0.014)],
        "wood",
    )
    p.turned(
        "TEAPOT",
        (-0.035, 0.022),
        [(0.046, 0.014), (0.066, 0.068), (0.052, 0.137), (0.036, 0.152)],
        "white",
    )
    p.cyl("LID_KNOB", (-0.035, 0.022, 0.162), 0.012, 0.019, "white")
    p.pipe("SPOUT", (0.004, 0.020, 0.075), (0.075, 0.035, 0.132), 0.015, "white")
    p.pipe(
        "HANDLE_UPPER", (-0.087, 0.022, 0.115), (-0.119, 0.022, 0.107), 0.010, "white"
    )
    p.pipe(
        "HANDLE_OUTER", (-0.119, 0.022, 0.107), (-0.119, 0.022, 0.067), 0.010, "white"
    )
    p.pipe(
        "HANDLE_LOWER", (-0.119, 0.022, 0.067), (-0.087, 0.022, 0.056), 0.010, "white"
    )
    for [x, y] in ((0.075, -0.073), (-0.019, -0.106), (0.101, 0.021)):
        p.cyl("CUP_SAUCER", (x, y, 0.017), 0.042, 0.006, "white")
        p.turned(
            "CUP_OUTER",
            (x, y),
            [(0.020, 0.020), (0.030, 0.058), (0.031, 0.064)],
            "white",
        )
        p.cyl("TEA_SURFACE", (x, y, 0.062), 0.024, 0.003, "coffee")


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
    for i in range(6):
        a = i * math.tau / 6
        x, y = math.cos(a), math.sin(a)
        leaf = p.box(
            "TAPERED_LEAF",
            (x * 0.072, y * 0.072, 0.170),
            (0.145, 0.042, 0.010),
            "green",
            0.005,
        )
        leaf.rotation_euler = (0, -0.26, a)
        tip = p.box(
            "LEAF_TIP",
            (x * 0.145, y * 0.145, 0.195),
            (0.065, 0.026, 0.007),
            "leaf_tip",
            0.003,
        )
        tip.rotation_euler = (0, 0.12, a)
    for sx, sy, height in (
        (-0.098, 0.055, 0.51),
        (0.072, -0.052, 0.57),
        (0.015, 0.10, 0.49),
    ):
        p.pipe("STEM", (0, 0, 0.14), (sx * 0.55, sy * 0.6, 0.37), 0.005, "green")
        p.pipe(
            "FLOWERING_STEM",
            (sx * 0.55, sy * 0.6, 0.37),
            (sx, sy, height),
            0.004,
            "green",
        )
        for b in range(3):
            cx, cy, cz = (
                sx * (0.72 + b * 0.13),
                sy * (0.72 + b * 0.13),
                height - 0.052 * b,
            )
            for i in range(5):
                a = i * math.tau / 5
                petal = p.box(
                    "PETAL",
                    (cx + 0.022 * math.cos(a), cy - 0.013, cz + 0.017 * math.sin(a)),
                    (0.034, 0.012, 0.028),
                    "white" if i % 3 else "orchid",
                    0.006,
                )
                petal.rotation_euler.y = -a
            p.box(
                "ORCHID_CENTER",
                (cx, cy - 0.020, cz),
                (0.016, 0.014, 0.017),
                "orchid_lip",
                0.005,
            )


def poster(p, size):
    width, _, height = size
    p.box("WOOD_BACK", (0, 0.013, height / 2), (width, 0.024, height), "wood", 0.004)
    p.box(
        "MAT_BOARD",
        (0, -0.003, height / 2),
        (width - 0.042, 0.008, height - 0.042),
        "paper",
        0.001,
    )
    art = p.box(
        "NEUTRAL_CARD",
        (0, -0.008, height / 2),
        (width - 0.072, 0.004, height - 0.072),
        "poster_art",
        0.001,
    )
    # Planar UV on the front poster card so the procedural artwork maps 0..1 cleanly
    mesh = art.data
    uv = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
    bw = max(1e-4, width - 0.072)
    bh = max(1e-4, height - 0.072)
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            v = mesh.vertices[mesh.loops[loop_idx].vertex_index].co
            uv.data[loop_idx].uv = (v.x / bw + 0.5, v.z / bh + 0.5)
    for side in (-1, 1):
        p.box(
            "VERTICAL_FRAME",
            (side * (width - 0.021) / 2, -0.012, height / 2),
            (0.021, 0.024, height),
            "wood",
            0.003,
        )
        p.box(
            "HORIZONTAL_FRAME",
            (0, -0.012, height / 2 + side * (height - 0.021) / 2),
            (width - 0.042, 0.024, 0.021),
            "wood",
            0.003,
        )


def clock(p, size):
    radius = size[0] / 2
    z = radius
    p.cyl("SILVER_BEZEL", (0, 0.005, z), radius, 0.044, "silver", "y")
    p.cyl("LIGHT_DIAL", (0, -0.018, z), radius - 0.011, 0.010, "white", "y")
    p.cyl("CLOCK_LENS", (0, -0.027, z), radius - 0.012, 0.003, "clock_glass", "y")
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
        p.pipe("CLOCK_HAND", (0, -0.025, z), (x, -0.025, z + y), 0.004, "black")
    p.cyl("HAND_PIN", (0, -0.025, z), 0.011, 0.004, "silver", "y")


def coffee(p, _size):
    p.box("DRIP_BASE", (0, 0, 0.030), (0.318, 0.321, 0.06), "black", 0.012)
    p.box("HEAT_PLATE", (0, -0.036, 0.066), (0.235, 0.223, 0.013), "silver", 0.008)
    p.box("TANK_BACK", (0, 0.111, 0.235), (0.304, 0.103, 0.35), "black", 0.013)
    p.box("BREW_HEAD", (0, 0.017, 0.355), (0.306, 0.287, 0.105), "black", 0.014)
    p.box("FRONT_CONTROLS", (0, -0.129, 0.367), (0.295, 0.015, 0.062), "silver", 0.005)
    p.box("COFFEE_LED", (0.085, -0.138, 0.365), (0.012, 0.004, 0.008), "led_green", 0.001)
    for i in range(3):
        p.box(
            "COFFEE_BUTTON",
            (-0.064 + i * 0.037, -0.140, 0.365),
            (0.021, 0.009, 0.012),
            "black",
            0.002,
        )
    p.cyl("BREWED_COFFEE", (0, -0.033, 0.118), 0.081, 0.088, "coffee")
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
