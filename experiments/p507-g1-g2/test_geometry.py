"""P507 layout, occupancy regression and schema compatibility, without Blender."""

import copy
import json
import unittest
from pathlib import Path

from geometry import (
    area_intersection,
    footprint_center,
    migrate_inventory,
    oriented_rectangle,
    overlaps,
    read_inventory,
    survey_to_three,
    verify,
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
            r["chair_inventory"], {"total": 36, "placed": 34, "unplaced": 2}
        )
        self.assertEqual(r["collision_count"], 0)

    def test_a_moves_towards_windows_preserving_all_ids(self):
        a = [o for o in self.data["objects"] if o["cluster"] == "A"]
        self.assertEqual(
            [o["id"] for o in a], [f"P507-DESK-A{i:02d}" for i in range(1, 7)]
        )
        self.assertEqual(a[0]["rect"], [1.8, 6.4, 3.3, 7.0])
        self.assertEqual(a[-1]["rect"], [4.8, 7.0, 6.3, 7.6])

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
        chair.update(status="PLACED_PROVISIONAL", footprint_offset=[0, 0])
        r = verify(d)
        self.assertFalse(r["ok"])
        self.assertIn(["P507-CHAIR-A-08", "P507-CABINET-LOW"], r["collisions"])

    def test_new_cabinet_chair_overlap_fails(self):
        d = copy.deepcopy(self.data)
        d["hero"]["cabinet"]["occupancy_rect"] = [3.1, 7.05, 4.6, 7.6]
        self.assertFails(d, "collision")

    def test_water_door_entry_overlap_fails(self):
        d = copy.deepcopy(self.data)
        d["hero"]["water_dispenser"]["occupancy_rect"] = [0.2, 7, 0.6, 7.5]
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
                "rect": [0.75, 0.15, 1.0, 0.35],
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
        d["openings"]["door"]["to_y"] = 9.4
        self.assertFails(d, "door opening")

    def test_door_provisional_size_and_no_swing_claim(self):
        door = self.data["openings"]["door"]
        self.assertAlmostEqual(door["to_y"] - door["from_y"], 1.5)
        self.assertEqual(door["height"], 2.5)
        self.assertEqual(door["leaf_count"], 2)
        self.assertEqual(door["leaf_count_source"], "PHOTO_OBSERVED")
        self.assertEqual(door["opening_angle_source"], "PROPOSED_LAYOUT")
        self.assertEqual(door["source"], "PROPOSED_LAYOUT")

    def test_unknown_is_not_clearance_pass(self):
        r = verify(self.data)
        self.assertTrue(r["unknown"])
        self.assertEqual(r["usable_walkways"]["A-B"]["clearance_status"], "UNKNOWN")
        self.assertAlmostEqual(r["desk_edge_gaps_m"]["A-B"], 1.45)
        self.assertAlmostEqual(
            r["usable_walkways"]["A-B"]["provisional_envelope_gap_m"], 0.50
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
        self.assertEqual(out["schema_version"], 3)
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
        # Historical R3 allowed withdrawing poses; the owner-approved R4 allocation is stricter.
        d = read_inventory(HERE / "fixtures/schema-v2-r3-baseline.json")
        c = d["chairs"]["instances"][0]
        c["status"] = "UNPLACED"
        c["placement_reason"] = "Pose withdrawn pending survey"
        c.pop("center")
        r = verify(d)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["chair_inventory"]["unplaced"], 13)
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
        self.assertFails(d, "wall collision")

    def test_support_relation_requires_support_height(self):
        d = copy.deepcopy(self.data)
        d["objects"].append(
            {
                "id": "P507-DECOR-TEST",
                "type": "decor",
                "rect": [2.0, 6.6, 2.3, 6.9],
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
            d = copy.deepcopy(self.data)
            target = d["openings"]["door"] if key == "source" else d["objects"][0]
            target[key] = "MEASURED" if key == "source" else "real_verified"
            self.assertFails(d, "source claim")

    def test_chair_cluster_is_required(self):
        for value in (None, "UNKNOWN", "AB", ""):
            d = copy.deepcopy(self.data)
            d["chairs"]["instances"][0]["cluster"] = value
            self.assertFails(d, "chair cluster")

    def test_supported_item_cannot_exceed_ceiling(self):
        d = copy.deepcopy(self.data)
        d["objects"][0]["bottom_z"] = 3
        self.assertFails(d, "vertical bounds")

    def test_third_right_chair_cannot_hide_behind_row_role(self):
        d = copy.deepcopy(self.data)
        chairs = {c["id"]: c for c in d["chairs"]["instances"]}
        for ident, y in (("09", 3.40), ("10", 3.90), ("11", 4.40)):
            c = chairs["P507-CHAIR-B-" + ident]
            c.update(
                center=[5.42, y],
                orientation_deg=90,
                desk_id="P507-DESK-B05",
                status="PLACED_PROVISIONAL",
            )
        self.assertEqual(chairs["P507-CHAIR-B-11"]["placement_role"], "left_end")
        self.assertFails(d, "geometrically right-end")

    def test_current_room_and_standard_height_cannot_be_scaled(self):
        for key in ("width_x", "length_y", "height_z"):
            d = copy.deepcopy(self.data)
            d["room"][key] *= 1.2
            self.assertFails(d, "room dimensions")
        d = copy.deepcopy(self.data)
        d["objects"][0]["height"] = 0.75
        self.assertFails(d, "surveyed .9m")

    def test_both_b_c_have_positive_window_translation(self):
        baseline = read_inventory(HERE / "fixtures/schema-v2-baseline.json")
        for group in "BC":
            old = next(
                o for o in baseline["objects"] if o["id"] == f"P507-DESK-{group}01"
            )
            new = next(o for o in self.data["objects"] if o["id"] == old["id"])
            self.assertGreater(new["rect"][0], old["rect"][0])
            d = copy.deepcopy(self.data)
            for o in d["objects"]:
                if o.get("cluster") == group:
                    o["rect"][0] -= 0.90
                    o["rect"][2] -= 0.90
            self.assertFails(d, "must move towards windows")

    def test_all_utility_categories_have_real_provisional_records(self):
        types = {o["type"] for o in self.data["objects"]}
        self.assertTrue(
            {
                "file_cabinet",
                "fridge",
                "storage_shelf",
                "shoe_rack",
                "waste_bin",
                "whiteboard",
                "tv_small",
            }.issubset(types)
        )
        for o in self.data["objects"]:
            if o["type"] in ("table_standard", "table_small"):
                continue
            for key in (
                "rights",
                "orientation_deg",
                "position_source",
                "size_source",
                "source_refs",
                "mesh_binding",
            ):
                self.assertIn(key, o)
            self.assertEqual(o["status"], "PLACED_PROVISIONAL")

    def test_new_utility_collision_is_not_excluded(self):
        d = copy.deepcopy(self.data)
        fridge = next(o for o in d["objects"] if o["type"] == "fridge")
        fridge["rect"] = next(
            o["rect"].copy() for o in d["objects"] if o["type"] == "file_cabinet"
        )
        self.assertFails(d, "footprint collision")

    def test_whiteboard_above_shoes_uses_vertical_separation(self):
        report = verify(self.data)
        self.assertTrue(
            any(
                "P507-WHITEBOARD" in pair
                and "P507-SHOE-RACK" in pair
                and pair[-1] == "vertical separation"
                for pair in report["allowed_relations"]
            )
        )
        d = copy.deepcopy(self.data)
        next(o for o in d["objects"] if o["id"] == "P507-WHITEBOARD")["bottom_z"] = 0.6
        self.assertFails(d, "footprint collision")

    def test_small_tv_and_neutral_displays_require_correct_supports(self):
        for ident in ("P507-TV-SMALL", "P507-DISPLAY-01"):
            d = copy.deepcopy(self.data)
            next(o for o in d["objects"] if o["id"] == ident)["bottom_z"] += 0.03
            self.assertFails(d, "support relation")

    def test_tv_diagonal_and_water_direction_are_required(self):
        self.assertEqual(self.data["hero"]["tv"]["orientation_deg"], 25)
        self.assertEqual(self.data["hero"]["water_dispenser"]["orientation_deg"], 90)
        d = copy.deepcopy(self.data)
        d["hero"]["tv"]["orientation_deg"] = 0
        self.assertFails(d, "tv must remain diagonal")
        d = copy.deepcopy(self.data)
        d["hero"]["water_dispenser"]["orientation_deg"] = 0
        self.assertFails(d, "water front")

    def test_diagonal_tv_cannot_intersect_room_wall(self):
        d = copy.deepcopy(self.data)
        d["hero"]["tv"]["center"][0] = 0.1
        self.assertFails(d, "wall collision")

    def test_only_declared_tv_mount_attachment_is_allowed(self):
        r = verify(self.data)
        self.assertTrue(
            any(
                pair[-1] == "anchored TV mount attachment"
                for pair in r["allowed_relations"]
            )
        )
        d = copy.deepcopy(self.data)
        mount = next(o for o in d["objects"] if o["type"] == "tv_mount")
        mount["attachment_id"] = "P507-DESK-A01"
        self.assertFails(d, "attachment")

    def test_ceiling_device_counts_and_mount_bounds(self):
        self.assertEqual(
            verify(self.data)["ceiling_counts"],
            {
                "light_panel": 8,
                "ceiling_fan": 4,
                "cassette_ac": 2,
                "projector": 1,
                "camera": 1,
            },
        )
        d = copy.deepcopy(self.data)
        d["ceiling"]["instances"].pop(0)
        self.assertFails(d, "light_panel count")
        d = copy.deepcopy(self.data)
        d["ceiling"]["instances"][0]["center"][2] = 3.7
        self.assertFails(d, "vertical bounds")

    def test_ceiling_fan_swept_envelope_cannot_hit_ac(self):
        d = copy.deepcopy(self.data)
        fan = next(i for i in d["ceiling"]["instances"] if i["type"] == "ceiling_fan")
        ac = next(i for i in d["ceiling"]["instances"] if i["type"] == "cassette_ac")
        fan["center"][:2] = ac["center"][:2]
        self.assertFails(d, "footprint collision")

    def test_four_blinds_are_bound_to_their_own_windows(self):
        self.assertEqual(verify(self.data)["blind_count"], 4)
        d = copy.deepcopy(self.data)
        d["openings"]["windows"][0]["blind"]["rect"][1] += 0.1
        self.assertFails(d, "own east window interval")

    def test_ai_wall_has_observed_letter_structure_and_independent_ids(self):
        r = verify(self.data)
        self.assertEqual(r["frame_groups"], {"A": 10, "I": 9, "ADJACENT": 8})
        ids = [f["id"] for f in self.data["photo_wall"]["frames"]]
        self.assertEqual(len(ids), len(set(ids)))
        d = copy.deepcopy(self.data)
        next(f for f in d["photo_wall"]["frames"] if f["group"] == "I")["center"][
            2
        ] += 0.1
        self.assertFails(d, "letter row structure")

    def test_all_original_36_chair_ids_survive_and_unplaced_is_not_hidden(self):
        baseline = read_inventory(HERE / "fixtures/schema-v2-baseline.json")
        self.assertEqual(
            {c["id"] for c in baseline["chairs"]["instances"]},
            {c["id"] for c in self.data["chairs"]["instances"]},
        )
        for c in self.data["chairs"]["instances"]:
            if c["status"] == "UNPLACED":
                self.assertNotIn("center", c)
                self.assertTrue(c["placement_reason"])
        d = copy.deepcopy(self.data)
        d["chairs"]["instances"][6]["id"] = "P507-RENAMED"
        self.assertFails(d, "stable baseline chair ids")

    def test_open_inventory_accepts_unknown_new_chair_without_maximum(self):
        d = copy.deepcopy(self.data)
        d["chairs"]["count"] += 1
        d["chairs"]["instances"].append(
            {
                "id": "P507-CHAIR-FUTURE-01",
                "cluster": "A",
                "type": "chair",
                "status": "UNPLACED",
                "source_kind": "UNKNOWN",
                "position_source": "UNKNOWN",
                "orientation_deg": None,
                "placement_reason": "Pending future survey",
            }
        )
        self.assertTrue(verify(d)["ok"], verify(d)["errors"])

    def test_unknown_new_furniture_is_not_invented_as_placed(self):
        d = copy.deepcopy(self.data)
        d["objects"].append(
            {
                "id": "P507-FUTURE-EQUIPMENT",
                "type": "equipment",
                "status": "UNPLACED",
                "source_kind": "UNKNOWN",
                "position_source": "UNKNOWN",
            }
        )
        r = verify(d)
        self.assertTrue(r["ok"], r["errors"])
        self.assertIn("P507-FUTURE-EQUIPMENT", r["unknown"])
        self.assertNotIn("P507-FUTURE-EQUIPMENT", {p["id"] for p in r["occupancy"]})

    def test_actual_v2_fixture_remains_readable(self):
        old = read_inventory(HERE / "fixtures/schema-v2-baseline.json")
        self.assertEqual(verify(old)["chair_inventory"]["placed"], 36)
        self.assertTrue(verify(old)["ok"], verify(old)["errors"])

    def test_circulation_improvement_does_not_falsely_certify_usage(self):
        r = verify(self.data)
        self.assertEqual(r["circulation_status"], "PARTIAL")
        self.assertGreater(
            r["usable_walkways"]["A-B"]["provisional_envelope_gap_m"], 0.20
        )
        self.assertGreater(
            r["usable_walkways"]["B-C"]["provisional_envelope_gap_m"], 0.40
        )
        self.assertAlmostEqual(
            r["static_clearances"]["B_right_chair_to_window_wall"]["inner_wall_gap_m"],
            0.38,
        )
        self.assertAlmostEqual(
            r["static_clearances"]["west_utility_to_desks"]["static_gaps_m"][
                "P507-SHOE-RACK"
            ],
            1.35,
        )

    def test_asymmetric_chair_proxy_offset_is_rotated_once(self):
        c = next(
            c for c in self.data["chairs"]["instances"] if c["id"] == "P507-CHAIR-B-09"
        )
        self.assertAlmostEqual(footprint_center(c)[0], 6.22)
        r = verify(self.data)
        p = next(p for p in r["occupancy"] if p["id"] == c["id"])
        self.assertAlmostEqual(min(v[0] for v in p["polygon"]), 5.97)
        self.assertAlmostEqual(max(v[0] for v in p["polygon"]), 6.47)
        self.assertEqual(c["footprint_size"], [0.46, 0.50])

    def test_false_verification_level_is_rejected(self):
        d = copy.deepcopy(self.data)
        next(o for o in d["objects"] if o["id"] == "P507-WHITEBOARD")[
            "verification_level"
        ] = "VERIFIED"
        self.assertFails(d, "source claim")

    def test_unknown_architectural_support_cannot_bypass_validation(self):
        d = copy.deepcopy(self.data)
        next(o for o in d["objects"] if o["id"] == "P507-WHITEBOARD")["support_id"] = (
            "P507-ARCH-NONEXISTENT"
        )
        self.assertFails(d, "structural support")

    def test_wrong_existing_architectural_support_is_rejected(self):
        d = copy.deepcopy(self.data)
        next(o for o in d["objects"] if o["id"] == "P507-WHITEBOARD")["support_id"] = (
            "P507-ARCH-CEILING"
        )
        self.assertFails(d, "structural support")

    def test_baseline_desk_cannot_be_unplaced_to_skip_collision(self):
        d = copy.deepcopy(self.data)
        d["objects"][0]["status"] = "UNPLACED"
        self.assertFails(d, "baseline desk must remain placed")

    def test_ceiling_mount_requires_contact_and_known_support(self):
        for update in ({"mount_support": "P507-ARCH-UNKNOWN"}, {"top_z": 3.4}):
            d = copy.deepcopy(self.data)
            next(
                o for o in d["ceiling"]["instances"] if o["type"] == "ceiling_fan"
            ).update(update)
            self.assertFails(d, "structural support")

    def test_tv_mount_support_name_cannot_be_faked(self):
        d = copy.deepcopy(self.data)
        d["hero"]["tv"]["mount_support"] = "P507-ARCH-UNKNOWN"
        self.assertFails(d, "structural support")

    def test_contact_is_allowed(self):
        self.assertEqual(area_intersection([0, 0, 1, 1], [1, 0, 2, 1]), 0)


if __name__ == "__main__":
    unittest.main()
