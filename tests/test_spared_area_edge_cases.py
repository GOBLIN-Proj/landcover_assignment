"""Spared-area inputs at the edges (step 7, findings 4 and 5): the national tree handles them or fails with a clear
message.

- Finding 4: a scenario with zero spared area runs; its grassland is unchanged and nothing is transitioned or planted.
  A spared-area column with more than one non-zero value is ambiguous and raises.
- Finding 5a: a scenario missing from the spared-area breakdown raises a ValueError naming it.
- Finding 5b: a scenario with no soil group 3 rows has no organic potential (0 ha) and the run completes.
"""
import contextlib
import io
import unittest

import pandas as pd

from _helpers import CAL, TARGET, classes, load_national

from landcover_assignment.national_landcover import NationalLandCover

LandCover, TransitionMatrix, Afforestation = classes("national")


def run(spared, breakdown):
    sc, grass, _, _ = load_national()
    with contextlib.redirect_stdout(io.StringIO()):
        landuse = LandCover(CAL, TARGET, sc, grass, spared, breakdown).combined_future_land_use_area()
        tm = TransitionMatrix(CAL, TARGET, sc, grass, spared, breakdown).create_transition_matrix()
        affor = Afforestation(CAL, TARGET, sc, tm).gen_cbm_afforestation_dataframe(breakdown)
    return landuse, tm, affor


def area(landuse, farm_id, land_use):
    return float(landuse[(landuse.farm_id == farm_id) & (landuse.land_use == land_use)].area_ha.sum())


class ZeroSparedArea(unittest.TestCase):
    """Finding 4."""

    @classmethod
    def setUpClass(cls):
        _, _, spared, breakdown = load_national()
        spared.loc[TARGET, 2] = 0
        breakdown.loc[breakdown.Scenario == 2, "area_ha"] = 0
        cls.landuse, cls.tm, cls.affor = run(spared, breakdown)

    def test_total_spared_area_is_zero(self):
        _, _, spared, _ = load_national()
        spared.loc[TARGET, 2] = 0
        self.assertEqual(NationalLandCover().get_total_spared_area(spared, 2), 0.0)

    def test_grassland_unchanged(self):
        self.assertAlmostEqual(area(self.landuse, 2, "grassland"), area(self.landuse, -CAL, "grassland"), delta=1e-3)

    def test_no_transitions_from_grassland(self):
        row = self.tm.loc[2, [c for c in self.tm.columns if c.startswith("Grassland_to_")]]
        self.assertTrue((row.abs() < 1e-6).all(), row[row.abs() >= 1e-6].to_dict())

    def test_nothing_planted(self):
        self.assertAlmostEqual(self.affor[self.affor.scenario == 2].total_area.sum(), 0.0, delta=1e-6)


class AmbiguousSparedArea(unittest.TestCase):
    """Finding 4: the scenario column must hold one non-zero value (the target year's spared area)."""

    def test_more_than_one_non_zero_value_raises(self):
        spared = pd.DataFrame({"index": [CAL, TARGET], "2": [10.0, 20.0]})
        with self.assertRaisesRegex(ValueError, "more than one non-zero"):
            NationalLandCover().get_total_spared_area(spared, 2)

    def test_goblin_lite_layout_still_read(self):
        spared = pd.DataFrame({"index": [CAL, TARGET], "2": [0.0, 20.0]})
        self.assertEqual(NationalLandCover().get_total_spared_area(spared, 2), 20.0)

    def test_missing_scenario_raises(self):
        spared = pd.DataFrame({"index": [CAL, TARGET], "1": [0.0, 20.0]})
        with self.assertRaisesRegex(ValueError, "Scenario 2 not found in spared_area"):
            NationalLandCover().get_total_spared_area(spared, 2)


class OrganicPotential(unittest.TestCase):
    """Finding 5."""

    def test_scenario_missing_from_breakdown_raises(self):
        _, _, spared, breakdown = load_national()
        breakdown = breakdown[breakdown.Scenario != 2]
        with self.assertRaisesRegex(ValueError, "Scenario 2 not found in the spared area breakdown"):
            NationalLandCover().get_area_with_organic_potential(breakdown, spared, 2)

    def test_no_soil_group_3_gives_zero(self):
        _, _, spared, breakdown = load_national()
        breakdown = breakdown[~((breakdown.Scenario == 2) & (breakdown.soil_group == 3))]
        self.assertEqual(NationalLandCover().get_area_with_organic_potential(breakdown, spared, 2), 0.0)

    def test_run_without_soil_group_3_completes_with_no_rewetting(self):
        _, _, spared, breakdown = load_national()
        breakdown = breakdown[~((breakdown.Scenario == 2) & (breakdown.soil_group == 3))]
        landuse, tm, affor = run(spared, breakdown)
        g = landuse[landuse.land_use == "grassland"].set_index("farm_id")
        rewet = lambda fid: g.loc[fid, "area_ha"] * (g.loc[fid, "share_rewetted_rich_organic"]
                                                     + g.loc[fid, "share_rewetted_poor_organic"])
        self.assertAlmostEqual(rewet(2), rewet(-CAL), delta=1e-3)
        self.assertAlmostEqual(affor[affor.scenario == 2].total_area.sum(), tm.loc[2, "Grassland_to_Forest"],
                               delta=1e-2)

    def test_all_zero_breakdown_is_not_a_cap(self):
        _, _, spared, breakdown = load_national()
        breakdown.loc[breakdown.Scenario == 2, "area_ha"] = 0
        n = NationalLandCover()
        self.assertEqual(n.get_area_with_organic_potential(breakdown, spared, 2), n.get_total_spared_area(spared, 2))


if __name__ == "__main__":
    unittest.main()
