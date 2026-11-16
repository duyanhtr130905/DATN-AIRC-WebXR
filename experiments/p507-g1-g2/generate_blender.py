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
from geometry import read_inventory, verify  # noqa: E402

try:
    import bpy
except ImportError as exc:
    raise SystemExit("Blender bpy unavailable. Run from Blender Python; do not claim GLB export PASS.") from exc


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=HERE / "p507-provisional.json")
    parser.add_argument("--output-dir", required=True, type=Path)
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
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
    mat = material("P507_PBR_PROCEDURAL_TILE_060M", (.82,.82,.79), .38)
    image = bpy.data.images.new("P507_SELF_GENERATED_NEUTRAL_TILE", width=256, height=256, alpha=True)
    pixels = []
    import random
    rng = random.Random(507)
    for y in range(256):
        for x in range(256):
            seam = x < 4 or y < 4 or x > 251 or y > 251
            variation = rng.uniform(-.013, .013)
            base = (.53,.54,.53) if seam else (.80,.80,.775)
            pixels.extend((base[0]+variation,base[1]+variation,base[2]+variation,1.0))
    image.pixels.foreach_set(pixels)
    image.pack()
    shader = mat.node_tree.nodes.get("Principled BSDF")
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "REPEAT"
    mat.node_tree.links.new(tex.outputs["Color"],shader.inputs["Base Color"])
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
        modifier.segments = 2
        if hasattr(modifier, "affect"):
            modifier.affect = "EDGES"
        o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    if ident:
        o["survey_instance_id"] = ident
        o["source_class"] = "PROPOSED_LAYOUT"
    move_to_collection(o, col)
    return o


