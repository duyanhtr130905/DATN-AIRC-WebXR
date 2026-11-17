"""Blender G1+G2 source generator: provisional P507 room + hero corner.

USAGE: blender -b --python generate_blender.py -- --inventory p507-provisional.json --output-dir /path/to/local/output
Requires Blender with bundled glTF exporter. Output is NOT AIRC-verified.
No private photographs, screen contents, or AIRC logo textures are embedded.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import itertools

from geometry import read_inventory, verify

try:
    import bpy
except ImportError as exc:
    raise SystemExit(
        "Blender bpy unavailable. Run from Blender Python; do not claim GLB export PASS."
    ) from exc


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inventory", type=Path, default=HERE / "p507-provisional.json"
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(values)


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def move_to_collection(obj, dest):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    dest.objects.link(obj)


def material(name, rgb, roughness=0.7, metalness=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metalness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    mat.diffuse_color = (*rgb, 1.0)
    return mat


def procedural_floor_tiles():
    """License-free color pattern authored here: warm, lightly speckled 0.60m tiles with grout."""
    mat = material("P507_PBR_PROCEDURAL_TILE_060M", (0.82, 0.82, 0.79), 0.38)
    image = bpy.data.images.new(
        "P507_SELF_GENERATED_NEUTRAL_TILE", width=256, height=256, alpha=True
    )
    pixels = []
    import random

    rng = random.Random(507)
    for y in range(256):
        for x in range(256):
            seam = x < 2 or y < 2
            variation = rng.uniform(-0.013, 0.013)
            base = (0.57, 0.58, 0.57) if seam else (0.79, 0.80, 0.78)
            pixels.extend(
                (base[0] + variation, base[1] + variation, base[2] + variation, 1.0)
            )
    image.pixels.foreach_set(pixels)
    image.pack()
    shader = mat.node_tree.nodes.get("Principled BSDF")
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "REPEAT"
    mat.node_tree.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
    return mat


def procedural_wood():
    mat = material("P507_PBR_SELF_AUTHORED_PALE_OAK", (0.68, 0.55, 0.39), 0.55)
    image = bpy.data.images.new(
        "P507_SELF_GENERATED_OAK_GRAIN", width=256, height=256, alpha=True
    )
    pixels = []
    for y in range(256):
        for x in range(256):
            grain = 0.020 * math.sin(
                x * 0.37 + math.sin(y * 0.025) * 2
            ) + 0.008 * math.sin(x * 1.3 + y * 0.03)
            pixels.extend((0.69 + grain, 0.58 + grain, 0.43 + grain, 1))
    image.pixels.foreach_set(pixels)
    image.pack()
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    mat.node_tree.links.new(
        tex.outputs["Color"],
        mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"],
    )
    return mat


def cube(name, center, size, mat, col, bevel=0.0, ident=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if bevel > 0:
        modifier = o.modifiers.new("Edge relief", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        if hasattr(modifier, "affect"):
            modifier.affect = "EDGES"
        o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    if ident:
        o["survey_instance_id"] = ident
        o["source_class"] = "PROPOSED_LAYOUT"
    move_to_collection(o, col)
    return o


def cylinder(name, center, radius, depth, mat, col, vertices=16, ident=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=center
    )
    o = bpy.context.object
    o.name = name
    if mat:
        o.data.materials.append(mat)
    if ident:
        o["survey_instance_id"] = ident
        o["source_class"] = "PROPOSED_LAYOUT"
    move_to_collection(o, col)
    return o


def room_shell(data, col, mats):
    w, length, height = [data["room"][k] for k in ("width_x", "length_y", "height_z")]
    wall_thickness = 0.10
    floor = cube(
        "P507_ARCH_FLOOR",
        (w / 2, length / 2, -0.045),
        (w, length, 0.09),
        mats["tile"],
        col,
    )
    floor["chair_inventory_count"] = data["chairs"]["count"]
    floor["chair_placed_count"] = sum(
        c["status"] == "PLACED_PROVISIONAL" for c in data["chairs"]["instances"]
    )
    floor["unplaced_chair_ids"] = json.dumps(
        [c["id"] for c in data["chairs"]["instances"] if c["status"] == "UNPLACED"]
    )
    floor["unplaced_chair_reasons"] = json.dumps(
        {
            c["id"]: c.get(
                "placement_reason", "Placement remains unknown in this proposed layout"
            )
            for c in data["chairs"]["instances"]
            if c["status"] == "UNPLACED"
        }
    )
    uv = floor.data.uv_layers.active or floor.data.uv_layers.new(name="MetricTileUV")
    for face in floor.data.polygons:
        if face.normal.z > 0.8:
            for loop_idx in face.loop_indices:
                vertex = floor.data.vertices[floor.data.loops[loop_idx].vertex_index]
                uv.data[loop_idx].uv = (
                    (vertex.co.x + w / 2) / 0.60,
                    (vertex.co.y + length / 2) / 0.60,
                )
    cube(
        "P507_ARCH_WALL_LOGO",
        (w / 2, 0, height / 2),
        (w, wall_thickness, height),
        mats["paint"],
        col,
    )
    cube(
        "P507_ARCH_WALL_TV",
        (w / 2, length, height / 2),
        (w, wall_thickness, height),
        mats["paint"],
        col,
    )
    door = data["openings"]["door"]
    if door["wall"] != "west":
        raise ValueError("G1 only supports entrance on west wall")
    segments = [(0, door["from_y"]), (door["to_y"], length)]
    for idx, (y0, y1) in enumerate(segments):
        if y1 > y0:
            cube(
                f"P507_ARCH_WALL_WEST_{idx:02d}",
                (0, (y0 + y1) / 2, height / 2),
                (wall_thickness, y1 - y0, height),
                mats["paint"],
                col,
            )
    cube(
        "P507_ARCH_WEST_DOOR_HEADER",
        (0, (door["from_y"] + door["to_y"]) / 2, (door["height"] + height) / 2),
        (wall_thickness, door["to_y"] - door["from_y"], height - door["height"]),
        mats["paint"],
        col,
    )
    # Architectural openings are real voids, not a door mesh over an intact wall.
    windows = data["openings"]["windows"]
    cursor = 0
    for idx, win in enumerate(windows):
        a, b = win["from_y"], win["to_y"]
        if a < cursor or b > length or a >= b:
            raise ValueError("Invalid or overlapping window intervals")
        if a > cursor:
            cube(
                f"P507_ARCH_WALL_EAST_{idx:02d}",
                (w, (cursor + a) / 2, height / 2),
                (wall_thickness, a - cursor, height),
                mats["paint"],
                col,
            )
        sill, top = win["sill_z"], win["top_z"]
        cube(
            f"P507_ARCH_EAST_SILL_{idx:02d}",
            (w, (a + b) / 2, sill / 2),
            (wall_thickness, b - a, sill),
            mats["paint"],
            col,
        )
        cube(
            f"P507_ARCH_EAST_HEADER_{idx:02d}",
            (w, (a + b) / 2, (top + height) / 2),
            (wall_thickness, b - a, height - top),
            mats["paint"],
            col,
        )
        cube(
            f"P507_ARCH_WINDOW_GLASS_{idx:02d}",
            (w - 0.005, (a + b) / 2, (sill + top) / 2),
            (0.008, b - a - 0.035, top - sill - 0.035),
            mats["glass"],
            col,
            ident=win.get("id"),
        )
        for y in (a, b):
            cube(
                f"P507_ARCH_WINDOW_JAMB_{idx:02d}_{int(y * 100):02d}",
                (w - 0.026, y, (sill + top) / 2),
                (0.045, 0.06, top - sill),
                mats["white_metal"],
                col,
                0.005,
            )
        cursor = b
    if cursor < length:
        cube(
            "P507_ARCH_WALL_EAST_LAST",
            (w, (cursor + length) / 2, height / 2),
            (wall_thickness, length - cursor, height),
            mats["paint"],
            col,
        )
    # PHOTO-03/12: distinct fabric drop at each opening, metric casing and weighted bar.
    for idx, win in enumerate(windows):
        yc = (win["from_y"] + win["to_y"]) / 2
        span = win["to_y"] - win["from_y"]
        blind = win.get("blind", {"id": f"P507-BLIND-{idx + 1:02d}", "drop_m": 0.8})
        drop = blind["drop_m"]
        top = 2.98
        parts = []
        parts.append(
            cube(
                f"P507_ARCH_ROLLER_SHADE_{idx:02d}",
                (w - 0.10, yc, top - drop / 2),
                (0.026, span - 0.05, drop),
                mats["blind"],
                col,
                0.005,
            )
        )
        roller = cylinder(
            f"P507_ARCH_BLIND_ROLLER_{idx:02d}",
            (w - 0.10, yc, top + 0.01),
            0.035,
            span,
            mats["white_metal"],
            col,
            20,
        )
        roller.rotation_euler.x = math.pi / 2
        parts.append(roller)
        parts.append(
            cube(
                f"P507_ARCH_BLIND_WEIGHTED_BAR_{idx:02d}",
                (w - 0.10, yc, top - drop + 0.0125),
                (0.035, span - 0.035, 0.025),
                mats["white_metal"],
                col,
                0.005,
            )
        )
        for yy in (win["from_y"] + 0.0125, win["to_y"] - 0.0125):
            parts.append(
                cube(
                    "P507_ARCH_BLIND_END_BRACKET",
                    (w - 0.10, yy, top + 0.01),
                    (0.07, 0.025, 0.07),
                    mats["white_metal"],
                    col,
                    0.006,
                )
            )
        pose_asset(
            parts,
            {**blind, "orientation_deg": 0, "type": "roller_blind"},
            col,
            angle=0,
            prefix=f"P507_ARCH_BLIND_ASSEMBLY_{idx:02d}",
        )
        # Window mullions/sliding split remain neutral; source screen/poster content excluded.
        for yy in (win["from_y"], yc, win["to_y"]):
            cube(
                "P507_ARCH_WINDOW_MULLION",
                (w - 0.025, yy, (win["sill_z"] + win["top_z"]) / 2),
                (0.04, 0.035, win["top_z"] - win["sill_z"]),
                mats["white_metal"],
                col,
                0.004,
                win.get("id"),
            )
        for zz in (win["sill_z"], win["top_z"]):
            cube(
                "P507_ARCH_WINDOW_TRANSOM",
                (w - 0.025, yc, zz),
                (0.045, span, 0.035),
                mats["white_metal"],
                col,
                0.004,
                win.get("id"),
            )
    cube(
        "P507_ARCH_BASEBOARD_LOGO",
        (w / 2, 0.075, 0.07),
        (w, 0.03, 0.14),
        mats["white_metal"],
        col,
        0.004,
    )
    cube(
        "P507_ARCH_BASEBOARD_EAST",
        (w - 0.07, length / 2, 0.07),
        (0.03, length, 0.14),
        mats["white_metal"],
        col,
        0.004,
    )
    cube(
        "P507_ARCH_DOOR_FRAME_LOW",
        (0, door["from_y"], door["height"] / 2),
        (0.14, 0.06, door["height"]),
        mats["white_metal"],
        col,
        0.008,
    )
    cube(
        "P507_ARCH_DOOR_FRAME_HIGH",
        (0, door["to_y"], door["height"] / 2),
        (0.14, 0.06, door["height"]),
        mats["white_metal"],
        col,
        0.008,
    )
    cube(
        "P507_ARCH_DOOR_FRAME_LINTEL",
        (0, (door["from_y"] + door["to_y"]) / 2, door["height"]),
        (0.18, door["to_y"] - door["from_y"] + 0.06, 0.07),
        mats["white_metal"],
        col,
        0.009,
    )
    for yy in (door["from_y"] - 0.035, door["to_y"] + 0.035):
        cube(
            "P507_ARCH_DOOR_REVEAL",
            (-0.055, yy, door["height"] / 2),
            (0.25, 0.035, door["height"]),
            mats["wood"],
            col,
            0.005,
        )
    # Two leaves are photo-observed; their opening angle remains a proposed pose below.
    # Real, editable modular ceiling tiles, rather than deleting the ceiling for plan shots.
    step = 0.60
    for ix in range(math.ceil(w / step)):
        x0, x1 = ix * step, min(w, (ix + 1) * step)
        for iy in range(math.ceil(length / step)):
            y0, y1 = iy * step, min(length, (iy + 1) * step)
            cube(
                f"P507_ARCH_CEILING_TILE_{ix:02d}_{iy:02d}",
                ((x0 + x1) / 2, (y0 + y1) / 2, height + 0.018),
                (x1 - x0 - 0.007, y1 - y0 - 0.007, 0.036),
                mats["ceiling"],
                col,
                0.002,
            )
    for ix in range(1, math.ceil(w / step)):
        cube(
            f"P507_ARCH_CEILING_GRID_X_{ix:02d}",
            (ix * step, length / 2, height - 0.004),
            (0.011, length, 0.018),
            mats["white_metal"],
            col,
            0.001,
        )
    for iy in range(1, math.ceil(length / step)):
        cube(
            f"P507_ARCH_CEILING_GRID_Y_{iy:02d}",
            (w / 2, iy * step, height - 0.004),
            (w, 0.011, 0.018),
            mats["white_metal"],
            col,
            0.001,
        )
    # Two physical leaves observed in PHOTO-13. Pose angle remains a proposal.
    for leaf in door.get("leaves", []):
        thickness, proxywidth, proxyheight = leaf["size"]
        width = proxywidth - 0.06
        lh = proxyheight - 0.08
        parts = []
        for yy in (-width / 2 + 0.018, width / 2 - 0.018):
            parts.append(
                cube(
                    "P507_ARCH_DOOR_LEAF_STILE",
                    (0, yy, 0),
                    (thickness, 0.036, lh),
                    mats["white_metal"],
                    col,
                    0.004,
                )
            )
        for zz in (-lh / 2 + 0.018, lh / 2 - 0.018, -0.40):
            parts.append(
                cube(
                    "P507_ARCH_DOOR_LEAF_RAIL",
                    (0, 0, zz),
                    (thickness, width, 0.036),
                    mats["white_metal"],
                    col,
                    0.004,
                )
            )
        parts.append(
            cube(
                "P507_ARCH_DOOR_LEAF_LOWER_PANEL",
                (0, 0, -0.80),
                (thickness * 0.70, width - 0.07, 0.73),
                mats["cabinet"],
                col,
                0.004,
            )
        )
        parts.append(
            cube(
                "P507_ARCH_DOOR_LEAF_FROSTED_GLASS",
                (0, 0, 0.385),
                (thickness * 0.36, width - 0.07, 1.47),
                mats["frosted_glass"],
                col,
                0.003,
            )
        )
        for yy in (width * 0.36,) if leaf["id"].endswith("01") else (-width * 0.36,):
            parts.append(
                cube(
                    "P507_ARCH_DOOR_LEAF_HANDLE",
                    (0.022, yy, -0.24),
                    (0.014, 0.10, 0.015),
                    mats["chrome"],
                    col,
                    0.005,
                )
            )
        pose_asset(
            parts,
            leaf,
            col,
            tuple(leaf["center"]),
            merge=True,
            prefix=leaf["id"].replace("-", "_") + "_ASSEMBLY",
        )


def combine(objects, name, col, ident=None):
    """Apply authored relief and combine a modular asset; shared chair data stays linked."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        for mod in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(False)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    if ident:
        obj["survey_instance_id"] = ident
        obj["source_class"] = "PROPOSED_LAYOUT"
    return obj


