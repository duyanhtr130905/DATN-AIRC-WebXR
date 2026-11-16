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
            seam = x < 2 or y < 2
            variation = rng.uniform(-.013, .013)
            base = (.57,.58,.57) if seam else (.79,.80,.78)
            pixels.extend((base[0]+variation,base[1]+variation,base[2]+variation,1.0))
    image.pixels.foreach_set(pixels)
    image.pack()
    shader = mat.node_tree.nodes.get("Principled BSDF")
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "REPEAT"
    mat.node_tree.links.new(tex.outputs["Color"],shader.inputs["Base Color"])
    return mat


def procedural_wood():
    mat=material("P507_PBR_SELF_AUTHORED_PALE_OAK",(.68,.55,.39),.55)
    image=bpy.data.images.new("P507_SELF_GENERATED_OAK_GRAIN",width=256,height=256,alpha=True)
    pixels=[]
    for y in range(256):
        for x in range(256):
            grain=.020*math.sin(x*.37+math.sin(y*.025)*2)+.008*math.sin(x*1.3+y*.03)
            pixels.extend((.69+grain,.58+grain,.43+grain,1))
    image.pixels.foreach_set(pixels); image.pack()
    tex=mat.node_tree.nodes.new("ShaderNodeTexImage"); tex.image=image
    mat.node_tree.links.new(tex.outputs["Color"],mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
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
    floor["chair_inventory_count"]=data["chairs"]["count"]
    floor["chair_placed_count"]=sum(c["status"]=="PLACED_PROVISIONAL" for c in data["chairs"]["instances"])
    floor["unplaced_chair_ids"]=json.dumps([c["id"] for c in data["chairs"]["instances"] if c["status"]=="UNPLACED"])
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
        roller = cylinder("P507_ARCH_BLIND_ROLLER_%02d" % idx,(w-.07,center_y,3.01),.035,
                 win["to_y"]-win["from_y"],mats["white_metal"],col)
        roller.rotation_euler.x = math.pi/2
    cube("P507_ARCH_BASEBOARD_LOGO",(w/2,.075,.07),(w,.03,.14),mats["white_metal"],col,.004)
    cube("P507_ARCH_BASEBOARD_EAST",(w-.07,length/2,.07),(.03,length,.14),mats["white_metal"],col,.004)
    cube("P507_ARCH_DOOR_FRAME_LOW",(0,door["from_y"],door["height"]/2),
         (.14,.06,door["height"]),mats["white_metal"],col,.008)
    cube("P507_ARCH_DOOR_FRAME_HIGH",(0,door["to_y"],door["height"]/2),
         (.14,.06,door["height"]),mats["white_metal"],col,.008)
    cube("P507_ARCH_DOOR_FRAME_LINTEL",(0,(door["from_y"]+door["to_y"])/2,door["height"]),
         (.18,door["to_y"]-door["from_y"]+.06,.07),mats["white_metal"],col,.009)
    for yy in (door["from_y"]-.035,door["to_y"]+.035):
        cube("P507_ARCH_DOOR_REVEAL",(-.055,yy,door["height"]/2),(.25,.035,door["height"]),mats["wood"],col,.005)
    # Door leaf count and swing are UNKNOWN: retain open portal, never invent surveyed leaves.
    # Ceiling tiles are lightweight geometry; no photographic or confidential texture.
    cube("P507_ARCH_CEILING", (w/2, length/2, height+.025), (w, length, .05), mats["ceiling"], col)
    for x in range(1, 10):
        cube("P507_ARCH_CEILING_GRID_X_%02d" % x, (x*.6, length/2, height-.015),
             (.012, length, .012), mats["white_metal"], col)
    for row in range(1, 14):
        cube("P507_ARCH_CEILING_GRID_Y_%02d" % row, (w/2, row*.6, height-.015),
             (w, .012, .012), mats["white_metal"], col)


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
    delta = Vector(end)-Vector(start)
    obj = cylinder(name, (Vector(start)+Vector(end))/2, radius, delta.length, mat, col, 12)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def chair_module(col, mats):
    parts = [cube("CHAIR_SEAT", (0,0,.475), (.44,.43,.065), mats["chair"], col, .045)]
    # Closed, gently curved moulded back; edges curl towards the sitter.
    vertices=[]
    segments=12
    for layer in (-.014,.014):
        for z in (.62,1.0):
            for i in range(segments+1):
                x=-.215+.43*i/segments
                y=-.245+.052*(x/.215)**2+layer
                vertices.append((x,y,z))
    n=segments+1
    faces=[]
    for i in range(segments):
        faces.extend([(i,i+1,n+i+1,n+i),
                      (2*n+i,3*n+i,3*n+i+1,2*n+i+1),
                      (i,2*n+i,2*n+i+1,i+1),
                      (n+i,n+i+1,3*n+i+1,3*n+i)])
    faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
    mesh=bpy.data.meshes.new("P507_CURVED_BACK_MODULE")
    mesh.from_pydata(vertices,[],faces); mesh.update()
    back=bpy.data.objects.new("CHAIR_CURVED_BACK",mesh); col.objects.link(back)
    mesh.materials.append(mats["chair"])
    for f in mesh.polygons: f.use_smooth=True
    bevel=back.modifiers.new("Moulded perimeter relief","BEVEL"); bevel.width=.009; bevel.segments=3
    back.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    parts.append(back)
    for x in (-.175,.175):
        for y in (-.165,.165):
            parts.append(tube("CHAIR_TUBULAR_LEG",(x*1.12,y*1.12,.022),(x,y,.45),.012,mats["metal"],col))
            parts.append(cylinder("CHAIR_RUBBER_FOOT",(x*1.12,y*1.12,.015),.017,.03,mats["chair"],col,12))
        parts.append(tube("CHAIR_BACK_SUPPORT",(x,-.17,.39),(x,-.225,.85),.011,mats["metal"],col))
        parts.append(tube("CHAIR_SIDE_RAIL",(x,-.17,.425),(x,.17,.425),.012,mats["metal"],col))
    obj=combine(parts,"P507_CHAIR_MODULE",col)
    # Put local origin at floor centre before creating linked instances.
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return obj


def tables_and_chairs(data, tables_col, chairs_col, mats):
    for item in data["objects"]:
        xmin,ymin,xmax,ymax=item["rect"]
        cx,cy,sx,sy=(xmin+xmax)/2,(ymin+ymax)/2,xmax-xmin,ymax-ymin
        ident=item["id"]; name=ident.replace("-","_"); h=item["height"]
        if item.get("type") not in ("table_standard","table_small"):
            cube(name+"_UNVERIFIED_PLACEHOLDER",(cx,cy,item.get("bottom_z",0)+h/2),(sx,sy,h),mats["cabinet"],tables_col,.01,ident)
            continue
        parts=[cube(name+"_LAMINATE_TOP",(cx,cy,h-.025),(sx,sy,.05),mats["laminate"],tables_col,.012)]
        for ix in (-1,1):
            for iy in (-1,1):
                x=cx+ix*(sx/2-.065); y=cy+iy*(sy/2-.065)
                parts.append(cube(name+"_STEEL_LEG",(x,y,(h-.05)/2),(.039,.039,h-.05),mats["metal"],tables_col,.004))
                parts.append(cube(name+"_FOOT",(x,y,.012),(.045,.045,.024),mats["chair"],tables_col,.005))
        for iy in (-1,1):
            parts.append(cube(name+"_APRON_X",(cx,cy+iy*(sy/2-.065),h-.10),(sx-.10,.029,.065),mats["metal"],tables_col,.004))
        for ix in (-1,1):
            parts.append(cube(name+"_APRON_Y",(cx+ix*(sx/2-.065),cy,h-.10),(.029,sy-.10,.065),mats["metal"],tables_col,.004))
        combine(parts,name+"_ASSEMBLY",tables_col,ident)
    module=None
    for item in data["chairs"]["instances"]:
        if item["status"] != "PLACED_PROVISIONAL":
            continue
        if module is None:
            module=chair_module(chairs_col,mats)
            obj=module
        else:
            obj=bpy.data.objects.new(item["id"],module.data)
            chairs_col.objects.link(obj)
        obj.name=item["id"]
        obj.location=(*item["center"],0)
        obj.rotation_euler.z=math.radians(item["orientation_deg"])
        obj["survey_instance_id"]=item["id"]
        obj["source_class"]=item["source_kind"]
        obj["placement_status"]=item["status"]
        obj["cluster"]=item["cluster"]
        obj["placement_role"]=item.get("placement_role","row")


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


def lathe(name, center, profile, mat, col, segments=48, ident=None):
    """Closed turned surface, profile ordered bottom to top (radius, height)."""
    vertices=[]
    for radius,z in profile:
        for i in range(segments):
            t=2*math.pi*i/segments
            vertices.append((center[0]+radius*math.cos(t),center[1]+radius*math.sin(t),z))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):
            ni=(i+1)%segments
            faces.append((j*segments+i,j*segments+ni,(j+1)*segments+ni,(j+1)*segments+i))
    faces.extend([tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))])
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(vertices,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj); mesh.materials.append(mat)
    for f in mesh.polygons: f.use_smooth=len(f.vertices)==4
    if ident: obj["survey_instance_id"]=ident; obj["source_class"]="PROPOSED_LAYOUT"
    return obj


