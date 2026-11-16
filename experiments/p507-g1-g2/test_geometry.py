"""P507 G1 deterministic geometry & extensibility tests (no Blender required)."""
import copy
import json
import unittest
from pathlib import Path
from geometry import area_intersection, read_inventory, verify

HERE = Path(__file__).resolve().parent


class P507GeometryTests(unittest.TestCase):
    def setUp(self):
        self.data = read_inventory(HERE / "p507-provisional.json")

    def test_initial_17_desks_and_clusters(self):
        r = verify(self.data)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["desk_count"], 17)
        self.assertEqual([r["clusters"][k]["count"] for k in "ABC"], [6, 6, 5])
        self.assertEqual(len([o for o in self.data["objects"] if o["type"] == "table_small"]), 1)

    def test_proposed_gaps_not_certified_egress(self):
        r = verify(self.data)
        self.assertAlmostEqual(r["desk_edge_gaps_m"]["A-B"], 1.25)
        self.assertAlmostEqual(r["desk_edge_gaps_m"]["B-C"], 1.30)
        self.assertTrue(any("not certify" in w for w in r["warnings"]))

    def test_footprints_inside_room_and_unchanged_ids(self):
        r = verify(self.data)
        self.assertEqual(r["unique_ids"], len(self.data["objects"]))
        self.assertFalse(r["errors"])
        for obj in self.data["objects"]:
            self.assertEqual(obj["position_source"], "PROPOSED_LAYOUT")

    def test_rejects_collision(self):
        data = copy.deepcopy(self.data)
        data["objects"][1]["rect"] = data["objects"][0]["rect"].copy()
        self.assertTrue(any("collision" in s.lower() for s in verify(data)["errors"]))

    def test_rejects_out_of_bounds(self):
        data = copy.deepcopy(self.data)
        data["objects"][0]["rect"][0] = -1
        self.assertFalse(verify(data)["ok"])

    def test_rejects_duplicate_id(self):
        data = copy.deepcopy(self.data)
        data["objects"][0]["id"] = data["objects"][1]["id"]
        self.assertFalse(verify(data)["ok"])

    def test_rejects_bad_standard_dimensions(self):
        data = copy.deepcopy(self.data)
        data["objects"][0]["rect"][2] -= 0.3
        self.assertTrue(any("dimensions" in e for e in verify(data)["errors"]))

    def test_inventory_open_appending_item_preserves_existing_ids(self):
        data = copy.deepcopy(self.data)
        before = [obj["id"] for obj in data["objects"]]
        data["objects"].append({
            "id": "P507-NEW-0001", "type": "furniture",
            "cluster": None, "rect": [0.20, 4.00, 0.55, 4.30],
            "height": 0.5, "position_source": "PROPOSED_LAYOUT",
        })
        out = verify(data)
        self.assertTrue(out["ok"], out["errors"])
        self.assertEqual([obj["id"] for obj in data["objects"][:-1]], before)
        self.assertEqual(out["object_count"], 18)

    def test_small_desk_not_claimed_measured(self):
        small = next(o for o in self.data["objects"] if o["type"] == "table_small")
        self.assertEqual(small["id"], "P507-DESK-B06")
        self.assertEqual(small["size_source"], "PROPOSED_LAYOUT")

    def test_known_footprints_touch_without_positive_overlap(self):
        self.assertEqual(area_intersection([0, 0, 1, 1], [1, 0, 2, 1]), 0)
        self.assertEqual(area_intersection([0, 0, 1, 1], [0.5, 0.5, 2, 2]), 0.25)

    def test_no_source_image_or_private_data_in_fixture(self):
        text = json.dumps(self.data, ensure_ascii=False).lower()
        self.assertNotIn("image/jpeg", text)
        self.assertNotIn("data:image/", text)
        self.assertNotIn("base64", text)
        self.assertEqual(self.data["rights"]["photo_and_brand"], "PENDING")


if __name__ == "__main__":
    unittest.main()
