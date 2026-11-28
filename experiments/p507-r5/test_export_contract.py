"""Small regression tests for independent R5 contract checks."""

import unittest

from verify_export import expected_bounds, index_instances
from verify_props import adjacent_platform, overlaps, within


class ExportContractTest(unittest.TestCase):
    def test_axes_change_once(self):
        self.assertEqual(expected_bounds({
            "id": "P507-TEST", "authored_bounds_survey": [1, 2, 3, 4, 5, 6],
        }), [1, 3, -5, 4, 6, -2])

    def test_bounds_reject_non_finite_or_flat_geometry(self):
        for bounds in ([0, 0, 0, 1, 1, float("inf")], [0, 0, 0, 1, 1, 0]):
            with self.assertRaisesRegex(ValueError, "authored bounds"):
                expected_bounds({"id": "P507-TEST", "authored_bounds_survey": bounds})

    def test_duplicate_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            index_instances({"instances": [{"id": "P507-TEST"}, {"id": "P507-TEST"}]})

    def test_printer_support_needs_continuous_coplanar_desks(self):
        first = {"rect": [0, 0, 3, 1], "z": .9}
        self.assertEqual(adjacent_platform([first, {"rect": [0, 1, 3, 2], "z": .9}]), [0, 0, 3, 2])
        with self.assertRaisesRegex(ValueError, "gap"):
            adjacent_platform([first, {"rect": [0, 1.02, 3, 2], "z": .9}])
        with self.assertRaisesRegex(ValueError, "different heights"):
            adjacent_platform([first, {"rect": [0, 1, 3, 2], "z": 1.0}])

    def test_support_detects_overhang_and_does_not_count_contact_as_overlap(self):
        first = [0, 0, 0, 1, 1, 1]
        self.assertTrue(within([0, 0, 1, 1], first))
        self.assertFalse(within([0, 0, 1, .8], first))
        self.assertFalse(overlaps(first, [0, 0, 1, 1, 1, 2]))
        self.assertTrue(overlaps(first, [0, 0, .9, 1, 1, 2]))


if __name__ == "__main__":
    unittest.main()
