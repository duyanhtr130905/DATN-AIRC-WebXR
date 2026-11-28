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
    bpy.data.objects["P507_ARCH_FLOOR"]["layout_revision"] = "R5"
    bpy.data.objects["P507_ARCH_FLOOR"]["virtual_adaptation"] = True
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
    slate = material("P507_R5_NEUTRAL_SLATE_TILE", (0.42, 0.43, 0.41), 0.47)
    dark_tiles = ((1, 3), (5, 6), (9, 5), (12, 9), (5, 14), (9, 18), (3, 21))
    for ix, iy in dark_tiles:
        x, y = (ix + 0.5) * 0.6, (iy + 0.5) * 0.6
        if x + 0.3 < width and y + 0.3 < length:
            cube(
                "P507_R5_SLATE_ACCENT_TILE",
                (x, y, 0.00015),
                (0.578, 0.578, 0.0003),
                slate,
                architecture,
            )
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
            elif obj.name == "P507_HERO_NORTH_SKIRTING":
                obj.location.y += design["room"]["length_y"] - 9.315
            else:
                raise ValueError(f"Unexpected untagged frozen mesh {obj.name}")
    shelf = next(
        record for record in design["objects"] if record["id"] == "P507-UTILITY-SHELF"
    )
    shelf_mesh(shelf, shelf_levels, collections[0])
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
