import { PLAYER, sweptCircle, type Point } from "../p507-e1/core.ts";

export type XYZ = [number, number, number];
export type Part = { min: XYZ; max: XYZ };
export type SurveyCollider = { id: string; polygon: Point[]; bottom_z: number; top_z: number };
export type Chair = {
    id: string; desk_id: string; orientation_deg: number;
    stored: XYZ; pulled: XYZ; seat_eye: XYZ; stand: XYZ;
    approach?: XYZ; approach_alternatives?: XYZ[]; components: Part[]; occupied_components: Part[];
};
export type Layout = {
    chairs: Chair[];
    walkable_rect: [number, number, number, number];
    static_walk_colliders: SurveyCollider[];
    static_interaction_colliders: SurveyCollider[];
};
export type ChairState = "stored" | "pulled-out" | "occupied";
export type Action = "pull" | "store" | "sit" | "stand";
export type Actor = { mode: "web" | "vr" | "ar"; position: Point };
export const labels: Record<Action, string> = {
    pull: "Kéo ghế ra", store: "Cất ghế", sit: "Ngồi xuống", stand: "Đứng dậy",
};
const animationSeconds = 0.32;
const areaEpsilon = 1e-7;
const toThree = ([x, y]: Point | XYZ): Point => [x, -y];
const toSurvey = ([x, z]: Point): Point => [x, -z];
const add = ([x, y]: Point, [u, v]: Point): Point => [x + u, y + v];
const sub = ([x, y]: Point, [u, v]: Point): Point => [x - u, y - v];
const cross = ([x, y]: Point, [u, v]: Point) => x * v - y * u;
const distance = (a: Point, b: Point) => Math.hypot(...sub(a, b));
const flat = ([x, y]: XYZ): Point => [x, y];

function hull(points: Point[]): Point[] {
    const sorted = points.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    function half(order: Point[]) {
        const result: Point[] = [];
        for (const point of order) {
            while (result.length >= 2 && cross(sub(result.at(-1)!, result.at(-2)!), sub(point, result.at(-1)!)) <= 0) {
                result.pop();
            }
            result.push(point);
        }
        return result.slice(0, -1);
    }
    return half(sorted).concat(half(sorted.reverse()));
}

function overlaps(a: SurveyCollider, b: SurveyCollider) {
    if (Math.min(a.top_z, b.top_z) - Math.max(a.bottom_z, b.bottom_z) <= areaEpsilon) return false;
    return [a.polygon, b.polygon].every(polygon => polygon.every((p, i) => {
        const [x, y] = sub(polygon[(i + 1) % polygon.length], p);
        const length = Math.hypot(x, y);
        if (length < areaEpsilon) return true;
        const project = ([u, v]: Point) => (u * y - v * x) / length;
        const valuesA = a.polygon.map(project), valuesB = b.polygon.map(project);
        return Math.min(Math.max(...valuesA), Math.max(...valuesB)) -
            Math.max(Math.min(...valuesA), Math.min(...valuesB)) > areaEpsilon;
    }));
}

function partCollider(chair: Chair, { min, max }: Part, a: XYZ, b: XYZ = a): SurveyCollider {
    const angle = chair.orientation_deg * Math.PI / 180;
    const c = Math.cos(angle), s = Math.sin(angle);
    const outline: Point[] = [[min[0], min[1]], [max[0], min[1]], [max[0], max[1]], [min[0], max[1]]];
    const rotated = outline.map(([x, y]): Point => [c * x - s * y, s * x + c * y]);
    const start = rotated.map(p => add(p, flat(a)));
    const swept = a === b ? start : hull(start.concat(rotated.map(p => add(p, flat(b)))));
    return { id: chair.id, polygon: swept, bottom_z: Math.min(a[2], b[2]) + min[2], top_z: Math.max(a[2], b[2]) + max[2] };
}

type Entry = { chair: Chair; state: ChairState; offset: number };
type Transition = { entry: Entry; from: number; to: number; elapsed: number };
export class ChairRoom {
    readonly spawn: Point;
    readonly layout: Layout;
    readonly entries: Map<string, Entry>;
    private transition?: Transition;
    private actorSeat?: Entry;
    private readonly staticWalk: SurveyCollider[];
    private readonly update: () => void;
    constructor(layout: Layout, spawn: XYZ, update: () => void = () => {}) {
        this.layout = layout;
        this.spawn = toThree(spawn);
        this.update = update;
        this.entries = new Map(layout.chairs.map(chair => [chair.id, { chair, state: "stored", offset: 0 }]));
        this.staticWalk = layout.static_walk_colliders.filter(p => p.bottom_z < PLAYER.height && p.top_z > 0);
    }

