"""Owner-approved virtual adaptation, distinct from survey facts."""

import copy
import unittest

from geometry import read_inventory, verify


class VirtualLayoutTests(unittest.TestCase):
    def setUp(self):
        self.data = read_inventory()

    def test_dual_dimensions_and_provenance(self):
        d = self.data
        self.assertEqual(
            [d["survey_baseline"][k] for k in ("width_x", "length_y", "height_z")],
            [6, 8.1, 3.5],
        )
        self.assertEqual(d["survey_baseline"]["source"], "USER_REPORTED")
        self.assertEqual(
            [d["room"][k] for k in ("width_x", "length_y", "height_z")],
            [6.9, 9.315, 3.5],
        )
        self.assertEqual(d["room"]["source"], "OWNER_APPROVED_VIRTUAL_ADAPTATION")

    def test_owner_allocation_real_34_and_historical_36(self):
        cs = self.data["chairs"]["instances"]
        self.assertEqual(len(cs), 36)
        self.assertEqual(
            [
                sum(
                    c["cluster"] == g and c["status"] == "PLACED_PROVISIONAL"
                    for c in cs
                )
                for g in "ABC"
            ],
            [12, 12, 10],
        )
        self.assertEqual(
            {c["id"] for c in cs if c["status"] == "UNPLACED"},
            {"P507-CHAIR-C-09", "P507-CHAIR-C-10"},
        )

    def test_outward_door_sweep_and_leaves(self):
        door = self.data["openings"]["door"]
        self.assertEqual(door["swing"], "OUTWARD")
        self.assertTrue(all(p[0] <= 0 for p in door["swing_polygon"]))
        self.assertTrue(all(c["center"][0] < 0 for c in door["leaves"]))

    def test_glass_cabinet_three_bays(self):
        c = next(o for o in self.data["objects"] if o["type"] == "file_cabinet")
        self.assertEqual(c["compartment_count"], 3)
        self.assertEqual(c["front_material"], "clear_glass")

    def test_shelf_widened_along_wall_not_depth(self):
        c = next(o for o in self.data["objects"] if o["type"] == "storage_shelf")
        r = c["rect"]
        self.assertAlmostEqual(r[3] - r[1], 1.5)
        self.assertAlmostEqual(r[2] - r[0], 0.47)

    def test_wall_vanilla_not_cold_white(self):
        self.assertEqual(self.data["appearance"]["wall_base_color_srgb"], "#F5E6C8")

    def test_occupied_use_report_is_separate(self):
        r = verify(self.data)
        self.assertIn("occupied_use", r)
        self.assertEqual(r["occupied_use"]["chair_pullback_m"], 0.15)

    def test_outward_exception_does_not_allow_chair_outside(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["center"] = [-0.2, 4]
        self.assertFalse(verify(d)["ok"])

    def test_survey_baseline_must_not_be_rewritten(self):
        d = copy.deepcopy(self.data)
        d["survey_baseline"]["width_x"] = 6.9
        self.assertTrue(
            any("survey baseline" in e.lower() for e in verify(d)["errors"])
        )

    def test_false_owner_label_does_not_bypass_bounds(self):
        d = copy.deepcopy(self.data)
        c = d["chairs"]["instances"][0]
        c["center"] = [-1, 5]
        c["source_kind"] = "OWNER_APPROVED_VIRTUAL_ADAPTATION"
        self.assertFalse(verify(d)["ok"])

    def test_all_historical_asset_dimensions_preserved_except_explicit_shelf(self):
        from pathlib import Path

        old = read_inventory(
            Path(__file__).parent / "fixtures/schema-v2-r3-baseline.json"
        )
        current = {o["id"]: o for o in self.data["objects"]}
        for o in old["objects"]:
            if o["id"] == "P507-UTILITY-SHELF":
                continue
            n = current[o["id"]]
            for axis in (0, 1):
                self.assertAlmostEqual(
                    o["rect"][axis + 2] - o["rect"][axis],
                    n["rect"][axis + 2] - n["rect"][axis],
                )
            self.assertEqual(o["height"], n["height"])
        for key in ("tv", "cabinet", "water_dispenser"):
            for field in ("width", "height", "radius", "size", "footprint_size"):
                if field in old["hero"][key]:
                    self.assertEqual(
                        old["hero"][key][field], self.data["hero"][key][field]
                    )
        for a, b in zip(old["openings"]["windows"], self.data["openings"]["windows"]):
            self.assertAlmostEqual(a["to_y"] - a["from_y"], b["to_y"] - b["from_y"])
        self.assertEqual(
            [c["size"] for c in old["ceiling"]["instances"]],
            [c["size"] for c in self.data["ceiling"]["instances"]],
        )

    def test_r3_fixture_import_never_invents_virtual_approval(self):
        from pathlib import Path

        d = read_inventory(
            Path(__file__).parent / "fixtures/schema-v2-r3-baseline.json"
        )
        self.assertEqual(d["schema_version"], 3)
        self.assertEqual(d["room"]["source"], "USER_REPORTED")
        self.assertNotIn("virtual_experience", d)
        self.assertTrue(verify(d)["ok"])

    def test_chair_cannot_be_hidden_to_satisfy_34(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["status"] = "UNPLACED"
        self.assertFalse(verify(d)["ok"])

    def test_unassigned_c09_cannot_be_rendered(self):
        d = copy.deepcopy(self.data)
        c = next(c for c in d["chairs"]["instances"] if c["id"] == "P507-CHAIR-C-09")
        c.update(status="PLACED_PROVISIONAL", center=[1, 8], orientation_deg=0)
        self.assertFalse(verify(d)["ok"])

    def test_outward_exterior_exception_is_not_global(self):
        for mutate in (
            "wrong_id",
            "inward",
            "huge_proxy",
            "wrong_hinge",
            "remote_leaf",
            "sweep_inward",
            "incomplete_sector",
        ):
            d = copy.deepcopy(self.data)
            door = d["openings"]["door"]
            leaf = door["leaves"][0]
            if mutate == "wrong_id":
                leaf["id"] = "P507-FAKE-DOOR"
            elif mutate == "inward":
                leaf["orientation_deg"] = -60
            elif mutate == "huge_proxy":
                leaf["footprint_size"] = [0.5, 0.75]
            elif mutate == "wrong_hinge":
                leaf["hinge_survey"][0] = -2
            elif mutate == "remote_leaf":
                leaf["center"][0] = -3
            elif mutate == "sweep_inward":
                door["swing_polygon"][0][0] = 0.5
            else:
                door["sweep_polygons"][0] = door["sweep_polygons"][0][:3]
            self.assertFalse(verify(d)["ok"], mutate)

    def test_rows_cannot_claim_correct_role_on_wrong_side(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["center"] = [1, 8.8]
        self.assertTrue(any("chair side" in e.lower() for e in verify(d)["errors"]))

    def test_occupied_use_cannot_be_disabled_by_zero_pullback(self):
        d = copy.deepcopy(self.data)
        d["occupied_use"]["chair_pullback_m"] = 0
        self.assertFalse(verify(d)["ok"])

    def test_proposed_occupied_use_is_collision_free_and_separate_from_static(self):
        r = verify(self.data)
        u = r["occupied_use"]
        self.assertEqual(u["collision_count"], 0)
        self.assertEqual(u["west_main_route_static_min_m"], 1.08)
        self.assertEqual(u["west_main_route_occupied_min_m"], 0.93)
        self.assertEqual(u["intercluster_clearance_m"], {"A-B": 0.2, "B-C": 0.3})
        self.assertEqual(u["status"], "PARTIAL")

    def test_proposed_entrance_start_has_nominal_2d_clearance(self):
        import math

        from geometry import occupancy, point_in_polygon

        x, y, z = self.data["handoff"]["starting_feet_survey"]
        radius = self.data["handoff"]["nominal_avatar_radius_m"]
        self.assertEqual(z, 0)
        self.assertTrue(radius < x < self.data["room"]["width_x"] - radius)
        for p in occupancy(self.data):
            if p["bottom_z"] >= 1.8:
                continue
            self.assertFalse(point_in_polygon([x, y], p["polygon"]), p["id"])
            for a, b in zip(p["polygon"], p["polygon"][1:] + p["polygon"][:1]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                t = max(
                    0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy))
                )
                self.assertGreaterEqual(
                    math.hypot(x - a[0] - t * dx, y - a[1] - t * dy), radius, p["id"]
                )


if __name__ == "__main__":
    unittest.main()