def cylinder(name, center, radius, depth, mat, col, vertices=16, ident=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
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
    floor = cube("P507_ARCH_FLOOR", (w/2, length/2, -0.045), (w, length, 0.09), mats["tile"], col)
    uv = floor.data.uv_layers.active or floor.data.uv_layers.new(name="MetricTileUV")
    for face in floor.data.polygons:
        if face.normal.z > .8:
            for loop_idx in face.loop_indices:
                vertex = floor.data.vertices[floor.data.loops[loop_idx].vertex_index]
                uv.data[loop_idx].uv = ((vertex.co.x+w/2)/.60,(vertex.co.y+length/2)/.60)
    cube("P507_ARCH_WALL_LOGO", (w/2, 0, height/2), (w, wall_thickness, height), mats["paint"], col)
    cube("P507_ARCH_WALL_TV", (w/2, length, height/2), (w, wall_thickness, height), mats["paint"], col)
    door = data["openings"]["door"]
    if door["wall"] != "west":
        raise ValueError("G1 only supports entrance on west wall")
    segments = [(0, door["from_y"]), (door["to_y"], length)]
    for idx, (y0, y1) in enumerate(segments):
        if y1 > y0:
            cube("P507_ARCH_WALL_WEST_%02d" % idx, (0, (y0+y1)/2, height/2),
                 (wall_thickness, y1-y0, height), mats["paint"], col)
    cube("P507_ARCH_WEST_DOOR_HEADER", (0, (door["from_y"]+door["to_y"])/2, (door["height"]+height)/2),
         (wall_thickness, door["to_y"]-door["from_y"], height-door["height"]), mats["paint"], col)
    # Architectural openings are real voids, not a door mesh over an intact wall.
    windows = data["openings"]["windows"]
    cursor = 0
    for idx, win in enumerate(windows):
        a, b = win["from_y"], win["to_y"]
        if a < cursor or b > length or a >= b:
            raise ValueError("Invalid or overlapping window intervals")
        if a > cursor:
            cube("P507_ARCH_WALL_EAST_%02d" % idx, (w, (cursor+a)/2, height/2),
                 (wall_thickness, a-cursor, height), mats["paint"], col)
        sill, top = win["sill_z"], win["top_z"]
        cube("P507_ARCH_EAST_SILL_%02d" % idx, (w, (a+b)/2, sill/2),
             (wall_thickness, b-a, sill), mats["paint"], col)
        cube("P507_ARCH_EAST_HEADER_%02d" % idx, (w, (a+b)/2, (top+height)/2),
             (wall_thickness, b-a, height-top), mats["paint"], col)
        cube("P507_ARCH_WINDOW_GLASS_%02d" % idx, (w, (a+b)/2, (sill+top)/2),
             (.015, b-a-.035, top-sill-.035), mats["glass"], col)
        for y in (a, b):
            cube("P507_ARCH_WINDOW_JAMB_%02d_%02d" % (idx, int(y*100)), (w-.018, y, (sill+top)/2),
                 (.045, .06, top-sill), mats["white_metal"], col, .005)
        cursor = b
    if cursor < length:
        cube("P507_ARCH_WALL_EAST_LAST", (w, (cursor+length)/2, height/2),
             (wall_thickness, length-cursor, height), mats["paint"], col)
    # Neutral roller blinds and skirting, matching the photographed object classes.
    for idx, win in enumerate(windows):
        center_y=(win["from_y"]+win["to_y"])/2
        cube("P507_ARCH_ROLLER_SHADE_%02d" % idx, (w-.075,center_y,2.78),
             (.035,win["to_y"]-win["from_y"]-.03,.43),mats["blind"],col,.012)
        cylinder("P507_ARCH_BLIND_ROLLER_%02d" % idx,(w-.07,center_y,3.01),.035,
                 win["to_y"]-win["from_y"],mats["white_metal"],col)
    cube("P507_ARCH_BASEBOARD_LOGO",(w/2,.075,.07),(w,.03,.14),mats["white_metal"],col,.004)
    cube("P507_ARCH_BASEBOARD_EAST",(w-.07,length/2,.07),(.03,length,.14),mats["white_metal"],col,.004)
    cube("P507_ARCH_DOOR_FRAME_LOW",(0,door["from_y"],door["height"]/2),
         (.14,.06,door["height"]),mats["white_metal"],col,.008)
    cube("P507_ARCH_DOOR_FRAME_HIGH",(0,door["to_y"],door["height"]/2),
         (.14,.06,door["height"]),mats["white_metal"],col,.008)
    # Ceiling tiles are lightweight geometry; no photographic or confidential texture.
    cube("P507_ARCH_CEILING", (w/2, length/2, height+.025), (w, length, .05), mats["ceiling"], col)
    for x in range(1, 10):
        cube("P507_ARCH_CEILING_GRID_X_%02d" % x, (x*.6, length/2, height-.015),
             (.012, length, .012), mats["metal"], col)
    for row in range(1, 14):
        cube("P507_ARCH_CEILING_GRID_Y_%02d" % row, (w/2, row*.6, height-.015),
             (w, .012, .012), mats["metal"], col)


def tables_and_chairs(data, tables_col, chairs_col, mats):
    for item in data["objects"]:
        b = item["rect"]
        xmin, ymin, xmax, ymax = b
        cx, cy, sx, sy = (xmin+xmax)/2, (ymin+ymax)/2, xmax-xmin, ymax-ymin
        ident = item["id"]
        name = ident.replace("-", "_")
        cube(name+"_TOP", (cx,cy,item["height"]-.04), (sx,sy,.08), mats["laminate"], tables_col, .016, ident)
        for ix in (-1,1):
            for iy in (-1,1):
                cube(name+"_LEG_%d_%d"%(ix,iy),
                     (cx+ix*(sx/2-.07),cy+iy*(sy/2-.07),(item["height"]-.08)/2),
                     (.044,.044,item["height"]-.08), mats["metal"], tables_col, .005, ident)
    # The 36 chairs are developer-only placeholders: these coordinates are not surveyed.
    # 12 around each desk group; room circulation/door swing is NOT certified.
    for group in "ABC":
        rows = [o["rect"] for o in data["objects"] if o.get("cluster")==group]
        minx = min(b[0] for b in rows); maxx = max(b[2] for b in rows)
        miny = min(b[1] for b in rows); maxy = max(b[3] for b in rows)
        for side in (0,1):
            for pos in range(6):
                idx = pos+1+side*6
                x = minx + ((pos+.5)/6)*(maxx-minx)
                y = (miny-.36) if side==0 else (maxy+.36)
                y = min(max(y,.35),data["room"]["length_y"]-.35)
                ident = f"P507-CHAIR-{group}-{idx:02d}"
                cylinder(ident+"_SEAT", (x,y,.48), .225,.08,mats["chair"],chairs_col,14,ident)
                cube(ident+"_BACK", (x,y+(-.22 if side==0 else .22),.78),
                     (.43,.05,.48),mats["chair"],chairs_col,.04,ident)
                for dx in (-.16,.16):
                    for dy in (-.14,.14):
                        cube(ident+"_LEG_%d_%d"%(int(dx*100),int(dy*100)),
                             (x+dx,y+dy,.23),(.022,.022,.46),mats["metal"],chairs_col,0,ident)


def ceiling_items(data, col, mats):
    h=data["room"]["height_z"]; z=h-.075
    for x in (1.52, 4.48):
        for y in (1.0, 3.0, 5.05, 7.0):
            cube(f"P507_CEILING_LED_{int(x*100)}_{int(y*100)}",
                 (x,y,z),(.60,.60,.026),mats["led"],col,.009)
    for x in (1.55,4.45):
        for y in (2.0,6.0):
            cylinder("P507_CEILING_FAN_CENTER", (x,y,h-.30),.095,.17,mats["metal"],col)
            for i in range(3):
                theta=2*math.pi*i/3
                o=cube("P507_CEILING_FAN_BLADE",
                    (x+.26*math.cos(theta),y+.26*math.sin(theta),h-.32),
                    (.54,.08,.025),mats["chair"],col,.03)
                o.rotation_euler.z=theta
    for y in (2.15,5.95):
        cube("P507_CEILING_AC_CASSETTE", (3.0,y,h-.05),
             (.68,.68,.04),mats["white_metal"],col,.025)
        cube("P507_CEILING_AC_VENT", (3.0,y,h-.076),
             (.38,.38,.01),mats["metal"],col,.01)
    cube("P507_CEILING_PROJECTOR", (3.0,4.05,h-.32),(.38,.29,.15),mats["white_metal"],col,.016)
    cylinder("P507_CEILING_PROJECTOR_LENS",(3.0,3.86,h-.34),.048,.04,mats["screen"],col)


def hero_assets(data, col, mats):
    tv = data["hero"]["tv"]; x=tv["center_x"]; z=tv["center_z"]
    # TV at north wall (Y=length) near door; unapproved visible screen is blank.
    y=data["room"]["length_y"]-.08
    cube("P507_HERO_TV_BEZEL",(x,y,z),(tv["width"],.085,tv["height"]),mats["screen_frame"],col,.025,"P507-TV-LARGE")
    cube("P507_HERO_TV_BLACK_SCREEN",(x,y-.048,z),(tv["width"]-.055,.015,tv["height"]-.065),mats["screen"],col,.01,"P507-TV-LARGE")
    cube("P507_HERO_TV_MOUNT",(x,y+.02,z),(.25,.15,.17),mats["metal"],col,.008,"P507-TV-LARGE")

    cabinet = data["hero"]["cabinet"]
    cx,cy,cz=cabinet["center"]; sx,sy,sz=cabinet["size"]
    cube("P507_HERO_CABINET_BODY",(cx,cy,cz),(sx,sy,sz),mats["cabinet"],col,.019,"P507-CABINET-LOW")
    cube("P507_HERO_CABINET_COUNTER",(cx,cy,sz+.045),(sx+.02,sy+.02,.05),mats["laminate"],col,.018,"P507-CABINET-LOW")
    for i in range(3):
        xx=cx-sx/2+(i+.5)*sx/3
        cube(f"P507_HERO_CABINET_FRONT_{i}",(xx,cy-sy/2-.013,sz*.50),(sx/3-.023,.022,sz-.11),mats["white_metal"],col,.012,"P507-CABINET-LOW")
        cube(f"P507_HERO_CABINET_HANDLE_{i}",(xx,cy-sy/2-.029,sz*.76),(.078,.02,.01),mats["metal"],col,.004,"P507-CABINET-LOW")
    # Wall photograph positions are retained as abstract, self-authored color fields:
    # no actual faces, historical photos or institutional logos are embedded.
    frame_layout = [
        (2.9,2.25,.42,.28),(3.35,2.58,.46,.31),(3.9,2.18,.52,.33),
        (4.55,2.63,.45,.30),(5.15,2.36,.54,.33),(3.05,1.80,.38,.27),
        (3.78,2.92,.46,.28),(4.8,1.91,.47,.29)
    ]
    for i, (xx,zz,ww,hh) in enumerate(frame_layout):
        cube("P507_HERO_PHOTO_FRAME_NEUTRAL_%02d" % i,(xx,7.99,zz),
             (ww,.055,hh),mats["frame_wood"],col,.012)
        cube("P507_HERO_PHOTO_ABSTRACT_NO_IDENTITIES_%02d" % i,(xx,7.950,zz),
             (ww-.065,.009,hh-.065),mats["abstract"][i%len(mats["abstract"])],col,.002)
    # Display pieces are anonymous geometric silhouettes, not copied certificates/awards.
    for i in range(3):
        xx=cx+(i-1)*.40
        cube(f"P507_HERO_NEUTRAL_DISPLAY_{i}",(xx,cy,sz+.24),(.23,.055,.31),mats["gold"],col,.015)

    water=data["hero"]["water_dispenser"]; px,py,_=water["center"]
    cube("P507_HERO_WATER_BASE",(px,py,.48),(.39,.43,.95),mats["white_metal"],col,.025,"P507-WATER-DISPENSER")
    cube("P507_HERO_WATER_PANEL",(px,py-.225,.66),(.27,.015,.15),mats["screen_frame"],col,.008,"P507-WATER-DISPENSER")
    cylinder("P507_HERO_WATER_BOTTLE",(px,py,1.19),.179,.48,mats["blue_water"],col,24,"P507-WATER-DISPENSER")
    cylinder("P507_HERO_WATER_CAP",(px,py,1.46),.075,.065,mats["blue_water"],col,20,"P507-WATER-DISPENSER")
    # Subtle skirting, and realistic edge contrasts for hero zone.
    cube("P507_HERO_NORTH_SKIRTING",(3.0,8.0,.055),(6.0,.026,.11),mats["white_metal"],col,.005)


def camera_and_lights(data, camera_col):
    length=data["room"]["length_y"]
    bpy.ops.object.camera_add(location=(1.6,5.65,1.65))
    cam=bpy.context.object; cam.name="CAM_TV_ART_APPROX"; move_to_collection(cam,camera_col)
    target = (1.45,length-.7,1.6)
    from mathutils import Vector
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z","Y").to_euler()
    cam.data.lens=24
    bpy.context.scene.camera=cam
    # Blender lookdev lights are not exported as runtime GLB lights.
    for name, center, power, color in [
        ("LOOKDEV_WINDOW_DAYLIGHT",(5.9,4.2,2.4),550,(.78,.88,1)),
        ("LOOKDEV_LED_FILL",(2.5,5.1,3.2),350,(1,.96,.86)),
    ]:
        lamp=bpy.data.lights.new(name,"AREA"); lamp.energy=power; lamp.color=color
        lamp.shape="RECTANGLE"; lamp.size=2.5; lamp.size_y=2.0
        obj=bpy.data.objects.new(name,lamp); camera_col.objects.link(obj); obj.location=center


def main():
    args=parse_args()
    data=read_inventory(args.inventory)
    result=verify(data)
    if not result["ok"]:
        raise SystemExit("Invalid geometry: "+json.dumps(result["errors"]))
    args.output_dir.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for existing in list(bpy.data.collections):
        if existing.name=="Collection" and not existing.objects:
            bpy.data.collections.remove(existing)
    scene=bpy.context.scene
    scene.unit_settings.system="METRIC"
    scene.unit_settings.scale_length=1
    mats={
        "paint":material("P507_PBR_CREAM_PAINT",(.74,.71,.64),.92),
        "tile":material("P507_PBR_WARM_TILE",(.80,.80,.75),.31),
        "ceiling":material("P507_PBR_CEILING",(.85,.85,.82),.93),
        "metal":material("P507_PBR_DARK_METAL",(.18,.20,.22),.43,.86),
        "white_metal":material("P507_PBR_OFFWHITE_ENAMEL",(.81,.83,.82),.43,.35),
        "laminate":material("P507_PBR_LAMINATE_WHITE",(.9,.91,.86),.41),
        "chair":material("P507_PBR_CHARCOAL_SEAT",(.08,.09,.10),.82),
        "glass":material("P507_PBR_WINDOW_PLACEHOLDER",(.54,.65,.70),.12,.25),
        "led":material("P507_PBR_LED_PANEL",(.95,.96,.95),.75,emission=1.35),
        "screen_frame":material("P507_PBR_TV_BEZEL",(.055,.061,.066),.40,.30),
        "screen":material("P507_PBR_TV_OFF_SCREEN",(.012,.014,.019),.19,.05),
        "cabinet":material("P507_PBR_CABINET_WARMWHITE",(.82,.79,.72),.6),
        "gold":material("P507_PBR_NEUTRAL_GOLD_PLACEHOLDER",(.43,.31,.12),.39,.70),
        "blue_water":material("P507_PBR_WATER_BOTTLE_PLACEHOLDER",(.22,.53,.78),.25,.15),
        "blind":material("P507_PBR_ROLLER_BLIND",(.70,.68,.64),.94),
        "frame_wood":material("P507_PBR_NEUTRAL_WOOD_FRAME",(.34,.28,.22),.58),
        "abstract":[
            material("P507_PBR_FAKE_COLOR_FIELD_01",(.34,.48,.50),.9),
            material("P507_PBR_FAKE_COLOR_FIELD_02",(.43,.36,.36),.9),
            material("P507_PBR_FAKE_COLOR_FIELD_03",(.40,.48,.35),.9),
        ],
    }
    arch=collection("10_ARCH"); furniture=collection("20_FURNITURE")
    equipment=collection("30_EQUIPMENT"); ceiling=collection("40_CEILING")
    lookdev=collection("80_LOOKDEV_CAMERAS")
    mats["tile"] = procedural_floor_tiles()
    room_shell(data,arch,mats)
    tables_and_chairs(data,furniture,furniture,mats)
    ceiling_items(data,ceiling,mats)
    hero_assets(data,equipment,mats)
    collection("50_DECOR")
    collection("60_INTERACTION_PROXY")
    collection("90_REFERENCE_LOCAL")
    camera_and_lights(data,lookdev)
    scene.render.resolution_x=1280; scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.world.color=(.18,.18,.18)
    blend_path=args.output_dir/"P507_G1_G2_PROVISIONAL.blend"
    glb_path=args.output_dir/"P507_G1_G2_PROVISIONAL.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.object.select_all(action="DESELECT")
    export_count=0
    for c in (arch,furniture,equipment,ceiling):
        for o in c.objects:
            if o.type=="MESH":
                o.select_set(True); export_count+=1
    export_result = bpy.ops.export_scene.gltf(filepath=str(glb_path),export_format="GLB",
                              use_selection=True,export_yup=True,export_extras=True)
    if "FINISHED" not in export_result or not glb_path.is_file() or glb_path.stat().st_size < 1024:
        raise RuntimeError("glTF export failed, cancelled or produced no GLB. Do not claim PASS.")
    out={**result,"blender_version":bpy.app.version_string,"export_objects":export_count,
         "glb_path":str(glb_path),"blend_path":str(blend_path),
         "notice":"PROVISIONAL dev only. Not AIRC-verified, not licensed real assets; no photos included."}
    (args.output_dir/"report.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
