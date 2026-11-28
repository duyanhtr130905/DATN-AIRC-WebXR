import assert from "node:assert/strict";
import test from "node:test";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { ChairRoom, type Chair, type Layout, type SurveyCollider } from "../src/p507-r5/chairs.ts";

const chair: Chair = {
    id: "chair", desk_id: "desk", orientation_deg: 0,
    stored: [2, 3, 0], pulled: [2, 2, 0], seat_eye: [2, 2.05, 1.2],
    stand: [2, 2.56, 0], approach: [2, 1.39, 0],
    components: [{ min: [-.22, -.25, 0], max: [.22, .22, .46] }],
    occupied_components: [{ min: [-.21, -.15, .46], max: [.21, .31, 1.25] }],
};
const layout: Layout = {
    walkable_rect: [0, 0, 6, 7], chairs: [chair],
    static_walk_colliders: [], static_interaction_colliders: [],
};
const point = ([x, y]: number[]): [number, number] => [x, -y];
const web = (survey: number[]) => ({ mode: "web" as const, position: point(survey) });
const ar = { mode: "ar" as const, position: [0, 0] as [number, number] };
const frames = (room: ChairRoom) => { for (let i = 0; i < 8; i++) room.tick(.05); };

test("chair animation reserves the full sweep and releases it after interruption", () => {
    const room = new ChairRoom(layout, [1, 1, 0]);
    assert.equal(room.state("chair"), "stored");
    assert.equal(room.action("chair", "sit", web(chair.stand)), "Thao tác không khả dụng");
    assert.equal(room.action("chair", "pull", web([2, 2.5])), "Hãy rời vùng di chuyển của ghế");
    assert.equal(room.action("chair", "pull", web(chair.approach!)), null);
    assert.equal(room.move([1.4, -2.5], [1.2, 0]).reason, "chair");
    assert.equal(room.action("chair", "pull", web(chair.approach!)), "Đang di chuyển một ghế");
    room.tick(10);
    assert.equal(room.state("chair"), "stored");
    assert.notDeepEqual(room.pose("chair"), chair.stored);
    room.interrupt();
    assert.deepEqual(room.pose("chair"), chair.stored);
    assert.equal(room.move([1.4, -2.3], [1.2, 0]).reason, null);
});

test("actor sits from verified stand, cannot walk when occupied, and exits safely", () => {
    const room = new ChairRoom(layout, [1, 1, 0]);
    assert.equal(room.action("chair", "pull", web(chair.approach!)), null);
    frames(room);
    assert.deepEqual(room.pose("chair"), chair.pulled);
    assert.equal(room.action("chair", "sit", web(chair.approach!)), "Hãy tới điểm tiếp cận phía trước ghế");
    assert.equal(room.action("chair", "sit", web(chair.stand)), null);
    assert.equal(room.seat?.id, "chair");
    assert.equal(room.move(point(chair.stand), [1, 0]).reason, "Đang ngồi");
    assert.deepEqual(room.actions("chair", "web"), ["stand"]);
    assert.equal(room.action("chair", "stand", web(chair.seat_eye)), null);
    assert.equal(room.seat, undefined);
    assert.equal(room.action("chair", "store", web(chair.stand)), "Hãy rời vùng di chuyển của ghế");
    assert.equal(room.action("chair", "store", web(chair.approach!)), null);
    frames(room);
    assert.deepEqual(room.pose("chair"), chair.stored);
});

test("tabletop permits pull and store only, and does not ignore scene collision", () => {
    const obstacle: SurveyCollider = {
        id: "obstacle", polygon: [[1.8,2.4],[2.2,2.4],[2.2,2.5],[1.8,2.5]], bottom_z: 0, top_z: 1,
    };
    const room = new ChairRoom({ ...layout, static_interaction_colliders: [obstacle] }, [1, 1, 0]);
    assert.equal(room.action("chair", "pull", ar), "Ghế bị cản bởi obstacle");
    const clear = new ChairRoom(layout, [1, 1, 0]);
    assert.equal(clear.action("chair", "pull", ar), null);
    frames(clear);
    assert.deepEqual(clear.actions("chair", "ar"), ["store"]);
    assert.equal(clear.action("chair", "sit", ar), "Thao tác không khả dụng");
    assert.equal(clear.action("chair", "store", ar), null);
    clear.reset();
    assert.equal(clear.moving, undefined);
    assert.equal(clear.state("chair"), "stored");
});


test("all 34 proposal chairs can complete the four-action cycle at verified candidate poses", () => {
    const checkout = fileURLToPath(new URL("../../..", import.meta.url));
    const result = spawnSync(process.env.API_PYTHON ?? "python", ["-c",
        'import sys,json;sys.path.insert(0,"experiments/p507-r5");from layout import build_layout;print(json.dumps(build_layout()))',
    ], { cwd: checkout, encoding: "utf8" });
    assert.equal(result.status, 0, result.error?.message ?? result.stderr);
    const candidate = JSON.parse(result.stdout) as Layout & { spawn: [number, number, number] };
    assert.equal(candidate.chairs.length, 34);
    for (const record of candidate.chairs) {
        const room = new ChairRoom(candidate, candidate.spawn);
        const approach = [record.approach, ...(record.approach_alternatives ?? [])]
            .find(anchor => anchor && !room.blocked(point(anchor), point(anchor)));
        assert.ok(approach, record.id + " approach");
        assert.equal(room.action(record.id, "pull", web(approach)), null, record.id + " pull");
        frames(room);
        assert.equal(room.action(record.id, "sit", web(record.stand)), null, record.id + " sit");
        assert.equal(room.action(record.id, "stand", web(record.seat_eye)), null, record.id + " stand");
        assert.equal(room.action(record.id, "store", web(approach)), null, record.id + " store");
        frames(room);
        assert.deepEqual(room.pose(record.id), record.stored, record.id + " restored pose");
    }
});