    actions(id: string, mode: Actor["mode"]): Action[] {
        switch (this.entries.get(id)?.state) {
            case "stored": return ["pull"];
            case "pulled-out": return mode === "ar" ? ["store"] : ["sit", "store"];
            case "occupied": return this.actorSeat?.chair.id === id && mode !== "ar" ? ["stand"] : [];
            default: return [];
        }
    }

    get seat() { return this.actorSeat?.chair; }
    get moving() { return this.transition?.entry.chair.id; }
    state(id: string) { return this.entries.get(id)?.state; }
    get chairIDs() { return this.entries.keys(); }
    reset() {
        this.transition = undefined;
        this.actorSeat = undefined;
        for (const entry of this.entries.values()) {
            entry.state = "stored";
            entry.offset = 0;
        }
        this.update();
    }
    interrupt() {
        if (!this.transition) return;
        this.transition.entry.offset = this.transition.from;
        this.transition = undefined;
        this.update();
    }

    pose(id: string): XYZ {
        const entry = this.entries.get(id)!;
        return this.interpolate(entry.chair, entry.offset);
    }
    private interpolate(chair: Chair, t: number): XYZ {
        const [x, y, z] = chair.stored;
        return [x + t * (chair.pulled[0] - x), y + t * (chair.pulled[1] - y), z + t * (chair.pulled[2] - z)];
    }

    tick(dt: number) {
        const transition = this.transition;
        if (!transition || !Number.isFinite(dt) || dt <= 0) return;
        transition.elapsed = Math.min(animationSeconds, transition.elapsed + Math.min(dt, 0.05));
        const t = transition.elapsed / animationSeconds;
        const eased = t * t * (3 - 2 * t);
        transition.entry.offset = transition.from + (transition.to - transition.from) * eased;
        if (t === 1) {
            transition.entry.state = transition.to === 1 ? "pulled-out" : "stored";
            this.transition = undefined;
            this.update();
        }
    }

    private pieces(entry: Entry, sweep: boolean, projectedState = entry.state) {
        const c = entry.chair;
        const a = this.pose(c.id);
        if (this.transition?.entry === entry && sweep) {
            const start = this.interpolate(c, this.transition.from);
            const finish = this.interpolate(c, this.transition.to);
            return c.components.map(part => partCollider(c, part, start, finish));
        }
        const parts = projectedState === "occupied" ? c.components.concat(c.occupied_components) : c.components;
        return parts.map(part => partCollider(c, part, a));
    }

    private inside(point: Point, radius: number) {
        const [xmin, ymin, xmax, ymax] = this.layout.walkable_rect;
        return point[0] > xmin + radius && point[0] < xmax - radius &&
            point[1] > ymin + radius && point[1] < ymax - radius;
    }

    private checkWalk(a: Point, b: Point, actorOccupant?: Entry) {
        if (![...a, ...b].every(Number.isFinite)) return "INVALID_POSITION";
        if (!this.inside(a, PLAYER.radius) || !this.inside(b, PLAYER.radius)) return "ROOM_BOUNDARY_OUTSIDE_UNSURVEYED";
        const collision = (p: SurveyCollider) => p.bottom_z < PLAYER.height && p.top_z > 0 &&
            sweptCircle(a, b, p.polygon, PLAYER.radius);
        for (const obstacle of this.staticWalk) if (collision(obstacle)) return obstacle.id;
        for (const [id, entry] of this.entries) {
            // Standing leaves the actor's own occupied envelope behind while the
            // chair remains a standing blocker at its actual pulled pose.
            const state = actorOccupant === entry ? "pulled-out" : entry.state;
            if (this.pieces(entry, true, state).some(collision)) return id;
        }
        return null;
    }

    blocked(a: Point, b: Point) { return this.checkWalk(toSurvey(a), toSurvey(b)); }
    move(a: Point, delta: Point) {
        const b = add(a, delta);
        const reason = this.seat ? "Đang ngồi" : this.blocked(a, b);
        return { position: reason ? a : b, reason };
    }