def tube(name, start, end, radius, mat, col):
    from mathutils import Vector

    delta = Vector(end) - Vector(start)
    obj = cylinder(
        name, (Vector(start) + Vector(end)) / 2, radius, delta.length, mat, col, 12
    )
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def curved_back_patch(name, x0, x1, z0, z1, mat, col):
    """Closed moulded shell segment. Separate patches leave a genuine hand slot."""
    n = 12
    vertices = []
    for layer in (-0.012, 0.012):
        for z in (z0, z1):
            for i in range(n + 1):
                x = x0 + (x1 - x0) * i / n
                vertices.append((x, -0.245 + 0.045 * (x / 0.215) ** 2 + layer, z))
    row = n + 1
    faces = []
    for i in range(n):
        faces.extend(
            [
                (i, i + 1, row + i + 1, row + i),
                (2 * row + i, 3 * row + i, 3 * row + i + 1, 2 * row + i + 1),
                (i, 2 * row + i, 2 * row + i + 1, i + 1),
                (row + i, row + i + 1, 3 * row + i + 1, 3 * row + i),
            ]
        )
    faces.extend(
        [(0, row, 3 * row, 2 * row), (row - 1, 3 * row - 1, 4 * row - 1, 2 * row - 1)]
    )
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.materials.append(mat)
    for f in mesh.polygons:
        f.use_smooth = True
    bevel = obj.modifiers.new("Moulded shell rim", "BEVEL")
    bevel.width = 0.007
    bevel.segments = 3
    obj.modifiers.new("Shell weighted normals", "WEIGHTED_NORMAL")
    return obj


def chair_module(col, mats):
    parts = [
        cube(
            "CHAIR_MOULDED_SEAT",
            (0, 0, 0.465),
            (0.44, 0.43, 0.055),
            mats["chair"],
            col,
            0.035,
        )
    ]
    # PHOTO-06/13 show a navy moulded back, handhold and metal sled/cantilever base.
    for suffix, x0, x1, z0, z1 in [
        ("LOWER", -0.215, 0.215, 0.60, 0.855),
        ("TOP", -0.215, 0.215, 0.91, 1.0),
        ("LEFT", -0.215, -0.075, 0.855, 0.91),
        ("RIGHT", 0.075, 0.215, 0.855, 0.91),
    ]:
        parts.append(
            curved_back_patch(
                "CHAIR_BACK_" + suffix, x0, x1, z0, z1, mats["chair"], col
            )
        )
    for x in (-0.178, 0.178):
        path = [
            (x, -0.225, 0.022),
            (x, 0.19, 0.022),
            (x, 0.19, 0.405),
            (x, 0.13, 0.432),
            (x, -0.17, 0.432),
            (x, -0.225, 0.83),
        ]
        for a, b in itertools.pairwise(path):
            parts.append(
                tube("CHAIR_CANTILEVER_TUBE", a, b, 0.012, mats["chrome"], col)
            )
        parts.append(
            cube(
                "CHAIR_REAR_GLIDE",
                (x, -0.20, 0.014),
                (0.043, 0.095, 0.028),
                mats["screen_frame"],
                col,
                0.01,
            )
        )
        parts.append(
            cube(
                "CHAIR_FRONT_GLIDE",
                (x, 0.16, 0.014),
                (0.043, 0.07, 0.028),
                mats["screen_frame"],
                col,
                0.01,
            )
        )
    parts.append(
        tube(
            "CHAIR_UNDERSEAT_BRACE",
            (-0.178, 0.12, 0.422),
            (0.178, 0.12, 0.422),
            0.011,
            mats["chrome"],
            col,
        )
    )
    obj = combine(parts, "P507_CHAIR_MODULE", col)
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return obj