def hero_assets(data, col, mats):
    tv=data["hero"]["tv"]; x=tv["center_x"]; z=tv["center_z"]
    y=data["room"]["length_y"]-.115; ident="P507-TV-LARGE"
    cube("P507_HERO_TV_MOUNT",(x,y+.025,z),(.30,.10,.22),mats["metal"],col,.009,ident)
    cube("P507_HERO_TV_REAR",(x,y,z),(tv["width"]-.06,.075,tv["height"]-.055),mats["screen_frame"],col,.028,ident)
    cube("P507_HERO_TV_BEZEL",(x,y-.035,z),(tv["width"],.027,tv["height"]),mats["screen_frame"],col,.018,ident)
    cube("P507_HERO_TV_BLACK_SCREEN",(x,y-.051,z+.006),(tv["width"]-.035,.008,tv["height"]-.044),mats["screen"],col,.01,ident)
    cube("P507_HERO_TV_POWER_LED",(x+.65,y-.057,z-tv["height"]/2+.015),(.009,.004,.003),mats["indicator"],col,.001,ident)

    cabinet=data["hero"]["cabinet"]
    cx,cy,cz=cabinet["center"]; sx,sy,sz=cabinet["size"]; ident="P507-CABINET-LOW"
    # Plinth touches floor; front details stay inside the validated occupancy envelope.
    cube("P507_HERO_CABINET_RECESSED_PLINTH",(cx,cy,.045),(sx-.10,sy-.08,.09),mats["frame_wood"],col,.009,ident)
    cube("P507_HERO_CABINET_CARCASS",(cx,cy,(sz+.09)/2),(sx,sy,sz-.09),mats["wood"],col,.012,ident)
    cube("P507_HERO_CABINET_COUNTER",(cx,cy,sz+.018),(sx+.02,sy+.02,.036),mats["laminate"],col,.009,ident)
    for i in range(3):
        xx=cx-sx/2+(i+.5)*sx/3
        cube(f"P507_HERO_CABINET_DOOR_{i}",(xx,cy-sy/2-.011,(sz+.10)/2),(sx/3-.012,.022,sz-.13),mats["cabinet"],col,.006,ident)
        for dx in (-.035,.035):
            cube("P507_HERO_CABINET_PULL_STANDOFF",(xx+dx,cy-sy/2-.026,sz-.12),(.009,.018,.009),mats["metal"],col,.003,ident)
        cube("P507_HERO_CABINET_PULL",(xx,cy-sy/2-.033,sz-.12),(.09,.009,.012),mats["metal"],col,.004,ident)
    for i in range(3):
        xx=cx+(i-1)*.41
        cube(f"P507_HERO_NEUTRAL_DISPLAY_BASE_{i}",(xx,cy,sz+.052),(.18,.12,.03),mats["screen_frame"],col,.008)
        award=cube(f"P507_HERO_NEUTRAL_DISPLAY_{i}",(xx,cy,sz+.20),(.145,.024,.26),mats["gold"],col,.015)
        award.rotation_euler.y=(i-1)*.12
        award["support_relation"]="P507-CABINET-LOW"

    # Self-authored neutral panels preserve only approximate wall dressing classes.
    frame_layout=[(2.9,2.25,.42,.28),(3.35,2.58,.46,.31),(3.9,2.18,.52,.33),
                  (4.55,2.63,.45,.30),(5.15,2.36,.54,.33),(3.05,1.80,.38,.27),
                  (3.78,2.92,.46,.28),(4.8,1.91,.47,.29)]
    for i,(xx,zz,ww,hh) in enumerate(frame_layout):
        cube(f"P507_HERO_FRAME_NEUTRAL_{i}",(xx,8.00,zz),(ww,.038,hh),mats["frame_wood"],col,.006)
        cube(f"P507_HERO_ABSTRACT_NO_IDENTITIES_{i}",(xx,7.976,zz),(ww-.04,.008,hh-.04),mats["abstract"][i%3],col,.002)

    water=data["hero"]["water_dispenser"]; px,py,_=water["center"]; ident="P507-WATER-DISPENSER"
    cube("P507_HERO_WATER_FOOT",(px,py,.035),(.36,.38,.07),mats["screen_frame"],col,.018,ident)
    cube("P507_HERO_WATER_BODY",(px,py,.48),(.39,.40,.89),mats["white_metal"],col,.035,ident)
    cube("P507_HERO_WATER_FRONT_LOWER",(px,py-.205,.27),(.335,.020,.39),mats["cabinet"],col,.018,ident)
    # Recess is a dark cavity bounded by raised side cheeks rather than a decal.
    cube("P507_HERO_WATER_RECESS",(px,py-.211,.655),(.285,.012,.28),mats["screen_frame"],col,.022,ident)
    for dx in (-.16,.16):
        cube("P507_HERO_WATER_CHEEK",(px+dx,py-.215,.665),(.035,.045,.31),mats["white_metal"],col,.012,ident)
    cube("P507_HERO_WATER_CONTROL",(px,py-.217,.865),(.29,.027,.09),mats["screen_frame"],col,.012,ident)
    for dx,mat in ((-.065,mats["hot"]),(.065,mats["blue_water"])):
        cube("P507_HERO_WATER_TAP",(px+dx,py-.230,.735),(.034,.038,.033),mat,col,.008,ident)
        cube("P507_HERO_WATER_BUTTON",(px+dx,py-.235,.87),(.038,.006,.018),mat,col,.007,ident)
    cube("P507_HERO_WATER_DRIP_TRAY",(px,py-.218,.515),(.28,.035,.026),mats["metal"],col,.008,ident)
    for i in range(7):
        cube("P507_HERO_WATER_TRAY_SLOT",(px-.11+i*.036,py-.239,.518),(.009,.007,.005),mats["screen_frame"],col,.002,ident)
    cylinder("P507_HERO_WATER_COLLAR",(px,py,.955),.10,.07,mats["screen_frame"],col,32,ident)
    lathe("P507_HERO_WATER_BOTTLE",(px,py),[(.055,.97),(.055,1.025),(.08,1.06),(.145,1.10),(.173,1.16),(.173,1.40),(.16,1.46),(.12,1.49),(.025,1.50)],mats["bottle"],col,48,ident)
    for zz in (1.18,1.23,1.36,1.40):
        lathe("P507_HERO_WATER_BOTTLE_RIB",(px,py),[(.173,zz-.008),(.179,zz),(.173,zz+.008)],mats["bottle"],col,48,ident)
    cube("P507_HERO_NORTH_SKIRTING",(3,8.025,.055),(6,.026,.11),mats["white_metal"],col,.005)


