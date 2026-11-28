"""Build the editable neutral P507 R5 asset from the frozen R4 Blender master."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R4_SOURCE = HERE.parent / "p507-g1-g2"
R4_RUNTIME = HERE.parent / "p507-webxr"

# The frozen Blender/geometry helpers remain unchanged; this script is its own
# entry point and does not use the R4 verification or export contract.
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(R4_RUNTIME))
sys.path.insert(0, str(R4_SOURCE))
from generate_blender import (
    camera_and_lights,
    combine,
    cube,
    material,
    room_shell,
    tube,
)
from geometry import occupancy, oriented_rectangle, survey_to_three
from layout import R5_LABEL, build_layout
from prop_meshes import build_mesh, palette, shelf_mesh
from props import build_props
from validate_asset import validate_bundle

BASE_BLEND = "P507_G1_G2_PROVISIONAL.blend"
BASE_BLEND_SHA = "3c092018ce2ed7ebd1c3065cf0e4aa7ef1ab5750aa109ffd771e72f8805689e2"
MODEL = "P507_R5_PROPOSAL.glb"
BLEND = "P507_R5_PROPOSAL.blend"


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frozen-bundle", type=Path, default=ROOT / ".local/p507-e0-e1/artifact"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(
        sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    )
    args.output_dir = args.output_dir.resolve()
    if not args.output_dir.is_relative_to((ROOT / ".local/p507-r5").resolve()):
        parser.error(
            "R5 assets must be generated in the ignored .local/p507-r5 directory"
        )
    if args.output_dir.exists():
        parser.error("Output exists. Use a new R5 output directory")
    return args


def read_base(frozen):
    verified = validate_bundle(frozen)
    blend = frozen / BASE_BLEND
    if sha_file(blend) != BASE_BLEND_SHA:
        raise ValueError(
            "Frozen R4 editable master does not match the pinned archive member"
        )
    return blend, {
        "revision": "R4",
        "blend_sha256": BASE_BLEND_SHA,
        "model_sha256": verified["modelSha256"],
        "manifest_sha256": sha_file(frozen / "asset-manifest.json"),
    }


def make_procedural_tile_image():
    """Generate a 512x512 4x4 metric floor tile image (no Z-fighting accent tiles)."""
    import random

    name = "P507_SELF_GENERATED_NEUTRAL_TILE"
    existing = bpy.data.images.get(name)
    if existing:
        bpy.data.images.remove(existing)
    size = 512
    tile = size // 4
    img = bpy.data.images.new(name, width=size, height=size, alpha=True)
    rng = random.Random(5075)
    accents = {(1, 0), (2, 2)}
    tile_tones = {}
    for ty in range(4):
        for tx in range(4):
            if (tx, ty) in accents:
                tile_tones[(tx, ty)] = (0.74, 0.75, 0.74)
            else:
                delta = rng.uniform(-0.012, 0.012)
                tile_tones[(tx, ty)] = (0.85 + delta, 0.855 + delta, 0.83 + delta)
    pixels = []
    for y in range(size):
        ty, ly = divmod(y, tile)
        for x in range(size):
            tx, lx = divmod(x, tile)
            grout = lx < 2 or ly < 2
            speck = rng.uniform(-0.009, 0.009)
            base = (0.54, 0.55, 0.53) if grout else tile_tones[(tx, ty)]
            pixels.extend((
                max(0.0, min(1.0, base[0] + speck)),
                max(0.0, min(1.0, base[1] + speck)),
                max(0.0, min(1.0, base[2] + speck)),
                1.0,
            ))
    img.pixels.foreach_set(pixels)
    img.pack()
    return img


def make_contact_shadow_image():
    """Generate a 64x64 soft rounded-box contact shadow alpha texture."""
    import math

    name = "P507_SELF_GENERATED_CONTACT_SHADOW"
    existing = bpy.data.images.get(name)
    if existing:
        bpy.data.images.remove(existing)
    size = 64
    img = bpy.data.images.new(name, width=size, height=size, alpha=True)
    pixels = []
    for y in range(size):
        v = abs((y + 0.5) / size * 2.0 - 1.0)
        for x in range(size):
            u = abs((x + 0.5) / size * 2.0 - 1.0)
            # Soft rounded rectangle falloff
            dx = max(0.0, u - 0.38) / 0.62
            dy = max(0.0, v - 0.38) / 0.62
            d = min(1.0, math.hypot(dx, dy))
            alpha = 0.34 * (1.0 - d * d * (3.0 - 2.0 * d))
            pixels.extend((0.03, 0.035, 0.045, max(0.0, alpha)))
    img.pixels.foreach_set(pixels)
    img.pack()
    return img


def contact_shadow_material():
    name = "P507_R5_CONTACT_SHADOW"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.03, 0.035, 0.045, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    spec_key = "Specular IOR Level" if "Specular IOR Level" in bsdf.inputs else "Specular"
    if spec_key in bsdf.inputs:
        bsdf.inputs[spec_key].default_value = 0.0
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = make_contact_shadow_image()
    tex.extension = "EXTEND"
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    mat.node_tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    if hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    return mat


def add_shadow_quad(name, center_xyz, size_xy, mat, col, ident=None):
    import bmesh

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    hw, hd = size_xy[0] / 2.0, size_xy[1] / 2.0
    v1 = bm.verts.new((-hw, -hd, 0.0))
    v2 = bm.verts.new((hw, -hd, 0.0))
    v3 = bm.verts.new((hw, hd, 0.0))
    v4 = bm.verts.new((-hw, hd, 0.0))
    bm.faces.new((v1, v2, v3, v4))
    bm.to_mesh(mesh)
    bm.free()
    uv = mesh.uv_layers.new(name="UVMap")
    for idx, co in enumerate(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))):
        uv.data[idx].uv = co
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center_xyz
    col.objects.link(obj)
    if ident:
        obj["survey_instance_id"] = ident
    return obj


def upgrade_r5_materials():
    """Refine PBR roughness, metallic, glass, polymer, and procedural textures for R5."""
    def tune(mat_name, rgb=None, roughness=None, metal=None, alpha=None, emission=None, spec=None, blend=None):
        mat = bpy.data.materials.get(mat_name)
        if not mat or not mat.use_nodes:
            return
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            return
        if rgb is not None:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
            mat.diffuse_color = (*rgb, 1.0)
        if roughness is not None:
            bsdf.inputs["Roughness"].default_value = roughness
        if metal is not None:
            bsdf.inputs["Metallic"].default_value = metal
        if alpha is not None:
            bsdf.inputs["Alpha"].default_value = alpha
        if emission is not None:
            if rgb is not None and "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission
        if spec is not None:
            sk = "Specular IOR Level" if "Specular IOR Level" in bsdf.inputs else "Specular"
            if sk in bsdf.inputs:
                bsdf.inputs[sk].default_value = spec
        if blend is not None:
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "BLENDED" if blend == "BLEND" else "DITHERED"
            if hasattr(mat, "blend_method"):
                mat.blend_method = blend

    tune("P507_PBR_CHARCOAL_SEAT", (0.036, 0.068, 0.118), roughness=0.46, metal=0.04, spec=0.45)
    tune("P507_PBR_SATIN_CHROME", (0.68, 0.71, 0.74), roughness=0.24, metal=0.88)
    tune("P507_PBR_GRAY_PAINTED_TABLE_STEEL", (0.58, 0.61, 0.64), roughness=0.38, metal=0.45)
    tune("P507_PBR_LAMINATE_WHITE", (0.91, 0.91, 0.88), roughness=0.36, spec=0.42)
    tune("P507_PBR_CREAM_PAINT", roughness=0.86, spec=0.25)
    tune("P507_PBR_CEILING", (0.90, 0.90, 0.88), roughness=0.86)
    tune("P507_PBR_LED_PANEL", (0.98, 0.99, 1.00), roughness=0.45, emission=1.85)
    tune("P507_PBR_OFFWHITE_ENAMEL", (0.88, 0.89, 0.88), roughness=0.36, metal=0.22)
    tune("P507_PBR_WINDOW_PLACEHOLDER", (0.72, 0.85, 0.92), roughness=0.07, metal=0.10, alpha=0.22, blend="BLEND")
    tune("P507_PBR_FILE_CABINET_CLEAR_GLASS", (0.82, 0.91, 0.94), roughness=0.08, metal=0.02, alpha=0.20, blend="BLEND")
    tune("P507_PBR_DOOR_FROSTED_GLASS", (0.74, 0.80, 0.82), roughness=0.42, metal=0.02, alpha=0.55, blend="BLEND")
    tune("P507_PBR_ROLLER_BLIND", (0.81, 0.79, 0.74), roughness=0.84)
    tune("P507_PBR_TRANSLUCENT_BLUE_PET", (0.24, 0.66, 0.86), roughness=0.12, alpha=0.56, blend="BLEND")
    tune("P507_PBR_TV_OFF_SCREEN", (0.015, 0.020, 0.028), roughness=0.14, metal=0.05, spec=0.48)
    tune("P507_PBR_CABINET_WARMWHITE", (0.89, 0.87, 0.81), roughness=0.48)
    tune("P507_PBR_NEUTRAL_WOOD_FRAME", (0.36, 0.22, 0.11), roughness=0.44)
    tune("P507_PBR_NEUTRAL_MAT_PAPER", (0.93, 0.92, 0.89), roughness=0.86)
    tune("P507_PBR_FAKE_COLOR_FIELD_01", (0.28, 0.48, 0.54), roughness=0.72)
    tune("P507_PBR_FAKE_COLOR_FIELD_02", (0.56, 0.36, 0.30), roughness=0.72)
    tune("P507_PBR_FAKE_COLOR_FIELD_03", (0.34, 0.50, 0.38), roughness=0.72)
    tune("P507_PBR_UTILITY_GRAY_STEEL", (0.46, 0.49, 0.51), roughness=0.44, metal=0.40)
    tune("P507_PBR_BRUSHED_FRIDGE_STEEL", (0.56, 0.57, 0.55), roughness=0.32, metal=0.55)
    tune("P507_PBR_SHELF_BLUE_ENAMEL", (0.04, 0.24, 0.48), roughness=0.36, metal=0.25)

    # Replace floor tile texture with 4x4 multi-tile procedural pattern (no Z-fighting overlay).
    tile_mat = bpy.data.materials.get("P507_PBR_PROCEDURAL_TILE_060M")
    if tile_mat and tile_mat.use_nodes:
        bsdf = tile_mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = 0.28
        tile_img = make_procedural_tile_image()
        for node in tile_mat.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                node.image = tile_img
                node.extension = "REPEAT"


def replace_architecture(design, architecture, lookdev):
    for col in (architecture, lookdev):
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    aliases = {
        "tile": "P507_PBR_PROCEDURAL_TILE_060M",
        "paint": "P507_PBR_CREAM_PAINT",
        "white_metal": "P507_PBR_OFFWHITE_ENAMEL",
        "glass": "P507_PBR_WINDOW_PLACEHOLDER",
        "blind": "P507_PBR_ROLLER_BLIND",
        "ceiling": "P507_PBR_CEILING",
        "wood": "P507_PBR_SELF_AUTHORED_PALE_OAK",
        "chrome": "P507_PBR_SATIN_CHROME",
        "cabinet": "P507_PBR_CABINET_WARMWHITE",
        "frosted_glass": "P507_PBR_DOOR_FROSTED_GLASS",
    }
    mats = {name: bpy.data.materials[key] for name, key in aliases.items()}
    room_shell(design, architecture, mats)
    width, length = (design["room"][key] for key in ("width_x", "length_y"))
    floor = bpy.data.objects["P507_ARCH_FLOOR"]
    floor["layout_revision"] = "R5"
    floor["virtual_adaptation"] = True
    # Scale UV so the 4x4 procedural image spans 4 x 0.60 m = 2.40 m cleanly.
    uv = floor.data.uv_layers.active
    if uv:
        for face in floor.data.polygons:
            if face.normal.z > 0.8:
                for loop_idx in face.loop_indices:
                    vertex = floor.data.vertices[floor.data.loops[loop_idx].vertex_index]
                    uv.data[loop_idx].uv = (
                        vertex.co.x / 2.40,
                        vertex.co.y / 2.40,
                    )
    for window in design["openings"]["windows"]:
        y0, y1 = window["from_y"], window["to_y"]
        z0, z1 = window["sill_z"], window["top_z"]
        x = width - 0.034
        for k in range(1, 8):
            y = y0 + (y1 - y0) * k / 8
            rod = tube(
                f"{window['id']}_GUARD",
                (x, y, z0 + 0.018),
                (x, y, z1 - 0.018),
                0.007,
                mats["white_metal"],
                architecture,
            )
            rod["survey_instance_id"] = window["id"]
            for side in (-1, 1):
                joint = tube(
                    f"{window['id']}_GUARD_SCROLL",
                    (x, y, z0 + 0.16),
                    (x, y + side * 0.024, z0 + 0.20),
                    0.004,
                    mats["white_metal"],
                    architecture,
                )
                joint["survey_instance_id"] = window["id"]
    grids = [
        obj
        for obj in architecture.objects
        if obj.name.startswith("P507_ARCH_CEILING_GRID")
    ]
    tiles = [
        obj
        for obj in architecture.objects
        if obj.name.startswith("P507_ARCH_CEILING_TILE_")
    ]
    if grids:
        combine(grids, "P507_ARCH_CEILING_GRID", architecture)
    if tiles:
        combine(tiles, "P507_ARCH_CEILING_TILES", architecture)
    camera_and_lights(design, lookdev)


def proxy_center(proxy):
    polygon = proxy["polygon"]
    return Vector(
        (
            sum(point[0] for point in polygon) / len(polygon),
            sum(point[1] for point in polygon) / len(polygon),
            proxy["bottom_z"],
        )
    )


def move_frozen_meshes(collections, old_proxies, new_proxies, design, shelf_levels):
    old = {record["id"]: record for record in old_proxies}
    new = {record["id"]: record for record in new_proxies}
    bound_preserved = set()
    chair_obj = None
    for col in collections:
        for obj in list(col.objects):
            ident = obj.get("survey_instance_id")
            if ident == "P507-UTILITY-SHELF":
                bpy.data.objects.remove(obj, do_unlink=True)
            elif ident:
                # Furniture dimensions and angles stay fixed; each asset moves
                # rigidly (TV mount follows the TV even if the R4 anchor was constant).
                expected, baseline = new[ident], old[ident]
                obj.location += proxy_center(expected) - proxy_center(baseline)
                bound_preserved.add(ident)
                if ident.startswith("P507-CHAIR-") and chair_obj is None:
                    chair_obj = obj
            elif obj.name == "P507_HERO_NORTH_SKIRTING":
                obj.location.x = design["room"]["width_x"] / 2
                obj.location.y += design["room"]["length_y"] - 9.315
                obj.scale.x = design["room"]["width_x"] / 6.9
            else:
                raise ValueError(f"Unexpected untagged frozen mesh {obj.name}")
    shelf = next(
        record for record in design["objects"] if record["id"] == "P507-UTILITY-SHELF"
    )
    shelf_mesh(shelf, shelf_levels, collections[0])

    # Add lightweight baked-gradient contact shadows under floor furniture and chairs.
    shadow_mat = contact_shadow_material()
    if chair_obj is not None:
        add_shadow_quad(
            "P507_CHAIR_CONTACT_SHADOW",
            (0.0, -0.02, 0.0015),
            (0.42, 0.42),
            shadow_mat,
            collections[0],
        ).parent = None
        # Add to every chair instance (stays inside chair's visual envelope and moves with it)
        for chair_item in design["chairs"]["instances"]:
            if chair_item["status"] != "PLACED_PROVISIONAL":
                continue
            cx, cy = chair_item["center"][:2]
            q = add_shadow_quad(
                chair_item["id"].replace("-", "_") + "_SHADOW",
                (cx, cy, 0.0015),
                (0.42, 0.42),
                shadow_mat,
                collections[0],
                ident=chair_item["id"],
            )
            q.rotation_euler.z = __import__("math").radians(chair_item["orientation_deg"])
        for obj in list(collections[0].objects):
            if obj.name == "P507_CHAIR_CONTACT_SHADOW":
                bpy.data.objects.remove(obj, do_unlink=True)

    shadow_kinds = {
        "table_standard", "table_small", "cabinet", "file_cabinet",
        "fridge", "storage_shelf", "waste_bin", "shoe_rack", "water_dispenser",
    }
    for proxy in new_proxies:
        if proxy.get("kind") not in shadow_kinds:
            continue
        xs = [pt[0] for pt in proxy["polygon"]]
        ys = [pt[1] for pt in proxy["polygon"]]
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        sx = max(0.10, (max(xs) - min(xs)) - 0.02)
        sy = max(0.10, (max(ys) - min(ys)) - 0.02)
        add_shadow_quad(
            proxy["id"].replace("-", "_") + "_CONTACT_SHADOW",
            (cx, cy, 0.0012),
            (sx, sy),
            shadow_mat,
            collections[0],
            ident=proxy["id"],
        )
    return bound_preserved


def group_repeated_ids(collections):
    groups = defaultdict(list)
    for col in collections:
        for obj in col.objects:
            if obj.get("survey_instance_id"):
                groups[obj["survey_instance_id"]].append((col, obj))
    bpy.context.view_layer.update()
    for ident, members in groups.items():
        if len(members) < 2:
            continue
        col = members[0][0]
        parent = bpy.data.objects.new(ident, None)
        col.objects.link(parent)
        parent["survey_instance_id"] = ident
        for _, obj in members:
            world = obj.matrix_world.copy()
            obj.parent = parent
            obj.matrix_world = world
            del obj["survey_instance_id"]
    return groups


def measured_bounds(groups):
    evaluated = bpy.context.evaluated_depsgraph_get()
    out = {}
    for ident, members in groups.items():
        lower = [float("inf")] * 3
        upper = [float("-inf")] * 3
        for _, obj in members:
            mesh_obj = obj.evaluated_get(evaluated)
            mesh = mesh_obj.to_mesh()
            try:
                for vertex in mesh.vertices:
                    world = mesh_obj.matrix_world @ vertex.co
                    for i, value in enumerate(world):
                        lower[i] = min(lower[i], value)
                        upper[i] = max(upper[i], value)
            finally:
                mesh_obj.to_mesh_clear()
        out[ident] = lower + upper
    return out


def prop_envelope(record):
    x, y, z = record["center"]
    return {
        "id": record["id"],
        "kind": record["type"],
        "polygon": oriented_rectangle(
            (x, y), record["size"][:2], record["orientation_deg"]
        ),
        "bottom_z": z,
        "top_z": z + record["size"][2],
    }


def inventory_records(design, props):
    return (
        design["objects"]
        + design["chairs"]["instances"]
        + list(design["hero"].values())
        + design["ceiling"]["instances"]
        + design["photo_wall"]["frames"]
        + design["openings"]["door"]["leaves"]
        + [
            item
            for window in design["openings"]["windows"]
            for item in (window, window["blind"])
        ]
        + props
    )


def support_geometry(design, props, levels):
    objects = {item["id"]: item for item in design["objects"]}
    width = design["room"]["width_x"]
    length = design["room"]["length_y"]
    shelves = objects["P507-UTILITY-SHELF"]
    return {
        "desk_surfaces": {
            item["id"]: {"rect": item["rect"], "z": item["height"]}
            for item in design["objects"]
            if item["id"].startswith("P507-DESK-")
        },
        "shelf_surfaces": {
            "id": shelves["id"],
            "rect": shelves["rect"],
            "surface_z": levels,
            "top_objects": [
                "P507-TV-SMALL",
                *[item["id"] for item in props if item.get("tier") == 1],
            ],
        },
        "wall_surfaces": {
            "TV_WALL": length - 0.05,
            "WEST_WALL": 0.05,
            "EAST_WALL": width - 0.05,
        },
        "window_intervals": [
            {"id": w["id"], "from_y": w["from_y"], "to_y": w["to_y"]}
            for w in design["openings"]["windows"]
        ],
        "door_interval": {
            key: design["openings"]["door"][key]
            for key in ("from_y", "to_y", "entry_rect", "sweep_polygons")
        },
        "whiteboard_rect": objects["P507-WHITEBOARD"]["rect"],
    }


def write_manifest(output, layout, ancestry, props, bounds, proxies):
    design = layout["design"]
    records = inventory_records(design, props)
    if len({item["id"] for item in records}) != len(records):
        raise ValueError("Duplicate R5 inventory identity")
    placed = {item["id"] for item in records if item.get("status") != "UNPLACED"}
    if placed != set(bounds):
        raise ValueError(
            f"Blender inventory mismatch: absent {placed - set(bounds)}; extra {set(bounds) - placed}"
        )
    instances = [
        {
            "id": item["id"],
            "status": item.get("status", "PLACED_PROVISIONAL"),
            "placement_allocation": item.get("placement_allocation"),
            "logical_type": item.get("type"),
            "survey_transform": {
                k: item[k]
                for k in (
                    "center",
                    "rect",
                    "orientation_deg",
                    "size",
                    "height",
                    "support_id",
                    "support_ids",
                    "source_kind",
                    "position_source",
                    "tier",
                    "chair_id",
                    "adjacent_windows",
                    "position",
                    "above_id",
                )
                if k in item
            },
            "authored_bounds_survey": bounds.get(item["id"]),
            "mesh_binding": "glTF node extras.survey_instance_id",
            "rights": item.get("rights", "NEUTRAL_GENERATED_GEOMETRY_ONLY"),
        }
        for item in records
    ]
    model = output / MODEL
    document = {
        "schema_version": 1,
        "revision": "R5",
        "state": R5_LABEL,
        "scope": "DEV_LOOPBACK_ONLY",
        "unit": "metre",
        "axis_conversion": "(x,z,-y)",
        "ancestry": ancestry,
        "model": MODEL,
        "model_sha256": sha_file(model),
        "model_bytes": model.stat().st_size,
        "source_sha256": {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(
                path.read_text(encoding="utf-8").encode()
            ).hexdigest()
            for path in (
                Path(__file__).resolve(),
                HERE / "layout.py",
                HERE / "props.py",
                HERE / "prop_meshes.py",
                R4_SOURCE / "geometry.py",
                R4_SOURCE / "generate_blender.py",
                R4_SOURCE / "p507-provisional.json",
            )
        },
        "survey_baseline": design["survey_baseline"],
        "virtual_dimensions": {
            key: design["room"][key] for key in ("width_x", "length_y", "height_z")
        },
        "starting_pose": {
            "feet_survey": layout["spawn"],
            "feet_gltf": survey_to_three(layout["spawn"]),
        },
        "floor": {
            "surface_z_survey": 0,
            "walkable_rect_survey": layout["walkable_rect"],
        },
        "layout": {
            key: layout[key]
            for key in (
                "chairs",
                "static_walk_colliders",
                "static_interaction_colliders",
                "walkable_rect",
                "spawn",
            )
        },
        "collision_proxies": layout["static_walk_colliders"],
        "interaction_colliders": layout["static_interaction_colliders"],
        "visual_envelopes": [*proxies, *map(prop_envelope, props)],
        "supports": support_geometry(design, props, layout["shelf_surfaces_z"]),
        "instances": instances,
        "toolchain": {"blender": bpy.app.version_string},
        "privacy": "Synthetic and neutral geometry. No real images, branding, credentials, or personal data.",
        "photo_reference": "PHOTO_REFERENCE_UNAVAILABLE",
        "owner_visual_approval": "PENDING",
    }
    (output / "asset-manifest.json").write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8"
    )
    return document


def build():
    args = parse_args()
    base_path, ancestry = read_base(args.frozen_bundle.resolve())
    layout = build_layout()
    design = layout["design"]
    old_design = json.loads(
        (R4_SOURCE / "p507-provisional.json").read_text(encoding="utf-8")
    )
    proxies = occupancy(design)
    layout_static = {entry["id"]: entry for entry in layout["static_walk_colliders"]}
    proxies = [layout_static.get(entry["id"], entry) for entry in proxies]
    tv = next(entry for entry in proxies if entry["id"] == "P507-TV-LARGE")
    tv_x = [point[0] for point in tv["polygon"]]
    props = build_props(design, layout["shelf_surfaces_z"], (min(tv_x), max(tv_x)))

    bpy.ops.wm.open_mainfile(filepath=str(base_path), load_ui=False, use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    if any(
        image.source == "FILE" and not image.packed_file for image in bpy.data.images
    ):
        raise ValueError("Unpacked external image reference in frozen editable master")
    collection = lambda name: bpy.data.collections[name]
    arch = collection("10_ARCH")
    furniture = collection("20_FURNITURE")
    equipment = collection("30_EQUIPMENT")
    ceiling = collection("40_CEILING")
    decor = collection("50_DECOR")
    upgrade_r5_materials()
    replace_architecture(design, arch, collection("80_LOOKDEV_CAMERAS"))
    move_frozen_meshes(
        (furniture, equipment, ceiling),
        occupancy(old_design),
        proxies,
        design,
        layout["shelf_surfaces_z"],
    )
    prop_materials = palette()
    for item in props:
        build_mesh(item, decor, prop_materials)
    collections = (arch, furniture, equipment, ceiling, decor)
    groups = group_repeated_ids(collections)
    bounds = measured_bounds(groups)

    args.output_dir.mkdir(parents=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output_dir / BLEND), copy=True)
    bpy.ops.object.select_all(action="DESELECT")
    for col in collections:
        for obj in col.objects:
            obj.select_set(obj.type in {"MESH", "EMPTY"})
    result = bpy.ops.export_scene.gltf(
        filepath=str(args.output_dir / MODEL),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_extras=True,
    )
    if "FINISHED" not in result or not (args.output_dir / MODEL).is_file():
        raise RuntimeError("R5 GLB export did not finish")
    manifest = write_manifest(args.output_dir, layout, ancestry, props, bounds, proxies)
    print(
        f"R5 {manifest['model_sha256']} {manifest['model_bytes']} bytes; {len(bounds)} placed IDs"
    )


if __name__ == "__main__":
    build()
