"""P507 layout, occupancy regression and schema compatibility, without Blender."""

import copy
import json
import unittest
from pathlib import Path
from geometry import (
    area_intersection,
    read_inventory,
    verify,
    migrate_inventory,
    oriented_rectangle,
    overlaps,
    survey_to_three,
)

HERE = Path(__file__).resolve().parent


class P507GeometryTests(unittest.TestCase):
    def setUp(self):
        self.data = read_inventory()

    def assertFails(self, data, term):
        report = verify(data)
        self.assertFalse(report["ok"])
        self.assertTrue(
            any(term.lower() in e.lower() for e in report["errors"]), report["errors"]
        )

    def test_17_desks_36_explicit_chairs(self):
        r = verify(self.data)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["desk_count"], 17)
        self.assertEqual([r["clusters"][g]["count"] for g in "ABC"], [6, 6, 5])
        self.assertEqual(
            r["chair_inventory"], {"total": 36, "placed": 36, "unplaced": 0}
        )
        self.assertEqual(r["collision_count"], 0)

    def test_a_moves_towards_windows_preserving_all_ids(self):
        a = [o for o in self.data["objects"] if o["cluster"] == "A"]
        self.assertEqual(
            [o["id"] for o in a], [f"P507-DESK-A{i:02d}" for i in range(1, 7)]
        )
        self.assertEqual(a[0]["rect"], [1.35, 6.25, 2.85, 6.85])
        self.assertEqual(a[-1]["rect"], [4.35, 6.85, 5.85, 7.45])

    def test_core_and_longitudinal_constraints(self):
        for ident in ("P507-DESK-B02", "P507-DESK-C05", "P507-DESK-B06"):
            d = copy.deepcopy(self.data)
            o = next(o for o in d["objects"] if o["id"] == ident)
            o["rect"][0] += 0.03
            self.assertFalse(verify(d)["ok"])

    def test_two_right_chairs_data_pose_each_cluster(self):
        for g in "BC":
            right = [
                c
                for c in self.data["chairs"]["instances"]
                if c["cluster"] == g and c["placement_role"] == "right_end"
            ]
            self.assertEqual(len(right), 2)
            self.assertEqual({c["orientation_deg"] for c in right}, {90})
            d = copy.deepcopy(self.data)
            next(c for c in d["chairs"]["instances"] if c["id"] == right[0]["id"])[
                "orientation_deg"
            ] = 270
            self.assertFails(d, "right-end chair pose")

    def test_no_right_chair_missing_or_extra(self):
        for g in "BC":
            d = copy.deepcopy(self.data)
            next(
                c
                for c in d["chairs"]["instances"]
                if c["cluster"] == g and c["placement_role"] == "right_end"
            )["placement_role"] = "row"
            self.assertFails(d, "exactly two")

    def test_previous_actual_cabinet_chair_overlap_fails(self):
        f = json.loads(
            (HERE / "fixtures/previous-cabinet-chair-overlap.json").read_text(
                encoding="utf-8-sig"
            )
        )
        d = copy.deepcopy(self.data)
        d["hero"]["cabinet"].update(f["cabinet"])
        chair = next(c for c in d["chairs"]["instances"] if c["id"] == f["chair"]["id"])
        chair.update(f["chair"])
        r = verify(d)
        self.assertFalse(r["ok"])
        self.assertIn(["P507-CHAIR-A-08", "P507-CABINET-LOW"], r["collisions"])

    def test_new_cabinet_chair_overlap_fails(self):
        d = copy.deepcopy(self.data)
        d["hero"]["cabinet"]["occupancy_rect"] = [1.7, 7.5, 3.2, 8.0]
        self.assertFails(d, "collision")

    def test_water_door_entry_overlap_fails(self):
        d = copy.deepcopy(self.data)
        d["hero"]["water_dispenser"]["occupancy_rect"] = [0.2, 6, 0.6, 6.5]
        self.assertFails(d, "door entry collision")

    def test_water_wall_overlap_fails(self):
        d = copy.deepcopy(self.data)
        d["hero"]["water_dispenser"]["occupancy_rect"] = [-0.1, 7, 0.3, 7.5]
        self.assertFails(d, "wall collision")

    def test_table_chair_collision_fails(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["center"] = [2, 6.5]
        self.assertFails(d, "footprint collision")

    def test_duplicate_id_fails(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["id"] = d["objects"][0]["id"]
        self.assertFails(d, "duplicate")

    def test_moving_retains_ids_and_append_is_open(self):
        d = copy.deepcopy(self.data)
        ids = [o["id"] for o in d["objects"]]
        d["objects"].append(
            {
                "id": "P507-NEW-0001",
                "type": "furniture",
                "rect": [0.2, 2.9, 0.55, 3.1],
                "height": 0.5,
                "position_source": "PROPOSED_LAYOUT",
            }
        )
        self.assertTrue(verify(d)["ok"], verify(d)["errors"])
        self.assertEqual([o["id"] for o in d["objects"][:-1]], ids)

    def test_invalid_standard_dimensions_fails(self):
        d = copy.deepcopy(self.data)
        d["objects"][0]["rect"][2] -= 0.3
        self.assertFails(d, "dimensions")

    def test_invalid_door_opening_fails(self):
        d = copy.deepcopy(self.data)
        d["openings"]["door"]["to_y"] = 8.2
        self.assertFails(d, "door opening")

    def test_door_provisional_size_and_no_swing_claim(self):
        door = self.data["openings"]["door"]
        self.assertAlmostEqual(door["to_y"] - door["from_y"], 1.5)
        self.assertEqual(door["height"], 2.5)
        self.assertEqual(door["swing"], "UNKNOWN")
        self.assertEqual(door["source"], "PROPOSED_LAYOUT")

    def test_unknown_is_not_clearance_pass(self):
        r = verify(self.data)
        self.assertTrue(r["unknown"])
        self.assertEqual(r["usable_walkways"]["A-B"]["clearance_status"], "UNKNOWN")
        self.assertAlmostEqual(r["desk_edge_gaps_m"]["A-B"], 1.25)
        self.assertAlmostEqual(
            r["usable_walkways"]["A-B"]["provisional_envelope_gap_m"], 0.2
        )

    def test_orientation_and_coordinate_conversion(self):
        p = oriented_rectangle([2, 3], [0.4, 0.8], 90)
        self.assertAlmostEqual(min(v[0] for v in p), 1.6)
        self.assertAlmostEqual(max(v[1] for v in p), 3.2)
        self.assertEqual(survey_to_three([2, 3, 1.65]), [2, 1.65, -3])
        self.assertFalse(
            overlaps(
                oriented_rectangle([0, 0], [1, 1], 0),
                oriented_rectangle([1, 0], [1, 1], 0),
            )
        )
        self.assertTrue(
            overlaps(
                oriented_rectangle([0, 0], [1, 1], 30),
                oriented_rectangle([0.1, 0], [1, 1], 90),
            )
        )

    def test_v1_migrates_without_inventing_chair_locations(self):
        d = copy.deepcopy(self.data)
        d["schema_version"] = 1
        d["chairs"] = {"count": 36}
        out = migrate_inventory(d)
        self.assertEqual(out["schema_version"], 2)
        self.assertEqual(len(out["chairs"]["instances"]), 36)
        self.assertTrue(
            all(
                c["status"] == "UNPLACED" and "center" not in c
                for c in out["chairs"]["instances"]
            )
        )
        self.assertEqual(
            [o["id"] for o in d["objects"]], [o["id"] for o in out["objects"]]
        )
        self.assertTrue(verify(out)["ok"], verify(out)["errors"])

    def test_unknown_chair_pose_is_not_renderable(self):
        d = copy.deepcopy(self.data)
        c = d["chairs"]["instances"][0]
        c["status"] = "UNPLACED"
        c.pop("center")
        r = verify(d)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["chair_inventory"]["unplaced"], 1)
        self.assertIn(c["id"], r["unknown"])

    def test_invalid_chair_pose_is_failure(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["orientation_deg"] = None
        self.assertFails(d, "chair pose")

    def test_no_fake_source_claims(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][0]["source_kind"] = "real_verified"
        self.assertFails(d, "source claim")
        self.assertEqual(
            next(o for o in self.data["objects"] if o["id"] == "P507-DESK-B06")[
                "size_source"
            ],
            "PROPOSED_LAYOUT",
        )
        self.assertEqual(self.data["rights"]["photo_and_brand"], "PENDING")
        self.assertNotIn("data:image", json.dumps(self.data).lower())

    def test_actual_v1_fixture_imports_without_inferred_placements(self):
        old = read_inventory(HERE / "fixtures/schema-v1-baseline.json")
        self.assertEqual(old["migrated_from"], 1)
        self.assertEqual(old["objects"][0]["rect"], [0.75, 6.25, 2.25, 6.85])
        self.assertEqual(verify(old)["chair_inventory"]["unplaced"], 36)
        self.assertTrue(verify(old)["ok"], verify(old)["errors"])

    def test_invalid_numeric_rect_fails_without_silent_skip(self):
        for value in (float("nan"), float("inf"), True, "bad"):
            d = copy.deepcopy(self.data)
            d["objects"][0]["rect"][0] = value
            self.assertFails(d, "rectangle")

    def test_required_desk_id_cannot_disappear(self):
        d = copy.deepcopy(self.data)
        d["objects"].pop(0)
        self.assertFails(d, "stable baseline")

    def test_hero_proxy_must_enclose_actual_model(self):
        d = copy.deepcopy(self.data)
        d["hero"]["water_dispenser"]["center"][0] = -1
        self.assertFails(d, "actual body")

    def test_support_relation_requires_support_height(self):
        d = copy.deepcopy(self.data)
        d["objects"].append(
            {
                "id": "P507-DECOR-TEST",
                "type": "decor",
                "rect": [1.5, 6.4, 1.8, 6.6],
                "height": 0.1,
                "bottom_z": 0.9,
                "support_id": "P507-DESK-A01",
                "position_source": "PROPOSED_LAYOUT",
            }
        )
        r = verify(d)
        self.assertTrue(r["ok"], r["errors"])
        self.assertTrue(r["allowed_relations"])
        d["objects"][-1]["bottom_z"] = 0
        self.assertFails(d, "collision")

    def test_unsubstantiated_measurement_claims_fail(self):
        for key in ("source", "size_source", "position_source", "source_kind"):
            d=copy.deepcopy(self.data)
            target=d["openings"]["door"] if key=="source" else d["objects"][0]
            target[key]="MEASURED" if key=="source" else "real_verified"
            self.assertFails(d,"source claim")

    def test_chair_cluster_is_required(self):
        for value in (None, "UNKNOWN", "AB", ""):
            d=copy.deepcopy(self.data)
            d["chairs"]["instances"][0]["cluster"]=value
            self.assertFails(d,"chair cluster")

    def test_supported_item_cannot_exceed_ceiling(self):
        d=copy.deepcopy(self.data)
        d["objects"][0]["bottom_z"]=3
        self.assertFails(d,"vertical bounds")

    def test_contact_is_allowed(self):
        self.assertEqual(area_intersection([0, 0, 1, 1], [1, 0, 2, 1]), 0)


if __name__ == "__main__":
    unittest.main()