def camera_and_lights(data, camera_col):
    length=data["room"]["length_y"]
    bpy.ops.object.camera_add(location=(1.1,5.15,1.65))
    cam=bpy.context.object; cam.name="CAM_TV_ART_APPROX"; move_to_collection(cam,camera_col)
    target = (.98,length-.25,1.55)
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
        obj.rotation_euler=(Vector((2.5,5.5,.3))-obj.location).to_track_quat("-Z","Y").to_euler()


def validate_authored_bounds(data, collections):
    """Measure evaluated Blender vertices, independently of the input proxy report."""
    from mathutils import Vector
    deps=bpy.context.evaluated_depsgraph_get()
    measured={}
    for col in collections:
        for obj in col.objects:
            ident=obj.get("survey_instance_id")
            if obj.type!="MESH" or not ident: continue
            evaluated=obj.evaluated_get(deps)
            for corner in evaluated.bound_box:
                v=evaluated.matrix_world @ Vector(corner)
                if ident not in measured: measured[ident]=[v.x,v.y,v.z,v.x,v.y,v.z]
                else:
                    b=measured[ident]
                    measured[ident]=[min(b[0],v.x),min(b[1],v.y),min(b[2],v.z),max(b[3],v.x),max(b[4],v.y),max(b[5],v.z)]
    expected={p["id"]:p for p in verify(data)["occupancy"]}
    for ident,proxy in expected.items():
        if ident not in measured: raise RuntimeError("Missing authored geometry: "+ident)
        b=measured[ident]; pts=proxy["polygon"]
        limits=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
        if b[0]<limits[0]-.001 or b[1]<limits[1]-.001 or b[3]>limits[2]+.001 or b[4]>limits[3]+.001:
            raise RuntimeError("Authored geometry exceeds validated proxy: "+ident+str(b)+str(limits))
        if b[2]<-.001: raise RuntimeError("Furniture below floor: "+ident)
        if proxy.get("bottom_z") is not None and abs(b[2]-proxy["bottom_z"])>.001:
            raise RuntimeError("Authored support height mismatch: "+ident)
    return measured


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
    scene.render.film_transparent=False
    bpy.context.preferences.filepaths.save_version=0
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
    screen=mats["screen"].node_tree.nodes.get("Principled BSDF")
    screen.inputs["Roughness"].default_value=.32
    screen.inputs["Specular IOR Level" if "Specular IOR Level" in screen.inputs else "Specular"].default_value=.06
    glass=mats["glass"].node_tree.nodes.get("Principled BSDF")
    glass.inputs["Alpha"].default_value=.16
    if hasattr(mats["glass"],"surface_render_method"):
        mats["glass"].surface_render_method="DITHERED"
    else:
        mats["glass"].blend_method="BLEND"
    arch=collection("10_ARCH"); furniture=collection("20_FURNITURE")
    equipment=collection("30_EQUIPMENT"); ceiling=collection("40_CEILING")
    lookdev=collection("80_LOOKDEV_CAMERAS")
    mats["tile"] = procedural_floor_tiles()
    mats["wood"]=procedural_wood()
    mats["indicator"]=material("P507_TV_STANDBY",(.09,.16,.12),.3,emission=.3)
    mats["hot"]=material("P507_WATER_RED_BUTTON",(.32,.025,.02),.4)
    mats["bottle"]=material("P507_PBR_TRANSLUCENT_BLUE_PET",(.20,.48,.67),.17)
    bottle=mats["bottle"].node_tree.nodes.get("Principled BSDF")
    bottle.inputs["Transmission Weight" if "Transmission Weight" in bottle.inputs else "Transmission"].default_value=.58
    bottle.inputs["IOR"].default_value=1.46
    room_shell(data,arch,mats)
    floor=bpy.data.objects.get("P507_ARCH_FLOOR")
    floor["chair_inventory_count"]=data["chairs"]["count"]
    floor["chair_placed_count"]=sum(c["status"]=="PLACED_PROVISIONAL" for c in data["chairs"]["instances"])
    floor["unplaced_chair_ids"]=json.dumps([c["id"] for c in data["chairs"]["instances"] if c["status"]=="UNPLACED"])
    tables_and_chairs(data,furniture,furniture,mats)
    ceiling_items(data,ceiling,mats)
    hero_assets(data,equipment,mats)
    collection("50_DECOR")
    collection("60_INTERACTION_PROXY")
    collection("90_REFERENCE_LOCAL")
    grids=[o for o in arch.objects if o.name.startswith("P507_ARCH_CEILING_GRID")]
    if grids: combine(grids,"P507_ARCH_CEILING_GRID",arch)
    camera_and_lights(data,lookdev)
    scene.render.resolution_x=1280; scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.world.color=(.18,.18,.18)
    authored_bounds=validate_authored_bounds(data,(furniture,equipment))
    door=data["openings"]["door"]
    for obj in arch.objects:
        if obj.name.startswith("P507_ARCH_WALL_WEST"):
            ys=[(obj.matrix_world @ __import__("mathutils").Vector(v)).y for v in obj.bound_box]
            if min(max(ys),door["to_y"])-max(min(ys),door["from_y"])>.001:
                raise RuntimeError("West wall blocks intended door opening")
    import hashlib, subprocess, os
    source_sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=HERE,text=True).strip()
    input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),HERE/"geometry.py",args.inventory)}
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
         "authored_bounds":authored_bounds,"checkout_sha":source_sha,"source_sha":os.environ.get("GITHUB_HEAD_SHA",source_sha),"input_sha256":input_hashes,
         "glb_bytes":glb_path.stat().st_size,"glb_sha256":hashlib.sha256(glb_path.read_bytes()).hexdigest(),
         "embedded_images":[i.name for i in bpy.data.images if i.packed_file],
         "glb_path":str(glb_path),"blend_path":str(blend_path),
         "notice":"PROVISIONAL dev only. Not AIRC-verified, not licensed real assets; no photos included."}
    (args.output_dir/"report.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
