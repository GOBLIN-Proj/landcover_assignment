"""Area accounting: land is conserved, and the land-use table, transition matrix, spared-area log and afforestation
table agree with each other.

These checks were moved from the old land_balance_test.py, geo_integrations/geo_test_land_balance.py and
areas_validation.py, and now run on every input set. The old files skipped scenario 0 (`if sc > 0`); here every
scenario is checked.
"""
import unittest

import pandas as pd

from _helpers import CAL, CASES, TARGET, run_case

TREE = {name: tree for name, (tree, _) in CASES.items()}


def grassland_input(case, year, sc):
    """Read a total grassland input the same way the package does (string or int scenario columns, year index or 'index' column)."""
    grass = CASES[case][1]()[1]
    if "index" in grass.columns:
        grass = grass.set_index("index")
    col = sc if sc in grass.columns else str(sc)
    return float(grass.loc[year, col])


def area(landuse, farm_id, land_use):
    rows = landuse[(landuse.farm_id == farm_id) & (landuse.land_use == land_use)]
    return float(rows.area_ha.sum())


class LandBalance(unittest.TestCase):
    def scenarios(self, case):
        lu = run_case(case)["landuse"]
        return [sc for sc in lu.farm_id.unique() if sc >= 0]

    def test_total_area_is_conserved(self):
        for case in CASES:
            lu = run_case(case)["landuse"]
            base = lu[lu.farm_id == -CAL].area_ha.sum()
            for sc in self.scenarios(case):
                with self.subTest(case=case, scenario=sc):
                    self.assertAlmostEqual(lu[lu.farm_id == sc].area_ha.sum(), base, delta=1e-3)

    def test_each_land_use_balances_with_the_matrix(self):
        """Future area = baseline area + Grassland_to_<use>; grassland loses |Grassland_to_Grassland|."""
        for case in CASES:
            out = run_case(case)
            lu, tm = out["landuse"], out["transition_matrix"]
            uses = sorted(set(lu.land_use) - {"grassland"})
            for sc in self.scenarios(case):
                with self.subTest(case=case, scenario=sc):
                    self.assertAlmostEqual(area(lu, sc, "grassland") + abs(tm.loc[sc, "Grassland_to_Grassland"]),
                                           area(lu, -CAL, "grassland"), delta=1e-3)
                    for use in uses:
                        col = f"Grassland_to_{use.title()}"
                        self.assertAlmostEqual(area(lu, -CAL, use) + tm.loc[sc, col], area(lu, sc, use), delta=1e-3,
                                               msg=f"{use}")

    def test_spared_area_log_accounts_for_all_spared_land(self):
        """Logged spared area + remaining grassland input = baseline grassland input."""
        for case in CASES:
            log = run_case(case)["spared_area_log"]
            area_cols = [c for c in ("mineral_area", "organic_area", "mineral_organic_area") if c in log.columns]
            for sc in self.scenarios(case):
                with self.subTest(case=case, scenario=sc):
                    logged = log[log.scenario == sc][area_cols].sum().sum()
                    self.assertAlmostEqual(logged + grassland_input(case, TARGET, sc), grassland_input(case, CAL, sc),
                                           delta=1e-3)

    def test_afforestation_equals_grassland_to_forest(self):
        for case in CASES:
            out = run_case(case)
            affor, tm = out["afforestation"], out["transition_matrix"]
            for sc in self.scenarios(case):
                with self.subTest(case=case, scenario=sc):
                    total = affor[affor.scenario == sc].total_area.sum()
                    self.assertAlmostEqual(total, tm.loc[sc, "Grassland_to_Forest"], delta=1e-2)


class SoilGroupSplit(unittest.TestCase):
    """The per-soil-group split of each transition must add up to the transition matrix (from areas_validation.py)."""

    @staticmethod
    def split(case="national"):
        from landcover_assignment.resource_manager.transition_data_fetcher import TransitionDataFetcher
        tm = run_case(case)["transition_matrix"]
        breakdown = CASES[case][1]()[3]
        by_group = TransitionDataFetcher(tm).get_grassland_to_landuse_soil_group_area(breakdown)
        return tm, by_group.groupby("scenario").sum(numeric_only=True)

    def test_forest_cropland_wetland(self):
        tm, totals = self.split()
        for sc in totals.index:
            for col in ("Grassland_to_Forest", "Grassland_to_Cropland", "Grassland_to_Wetland"):
                with self.subTest(scenario=sc, column=col):
                    self.assertAlmostEqual(totals.loc[sc, col], tm.loc[sc, col], delta=1e-2)

    @unittest.expectedFailure
    def test_farmable_condition(self):
        """Finding 3: every soil group gives its whole remaining pool to farmable condition, including the rewetted
        organic area, which stays grassland. Scenario 0 is over by 28,337.98 ha (its rewetted area)."""
        tm, totals = self.split()
        for sc in totals.index:
            self.assertAlmostEqual(totals.loc[sc, "Grassland_to_Farmable_Condition"],
                                   tm.loc[sc, "Grassland_to_Farmable_Condition"], delta=1e-2)


if __name__ == "__main__":
    unittest.main()
