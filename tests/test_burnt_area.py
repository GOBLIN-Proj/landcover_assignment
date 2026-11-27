"""D6b: burnt area of grassland, wetland and cropland in the national land-use table.

- Calibration-year rows: that year's inventory burnt area / area (CRF 2024; checked in test_national_validation).
- Target-year rows: the 3-year rate over BURNT_RATE_YEARS (2022-2024): sum of burnt area / sum of area, applied to
  the whole row (so new wetland or cropland area burns at the same rate). Settlement and farmable_condition: 0.
- Forest is cbm_runner's fire (D6a, tests/test_forest_cbm.py).
The catchment tree is not changed (see .artifacts/geo_todo.md).
"""
import sqlite3
import unittest

from _helpers import CAL, TARGET, run_case

from landcover_assignment.database import get_database_path
from landcover_assignment.national_landcover import BURNT_RATE_YEARS, NationalLandCover

CASES = ("national", "goblin_lite")
TABLES = {"grassland": "grassland_data", "wetland": "wetland_data", "cropland": "cropland_data",
          "settlement": "settlement_data"}


def rate(land_use):
    """Independent of the package: sum burnt_kha / sum total_kha over 2022-2024, from the database."""
    con = sqlite3.connect(f"file:{get_database_path()}?mode=ro", uri=True)
    try:
        burnt, area = con.execute(f"SELECT sum(burnt_kha), sum(total_kha) FROM {TABLES[land_use]} "
                                  "WHERE year BETWEEN 2022 AND 2024").fetchone()
    finally:
        con.close()
    return burnt / area


class BurntArea(unittest.TestCase):
    def test_window(self):
        self.assertEqual(BURNT_RATE_YEARS, (2022, 2024))

    def test_rates(self):
        expected = {"grassland": 1.6365e-4, "wetland": 2.6061e-4, "cropland": 6.3696e-5, "settlement": 0.0}
        nlc = NationalLandCover()
        for land_use, want in expected.items():
            with self.subTest(land_use=land_use):
                self.assertAlmostEqual(nlc.get_burnt_rate(land_use), rate(land_use), places=15)
                self.assertAlmostEqual(nlc.get_burnt_rate(land_use), want, delta=1e-8)
        self.assertEqual(nlc.get_burnt_rate("farmable_condition"), 0.0)
        with self.assertRaises(ValueError):
            nlc.get_burnt_rate("forest")

    def test_target_rows_use_the_rate(self):
        for case in CASES:
            lu = run_case(case)["landuse"]
            target = lu[lu.year == TARGET]
            for _, row in target.iterrows():
                with self.subTest(case=case, scenario=row.farm_id, land_use=row.land_use):
                    if row.land_use in ("grassland", "wetland", "cropland"):
                        self.assertAlmostEqual(row.share_burnt, rate(row.land_use), places=15)
                    elif row.land_use in ("settlement", "farmable_condition"):
                        self.assertEqual(row.share_burnt, 0.0)

    def test_target_burnt_hectares(self):
        """National scenario 0 in 2050 (dossier D6b)."""
        lu = run_case("national")["landuse"]
        sc0 = lu[(lu.farm_id == 0) & (lu.year == TARGET)].set_index("land_use")
        burnt = sc0.area_ha * sc0.share_burnt
        self.assertAlmostEqual(burnt["grassland"], 231.2, delta=0.1)
        self.assertAlmostEqual(burnt["wetland"], 316.0, delta=0.1)
        self.assertAlmostEqual(burnt["cropland"], 47.6, delta=0.1)

    def test_calibration_rows_keep_the_year(self):
        nlc = NationalLandCover()
        for case in CASES:
            lu = run_case(case)["landuse"]
            cal = lu[lu.farm_id == -CAL].set_index("land_use")
            for land_use in ("wetland", "cropland"):
                with self.subTest(case=case, land_use=land_use):
                    self.assertAlmostEqual(cal.loc[land_use, "share_burnt"],
                                           nlc.get_national_burn(land_use, CAL), places=15)

    def test_new_area_burns_at_the_rate(self):
        """A land use that gains spared area in the target year burns at the rate on its whole area."""
        from _helpers import load_national
        from landcover_assignment.distribution import LandDistribution
        dist = LandDistribution(load_national()[0])
        row = dist.land_distribution(CAL, "cropland", 10000.0, target_year=TARGET)
        self.assertAlmostEqual(row["share_burnt"], rate("cropland"), places=15)
        base = dist.land_distribution(CAL, "cropland", 10000.0)          # no target year: calibration share, diluted
        self.assertLess(base["share_burnt"], NationalLandCover().get_national_burn("cropland", CAL))


if __name__ == "__main__":
    unittest.main()
