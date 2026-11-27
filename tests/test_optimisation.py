"""Behaviour of the spared mineral-area allocation (Pyomo model, solved with the open-source HiGHS solver).

These tests characterise what the model does now. Expected failures mark known bugs; each names its finding in the
plan, and the fix removes the marker.
"""
import unittest

import pyomo.environ as pyo

from landcover_assignment.optimisation.landcover_optimisation import LandCoverOptimisation


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

    def test_short_area_cuts_equal_percentage(self):
        """Item 13 (owner 2026-11-27, dossier S7_item13_short_area): when the targets exceed the area, every target
        is cut by the same percentage, so a small target is not wiped out first.

        The plan's worked example (2020 national numbers): forest 94% and crop 1% of all grassland, 118,956 ha short.
        Equal hectares would give crop 0; equal percentage gives -3.2% each.
        """
        area, targets = 3_590_677.0, {"forest": 3_670_584.0, "cropland": 39_049.0}
        out = solve(area, targets)
        ratio = area / sum(targets.values())
        self.assertAlmostEqual(out["forest"], targets["forest"] * ratio, delta=1e-2)
        self.assertAlmostEqual(out["cropland"], targets["cropland"] * ratio, delta=1e-2)
        self.assertAlmostEqual(out["cropland"], 37_797.0, delta=1.0)
        self.assertAlmostEqual(out["farmable_condition"], 0.0, delta=1e-3)

    def test_short_area_larger_crop_target(self):
        """Dossier example B: forest 90%, crop 5% of 3,904,877 ha with 3,590,237 ha of mineral land: -3.2% each."""
        area, targets = 3_590_237.0, {"forest": 3_514_389.3, "cropland": 195_243.85}
        out = solve(area, targets)
        ratio = area / sum(targets.values())
        for land_use, target in targets.items():
            self.assertAlmostEqual(out[land_use], target * ratio, delta=1e-2)

    def test_short_area_three_land_uses(self):
        """The equal-percentage cut holds for any set of land uses (extensibility); a zero target stays at 0."""
        targets = {"forest": 600.0, "cropland": 300.0, "willow": 100.0, "other": 0.0}
        out = solve(800.0, targets)
        for land_use, target in targets.items():
            self.assertAlmostEqual(out[land_use], target * 0.8, places=4)
        self.assertAlmostEqual(out["farmable_condition"], 0.0, places=4)

    def test_extra_land_use(self):
        """The model takes any set of land uses (extensibility: willow, other crops, ...)."""
        out = solve(1000.0, {"forest": 300.0, "cropland": 200.0, "willow": 100.0})
        self.assertAlmostEqual(out["willow"], 100.0, places=4)
        self.assertAlmostEqual(out["farmable_condition"], 400.0, places=4)

    def test_zero_area(self):
        """Finding 1 (fixed in step 3): no available area returns all zeros instead of ZeroDivisionError."""
        out = solve(0.0, {"forest": 100.0, "cropland": 50.0})
        self.assertEqual(out, {"forest": 0.0, "cropland": 0.0, "farmable_condition": 0.0})

    def test_extra_constraint(self):
        """Extra constraints can be added without changing the class (extensibility)."""
        def cap_cropland(model):
            model.cap_cropland = pyo.Constraint(expr=model.allocation["cropland"] <= 0.05)   # share of the area

        out = LandCoverOptimisation().optimise_mineral_spared_area_distribution(
            1000.0, {"forest": 300.0, "cropland": 200.0}, extra_constraints=[cap_cropland])
        self.assertAlmostEqual(out["cropland"], 50.0, places=4)
        self.assertAlmostEqual(out["forest"], 300.0, places=4)
        self.assertAlmostEqual(out["farmable_condition"], 650.0, places=4)

    def test_default_solver_is_open_source(self):
        self.assertEqual(LandCoverOptimisation().solver, "highs")

    def test_unavailable_solver_raises(self):
        with self.assertRaises(RuntimeError):
            LandCoverOptimisation(solver="no_such_solver").optimise_mineral_spared_area_distribution(
                100.0, {"forest": 50.0})


class ShortAreaPipeline(unittest.TestCase):
    """Item 13 through the whole pipeline: national scenario 3 inputs (all herd grassland spared, mineral land used
    up) with forest 94%, crop 1%, rewetting 5% (dossier S7_item13_short_area, example A)."""

    @classmethod
    def setUpClass(cls):
        from _helpers import CAL, TARGET, load_national
        from landcover_assignment.landcover import LandCover
        from landcover_assignment.transition_matrix import TransitionMatrix
        sc, grass, spared, breakdown = load_national()
        sc = sc[sc["Scenarios"] == 3].copy()
        sc["Forest area"], sc["Crop area"], sc["Wetland area"] = 0.94, 0.01, 0.05
        land = LandCover(CAL, TARGET, sc, grass, spared, breakdown)
        land.combined_future_land_use_area()
        cls.log = land.get_spared_area_log().set_index("land_use")["mineral_area"]
        cls.tm = TransitionMatrix(CAL, TARGET, sc, grass, spared, breakdown).create_transition_matrix()

    def test_forest_and_crop_cut_by_the_same_percentage(self):
        forest, crop = self.log["forest"], self.log["cropland"]
        mineral = forest + crop + self.log["farmable_condition"]
        self.assertAlmostEqual(self.log["farmable_condition"], 0.0, delta=1e-3)
        self.assertGreater(crop, 0.0)
        self.assertAlmostEqual(forest / 0.94, crop / 0.01, delta=1.0)     # same share of each target
        self.assertAlmostEqual(self.tm.loc[3, "Grassland_to_Cropland"], crop, delta=1e-3)
        self.assertAlmostEqual(-self.tm.loc[3, "Grassland_to_Grassland"], mineral, delta=1e-3)


if __name__ == "__main__":
    unittest.main()
