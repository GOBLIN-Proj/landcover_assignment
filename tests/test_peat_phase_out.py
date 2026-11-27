"""Decision D10 (owner, 2026-11-27): peat extraction, industrial and domestic, phases out linearly from the
calibration year to 0 in ``PEAT_PHASE_OUT_YEAR`` (2040), a documented modelling assumption (docs/peat_extraction.md).

The stopped area moves to the matching rewetted share; the wetland area and every other share are unchanged.
Calibration-year rows stay the inventory. National tree only (catchment: geo to-do G10).
"""
import unittest

from _helpers import CAL, TARGET, load_national, run_case
from landcover_assignment.distribution import LandDistribution
from landcover_assignment.national_landcover import NationalLandCover, PEAT_PHASE_OUT, PEAT_PHASE_OUT_YEAR

PAIRS = {
    "share_industrial_peat_extraction": "share_rewetted_industrial_peat_extraction",
    "share_domestic_peat_extraction": "share_rewetted_domestic_peat_extraction",
}
OTHER_SHARES = ("share_near_natural_wetland", "share_unmanaged_wetland", "share_rewetted_in_organic",
                "share_rewetted_in_mineral", "share_organic", "share_mineral")


def wetland_rows(case):
    land_use = run_case(case)["landuse"]
    wetland = land_use[land_use["land_use"] == "wetland"]
    return wetland[wetland["year"] == CAL].iloc[0], wetland[wetland["year"] == TARGET]


def wetland_target_row(target_year):
    return LandDistribution(load_national()[0]).land_distribution(CAL, "wetland", None, target_year=target_year)


class PeatPhaseOut(unittest.TestCase):
    def test_assumption_is_2040_for_industrial_and_domestic(self):
        self.assertEqual(PEAT_PHASE_OUT_YEAR, 2040)
        self.assertEqual(PEAT_PHASE_OUT, PAIRS)

    def test_remaining_fraction(self):
        remaining = NationalLandCover.get_peat_extraction_remaining
        self.assertEqual(remaining(2020, 2050), 0.0)
        self.assertEqual(remaining(2020, 2040), 0.0)
        self.assertAlmostEqual(remaining(2020, 2030), 0.5)
        self.assertAlmostEqual(remaining(2020, 2025), 0.75)
        self.assertEqual(remaining(2020, 2020), 1.0)
        self.assertEqual(remaining(2041, 2050), 0.0)      # calibration after the end year: already phased out

    def test_target_rows_fully_phased_out_by_2050(self):
        for case in ("national", "goblin_lite"):
            calibration, targets = wetland_rows(case)
            for _, target in targets.iterrows():
                with self.subTest(case=case, scenario=target["farm_id"]):
                    self.assertAlmostEqual(target["area_ha"], calibration["area_ha"], delta=1e-6)
                    for drained, rewetted in PAIRS.items():
                        self.assertEqual(target[drained], 0.0)
                        self.assertAlmostEqual(target[rewetted], calibration[drained] + calibration[rewetted],
                                               places=12)
                    for share in OTHER_SHARES:
                        self.assertAlmostEqual(target[share], calibration[share], places=12)

    def test_halfway_in_2030(self):
        calibration, target = wetland_target_row(None), wetland_target_row(2030)
        for drained, rewetted in PAIRS.items():
            self.assertAlmostEqual(target[drained], calibration[drained] / 2, places=12)
            self.assertAlmostEqual(target[rewetted], calibration[rewetted] + calibration[drained] / 2, places=12)
        self.assertEqual(target["area_ha"], calibration["area_ha"])

    def test_calibration_row_is_the_inventory(self):
        national = NationalLandCover()
        calibration, _ = wetland_rows("national")
        for drained, rewetted in PAIRS.items():
            self.assertAlmostEqual(calibration[drained], national.get_national_share(drained, "wetland", CAL),
                                   places=12)
            self.assertAlmostEqual(calibration[rewetted], national.get_national_share(rewetted, "wetland", CAL),
                                   places=12)
        self.assertGreater(calibration["share_industrial_peat_extraction"], 0.04)   # 55.5 kha of 1,212.5 (2020)


if __name__ == "__main__":
    unittest.main()
