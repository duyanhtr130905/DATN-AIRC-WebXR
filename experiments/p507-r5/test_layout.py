"""Geometry regressions for R5. No survey source or private export is needed."""

import copy
import json
import unittest

from layout import AISLE_TARGET, HISTORICAL_UNPLACED, R4, build_layout
from layout_checks import WalkSpace, aisle_widths, check_routes, swept_components


class P507LayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = build_layout()
        cls.report = check_routes(cls.layout)

    def test_frozen_inventory_counts_and_historical_unplaced(self):
        frozen = json.loads((R4 / "p507-provisional.json").read_text(encoding="utf-8"))
        actual = self.layout["design"]
        self.assertEqual(actual["survey_baseline"], frozen["survey_baseline"])
        self.assertEqual({c["id"] for c in actual["chairs"]["instances"] if c["status"] == "UNPLACED"},
                         HISTORICAL_UNPLACED)
        self.assertEqual(len(self.layout["chairs"]), 34)
        for cluster, desks, chairs in (("A", 6, 12), ("B", 6, 12), ("C", 5, 10)):
            desk_ids = {d["id"] for d in actual["objects"] if d.get("cluster") == cluster}
            in_cluster = [c for c in self.layout["chairs"] if c["cluster"] == cluster]
            self.assertEqual(len(desk_ids), desks)
            self.assertEqual(len(in_cluster), chairs)
            self.assertTrue(all(c["desk_id"] in desk_ids for c in in_cluster))

    def test_r4_baseline_is_insufficient(self):
        from geometry import occupancy, occupied_use_report

        frozen = json.loads((R4 / "p507-provisional.json").read_text(encoding="utf-8"))
        occupied = occupied_use_report(frozen, occupancy(frozen))["intercluster_clearance_m"]
        self.assertEqual(occupied, {"A-B": .20, "B-C": .15})
        self.assertTrue(all(width < AISLE_TARGET for width in occupied.values()))

    def test_aisles_and_accessible_seats(self):
        self.assertEqual(self.report["component_errors"], [])
        self.assertEqual(self.report["unreachable"], [])
        for corridor in ("A-B", "B-C"):
            self.assertGreaterEqual(self.report["aisles"]["occupied"][corridor]["width_m"], AISLE_TARGET)
        for fixture, count in (("stored", 36), ("pulled", 36), ("mixed", 36),
                               ("occupied", 2), ("end-occupied", 30), ("individual-pull", 34)):
            self.assertEqual(len(self.report["routes"][fixture]), count, fixture)

    def test_higher_than_1_8m_obstacle_does_not_create_false_wall(self):
        fixture = {
            "walkable_rect": [0, 0, 4, 4],
            "chairs": [],
            "static_walk_colliders": [
                {"id": "high", "polygon": [[1,1],[2,1],[2,2],[1,2]], "bottom_z": 1.81, "top_z": 2.2},
            ],
        }
        self.assertIsNone(WalkSpace(fixture, {}).block((.45,1.5),(2.5,1.5)))
        fixture["static_walk_colliders"][0]["bottom_z"] = 1.7
        self.assertEqual(WalkSpace(fixture, {}).block((.45,1.5),(2.5,1.5)), "high")

    def test_circle_sweep_rejects_tunnel_and_tangency(self):
        fixture = {
            "walkable_rect": [0, 0, 4, 4],
            "chairs": [],
            "static_walk_colliders": [
                {"id": "blocker", "polygon": [[2,1],[2.001,1],[2.001,2],[2,2]], "bottom_z": 0, "top_z": 1},
            ],
        }
        scenario = WalkSpace(fixture, {})
        self.assertIsNone(scenario.block((1,1.5),(1,1.5)))
        self.assertIsNone(scenario.block((3,1.5),(3,1.5)))
        self.assertEqual(scenario.block((1,1.5),(3,1.5)), "blocker")
        self.assertEqual(scenario.block((1,2.3),(3,2.3)), "blocker")
        self.assertIsNone(scenario.block((1,2.301),(3,2.301)))

    def test_blocked_chair_sweep_and_desk_aisle_protrusion(self):
        invalid = copy.deepcopy(self.layout)
        chair = invalid["chairs"][0]
        x, y, _ = chair["pulled"]
        bad = {"id": "bad", "polygon": [[x-.1,y-.1],[x+.1,y-.1],[x+.1,y+.1],[x-.1,y+.1]],
               "bottom_z": .44, "top_z": .50, "cluster": "A"}
        invalid["static_interaction_colliders"].append(bad)
        self.assertIn((chair["id"], "seat", "bad", None), swept_components(invalid))
        bad["polygon"] = [[x,9.6],[x+.1,9.6],[x+.1,10.2],[x,10.2]]
        invalid["static_walk_colliders"].append(bad)
        states = {c["id"]: "occupied" for c in invalid["chairs"]}
        widths = aisle_widths(invalid, states)
        self.assertLess(widths["A-B"]["width_m"], AISLE_TARGET)


if __name__ == "__main__":
    unittest.main()
