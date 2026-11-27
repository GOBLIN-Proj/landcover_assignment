"""Area accounting: land is conserved, and the land-use table, transition matrix, spared-area log and afforestation
table agree with each other.

These checks were moved from the old land_balance_test.py, geo_integrations/geo_test_land_balance.py and
areas_validation.py, and now run on every input set. The old files skipped scenario 0 (`if sc > 0`); here every
scenario is checked.

National tree (D6a): the forest row mirrors cbm_runner's managed forest (FM + AF), which changes between the
calibration and target years in every scenario (AF baseline planting less FM deforestation, +141,392.8 ha by 2050).
That change is not a transition from grassland, so the target-year total is the baseline total plus the managed-forest
change, and the forest row is baseline + Grassland_to_Forest + that change. The catchment tree has no such change.
"""
import unittest

import pandas as pd

from _helpers import CAL, CASES, ROOT, TARGET, run_case

TREE = {name: tree for name, (tree, _) in CASES.items()}
CBM = pd.read_csv(ROOT / "data_sources/cbm_runner_forest.csv").set_index("year")


def managed_forest_change(case):
    """D6a: cbm_runner managed forest (FM + AF), target year minus calibration year; 0 in the catchment tree."""
    if TREE[case] != "national":
        return 0.0
    managed = CBM.fm_area_ha + CBM.af_area_ha
    return float(managed[TARGET] - managed[CAL])


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
                    self.assertAlmostEqual(lu[lu.farm_id == sc].area_ha.sum(), base + managed_forest_change(case),
                                           delta=1e-3)

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
                        managed = managed_forest_change(case) if use == "forest" else 0.0
                        self.assertAlmostEqual(area(lu, -CAL, use) + tm.loc[sc, col] + managed, area(lu, sc, use),
                                               delta=1e-3, msg=f"{use}")

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

    def test_farmable_condition(self):
        """Finding 3 (fixed): farmable condition by soil group adds up to the matrix. It used to take the whole remaining
        pool of each soil group, including the rewetted organic area, which stays grassland."""
        tm, totals = self.split()
        for sc in totals.index:
            with self.subTest(scenario=sc):
                self.assertAlmostEqual(totals.loc[sc, "Grassland_to_Farmable_Condition"],
                                       tm.loc[sc, "Grassland_to_Farmable_Condition"], delta=1e-2)

    def test_soil_groups_hold_all_spared_land(self):
        """Forest + cropland + farmable + spared organic land (stays grassland) in each soil group = that group's spared
        area."""
        from landcover_assignment.resource_manager.transition_data_fetcher import TransitionDataFetcher
        cols = ["Grassland_to_Forest", "Grassland_to_Cropland", "Grassland_to_Wetland",
                "Grassland_to_Farmable_Condition", "Grassland_Spared_Organic"]
        for case in ("national", "goblin_lite"):
            tm = run_case(case)["transition_matrix"]
            breakdown = CASES[case][1]()[3]
            by_group = TransitionDataFetcher(tm).get_grassland_to_landuse_soil_group_area(breakdown)
            placed = by_group.set_index(["scenario", "soil_group"])[cols].sum(axis=1)
            spared = breakdown.groupby(["Scenario", "soil_group"]).area_ha.sum()
            for key, value in placed.items():
                with self.subTest(case=case, scenario_soil_group=key):
                    self.assertAlmostEqual(value, spared.loc[key], delta=1e-2)

    def test_spared_organic_area_is_in_soil_group_3(self):
        """The spared organic land that stays grassland is all in soil group 3 and equals the log's three organic
        entries (rewet_grassland, spared_drained_organic_grassland, spared_rewetted_organic_grassland), in every
        scenario."""
        from landcover_assignment.resource_manager.transition_data_fetcher import TransitionDataFetcher
        entries = ["rewet_grassland", "spared_drained_organic_grassland", "spared_rewetted_organic_grassland"]
        for case in ("national", "goblin_lite"):
            out = run_case(case)
            log = out["spared_area_log"]
            organic = TransitionDataFetcher(out["transition_matrix"]).get_grassland_spared_organic_soil_group_areas(
                CASES[case][1]()[3]).set_index(["scenario", "soil_group"]).Grassland_Spared_Organic
            for sc in sorted(set(organic.index.get_level_values(0))):
                logged = log[(log.scenario == sc) & log.land_use.isin(entries)].organic_area.sum()
                with self.subTest(case=case, scenario=sc):
                    self.assertAlmostEqual(organic.loc[(sc, 3)], logged, delta=1e-2)
                    self.assertAlmostEqual(organic.loc[sc].drop(3).sum(), 0.0, delta=1e-6)


class ComputedOnce(unittest.TestCase):
    """combined_future_land_use_area() runs the allocation once per LandCover instance and returns copies."""

    def test_second_call_reuses_the_table(self):
        from unittest import mock
        from _helpers import CASES, CAL, TARGET, classes
        for tree, case in (("national", "national"), ("geo", "geo")):
            LandCover = classes(tree)[0]
            land = LandCover(CAL, TARGET, *CASES[case][1]())
            first = land.combined_future_land_use_area()
            with mock.patch.object(land, "calculate_spared_area_allocation",
                                   side_effect=AssertionError("allocation ran again")):
                second = land.combined_future_land_use_area()
            pd.testing.assert_frame_equal(first, second)
            first.loc[:, "area_ha"] = -1.0                      # changing a returned table changes nothing else
            pd.testing.assert_frame_equal(land.combined_future_land_use_area(), second)

if __name__ == "__main__":
    unittest.main()
