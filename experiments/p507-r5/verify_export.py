"""Independently validate the exported R5 candidate and prepare DEV-only copies."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import isfinite
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = ROOT / ".local/p507-e0-e1/artifact"
R5_LOCAL = ROOT / ".local/p507-r5"
MODEL = "P507_R5_PROPOSAL.glb"
MANIFEST = "asset-manifest.json"
REFERENCE = "export-reference.json"
LOCK = HERE / "asset-lock.json"
# Same authored-versus-exported comparison as frozen R4. Translation and
# evaluated modifiers should round-trip within this error.
BOUNDS_TOLERANCE_M = 0.003

sys.path.insert(0, str(HERE.parent / "p507-webxr"))
from tv_diagnostic_math import glb_components, prism_clearance, read_glb, union_bounds
from validate_asset import validate_bundle
from verify_props import verify_props


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def file_identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def index_instances(manifest):
    items = {}
    for item in manifest["instances"]:
        ident = item["id"]
        require(ident not in items, f"Duplicate manifest ID {ident}")
        items[ident] = item
    return items


def expected_bounds(record):
    bounds = record["authored_bounds_survey"]
    ident = record["id"]
    require(len(bounds) == 6 and all(isfinite(n) for n in bounds), f"Invalid authored bounds: {ident}")
    x0, y0, z0, x1, y1, z1 = bounds
    require(x0 < x1 and y0 < y1 and z0 < z1, f"Non-solid authored bounds: {ident}")
    return [x0, z0, -y1, x1, z1, -y0]


def validate_identity(directory, frozen):
    frozen_identity = validate_bundle(frozen)
    old_manifest = read_json(frozen / MANIFEST)
    manifest = read_json(directory / MANIFEST)
    require(manifest["revision"] == "R5", "R5 revision mismatch")
    require(manifest["survey_baseline"] == old_manifest["survey_baseline"], "Historical survey changed")
    require(manifest["unit"] == "metre", "R5 unit mismatch")
    ancestry = manifest["ancestry"]
    require(ancestry["revision"] == "R4", "R4 ancestry mismatch")
    require(ancestry["model_sha256"] == frozen_identity["modelSha256"], "R4 model ancestry mismatch")
    require(ancestry["manifest_sha256"] == file_identity(frozen / MANIFEST)["sha256"], "R4 manifest ancestry mismatch")
    model = file_identity(directory / MODEL)
    require(manifest["model_sha256"] == model["sha256"] and manifest["model_bytes"] == model["bytes"],
            "Manifest/model bytes or hash mismatch")
    old, revised = index_instances(old_manifest), index_instances(manifest)
    require(old.keys() <= revised.keys(), "A frozen R4 ID is missing")
    unplaced = {i for i, item in revised.items() if item["status"] == "UNPLACED"}
    require(unplaced == {"P507-CHAIR-C-09", "P507-CHAIR-C-10"}, "Historical unplaced IDs changed")
    placed = {i: item for i, item in revised.items() if i not in unplaced}
    for prefix, count in (("P507-DESK-", 17), ("P507-CHAIR-", 34)):
        require(sum(i.startswith(prefix) for i in placed) == count, f"Unexpected inventory for {prefix}")
    return model, placed


def inspect(directory, frozen=FROZEN):
    model, placed = validate_identity(directory, frozen)
    doc, _ = read_glb(directory / MODEL)
    tags = Counter(node["extras"]["survey_instance_id"] for node in doc["nodes"]
                   if "survey_instance_id" in node.get("extras", {}))
    require(tags == Counter(placed.keys()), "GLB logical tags differ from placed manifest IDs")
    require(not any(buffer.get("uri") for buffer in doc["buffers"]), "External GLB buffer")
    for image in doc.get("images", []):
        require(image.get("name", "").startswith("P507_SELF_GENERATED_")
                and "bufferView" in image and "uri" not in image, "Unapproved GLB image")
    groups = defaultdict(list)
    components = glb_components(directory / MODEL)
    for part in components:
        require(all(isfinite(n) for n in part["bounds_gltf"]), "Non-finite exported bounds")
        if part["id"] is not None:
            groups[part["id"]].append(part)
    require(groups.keys() == placed.keys(), "Placed GLB mesh identities differ from manifest")
    manifest = read_json(directory / MANIFEST)
    volumes = {volume["id"]: volume for volume in manifest["visual_envelopes"]}
    require(volumes.keys() == placed.keys() and len(volumes) == len(manifest["visual_envelopes"]),
            "R5 visual envelope coverage differs")
    records = []
    for ident, record in sorted(placed.items()):
        parts = groups[ident]
        actual = union_bounds([part["bounds_gltf"] for part in parts])
        delta = max(abs(a - b) for a, b in zip(actual, expected_bounds(record), strict=True))
        require(delta <= BOUNDS_TOLERANCE_M, f"{ident} authored/export bound drift {delta:.6f} m")
        nearest_proxy_edge = min(prism_clearance(vertex, volumes[ident])
                                 for part in parts for vertex in part["positions_gltf"])
        require(nearest_proxy_edge >= -.001, f"{ident} vertex outside oriented proxy {nearest_proxy_edge:.6f} m")
        records.append({
            "id": ident,
            "bounds_gltf": actual,
            "max_authored_delta_m": delta,
            "min_proxy_margin_m": nearest_proxy_edge,
            "primitive_count": len(parts),
            "vertex_samples": sum(part["vertex_count"] for part in parts),
        })
    return {
        "schema_version": 1,
        "revision": "R5",
        "model": model,
        "primitives": len(components),
        "prop_checks": verify_props(manifest),
        "vertex_samples": sum(part["vertex_count"] for part in components),
        "records": records,
    }


def prepare(directory):
    served = R5_LOCAL / "served"
    files = (MODEL, MANIFEST)
    lock = read_json(LOCK)
    require(lock["revision"] == "R5" and lock["schema_version"] == 1
            and set(lock["files"]) == set(files), "Invalid R5 lock")
    identities = {name: file_identity(directory / name) for name in files}
    require(identities == lock["files"], "Candidate bytes differ from the checked-in lock")
    if served.exists():
        require(all((served / name).is_file() and file_identity(served / name) == identities[name]
                    for name in files), "DEV destination differs; preserve the existing bundle before preparing")
        return
    served.mkdir()
    for name in files:
        with (served / name).open("xb") as target, (directory / name).open("rb") as source:
            shutil.copyfileobj(source, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--record", action="store_true", help="Write a new independent reference")
    action.add_argument("--verify", action="store_true", help="Compare against reference without rewriting it")
    action.add_argument("--prepare", action="store_true", help="Verify reference and stage checked-in locked bytes")
    args = parser.parse_args()
    directory = args.directory.resolve()
    require(directory.is_relative_to(R5_LOCAL.resolve()) and directory != R5_LOCAL / "served",
            "Use a generated directory below ignored .local/p507-r5, separate from the DEV destination")
    result = inspect(directory)
    if args.record:
        write_new(directory / REFERENCE, result)
    else:
        require(result == read_json(directory / REFERENCE), "R5 export reference mismatch")
        if args.prepare:
            prepare(directory)
    print(json.dumps({"revision": "R5", "status": "PASS", "placed": len(result["records"]),
                      "primitives": result["primitives"], "vertex_samples": result["vertex_samples"]}))


if __name__ == "__main__":
    main()