    private physicalBlock(volumes: SurveyCollider[], chair: Chair) {
        const [xmin, ymin, xmax, ymax] = this.layout.walkable_rect;
        for (const volume of volumes) {
            if (volume.polygon.some(([x, y]) => x < xmin || x > xmax || y < ymin || y > ymax) || volume.bottom_z < -areaEpsilon) {
                return "Vượt khỏi giới hạn phòng";
            }
            for (const obstacle of this.layout.static_interaction_colliders) if (overlaps(volume, obstacle)) return obstacle.id;
            for (const other of this.entries.values()) {
                if (other.chair.id !== chair.id && this.pieces(other, true).some(piece => overlaps(volume, piece))) return other.chair.id;
            }
        }
        return null;
    }

    action(id: string, action: Action, actor: Actor): string | null {
        if (this.transition) return "Đang di chuyển một ghế";
        const entry = this.entries.get(id);
        if (!entry || !this.actions(id, actor.mode).includes(action)) return "Thao tác không khả dụng";
        const chair = entry.chair, current = toSurvey(actor.position);
        if (![...current].every(Number.isFinite)) return "Vị trí không hợp lệ";
        if (action === "pull" || action === "store") {
            if (this.actorSeat && actor.mode !== "ar") return "Hãy đứng dậy trước";
            const a = action === "pull" ? chair.stored : chair.pulled;
            const b = action === "pull" ? chair.pulled : chair.stored;
            const anchors = [chair.approach, ...(chair.approach_alternatives ?? [])].filter(p => p !== undefined);
            const nearApproach = action === "pull" && anchors.some(p => distance(current, flat(p)) <= .18);
            if (actor.mode !== "ar" && !nearApproach && distance(current, flat(a)) > 1.2) return "Hãy tới gần ghế";
            const volumes = chair.components.map(part => partCollider(chair, part, a, b));
            const obstacle = this.physicalBlock(volumes, chair);
            if (obstacle) return "Ghế bị cản bởi " + obstacle;
            if (actor.mode !== "ar" && volumes.some(v => v.bottom_z < PLAYER.height && v.top_z > 0 &&
                sweptCircle(current, current, v.polygon, PLAYER.radius))) return "Hãy rời vùng di chuyển của ghế";
            this.transition = { entry, from: entry.offset, to: action === "pull" ? 1 : 0, elapsed: 0 };
        } else {
            if (action === "sit" && this.actorSeat) return "Đang ngồi ở ghế khác";
            const stand = flat(chair.stand);
            if (action === "sit" && (distance(current, stand) > .25 || this.checkWalk(current, stand))) {
                return "Hãy tới điểm tiếp cận phía trước ghế";
            }
            const blocker = this.checkWalk(stand, stand, action === "stand" ? entry : undefined);
            if (blocker) return "Vùng đứng bị cản bởi " + blocker;
            const occupied = chair.occupied_components.map(part => partCollider(chair, part, chair.pulled));
            const obstacle = this.physicalBlock(occupied, chair);
            if (obstacle) return "Vùng ngồi bị cản bởi " + obstacle;
            // During the seat action only, the actor's own chair is traversable. The
            // lower legs may reach below the desk, so check a smaller upper-body sweep
            // at the surveyed eye/shoulder height and keep the full capsule at stand.
            for (const p of this.layout.static_interaction_colliders) {
                if (p.bottom_z < 1.8 && p.top_z > Math.min(chair.seat_eye[2] - .32, 1.1) &&
                    sweptCircle(stand, flat(chair.seat_eye), p.polygon, .24)) return "Vùng chuyển tiếp bị cản bởi " + p.id;
            }
            for (const other of this.entries.values()) {
                if (other === entry) continue;
                if (this.pieces(other, true).some(p => p.top_z > .8 &&
                    sweptCircle(stand, flat(chair.seat_eye), p.polygon, .24))) return "Vùng chuyển tiếp bị cản bởi " + other.chair.id;
            }
            entry.state = action === "sit" ? "occupied" : "pulled-out";
            this.actorSeat = action === "sit" ? entry : undefined;
        }
        this.update();
        return null;
    }
}