def tables_and_chairs(data, tables_col, chairs_col, mats):
    for item in data["objects"]:
        if item.get("status") == "UNPLACED":
            continue
        xmin, ymin, xmax, ymax = item["rect"]
        cx, cy, sx, sy = (xmin + xmax) / 2, (ymin + ymax) / 2, xmax - xmin, ymax - ymin
        ident = item["id"]
        name = ident.replace("-", "_")
        h = item["height"]
        if item.get("type") not in ("table_standard", "table_small"):
            continue
        parts = [
            cube(
                name + "_LAMINATE_TOP",
                (cx, cy, h - 0.025),
                (sx, sy, 0.05),
                mats["laminate"],
                tables_col,
                0.012,
            )
        ]
        for ix in (-1, 1):
            for iy in (-1, 1):
                x = cx + ix * (sx / 2 - 0.065)
                y = cy + iy * (sy / 2 - 0.065)
                parts.append(
                    cube(
                        name + "_STEEL_LEG",
                        (x, y, (h - 0.05) / 2),
                        (0.039, 0.039, h - 0.05),
                        mats["table_steel"],
                        tables_col,
                        0.004,
                    )
                )
                parts.append(
                    cube(
                        name + "_FOOT",
                        (x, y, 0.012),
                        (0.045, 0.045, 0.024),
                        mats["chair"],
                        tables_col,
                        0.005,
                    )
                )
        for iy in (-1, 1):
            parts.append(
                cube(
                    name + "_APRON_X",
                    (cx, cy + iy * (sy / 2 - 0.065), h - 0.10),
                    (sx - 0.10, 0.029, 0.065),
                    mats["table_steel"],
                    tables_col,
                    0.004,
                )
            )
        for ix in (-1, 1):
            parts.append(
                cube(
                    name + "_APRON_Y",
                    (cx + ix * (sx / 2 - 0.065), cy, h - 0.10),
                    (0.029, sy - 0.10, 0.065),
                    mats["table_steel"],
                    tables_col,
                    0.004,
                )
            )
        combine(parts, name + "_ASSEMBLY", tables_col, ident)
    module = None
    for item in data["chairs"]["instances"]:
        if item["status"] != "PLACED_PROVISIONAL":
            continue
        if module is None:
            module = chair_module(chairs_col, mats)
            obj = module
        else:
            obj = bpy.data.objects.new(item["id"], module.data)
            chairs_col.objects.link(obj)
        obj.name = item["id"]
        obj.location = (*item["center"], 0)
        obj.rotation_euler.z = math.radians(item["orientation_deg"])
        obj["survey_instance_id"] = item["id"]
        obj["source_class"] = item["source_kind"]
        obj["placement_status"] = item["status"]
        obj["cluster"] = item["cluster"]
        obj["placement_role"] = item.get("placement_role", "row")


def pose_asset(parts, item, col, center=(0, 0, 0), angle=None, merge=True, prefix=None):
    """Apply actual mesh transforms, then attach stable logical identity and provenance."""
    from mathutils import Matrix, Vector

    bpy.context.view_layer.update()
    theta = math.radians(item.get("orientation_deg", 0) if angle is None else angle)
    matrix = Matrix.Translation(Vector(center)) @ Matrix.Rotation(theta, 4, "Z")
    for obj in parts:
        obj.matrix_world = matrix @ obj.matrix_world
        obj["survey_instance_id"] = item["id"]
        obj["source_class"] = item.get("source_kind", "PROPOSED_LAYOUT")
        obj["placement_status"] = item.get("status", "PLACED_PROVISIONAL")
        obj["orientation_deg"] = math.degrees(theta)
        obj["surface_front_survey"] = [math.sin(theta), -math.cos(theta), 0.0]
        obj["logical_type"] = item.get("type", "hero")
        if item.get("support_id"):
            obj["support_id"] = item["support_id"]
    if merge and len(parts) > 1:
        obj = combine(
            parts, prefix or item["id"].replace("-", "_") + "_ASSEMBLY", col, item["id"]
        )
        obj["orientation_deg"] = math.degrees(theta)
        obj["surface_front_survey"] = [math.sin(theta), -math.cos(theta), 0.0]
        obj["logical_type"] = item.get("type", "hero")
        if item.get("support_id"):
            obj["support_id"] = item["support_id"]
        return obj
    return parts[0] if parts else None


