"""Behaviour of the spared mineral-area allocation (Pyomo model, solved with HiGHS).

These tests characterise what the model does now. Expected failures mark known bugs; each names its finding in the
plan, and the fix removes the marker.
"""
import unittest

from _helpers import use_highs

use_highs()
from landcover_assignment.optimisation.landcover_optimisation import LandCoverOptimisation  # noqa: E402


def solve(area, targets):
    return LandCoverOptimisation().optimise_mineral_spared_area_distribution(area, targets)


class Allocation(unittest.TestCase):
    def test_targets_met_remainder_to_farmable(self):
        out = solve(1000.0, {"forest": 600.0, "cropland": 100.0})
        self.assertAlmostEqual(out["forest"], 600.0, places=4)
        self.assertAlmostEqual(out["cropland"], 100.0, places=4)
        self.assertAlmostEqual(out["farmable_condition"], 300.0, places=4)

    def test_area_is_conserved(self):
        out = solve(2_833_797.8, {"forest": 1_700_278.7, "cropland": 0.0})
        self.assertAlmostEqual(sum(out.values()), 2_833_797.8, delta=1e-3)

    def test_short_area_cuts_equal_hectares(self):
        """Current rule (plan Q1): when the targets exceed the area, each target is cut by the same hectares.

        This uses the worked example from the plan (2020 national numbers): forest 94% and crop 1% of all grassland,
        118,956 ha short. Crop goes to 0. If the owner chooses proportional cuts, this test changes in that dossier.
        """
        out = solve(3_590_677.0, {"forest": 3_670_584.0, "cropland": 39_049.0})
        self.assertAlmostEqual(out["cropland"], 0.0, delta=1e-3)
        self.assertAlmostEqual(out["forest"], 3_590_677.0, delta=1e-3)
        self.assertAlmostEqual(out["farmable_condition"], 0.0, delta=1e-3)

    def test_extra_land_use(self):
        """The model takes any set of land uses (extensibility: willow, other crops, ...)."""
        out = solve(1000.0, {"forest": 300.0, "cropland": 200.0, "willow": 100.0})
        self.assertAlmostEqual(out["willow"], 100.0, places=4)
        self.assertAlmostEqual(out["farmable_condition"], 400.0, places=4)

    @unittest.expectedFailure
    def test_zero_area(self):
        """Finding 1: divides by the available area (ZeroDivisionError). The result should be all zeros."""
        out = solve(0.0, {"forest": 100.0, "cropland": 50.0})
        self.assertEqual(sum(out.values()), 0.0)


if __name__ == "__main__":
    unittest.main()
