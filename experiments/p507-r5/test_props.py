"""Check the R5 proposal's planned prop placements before Blender export."""

import itertools
import unittest
from collections import Counter

from layout import build_layout
from props import build_props, horizontal_bounds


def contains_rect(parent, child, epsilon=1e-8):
    return all(
        lo - epsilon <= value <= hi + epsilon
        for lo, hi, value in zip(parent[:2], parent[2:], child[:2], strict=True)
    ) and all(
        lo - epsilon <= value <= hi + epsilon
        for lo, hi, value in zip(parent[:2], parent[2:], child[2:], strict=True)
    )


def overlap(one, two):
    return all(
        min(one[axis + 2], two[axis + 2]) - max(one[axis], two[axis]) > 1e-8
        for axis in (0, 1)
    )


class PropLayoutTest(unittest.TestCase):
    def setUp(self):
        self.layout = build_layout()
        self.design = self.layout["design"]
        self.objects = {record["id"]: record for record in self.design["objects"]}
        tv = next(
            p
            for p in self.layout["static_walk_colliders"]
            if p["id"] == "P507-TV-LARGE"
        )
        x = [point[0] for point in tv["polygon"]]
        self.tv_x = (min(x), max(x))
        self.props = build_props(
            self.design, self.layout["shelf_surfaces_z"], self.tv_x
        )

    def test_ids_counts_and_computer_orientation(self):
        self.assertEqual(len({p["id"] for p in self.props}), 29)
        counts = Counter(p["type"] for p in self.props)
        for kind, expected in {
            "computer": 6,
            "printer": 1,
            "tea": 1,
            "orchid": 1,
            "poster": 5,
            "clock": 1,
            "coffee": 1,
            "water_jug": 4,
        }.items():
            with self.subTest(kind=kind):
                self.assertEqual(counts[kind], expected)
        chair_by_id = {c["id"]: c for c in self.layout["chairs"]}
        for prop in (p for p in self.props if p["type"] == "computer"):
            with self.subTest(id=prop["id"]):
                chair = chair_by_id[prop["chair_id"]]
                self.assertEqual(chair["desk_id"], prop["support_ids"][0])
                self.assertEqual(chair["orientation_deg"], prop["orientation_deg"])

    def test_desk_support_and_continuous_printer_surface(self):
        articles = [
            p for p in self.props if p["support_ids"][0].startswith("P507-DESK-")
        ]
        for p in articles:
            with self.subTest(id=p["id"]):
                desks = [self.objects[i] for i in p["support_ids"]]
                self.assertTrue(all(d["height"] == p["center"][2] for d in desks))
                rects = [d["rect"] for d in desks]
                if len(rects) == 2:
                    lower, higher = sorted(rects, key=lambda r: r[1])
                    self.assertEqual((lower[0], lower[2]), (higher[0], higher[2]))
                    self.assertAlmostEqual(lower[3], higher[1], places=8)
                    self.assertEqual(p["orientation_deg"], 270)
                    self.assertAlmostEqual(lower[3], p["center"][1], places=8)
                    target = [lower[0], lower[1], higher[2], higher[3]]
                else:
                    target = rects[0]
                self.assertTrue(contains_rect(target, horizontal_bounds(p)))
        for p, q in itertools.combinations(articles, 2):
            self.assertFalse(
                overlap(horizontal_bounds(p), horizontal_bounds(q)), (p["id"], q["id"])
            )
        tea = next(p for p in articles if p["type"] == "tea")
        orchids = next(p for p in articles if p["type"] == "orchid")
        self.assertLess(tea["center"][0], orchids["center"][0])

    def test_wall_space_and_inventory(self):
        left, right, near_board, between_one_two, between_two_three = (
            p for p in self.props if p["type"] == "poster"
        )
        self.assertLess(horizontal_bounds(left)[2], self.tv_x[0])
        self.assertGreater(horizontal_bounds(right)[0], self.tv_x[1])
        self.assertGreater(
            horizontal_bounds(near_board)[1], self.objects["P507-WHITEBOARD"]["rect"][3]
        )
        self.assertLess(
            horizontal_bounds(near_board)[3], self.design["openings"]["door"]["from_y"]
        )
        self.assertEqual(
            between_one_two["adjacent_windows"], ["P507-WINDOW-04", "P507-WINDOW-03"]
        )
        self.assertEqual(
            between_two_three["adjacent_windows"], ["P507-WINDOW-03", "P507-WINDOW-02"]
        )
        windows = {w["id"]: w for w in self.design["openings"]["windows"]}
        for prop in (between_one_two, between_two_three):
            first, second = (windows[i] for i in prop["adjacent_windows"])
            self.assertGreater(horizontal_bounds(prop)[1], second["to_y"])
            self.assertLess(horizontal_bounds(prop)[3], first["from_y"])
        with self.assertRaisesRegex(ValueError, "TV-left wall span"):
            build_props(
                self.design, self.layout["shelf_surfaces_z"], (0.2, self.tv_x[1])
            )

    def test_shelf_tiers_and_clearances(self):
        shelf = self.objects["P507-UTILITY-SHELF"]
        tv = self.objects["P507-TV-SMALL"]
        x0, y0, x1, y1 = shelf["rect"]
        self.assertAlmostEqual(x1 - x0, 0.47)
        self.assertAlmostEqual(y1 - y0, 2.25)
        self.assertAlmostEqual(shelf["height"], 2.175)
        self.assertGreater(shelf["height"], self.objects["P507-FRIDGE"]["height"])
        levels = self.layout["shelf_surfaces_z"]
        self.assertEqual(tv["bottom_z"], levels[-1])
        self.assertEqual(tv["height"], 0.65)
        self.assertLess(tv["bottom_z"] + tv["height"], self.design["room"]["height_z"])
        self.assertTrue(contains_rect(shelf["rect"], tv["rect"]))
        rows = {tier: [] for tier in range(1, 5)}
        for p in (p for p in self.props if "tier" in p):
            tier = p["tier"]
            self.assertEqual(p["center"][2], levels[-tier])
            self.assertTrue(contains_rect(shelf["rect"], horizontal_bounds(p)))
            ceiling = (
                levels[1 - tier] - 0.05 if tier > 1 else self.design["room"]["height_z"]
            )
            self.assertLess(p["center"][2] + p["size"][2], ceiling)
            rows[tier].append(horizontal_bounds(p))
        rows[1].append(tv["rect"])
        self.assertEqual([len(row) for row in rows.values()], [4, 3, 4, 4])
        for row in rows.values():
            self.assertFalse(
                any(overlap(p, q) for p, q in itertools.combinations(row, 2))
            )
        refs = ("CABINET-FILES", "FRIDGE", "UTILITY-SHELF", "WASTE-BIN", "SHOE-RACK")
        utility = [self.objects["P507-" + key]["rect"] for key in refs]
        self.assertTrue(all(a[3] < b[1] for a, b in itertools.pairwise(utility)))
        self.assertLess(utility[-1][3], self.design["openings"]["door"]["from_y"])


if __name__ == "__main__":
    unittest.main()
