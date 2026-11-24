"""Dossier LA2: the national grassland balance (national tree only; the catchment tree is unchanged by design).

The grassland area in GOBLIN is herd-derived (grassland_production). The national grassland that the herd doesn't need
(the balance) is added to the grassland row so that its emissions are counted:

    balance = national grassland area (calibration year) - herd grassland area (calibration year),  floor 0

- National area: package database, grassland_data.total_kha (EPA CRT 2026 Table4.C total grassland), for whatever
  calibration year the run uses.
- Herd area: grassland_production's total_grassland input, calibration-year row.
- The balance is the same in the baseline and every scenario, and it is never available to be spared.
- LandCover.get_grassland_area_breakdown() reports herd / rewetted spared / other (balance) grassland per row.
"""
import logging
import unittest

import pandas as pd

from _helpers import CAL, TARGET, classes, input_grassland_area, load_national, national_grassland_area, run_case

NATIONAL_CASES = ("national", "goblin_lite")


def grassland_rows(case):
    lu = run_case(case)["landuse"]
    return lu[lu.land_use == "grassland"].set_index("farm_id").area_ha


def balance(case):
    return max(national_grassland_area(CAL) - input_grassland_area(case, CAL), 0.0)


class Balance(unittest.TestCase):
    def test_baseline_grassland_is_the_national_area(self):
        """Mass balance: herd area + balance = the national grassland area in the calibration year."""
        for case in NATIONAL_CASES:
            self.assertAlmostEqual(grassland_rows(case)[-CAL], national_grassland_area(CAL), delta=1e-3, msg=case)

    def test_balance_is_carried_forward_unchanged(self):
        """Every scenario row = its herd area (target year) + rewetted spared grassland + the same balance."""
        for case in NATIONAL_CASES:
            rows = grassland_rows(case)
            log = run_case(case)["spared_area_log"]
            for sc in rows.index[rows.index >= 0]:
                rewetted = log[(log.scenario == sc) & (log.land_use == "rewet_grassland")].organic_area.sum()
                herd = input_grassland_area(case, TARGET, sc)
                self.assertAlmostEqual(rows[sc], herd + rewetted + balance(case), delta=1e-3, msg=f"{case} {sc}")

    def test_balance_is_not_spared(self):
        """Scenario 3 spares all herd grassland (target herd area 0); the balance stays in the grassland row."""
        rows = grassland_rows("national")
        self.assertEqual(input_grassland_area("national", TARGET, 3), 0.0)
        self.assertGreaterEqual(rows[3], balance("national") - 1e-3)

    def test_spared_area_unchanged(self):
        """The spareable mineral area is still the herd's: spared mineral land in scenario 3 equals the herd's mineral
        grassland, not the national mineral grassland."""
        lu = run_case("national")["landuse"]
        base = lu[(lu.farm_id == -CAL) & (lu.land_use == "grassland")].iloc[0]
        herd_mineral = input_grassland_area("national", CAL) * base.share_mineral
        log = run_case("national")["spared_area_log"]
        spared_mineral = log[log.scenario == 3].mineral_area.sum()
        self.assertAlmostEqual(spared_mineral, herd_mineral, delta=1e-3)


class Breakdown(unittest.TestCase):
    COLUMNS = ["farm_id", "year", "herd_grassland_ha", "rewetted_spared_ha", "other_grassland_ha", "total_grassland_ha"]

    def breakdown(self, case):
        LandCover = classes("national")[0]
        from _helpers import CASES
        land = LandCover(CAL, TARGET, *CASES[case][1]())
        return land, land.get_grassland_area_breakdown()

    def test_columns_and_rows(self):
        _, table = self.breakdown("national")
        self.assertEqual(list(table.columns), self.COLUMNS)
        self.assertEqual(list(table.farm_id), [-CAL, 0, 1, 2, 3])
        self.assertEqual(list(table.year), [CAL, TARGET, TARGET, TARGET, TARGET])

    def test_parts_add_up_to_the_grassland_row(self):
        for case in NATIONAL_CASES:
            _, table = self.breakdown(case)
            rows = grassland_rows(case)
            parts = table.herd_grassland_ha + table.rewetted_spared_ha + table.other_grassland_ha
            pd.testing.assert_series_equal(parts, table.total_grassland_ha, check_names=False, atol=1e-6)
            self.assertTrue(((table.total_grassland_ha - rows.loc[table.farm_id].values).abs() < 1e-3).all(), case)

    def test_values(self):
        for case in NATIONAL_CASES:
            _, table = self.breakdown(case)
            t = table.set_index("farm_id")
            log = run_case(case)["spared_area_log"]
            self.assertAlmostEqual(t.loc[-CAL, "herd_grassland_ha"], input_grassland_area(case, CAL), delta=1e-6)
            self.assertEqual(t.loc[-CAL, "rewetted_spared_ha"], 0.0)
            for sc in t.index[t.index >= 0]:
                self.assertAlmostEqual(t.loc[sc, "herd_grassland_ha"], input_grassland_area(case, TARGET, sc), delta=1e-3)
                rewetted = log[(log.scenario == sc) & (log.land_use == "rewet_grassland")].organic_area.sum()
                self.assertAlmostEqual(t.loc[sc, "rewetted_spared_ha"], rewetted, delta=1e-3)
            self.assertTrue((t.other_grassland_ha - balance(case)).abs().max() < 1e-6, case)

    def test_reporting_only(self):
        """The breakdown doesn't change the land-use table."""
        land, _ = self.breakdown("national")
        pd.testing.assert_frame_equal(land.combined_future_land_use_area(), run_case("national")["landuse"])


class Edges(unittest.TestCase):
    def national(self):
        from landcover_assignment.national_landcover import NationalLandCover
        return NationalLandCover()

    def test_balance_uses_the_calibration_year(self):
        """The balance is taken in whatever calibration year the run uses."""
        grass = load_national()[1]
        for year in (2015, 2020, 2022):
            want = national_grassland_area(year) - input_grassland_area("national", CAL)
            self.assertAlmostEqual(self.national().get_grassland_balance_area(year, grass), want, delta=1e-6)

    def test_negative_balance_is_zero_with_a_warning(self):
        grass = load_national()[1] * 10                      # herd area larger than the country's grassland
        with self.assertLogs("landcover_assignment.national_landcover", level=logging.WARNING):
            self.assertEqual(self.national().get_grassland_balance_area(CAL, grass), 0.0)

    def test_year_not_in_the_database(self):
        with self.assertRaisesRegex(ValueError, "2035"):
            self.national().get_grassland_balance_area(2035, load_national()[1])


if __name__ == "__main__":
    unittest.main()