def utility_assets(data, col, mats):
    for item in data["objects"]:
        kind = item.get("type")
        if (
            kind in ("table_standard", "table_small", "decor_display", "tv_mount")
            or item.get("status") == "UNPLACED"
        ):
            continue
        x0, y0, x1, y1 = item["rect"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        angle = item.get("orientation_deg", 0)
        w, d = (y1 - y0, x1 - x0) if angle % 180 == 90 else (x1 - x0, y1 - y0)
        # Overall rect includes handles/door relief; appliance carcass reserves20mm for them.
        if kind in ("file_cabinet", "fridge"):
            d -= 0.02
        h = item["height"]
        z0 = item.get("bottom_z", 0)
        parts = []

        def box(name, xyz, size, mat, bevel=0.006, item=item, z0=z0, parts=parts):
            obj = cube(
                item["id"].replace("-", "_") + "_" + name,
                (xyz[0], xyz[1], xyz[2] + z0),
                size,
                mats[mat],
                col,
                bevel,
            )
            parts.append(obj)
            return obj

        def pipe(name, a, b, r=0.012, mat="chrome", item=item, z0=z0, parts=parts):
            obj = tube(
                item["id"] + "_" + name,
                (a[0], a[1], a[2] + z0),
                (b[0], b[1], b[2] + z0),
                r,
                mats[mat],
                col,
            )
            parts.append(obj)

        if kind == "file_cabinet":
            box(
                "STEEL_CARCASS",
                (0, 0, h / 2),
                (w - 0.02, d - 0.02, h),
                "utility_steel",
                0.012,
            )
            box(
                "DARK_INTERIOR",
                (0, -d / 2 + 0.025, h * 0.69),
                (w - 0.055, 0.018, h * 0.53),
                "screen_frame",
            )
            for xx in (-w / 4, w / 4):
                # Separate upper glazed and lower opaque leaves with actual borders.
                for zz, hh in ((h * 0.215, h * 0.40), (h * 0.70, h * 0.55)):
                    box(
                        "DOOR_BORDER",
                        (xx, -d / 2 + 0.012, zz),
                        (w / 2 - 0.014, 0.021, hh),
                        "utility_steel",
                    )
                    if zz > h * 0.5:
                        box(
                            "GLAZED_UPPER_LEAF",
                            (xx, -d / 2 - 0.001, zz),
                            (w / 2 - 0.08, 0.005, hh - 0.075),
                            "smoked_glass",
                            0.002,
                        )
                box(
                    "PULL",
                    (xx + (-1 if xx > 0 else 1) * w * 0.18, -d / 2 + 0.001, h * 0.51),
                    (0.013, 0.017, 0.12),
                    "chrome",
                    0.004,
                )
            for zz in (0.47, 0.77, 1.08, 1.4):
                if zz < h - 0.1:
                    box(
                        "INNER_SHELF",
                        (0, 0.015, zz),
                        (w - 0.085, d - 0.09, 0.025),
                        "utility_steel",
                        0.002,
                    )
            # Anonymous books provide depth, no actual paperwork or readable content.
            for i in range(7):
                box(
                    "NEUTRAL_BINDER",
                    (-w * 0.34 + i * w * 0.085, -0.02, h * 0.61),
                    (0.04, d * 0.45, h * 0.17),
                    "abstract" + str(i % 3),
                    0.002,
                )
        elif kind == "fridge":
            box(
                "BODY",
                (0, 0.012, h / 2),
                (w - 0.018, d - 0.024, h),
                "brushed_steel",
                0.025,
            )
            box(
                "BLACK_GASKET",
                (0, -d / 2 + 0.025, h / 2),
                (w - 0.025, 0.025, h - 0.035),
                "screen_frame",
                0.014,
            )
            for zz, hh in ((h * 0.32, h * 0.62), (h * 0.805, h * 0.325)):
                box(
                    "DOOR",
                    (0, -d / 2 + 0.010, zz),
                    (w - 0.028, 0.020, hh),
                    "brushed_steel",
                    0.018,
                )
            for zz in (h * 0.59, h * 0.67):
                box(
                    "RECESSED_HANDLE",
                    (w * 0.23, -d / 2 - 0.001, zz),
                    (w * 0.34, 0.008, 0.022),
                    "screen_frame",
                    0.008,
                )
            for xx in (-w * 0.34, w * 0.34):
                box(
                    "RUBBER_FOOT",
                    (xx, 0, 0.018),
                    (0.045, d * 0.65, 0.036),
                    "screen_frame",
                    0.008,
                )
        elif kind == "storage_shelf":
            for xx in (-w / 2 + 0.025, w / 2 - 0.025):
                for yy in (-d / 2 + 0.025, d / 2 - 0.025):
                    box(
                        "PERFORATED_UPRIGHT",
                        (xx, yy, h / 2),
                        (0.035, 0.035, h),
                        "utility_steel",
                        0.003,
                    )
            for zz in (0.035, h * 0.33, h * 0.66, h - 0.0175):
                box(
                    "SHELF_PAN",
                    (0, 0, zz),
                    (w - 0.025, d - 0.025, 0.035),
                    "brushed_steel",
                    0.003,
                )
                box(
                    "BLUE_FRONT_LIP",
                    (0, -d / 2 + 0.01, min(zz + 0.005, h - 0.0225)),
                    (w, 0.02, 0.045),
                    "shelf_blue",
                    0.003,
                )
                box(
                    "BLUE_BACK_LIP",
                    (0, d / 2 - 0.01, min(zz + 0.005, h - 0.0225)),
                    (w, 0.02, 0.045),
                    "shelf_blue",
                    0.003,
                )
            for xx in (-w * 0.3, w * 0.26):
                box(
                    "NEUTRAL_STORAGE_BIN",
                    (xx, 0, h * 0.43),
                    (w * 0.25, d * 0.65, h * 0.15),
                    "cabinet",
                    0.015,
                )
        elif kind == "shoe_rack":
            for xx in (-w / 2 + 0.018, w / 2 - 0.018):
                for yy in (-d / 2 + 0.02, d / 2 - 0.02):
                    pipe("CHROME_UPRIGHT", (xx, yy, 0.012), (xx, yy, h - 0.015), 0.011)
            for xx in (-w / 2 + 0.018, w / 2 - 0.018):
                for yy in (-d / 2 + 0.02, d / 2 - 0.02):
                    parts.append(
                        cylinder(
                            "P507_SHOE_RACK_FOOT",
                            (xx, yy, z0 + 0.011),
                            0.018,
                            0.022,
                            mats["screen_frame"],
                            col,
                            12,
                        )
                    )
            for zz in (0.08, h * 0.48, h - 0.04):
                for yy in (-d * 0.35, 0, d * 0.35):
                    pipe(
                        "SHELF_RAIL",
                        (-w / 2 + 0.016, yy, zz),
                        (w / 2 - 0.016, yy, zz),
                        0.009,
                    )
            # Generic shoe forms are original anonymous silhouettes, no brands/real pairs.
            for row, zz in enumerate((0.12, h * 0.48 + 0.04)):
                for i in range(4):
                    xx = -w * 0.34 + i * w * 0.22
                    box(
                        "NEUTRAL_SHOE",
                        (xx, 0, zz),
                        (0.12, d * 0.68, 0.07),
                        "shoe_dark" if (i + row) % 2 else "cabinet",
                        0.035,
                    )
                    box(
                        "SHOE_SOLE",
                        (xx, 0.005, zz - 0.035),
                        (0.125, d * 0.69, 0.016),
                        "chair",
                        0.008,
                    )
        elif kind == "waste_bin":
            box(
                "TAPERED_BODY",
                (0, 0, h * 0.43),
                (w * 0.90, d * 0.90, h * 0.86),
                "bin_plastic",
                0.035,
            )
            box("LID_RIM", (0, 0, h * 0.89), (w, d, h * 0.12), "frame_wood", 0.018)
            box(
                "LID",
                (0, 0, h * 0.97),
                (w * 0.91, d * 0.91, h * 0.06),
                "bin_plastic",
                0.025,
            )
        elif kind == "whiteboard":
            # Completely blank glossy board; no private writing is transcribed.
            box("BACKING", (0, 0, h / 2), (w, d * 0.75, h), "white_metal", 0.005)
            box(
                "BLANK_ENAMEL",
                (0, -d * 0.43, h / 2),
                (w - 0.045, 0.006, h - 0.045),
                "whiteboard",
                0.003,
            )
            for xx in (-w / 2 + 0.01, w / 2 - 0.01):
                box(
                    "SIDE_FRAME",
                    (xx, -d * 0.33, h / 2),
                    (0.02, 0.02, h),
                    "chrome",
                    0.003,
                )
            for zz in (0.012, h - 0.012):
                box(
                    "HORIZONTAL_FRAME",
                    (0, -d * 0.33, zz),
                    (w, 0.02, 0.024),
                    "chrome",
                    0.003,
                )
            box(
                "MARKER_TRAY",
                (0, -d * 0.30, 0.009),
                (w * 0.85, d * 0.35, 0.018),
                "chrome",
                0.003,
            )
        elif kind == "tv_small":
            box(
                "STAND_FOOT",
                (0, 0, 0.018),
                (w * 0.45, d * 0.85, 0.036),
                "screen_frame",
                0.012,
            )
            box(
                "STAND_STEM",
                (0, 0.015, 0.09),
                (0.045, 0.035, 0.15),
                "screen_frame",
                0.008,
            )
            box("BEZEL", (0, 0, h * 0.59), (w, 0.065, h * 0.82), "screen_frame", 0.016)
            box(
                "BLANK_SCREEN",
                (0, -0.037, h * 0.59),
                (w - 0.035, 0.008, h * 0.82 - 0.035),
                "screen",
                0.008,
            )
        elif kind == "wall_placeholder":
            if item.get("variant") == "neutral_ring_bars":
                bpy.ops.mesh.primitive_torus_add(
                    major_radius=0.25,
                    minor_radius=0.012,
                    major_segments=48,
                    minor_segments=10,
                    location=(0, 0, z0 + 0.565),
                )
                ring = bpy.context.object
                ring.name = "P507_NEUTRAL_RECOGNITION_RING_NOT_LOGO"
                ring.rotation_euler.x = math.pi / 2
                ring.data.materials.append(mats["frame_wood"])
                move_to_collection(ring, col)
                parts.append(ring)
                for zz, ww in ((0.07, w * 0.88), (0.15, w * 0.72), (0.23, w * 0.58)):
                    box(
                        "GENERIC_WORDMARK_BAR",
                        (0, -d * 0.2, zz),
                        (ww, 0.012, 0.025),
                        "utility_steel",
                        0.008,
                    )
            else:
                # Original neutral13-cell arrangement, not a copied photo count/content.
                rows = [
                    [-0.26, 0, 0.26],
                    [-0.39, -0.13, 0.13, 0.39],
                    [-0.26, 0, 0.26],
                    [-0.26, 0, 0.26],
                ]
                for row, xs in enumerate(rows):
                    for j, xx in enumerate(xs):
                        zz = 0.115 + row * 0.22
                        rim = cylinder(
                            "P507_NEUTRAL_HEX_BORDER",
                            (xx, -d * 0.12, z0 + zz),
                            0.108,
                            0.018,
                            mats["cabinet"],
                            col,
                            6,
                        )
                        rim.rotation_euler.x = math.pi / 2
                        parts.append(rim)
                        card = cylinder(
                            "P507_NEUTRAL_HEX_ORIGINAL_FIELD",
                            (xx, -d * 0.34, z0 + zz),
                            0.09,
                            0.004,
                            mats["abstract"][(row + j) % 3],
                            col,
                            6,
                        )
                        card.rotation_euler.x = math.pi / 2
                        parts.append(card)
        else:
            box("PROVISIONAL_BODY", (0, 0, h / 2), (w, d, h), "cabinet", 0.008)
        pose_asset(parts, item, col, (cx, cy, 0), angle)


def ceiling_items(data, col, mats):
    for item in data.get("ceiling", {}).get("instances", []):
        if item.get("status") == "UNPLACED":
            continue
        kind = item["type"]
        x, y, z = item["center"]
        sx, sy, sz = item["size"]
        parts = []

        def box(name, center, size, mat, bevel=0.005, item=item, parts=parts):
            obj = cube(
                "P507_CEILING_" + item["id"].replace("-", "_") + "_" + name,
                center,
                size,
                mats[mat],
                col,
                bevel,
            )
            parts.append(obj)
            return obj

        def cyl(name, center, r, depth, mat, vertices=24, parts=parts):
            obj = cylinder(
                "P507_CEILING_" + name, center, r, depth, mats[mat], col, vertices
            )
            parts.append(obj)
            return obj

        def pipe(name, a, b, r=0.012, mat="white_metal", parts=parts):
            obj = tube("P507_CEILING_" + name, a, b, r, mats[mat], col)
            parts.append(obj)
            return obj

        if kind == "light_panel":
            box(
                "HOUSING", (x, y, z + 0.008), (sx, sy, sz - 0.016), "white_metal", 0.007
            )
            # The luminous face is genuinely in front of the dark rebate from below.
            # Separate Z planes prevent coincident dark/diffuser undersides.
            bottom = z - sz / 2
            box(
                "DARK_RECESS",
                (x, y, bottom + 0.017),
                (sx - 0.035, sy - 0.035, 0.016),
                "utility_steel",
                0.003,
            )
            box(
                "OPAL_DIFFUSER",
                (x, y, bottom + 0.005),
                (sx - 0.06, sy - 0.06, 0.008),
                "led",
                0.003,
            )
        elif kind == "ceiling_fan":
            blade_z = item.get("blade_z", z)
            bottom = item.get("bottom_z", 3.03)
            top = item.get("top_z", 3.5)
            cyl("FAN_CANOPY", (x, y, top - 0.025), 0.075, 0.05, "white_metal")
            cyl(
                "FAN_DOWNROD",
                (x, y, (blade_z + 0.06 + top - 0.045) / 2),
                0.019,
                top - 0.045 - (blade_z + 0.06),
                "chrome",
            )
            cyl("FAN_MOTOR", (x, y, blade_z + 0.025), 0.10, 0.10, "white_metal", 32)
            cyl("FAN_LOWER_HUB", (x, y, bottom + 0.04), 0.065, 0.08, "white_metal", 24)
            for i in range(3):
                theta = i * 2 * math.pi / 3
                blade = box(
                    "FAN_SHAPED_BLADE",
                    (x + 0.29 * math.cos(theta), y + 0.29 * math.sin(theta), blade_z),
                    (0.40, 0.095, 0.024),
                    "white_metal",
                    0.045,
                )
                blade.rotation_euler.z = theta + 0.06
        elif kind == "cassette_ac":
            bottom = item.get("bottom_z", z - sz / 2)
            top = item.get("top_z", z + sz / 2)
            # Recess the main carcass: a solid coplanar underside would hide the vents.
            body_bottom = bottom + 0.03
            box(
                "AC_HOUSING",
                (x, y, (body_bottom + top) / 2),
                (sx, sy, top - body_bottom),
                "white_metal",
                0.015,
            )
            trim = 0.035
            for sign in (-1, 1):
                box(
                    "AC_OUTER_TRIM_X",
                    (x + sign * (sx / 2 - trim / 2), y, bottom + 0.018),
                    (trim, sy, 0.036),
                    "white_metal",
                    0.006,
                )
                box(
                    "AC_OUTER_TRIM_Y",
                    (x, y + sign * (sy / 2 - trim / 2), bottom + 0.018),
                    (sx - 2 * trim, trim, 0.036),
                    "white_metal",
                    0.006,
                )
            box(
                "AC_INTAKE_RECESS",
                (x, y, bottom + 0.017),
                (sx * 0.58, sy * 0.58, 0.016),
                "screen_frame",
                0.008,
            )
            for i in range(-5, 6):
                box(
                    "AC_FILTER_SLAT_X",
                    (x + i * 0.029, y, bottom + 0.006),
                    (0.012, sy * 0.55, 0.012),
                    "utility_steel",
                    0.002,
                )
                box(
                    "AC_FILTER_SLAT_Y",
                    (x, y + i * 0.029, bottom + 0.006),
                    (sx * 0.55, 0.012, 0.012),
                    "utility_steel",
                    0.002,
                )
            for axis in (0, 1):
                for sign in (-1, 1):
                    xx = x + (sign * sx * 0.40 if axis == 0 else 0)
                    yy = y + (sign * sy * 0.40 if axis == 1 else 0)
                    box(
                        "AC_OUTLET_SHADOW",
                        (xx, yy, bottom + 0.017),
                        (0.067, sy * 0.75, 0.016)
                        if axis == 0
                        else (sx * 0.75, 0.067, 0.016),
                        "screen_frame",
                        0.008,
                    )
                    for k in (-1, 1):
                        xx2 = xx + (k * 0.014 if axis == 0 else 0)
                        yy2 = yy + (k * 0.014 if axis == 1 else 0)
                        box(
                            "AC_OUTLET_LOUVRE",
                            (xx2, yy2, bottom + 0.006),
                            (0.01, sy * 0.72, 0.012)
                            if axis == 0
                            else (sx * 0.72, 0.01, 0.012),
                            "white_metal",
                            0.003,
                        )
        elif kind == "projector":
            bottom = item.get("bottom_z", z - sz / 2)
            top = item.get("top_z", 3.5)
            body_h = 0.15
            body_z = bottom + body_h / 2
            box(
                "PROJECTOR_BODY",
                (x, y, body_z),
                (sx, sy - 0.02, body_h),
                "white_metal",
                0.022,
            )
            box(
                "PROJECTOR_MOUNT_PLATE",
                (x, y, 3.475),
                (0.16, 0.12, 0.05),
                "utility_steel",
                0.006,
            )
            cyl(
                "PROJECTOR_MOUNT_ROD",
                (x, y, (3.45 + body_z + 0.075) / 2),
                0.018,
                3.45 - (body_z + 0.075),
                "chrome",
                16,
            )
            lens = cyl(
                "PROJECTOR_LENS",
                (x + 0.08, y - sy / 2 + 0.017, body_z),
                0.039,
                0.033,
                "screen",
                32,
            )
            lens.rotation_euler.x = math.pi / 2
            for i in range(6):
                box(
                    "PROJECTOR_VENT",
                    (x - sx / 2 + 0.004, y - 0.075 + i * 0.028, body_z),
                    (0.008, 0.014, 0.064),
                    "screen_frame",
                    0.002,
                )
        elif kind == "camera":
            # Dome-like neutral camera near high window corner; no image/video feed.
            box(
                "CAMERA_BACKPLATE",
                (x + 0.075, y, z + 0.05),
                (0.04, 0.12, 0.14),
                "white_metal",
                0.012,
            )
            pipe("CAMERA_BRACKET", (x + 0.075, y, z + 0.06), (x, y, z + 0.03), 0.012)
            cyl("CAMERA_CANOPY", (x, y, 3.48), 0.045, 0.04, "white_metal", 20)
            cyl(
                "CAMERA_HANGING_STEM",
                (x, y, (3.46 + z + 0.055) / 2),
                0.012,
                3.46 - (z + 0.055),
                "chrome",
                16,
            )
            cyl("CAMERA_BODY", (x, y, z), 0.065, 0.095, "white_metal", 24)
            lens = cyl(
                "CAMERA_DARK_LENS",
                (x, y - 0.055, z - 0.015),
                0.033,
                0.025,
                "screen",
                24,
            )
            lens.rotation_euler.x = math.pi / 2
        if parts:
            if kind == "camera":
                from mathutils import Matrix

                bpy.context.view_layer.update()
                for obj in parts:
                    obj.matrix_world = (
                        Matrix.Translation((-x, -y, 0)) @ obj.matrix_world
                    )
                pose_asset(
                    parts,
                    item,
                    col,
                    (x, y, 0),
                    prefix="P507_CEILING_" + item["id"].replace("-", "_") + "_ASSEMBLY",
                )
            else:
                pose_asset(
                    parts,
                    item,
                    col,
                    angle=0,
                    prefix="P507_CEILING_" + item["id"].replace("-", "_") + "_ASSEMBLY",
                )


def lathe(name, center, profile, mat, col, segments=48, ident=None):
    """Closed turned surface, profile ordered bottom to top (radius, height)."""
    vertices = []
    for radius, z in profile:
        for i in range(segments):
            t = 2 * math.pi * i / segments
            vertices.append(
                (center[0] + radius * math.cos(t), center[1] + radius * math.sin(t), z)
            )
    faces = []
    for j in range(len(profile) - 1):
        for i in range(segments):
            ni = (i + 1) % segments
            faces.append(
                (
                    j * segments + i,
                    j * segments + ni,
                    (j + 1) * segments + ni,
                    (j + 1) * segments + i,
                )
            )
    faces.extend(
        [
            tuple(reversed(range(segments))),
            tuple((len(profile) - 1) * segments + i for i in range(segments)),
        ]
    )
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.materials.append(mat)
    for f in mesh.polygons:
        f.use_smooth = len(f.vertices) == 4
    if ident:
        obj["survey_instance_id"] = ident
        obj["source_class"] = "PROPOSED_LAYOUT"
    return obj


def hero_assets(data, col, mats):
    tv = data["hero"]["tv"]
    w = tv["width"]
    h = tv["height"]
    parts = []

    def tvbox(name, xyz, size, mat, bevel=0.008):
        obj = cube("P507_HERO_TV_" + name, xyz, size, mats[mat], col, bevel)
        parts.append(obj)
        return obj

    tvbox(
        "REAR_CASING",
        (0, 0.009, 0),
        (w - 0.055, 0.075, h - 0.055),
        "screen_frame",
        0.025,
    )
    tvbox("BEZEL", (0, -0.035, 0), (w, 0.027, h), "screen_frame", 0.016)
    screen = tvbox(
        "BLACK_SCREEN",
        (0, -0.051, 0.006),
        (w - 0.034, 0.008, h - 0.044),
        "screen",
        0.009,
    )
    screen["semantic_part"] = "display_front"
    tvbox(
        "REAR_MOUNT_RAIL", (0.3, 0.065, 0), (1.1, 0.023, 0.10), "utility_steel", 0.005
    )
    tvbox(
        "STANDBY_INDICATOR",
        (w * 0.38, -0.057, -h / 2 + 0.017),
        (0.008, 0.004, 0.003),
        "indicator",
        0.001,
    )
    pose_asset(
        parts,
        tv,
        col,
        tuple(tv.get("center", [tv["center_x"], 7.59, tv["center_z"]])),
        merge=False,
    )
    # A real attachment to north-wall anchor, declared separately in inventory/proxies.
    mount = next((o for o in data["objects"] if o.get("type") == "tv_mount"), None)
    if mount:
        x0, y0, x1, y1 = mount["rect"]
        mx = (x0 + x1) / 2
        mz = mount["bottom_z"] + mount["height"] / 2
        parts = [
            cube(
                "P507_HERO_TV_WALL_ANCHOR",
                (mx, 8.02, mz),
                (x1 - x0, 0.055, mount["height"]),
                mats["utility_steel"],
                col,
                0.004,
            )
        ]
        for dz in (-0.09, 0.09):
            parts.append(
                tube(
                    "P507_HERO_TV_ARTICULATED_BRACKET",
                    (mx, 7.956, mz + dz),
                    (mx, 8.02, mz + dz),
                    0.011,
                    mats["utility_steel"],
                    col,
                )
            )
        pose_asset(parts, mount, col, angle=0)

    cabinet = data["hero"]["cabinet"]
    cx, cy, _ = cabinet["center"]
    sx, sy, sz = cabinet["size"]
    parts = []

    def cabbox(name, xyz, size, mat, bevel=0.006):
        obj = cube("P507_HERO_CABINET_" + name, xyz, size, mats[mat], col, bevel)
        parts.append(obj)
        return obj

    cabbox(
        "RECESSED_PLINTH",
        (cx, cy, 0.04),
        (sx - 0.1, sy - 0.07, 0.08),
        "frame_wood",
        0.008,
    )
    cabbox(
        "LIGHT_OAK_CARCASS",
        (cx, cy, (0.08 + sz - 0.036) / 2),
        (sx, sy, sz - 0.116),
        "wood",
        0.01,
    )
    cabbox(
        "COUNTER_TOP",
        (cx, cy, sz - 0.018),
        (sx + 0.02, sy + 0.02, 0.036),
        "wood",
        0.008,
    )
    drawer_bottom = sz - 0.22
    for i in range(3):
        xx = cx - sx / 2 + (i + 0.5) * sx / 3
        cabbox(
            "LOWER_LEAF",
            (xx, cy - sy / 2 - 0.01, (0.10 + drawer_bottom - 0.015) / 2),
            (sx / 3 - 0.014, 0.02, drawer_bottom - 0.115),
            "cabinet",
            0.005,
        )
        cabbox(
            "LOWER_PULL",
            (xx, cy - sy / 2 - 0.037, drawer_bottom - 0.095),
            (0.078, 0.012, 0.013),
            "chrome",
            0.004,
        )
    for i in range(2):
        xx = cx - sx / 2 + (i + 0.5) * sx / 2
        cabbox(
            "DRAWER_FRONT",
            (xx, cy - sy / 2 - 0.011, sz - 0.12),
            (sx / 2 - 0.014, 0.022, 0.17),
            "cabinet",
            0.005,
        )
        cabbox(
            "DRAWER_PULL",
            (xx, cy - sy / 2 - 0.037, sz - 0.12),
            (0.13, 0.012, 0.013),
            "chrome",
            0.004,
        )
    pose_asset(parts, cabinet, col, angle=0)

    # Original anonymous trophy/plaque silhouettes; all are declared supported records.
    for i, item in enumerate(
        o for o in data["objects"] if o.get("type") == "decor_display"
    ):
        x0, y0, x1, y1 = item["rect"]
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        z = item.get("bottom_z", sz)
        item["height"]
        parts = []
        parts.append(
            cube(
                "P507_HERO_DISPLAY_PLINTH",
                (x, y, z + 0.015),
                (0.18, 0.12, 0.03),
                mats["screen_frame"],
                col,
                0.006,
            )
        )
        if i % 3 == 0:
            plaque = cube(
                "P507_HERO_DISPLAY_PLAQUE",
                (x, y, z + 0.15),
                (0.15, 0.032, 0.24),
                mats["gold"],
                col,
                0.012,
            )
            parts.append(plaque)
        elif i % 3 == 1:
            profile = [
                (0.045, z + 0.03),
                (0.045, z + 0.055),
                (0.018, z + 0.065),
                (0.016, z + 0.14),
                (0.045, z + 0.15),
                (0.06, z + 0.22),
                (0.055, z + 0.26),
            ]
            parts.append(
                lathe(
                    "P507_HERO_DISPLAY_TROPHY", (x, y), profile, mats["gold"], col, 24
                )
            )
            parts.append(
                cylinder(
                    "P507_HERO_DISPLAY_TROPHY_TOP",
                    (x, y, z + 0.268),
                    0.055,
                    0.016,
                    mats["gold"],
                    col,
                    24,
                )
            )
        else:
            parts.append(
                cube(
                    "P507_HERO_DISPLAY_CLEAR_AWARD",
                    (x, y, z + 0.15),
                    (0.11, 0.025, 0.24),
                    mats["smoked_glass"],
                    col,
                    0.014,
                )
            )
            parts.append(
                cube(
                    "P507_HERO_DISPLAY_GOLD_INSET",
                    (x, y - 0.016, z + 0.15),
                    (0.08, 0.005, 0.16),
                    mats["gold"],
                    col,
                    0.008,
                )
            )
        pose_asset(parts, item, col, angle=0)

    water = data["hero"]["water_dispenser"]
    px, py, _ = water["center"]
    parts = []

    def waterbox(name, xyz, size, mat, bevel=0.009):
        obj = cube("P507_HERO_WATER_" + name, xyz, size, mats[mat], col, bevel)
        parts.append(obj)
        return obj

    waterbox("FOOT", (0, 0, 0.025), (0.37, 0.38, 0.05), "screen_frame", 0.014)
    waterbox("GRAY_ENCLOSURE", (0, 0, 0.48), (0.39, 0.40, 0.91), "water_body", 0.032)
    waterbox(
        "RED_LOWER_PANEL", (0, -0.207, 0.28), (0.335, 0.018, 0.43), "water_red", 0.012
    )
    waterbox(
        "LOWER_PANEL_GASKET",
        (0, -0.219, 0.503),
        (0.31, 0.006, 0.016),
        "screen_frame",
        0.003,
    )
    waterbox(
        "TAKE_WATER_RECESS",
        (0, -0.211, 0.675),
        (0.28, 0.012, 0.265),
        "screen_frame",
        0.018,
    )
    for dx in (-0.162, 0.162):
        waterbox(
            "RECESS_CHEEK", (dx, -0.215, 0.68), (0.031, 0.04, 0.29), "water_body", 0.01
        )
    control = waterbox(
        "CONTROL", (0, -0.22, 0.875), (0.29, 0.025, 0.075), "screen_frame", 0.01
    )
    control["semantic_part"] = "control_front"
    for dx, mat in ((-0.07, "hot"), (0.07, "blue_water")):
        waterbox("TAP", (dx, -0.231, 0.754), (0.034, 0.036, 0.035), mat, 0.007)
        waterbox("BUTTON", (dx, -0.237, 0.875), (0.033, 0.006, 0.017), mat, 0.005)
    waterbox("DRIP_TRAY", (0, -0.223, 0.53), (0.29, 0.03, 0.026), "chrome", 0.006)
    for i in range(6):
        waterbox(
            "TRAY_DRAIN_SLOT",
            (-0.10 + i * 0.04, -0.240, 0.535),
            (0.012, 0.005, 0.004),
            "screen_frame",
            0.001,
        )
    parts.append(
        cylinder(
            "P507_HERO_WATER_COLLAR",
            (0, 0, 0.955),
            0.10,
            0.07,
            mats["screen_frame"],
            col,
            32,
        )
    )
    bottle_profile = [
        (0.055, 0.97),
        (0.055, 1.025),
        (0.08, 1.06),
        (0.145, 1.10),
        (0.173, 1.16),
        (0.173, 1.40),
        (0.16, 1.46),
        (0.12, 1.49),
        (0.025, 1.50),
    ]
    parts.append(
        lathe("P507_HERO_WATER_BOTTLE", (0, 0), bottle_profile, mats["bottle"], col, 48)
    )
    for zz in (1.18, 1.23, 1.36, 1.40):
        parts.append(
            lathe(
                "P507_HERO_WATER_BOTTLE_RIB",
                (0, 0),
                [(0.173, zz - 0.007), (0.179, zz), (0.173, zz + 0.007)],
                mats["bottle"],
                col,
                48,
            )
        )
    pose_asset(parts, water, col, (px, py, 0), merge=False)
    cube(
        "P507_HERO_NORTH_SKIRTING",
        (3, 8.025, 0.055),
        (6, 0.026, 0.11),
        mats["white_metal"],
        col,
        0.005,
    )


def photo_wall_assets(data, col, mats):
    templates = {}
    for i, item in enumerate(data.get("photo_wall", {}).get("frames", [])):
        x, y, z = item["center"]
        w, d, h = item["size"]
        parts = []
        key = (w, d, h, i % 3)
        if key in templates:
            template = templates[key]
            obj = bpy.data.objects.new(
                item["id"].replace("-", "_") + "_ASSEMBLY", template.data
            )
            col.objects.link(obj)
            obj.location = (x, y, z)
            pose_asset([obj], item, col, angle=0)
            obj["frame_group"] = item.get("group", "UNKNOWN")
            continue
        # White mat board, fine warm edge and a separate inset original colour composition.
        parts.append(
            cube(
                "P507_PHOTO_WALL_BACKING",
                (x, y + d / 2 - 0.003, z),
                (w - 0.022, 0.006, h - 0.022),
                mats["frame_wood"],
                col,
                0.002,
            )
        )
        for xx in (-w / 2 + 0.007, w / 2 - 0.007):
            parts.append(
                cube(
                    "P507_PHOTO_WALL_SIDE_BORDER",
                    (x + xx, y, z),
                    (0.014, d, h),
                    mats["cabinet"],
                    col,
                    0.003,
                )
            )
        for zz in (-h / 2 + 0.007, h / 2 - 0.007):
            parts.append(
                cube(
                    "P507_PHOTO_WALL_HORIZONTAL_BORDER",
                    (x, y, z + zz),
                    (w - 0.028, d, 0.014),
                    mats["cabinet"],
                    col,
                    0.003,
                )
            )
        parts.append(
            cube(
                "P507_PHOTO_WALL_WHITE_MAT",
                (x, y, z),
                (w - 0.028, 0.002, h - 0.028),
                mats["paper"],
                col,
                0.001,
            )
        )
        parts.append(
            cube(
                "P507_PHOTO_WALL_ABSTRACT_CARD",
                (x, y - 0.003, z),
                (w - 0.055, 0.001, h - 0.05),
                mats["abstract"][i % 3],
                col,
                0.001,
            )
        )
        # Small self-authored geometric inserts add framed-image depth without using source art.
        parts.append(
            cube(
                "P507_PHOTO_WALL_ORIGINAL_FIELD",
                (x - w * 0.09, y - 0.005, z - h * 0.08),
                (w * 0.35, 0.001, h * 0.25),
                mats["abstract"][(i + 1) % 3],
                col,
                0.001,
            )
        )
        obj = pose_asset(parts, item, col, angle=0)
        bpy.context.scene.cursor.location = (x, y, z)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        obj["frame_group"] = item.get("group", "UNKNOWN")
        templates[key] = obj


def camera_and_lights(data, camera_col):
    length = data["room"]["length_y"]
    bpy.ops.object.camera_add(location=(1.1, 5.15, 1.65))
    cam = bpy.context.object
    cam.name = "CAM_TV_ART_APPROX"
    move_to_collection(cam, camera_col)
    target = (0.98, length - 0.25, 1.55)
    from mathutils import Vector

    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 24
    bpy.context.scene.camera = cam
    # Blender lookdev lights are not exported as runtime GLB lights.
    for name, center, power, color in [
        ("LOOKDEV_WINDOW_DAYLIGHT", (5.9, 4.2, 2.4), 550, (0.78, 0.88, 1)),
        ("LOOKDEV_LED_FILL", (2.5, 5.1, 3.2), 350, (1, 0.96, 0.86)),
    ]:
        lamp = bpy.data.lights.new(name, "AREA")
        lamp.energy = power
        lamp.color = color
        lamp.shape = "RECTANGLE"
        lamp.size = 2.5
        lamp.size_y = 2.0
        obj = bpy.data.objects.new(name, lamp)
        camera_col.objects.link(obj)
        obj.location = center
        obj.rotation_euler = (
            (Vector((2.5, 5.5, 0.3)) - obj.location).to_track_quat("-Z", "Y").to_euler()
        )


def validate_authored_bounds(data, collections):
    """Independently test evaluated mesh vertices against every 3D oriented proxy."""

    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    measured = {}
    points = {}
    poses = {}
    for col in collections:
        for obj in col.objects:
            ident = obj.get("survey_instance_id")
            if obj.type != "MESH" or not ident:
                continue
            evaluated = obj.evaluated_get(deps)
            mesh = evaluated.to_mesh()
            try:
                for vert in mesh.vertices:
                    v = evaluated.matrix_world @ vert.co
                    points.setdefault(ident, []).append(
                        (float(v.x), float(v.y), float(v.z))
                    )
                    if ident not in measured:
                        measured[ident] = [v.x, v.y, v.z, v.x, v.y, v.z]
                    else:
                        q = measured[ident]
                        measured[ident] = [
                            min(q[0], v.x),
                            min(q[1], v.y),
                            min(q[2], v.z),
                            max(q[3], v.x),
                            max(q[4], v.y),
                            max(q[5], v.z),
                        ]
            finally:
                evaluated.to_mesh_clear()
            if "surface_front_survey" in obj:
                poses[ident] = {
                    "orientation_deg": obj.get("orientation_deg", 0),
                    "surface_front_survey": list(obj["surface_front_survey"]),
                }
    expected = {p["id"]: p for p in verify(data)["occupancy"]}
    checks = {}
    errors = []
    for ident in measured:
        if ident not in expected:
            errors.append("Rendered logical ID has no occupancy proxy: " + ident)
    for ident, proxy in expected.items():
        if ident not in measured:
            errors.append("Missing authored geometry: " + ident)
            continue
        polygon = proxy["polygon"]
        bottom = proxy.get("bottom_z", 0)
        top = proxy.get("top_z", bottom + proxy.get("height", 3.5))
        for vx, vy, vz in points[ident]:
            distances = []
            for a, b in zip(polygon, polygon[1:] + polygon[:1]):
                edge = math.hypot(b[0] - a[0], b[1] - a[1])
                distances.append(
                    ((b[0] - a[0]) * (vy - a[1]) - (b[1] - a[1]) * (vx - a[0])) / edge
                )
            if not (
                all(d >= -0.001 for d in distances)
                or all(d <= 0.001 for d in distances)
            ):
                errors.append(
                    "Authored vertex exceeds oriented footprint: "
                    + ident
                    + str((vx, vy, vz))
                )
                break
            if vz < bottom - 0.001 or vz > top + 0.001:
                errors.append(
                    "Authored vertex exceeds vertical proxy: "
                    + ident
                    + str((vz, bottom, top))
                )
                break
        checks[ident] = {
            "result": "PASS",
            "evaluated_vertex_count": len(points[ident]),
            "method": "convex signed distances + Z interval, tolerance1mm",
            "proxy_bottom_z": bottom,
            "proxy_top_z": top,
        }
    if errors:
        raise RuntimeError("Authored mesh validation failed: " + json.dumps(errors))
    return measured, checks, poses


def validate_ceiling_surface_visibility(data, mats):
    """Ray-test the real undersides that were previously occluded by their casings.

    This is a technical layer/exposure regression, never an aesthetic approval.
    """
    from mathutils import Vector

    deps = bpy.context.evaluated_depsgraph_get()
    checks = []
    for item in data.get("ceiling", {}).get("instances", []):
        kind = item["type"]
        if kind not in ("light_panel", "cassette_ac"):
            continue
        x, y, z = item["center"]
        if kind == "cassette_ac":
            x += 0.0145
            y += 0.0145
        bottom = item.get("bottom_z", z - item["size"][2] / 2)
        hit, location, _normal, face, obj, _ = bpy.context.scene.ray_cast(
            deps, Vector((x, y, bottom - 0.20)), Vector((0, 0, 1)), distance=0.5
        )
        expected = mats["led"] if kind == "light_panel" else mats["screen_frame"]
        actual = None
        if hit and face >= 0:
            evaluated = obj.evaluated_get(deps)
            actual = evaluated.data.materials[
                evaluated.data.polygons[face].material_index
            ]
        if (
            actual is None
            or actual.name != expected.name
            or obj.original.get("survey_instance_id") != item["id"]
        ):
            raise RuntimeError(
                "Ceiling visible underside is blocked or wrong material: "
                + item["id"]
                + " / "
                + str(actual.name if actual else None)
                + " / hit="
                + str(obj.name if obj else None)
                + " / id="
                + str(obj.original.get("survey_instance_id") if obj else None)
            )
        checks.append(
            {
                "id": item["id"],
                "sample_survey_xy": [x, y],
                "first_hit_z": location.z,
                "material": actual.name,
                "ok": True,
            }
        )
    return checks


def main():
    args = parse_args()
    data = read_inventory(args.inventory)
    result = verify(data)
    if not result["ok"]:
        raise SystemExit("Invalid geometry: " + json.dumps(result["errors"]))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for existing in list(bpy.data.collections):
        if existing.name == "Collection" and not existing.objects:
            bpy.data.collections.remove(existing)
    scene = bpy.context.scene
    scene.render.film_transparent = False
    bpy.context.preferences.filepaths.save_version = 0
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    mats = {
        "paint": material("P507_PBR_CREAM_PAINT", (0.74, 0.71, 0.64), 0.92),
        "tile": material("P507_PBR_WARM_TILE", (0.80, 0.80, 0.75), 0.31),
        "ceiling": material("P507_PBR_CEILING", (0.85, 0.85, 0.82), 0.93),
        "metal": material("P507_PBR_DARK_METAL", (0.18, 0.20, 0.22), 0.43, 0.86),
        "white_metal": material(
            "P507_PBR_OFFWHITE_ENAMEL", (0.81, 0.83, 0.82), 0.43, 0.35
        ),
        "laminate": material("P507_PBR_LAMINATE_WHITE", (0.9, 0.91, 0.86), 0.41),
        "chair": material("P507_PBR_CHARCOAL_SEAT", (0.08, 0.09, 0.10), 0.82),
        "glass": material(
            "P507_PBR_WINDOW_PLACEHOLDER", (0.54, 0.65, 0.70), 0.12, 0.25
        ),
        "led": material("P507_PBR_LED_PANEL", (0.95, 0.96, 0.95), 0.75, emission=1.35),
        "screen_frame": material(
            "P507_PBR_TV_BEZEL", (0.055, 0.061, 0.066), 0.40, 0.30
        ),
        "screen": material("P507_PBR_TV_OFF_SCREEN", (0.012, 0.014, 0.019), 0.19, 0.05),
        "cabinet": material("P507_PBR_CABINET_WARMWHITE", (0.82, 0.79, 0.72), 0.6),
        "gold": material(
            "P507_PBR_NEUTRAL_GOLD_PLACEHOLDER", (0.43, 0.31, 0.12), 0.39, 0.70
        ),
        "blue_water": material(
            "P507_PBR_WATER_BOTTLE_PLACEHOLDER", (0.22, 0.53, 0.78), 0.25, 0.15
        ),
        "blind": material("P507_PBR_ROLLER_BLIND", (0.70, 0.68, 0.64), 0.94),
        "frame_wood": material("P507_PBR_NEUTRAL_WOOD_FRAME", (0.34, 0.28, 0.22), 0.58),
        "abstract": [
            material("P507_PBR_FAKE_COLOR_FIELD_01", (0.34, 0.48, 0.50), 0.9),
            material("P507_PBR_FAKE_COLOR_FIELD_02", (0.43, 0.36, 0.36), 0.9),
            material("P507_PBR_FAKE_COLOR_FIELD_03", (0.40, 0.48, 0.35), 0.9),
        ],
    }
    mats.update(
        {
            "chrome": material("P507_PBR_SATIN_CHROME", (0.48, 0.52, 0.55), 0.31, 0.82),
            "table_steel": material(
                "P507_PBR_GRAY_PAINTED_TABLE_STEEL", (0.45, 0.48, 0.50), 0.48, 0.34
            ),
            "utility_steel": material(
                "P507_PBR_UTILITY_GRAY_STEEL", (0.40, 0.43, 0.44), 0.52, 0.32
            ),
            "brushed_steel": material(
                "P507_PBR_BRUSHED_FRIDGE_STEEL", (0.46, 0.46, 0.43), 0.40, 0.45
            ),
            "shelf_blue": material(
                "P507_PBR_SHELF_BLUE_ENAMEL", (0.025, 0.18, 0.38), 0.43, 0.22
            ),
            "whiteboard": material(
                "P507_PBR_BLANK_WHITEBOARD", (0.81, 0.82, 0.79), 0.27
            ),
            "paper": material("P507_PBR_NEUTRAL_MAT_PAPER", (0.84, 0.82, 0.76), 0.88),
            "shoe_dark": material("P507_PBR_ANONYMOUS_SHOE", (0.15, 0.11, 0.08), 0.80),
            "bin_plastic": material("P507_PBR_BIN_WARMGRAY", (0.43, 0.40, 0.35), 0.67),
            "water_body": material(
                "P507_PBR_WATER_GRAY_PLASTIC", (0.43, 0.46, 0.47), 0.39, 0.12
            ),
            "water_red": material(
                "P507_PBR_WATER_LOWER_BURGUNDY", (0.24, 0.035, 0.024), 0.48
            ),
            "smoked_glass": material(
                "P507_PBR_CABINET_SMOKED_GLASS", (0.28, 0.35, 0.36), 0.24, 0.04
            ),
            "frosted_glass": material(
                "P507_PBR_DOOR_FROSTED_GLASS", (0.48, 0.54, 0.55), 0.58
            ),
        }
    )
    for i, mat in enumerate(mats["abstract"]):
        mats["abstract" + str(i)] = mat
    mats["chair"].node_tree.nodes.get("Principled BSDF").inputs[
        "Base Color"
    ].default_value = (0.026, 0.042, 0.065, 1)
    screen = mats["screen"].node_tree.nodes.get("Principled BSDF")
    screen.inputs["Roughness"].default_value = 0.32
    screen.inputs[
        "Specular IOR Level" if "Specular IOR Level" in screen.inputs else "Specular"
    ].default_value = 0.06
    glass = mats["glass"].node_tree.nodes.get("Principled BSDF")
    glass.inputs["Alpha"].default_value = 0.16
    if hasattr(mats["glass"], "surface_render_method"):
        mats["glass"].surface_render_method = "DITHERED"
    else:
        mats["glass"].blend_method = "BLEND"
    arch = collection("10_ARCH")
    furniture = collection("20_FURNITURE")
    equipment = collection("30_EQUIPMENT")
    ceiling = collection("40_CEILING")
    lookdev = collection("80_LOOKDEV_CAMERAS")
    mats["tile"] = procedural_floor_tiles()
    mats["wood"] = procedural_wood()
    mats["indicator"] = material(
        "P507_TV_STANDBY", (0.09, 0.16, 0.12), 0.3, emission=0.3
    )
    mats["hot"] = material("P507_WATER_RED_BUTTON", (0.32, 0.025, 0.02), 0.4)
    mats["bottle"] = material("P507_PBR_TRANSLUCENT_BLUE_PET", (0.20, 0.48, 0.67), 0.17)
    bottle = mats["bottle"].node_tree.nodes.get("Principled BSDF")
    bottle.inputs[
        "Transmission Weight"
        if "Transmission Weight" in bottle.inputs
        else "Transmission"
    ].default_value = 0.58
    bottle.inputs["IOR"].default_value = 1.46
    room_shell(data, arch, mats)
    floor = bpy.data.objects.get("P507_ARCH_FLOOR")
    floor["chair_inventory_count"] = data["chairs"]["count"]
    floor["chair_placed_count"] = sum(
        c["status"] == "PLACED_PROVISIONAL" for c in data["chairs"]["instances"]
    )
    floor["unplaced_chair_ids"] = json.dumps(
        [c["id"] for c in data["chairs"]["instances"] if c["status"] == "UNPLACED"]
    )
    tables_and_chairs(data, furniture, furniture, mats)
    utility_assets(data, furniture, mats)
    ceiling_items(data, ceiling, mats)
    hero_assets(data, equipment, mats)
    photo_wall_assets(data, equipment, mats)
    collection("50_DECOR")
    collection("60_INTERACTION_PROXY")
    collection("90_REFERENCE_LOCAL")
    grids = [o for o in arch.objects if o.name.startswith("P507_ARCH_CEILING_GRID")]
    if grids:
        combine(grids, "P507_ARCH_CEILING_GRID", arch)
    tiles = [o for o in arch.objects if o.name.startswith("P507_ARCH_CEILING_TILE_")]
    if tiles:
        combine(tiles, "P507_ARCH_CEILING_TILES", arch)
    camera_and_lights(data, lookdev)
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.world.color = (0.18, 0.18, 0.18)
    authored_bounds, authored_proxy_checks, authored_poses = validate_authored_bounds(
        data, (arch, furniture, equipment, ceiling)
    )
    ceiling_surface_checks = validate_ceiling_surface_visibility(data, mats)
    door = data["openings"]["door"]
    for obj in arch.objects:
        if obj.name.startswith("P507_ARCH_WALL_WEST"):
            ys = [
                (obj.matrix_world @ __import__("mathutils").Vector(v)).y
                for v in obj.bound_box
            ]
            if min(max(ys), door["to_y"]) - max(min(ys), door["from_y"]) > 0.001:
                raise RuntimeError("West wall blocks intended door opening")
    import hashlib
    import os
    import subprocess

    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=HERE, text=True
    ).strip()
    source_work_tree_dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=HERE, text=True
        ).strip()
    )
    input_hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (Path(__file__), HERE / "geometry.py", args.inventory)
    }
    blend_path = args.output_dir / "P507_G1_G2_PROVISIONAL.blend"
    glb_path = args.output_dir / "P507_G1_G2_PROVISIONAL.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.object.select_all(action="DESELECT")
    export_count = 0
    for c in (arch, furniture, equipment, ceiling):
        for o in c.objects:
            if o.type == "MESH":
                o.select_set(True)
                export_count += 1
    export_result = bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_extras=True,
    )
    if (
        "FINISHED" not in export_result
        or not glb_path.is_file()
        or glb_path.stat().st_size < 1024
    ):
        raise RuntimeError(
            "glTF export failed, cancelled or produced no GLB. Do not claim PASS."
        )
    out = {
        **result,
        "blender_version": bpy.app.version_string,
        "export_objects": export_count,
        "ceiling_surface_checks": ceiling_surface_checks,
        "authored_bounds": authored_bounds,
        "authored_proxy_checks": authored_proxy_checks,
        "authored_poses": authored_poses,
        "checkout_sha": source_sha,
        "source_sha": os.environ.get("GITHUB_HEAD_SHA", source_sha),
        "source_work_tree_dirty": source_work_tree_dirty,
        "input_sha256": input_hashes,
        "glb_bytes": glb_path.stat().st_size,
        "glb_sha256": hashlib.sha256(glb_path.read_bytes()).hexdigest(),
        "embedded_images": [i.name for i in bpy.data.images if i.packed_file],
        "glb_path": str(glb_path),
        "blend_path": str(blend_path),
        "notice": "PROVISIONAL dev only. Not AIRC-verified, not licensed real assets; no photos included.",
    }
    (args.output_dir / "report.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
