"""Independent conservative route and swept-component checks for the R5 proposal."""

from collections import deque
import math

from layout import AISLE_TARGET, PLAYER_HEIGHT, PLAYER_RADIUS, build_layout, chair_colliders

GRID = .05
COLUMN = .40
EPS = 1e-8


def bounds(proxy):
    xs, ys = zip(*proxy["polygon"])
    return (min(xs), min(ys), max(xs), max(ys))


def union_bounds(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def boxes_overlap(a, b):
    return min(a[2], b[2])-max(a[0], b[0]) > EPS and min(a[3], b[3])-max(a[1], b[1]) > EPS


def point_distance(point, box):
    x, y = point
    x0, y0, x1, y1 = box
    return math.hypot(max(x0-x, x-x1, 0), max(y0-y, y-y1, 0))


def point_segment_distance(point, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    magnitude = dx*dx + dy*dy
    t = 0 if magnitude < EPS else max(0, min(1, ((point[0]-a[0])*dx + (point[1]-a[1])*dy) / magnitude))
    return math.hypot(point[0]-a[0]-t*dx, point[1]-a[1]-t*dy)


def crosses_box(a, b, box):
    low, high = 0., 1.
    for axis in (0, 1):
        move = b[axis]-a[axis]
        if abs(move) < EPS:
            if not box[axis] <= a[axis] <= box[axis+2]:
                return False
            continue
        first, last = sorted(((box[axis]-a[axis])/move, (box[axis+2]-a[axis])/move))
        low, high = max(low, first), min(high, last)
        if low > high:
            return False
    return True


def segment_distance(a, b, box):
    if crosses_box(a, b, box):
        return 0.
    x0, y0, x1, y1 = box
    return min(point_distance(a, box), point_distance(b, box),
               *(point_segment_distance(p, a, b) for p in [(x0,y0),(x0,y1),(x1,y0),(x1,y1)]))


class WalkSpace:
    """Every reported segment is collision-tested as a swept 0.30 m disk."""

    def __init__(self, layout, states):
        self.room = layout["walkable_rect"]
        self.obstacles = [
            (p["id"], bounds(p)) for p in (
                *layout["static_walk_colliders"],
                *(p for chair in layout["chairs"] for p in chair_colliders(chair, states[chair["id"]])),
            ) if p["bottom_z"] < PLAYER_HEIGHT - EPS and p["top_z"] > EPS
        ]
        self.buckets = {}
        self.occupied_cells = set()
        for id_, (x0, y0, x1, y1) in self.obstacles:
            for bucket in range(math.floor(x0/COLUMN), math.floor(x1/COLUMN)+1):
                self.buckets.setdefault(bucket, []).append((id_, (x0, y0, x1, y1)))
            for i in range(math.ceil((x0-PLAYER_RADIUS)/GRID), math.floor((x1+PLAYER_RADIUS)/GRID)+1):
                for j in range(math.ceil((y0-PLAYER_RADIUS)/GRID), math.floor((y1+PLAYER_RADIUS)/GRID)+1):
                    if point_distance((i*GRID, j*GRID), (x0,y0,x1,y1)) <= PLAYER_RADIUS + EPS:
                        self.occupied_cells.add((i,j))

    def block(self, a, b):
        x0,y0,x1,y1 = self.room
        for x, y in (a, b):
            if not (x0 + PLAYER_RADIUS <= x <= x1 - PLAYER_RADIUS and
                    y0 + PLAYER_RADIUS <= y <= y1 - PLAYER_RADIUS):
                return "room boundary"
        path_box = (min(a[0],b[0])-PLAYER_RADIUS, min(a[1],b[1])-PLAYER_RADIUS,
                    max(a[0],b[0])+PLAYER_RADIUS, max(a[1],b[1])+PLAYER_RADIUS)
        px0, py0, px1, py1 = path_box
        for bucket in range(math.floor((px0-EPS)/COLUMN), math.floor((px1+EPS)/COLUMN)+1):
            for id_, box in self.buckets.get(bucket, ()):
                x0, y0, x1, y1 = box
                potentially_touching = (
                    px0 <= x1 + EPS and x0 <= px1 + EPS and py0 <= y1 + EPS and y0 <= py1 + EPS
                )
                if potentially_touching and segment_distance(a, b, box) <= PLAYER_RADIUS + EPS:
                    return id_
        return None

    def roots(self, point):
        i, j = round(point[0]/GRID), round(point[1]/GRID)
        for u in range(i-2, i+3):
            for v in range(j-2, j+3):
                if (u,v) not in self.occupied_cells and not self.block(point,(u*GRID,v*GRID)):
                    yield u,v

    def flood(self, start):
        x0,y0,x1,y1 = self.room
        limits = (math.ceil((x0+PLAYER_RADIUS)/GRID), math.ceil((y0+PLAYER_RADIUS)/GRID),
                  math.floor((x1-PLAYER_RADIUS)/GRID), math.floor((y1-PLAYER_RADIUS)/GRID))
        parents = {cell: None for cell in self.roots(start)}
        queue = deque(parents)
        while queue:
            i,j = cell = queue.popleft()
            for u,v in ((i+1,j), (i-1,j), (i,j+1), (i,j-1)):
                if (u,v) in parents or (u,v) in self.occupied_cells:
                    continue
                if not (limits[0] <= u <= limits[2] and limits[1] <= v <= limits[3]):
                    continue
                if self.block((i*GRID,j*GRID),(u*GRID,v*GRID)):
                    continue
                parents[(u,v)] = cell
                queue.append((u,v))
        return parents

    def route(self, start, target, parents):
        for cell in self.roots(target):
            if cell in parents:
                path = [target]
                while cell is not None:
                    path.append((cell[0]*GRID, cell[1]*GRID))
                    cell = parents[cell]
                path.append(start)
                return list(reversed(path))
        return None


def aisle_widths(layout, states):
    edges = {cluster: [] for cluster in "ABC"}
    for proxy in layout["static_walk_colliders"]:
        if proxy.get("cluster") in edges:
            edges[proxy["cluster"]].append((proxy["id"], bounds(proxy)))
    for chair in layout["chairs"]:
        for part in chair_colliders(chair, states[chair["id"]]):
            edges[chair["cluster"]].append((chair["id"], bounds(part)))
    result = {}
    for north, south in ("AB", "BC"):
        north_id, north_box = min(edges[north], key=lambda edge: edge[1][1])
        south_id, south_box = max(edges[south], key=lambda edge: edge[1][3])
        # The extrema over entire clusters bound every X, including unequal extents.
        result[north+"-"+south] = {
            "width_m": round(north_box[1] - south_box[3], 6),
            "north_edge": {"id": north_id, "y_m": north_box[1]},
            "south_edge": {"id": south_id, "y_m": south_box[3]},
        }
    return result


def swept_components(layout):
    errors = []
    room = layout["walkable_rect"]
    chair_sweeps = []
    occupants = []
    for chair in layout["chairs"]:
        physical_occupied = list(chair_colliders(chair, "occupied", physical=True))
        body = physical_occupied[len(chair["components"]):]
        for part in body:
            body_box = bounds(part)
            occupants.append((part, body_box))
            for obstacle in (*layout["static_interaction_colliders"], *physical_occupied[:len(chair["components"])]):
                overlap_z = min(part["top_z"], obstacle["top_z"])-max(part["bottom_z"], obstacle["bottom_z"])
                if overlap_z > EPS and boxes_overlap(body_box, bounds(obstacle)):
                    errors.append((chair["id"], part["name"], obstacle["id"], obstacle.get("name")))
        initial = chair_colliders(chair, "stored", physical=True)
        final = chair_colliders(chair, "pulled", physical=True)
        for a, b in zip(initial, final, strict=True):
            sweep = union_bounds(bounds(a), bounds(b))
            chair_sweeps.append((a, sweep))
            if any((sweep[0] < room[0]-EPS, sweep[1] < room[1]-EPS,
                    sweep[2] > room[2]+EPS, sweep[3] > room[3]+EPS)):
                errors.append((chair["id"], a["name"], "room boundary"))
            for obstacle in layout["static_interaction_colliders"]:
                overlap_z = min(a["top_z"], obstacle["top_z"])-max(a["bottom_z"], obstacle["bottom_z"])
                if overlap_z > EPS and boxes_overlap(sweep, bounds(obstacle)):
                    errors.append((chair["id"], a["name"], obstacle["id"], obstacle.get("name")))
    for part, body_box in occupants:
        for other, other_box in chair_sweeps:
            if part["id"] != other["id"]:
                overlap_z = min(part["top_z"], other["top_z"])-max(part["bottom_z"], other["bottom_z"])
                if overlap_z > EPS and boxes_overlap(body_box, other_box):
                    errors.append((part["id"], part["name"], other["id"], other["name"]))
    for i, (part, sweep) in enumerate(chair_sweeps):
        for other, other_sweep in chair_sweeps[i+1:]:
            if part["id"] == other["id"]:
                continue
            overlap_z = min(part["top_z"], other["top_z"])-max(part["bottom_z"], other["bottom_z"])
            if overlap_z > EPS and boxes_overlap(sweep, other_sweep):
                errors.append((part["id"], part["name"], other["id"], other["name"]))
    return errors


def check_routes(layout):
    spawn = tuple(layout["spawn"][:2])
    chairs = layout["chairs"]
    states = {
        "stored": {c["id"]: "stored" for c in chairs},
        "pulled": {c["id"]: "pulled" for c in chairs},
        "occupied": {c["id"]: "occupied" for c in chairs},
        "mixed": {c["id"]: ("pulled" if i % 2 else "stored") for i,c in enumerate(chairs)},
        "end-occupied": {c["id"]: ("occupied" if c["id"].endswith(("-01", "-07")) else "pulled")
                         for c in chairs},
    }
    report = {"aisles": {}, "unreachable": [], "routes": {}, "component_errors": swept_components(layout)}
    report["facilities"] = {}
    facilities = {
        "door": (.40, spawn[1]),
        "shelf": (.94, sum(
            proxy["polygon"][i][1] / 2
            for proxy in layout["static_walk_colliders"] if proxy["id"] == "P507-UTILITY-SHELF"
            for i in (0, 2)
        )),
        "display-case": (1.11, layout["walkable_rect"][3] - .43),
    }
    for name, state in states.items():
        report["aisles"][name] = aisle_widths(layout, state)
        scenario = WalkSpace(layout, state)
        parents = scenario.flood(spawn)
        paths = {}
        if name != "occupied":
            for chair in chairs:
                pose = state[chair["id"]]
                if pose == "occupied":
                    continue
                targets = ([chair["approach"], *chair["approach_alternatives"]]
                           if pose == "stored" else [chair["stand"]])
                target = tuple(targets[0][:2])
                path = next((path for candidate in targets
                             if (path := scenario.route(spawn, tuple(candidate[:2]), parents))), None)
                if path is None:
                    report["unreachable"].append((name,chair["id"],scenario.block(target,target)))
                else:
                    paths[chair["id"]] = path
        for aisle, edges in report["aisles"][name].items():
            y = (edges["north_edge"]["y_m"] + edges["south_edge"]["y_m"])/2
            a,b = (1.1,y),(layout["walkable_rect"][2]-.4,y)
            path = scenario.route(spawn, a, parents)
            blocked = scenario.block(a,b)
            if path is None or blocked:
                report["unreachable"].append((name,aisle,blocked))
            else:
                paths[aisle] = [*path,b]
        report["routes"][name] = paths
        report["facilities"][name] = {}
        for place, target in facilities.items():
            path = scenario.route(spawn, target, parents)
            if path is None:
                report["unreachable"].append((name, place, scenario.block(target, target)))
            else:
                report["facilities"][name][place] = path
    report["routes"]["individual-pull"] = {}
    for chair in chairs:
        id_ = chair["id"]
        before = report["routes"]["stored"].get(id_)
        if before is None:
            continue
        scenario = WalkSpace(layout, {**states["stored"], id_: "pulled"})
        start = before[-1]
        target = tuple(chair["stand"][:2])
        route = scenario.route(start, target, scenario.flood(start))
        if route is None:
            report["unreachable"].append(("individual-pull", id_, scenario.block(start, start)))
        else:
            report["routes"]["individual-pull"][id_] = route
    return report


if __name__ == "__main__":
    import json

    layout = build_layout()
    report = check_routes(layout)
    print(json.dumps({**report, "routes": {name: len(routes) for name,routes in report["routes"].items()}}, indent=2))
    target_met = all(aisle["width_m"] >= AISLE_TARGET for aisle in report["aisles"]["occupied"].values())
    raise SystemExit(not target_met or bool(report["unreachable"] or report["component_errors"]))
