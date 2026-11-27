"""Step 7, finding 8 (owner, 2026-11-27): rewetting never goes beyond the scenario's target.

Rewetting target = spared area x the scenario's rewetted proportion, capped by the herd's drained organic grassland
(and by the soil group 3 spared area). When a scenario spares more land than the mineral land plus the rewetting target
(national test scenario 3 spares all herd grassland with a target of 0), the organic land beyond the target stays in the
grassland row in its current condition. Only the animals go:

- drained land stays drained: logged as ``spared_drained_organic_grassland``;
- land that already had rewet status (CRT "Other organic soils") stays so: ``spared_rewetted_organic_grassland``.

Before, this land was rewetted beyond the target (126,410 ha in scenario 3) and the log recorded 314,640 ha as rewetted.
See docs/rewetting.md.
"""
import unittest

from _helpers import CAL, CASES, TARGET, classes, input_grassland_area, run_case

NATIONAL_CASES = ("national", "goblin_lite")
ENTRIES = ["rewet_grassland", "spared_drained_organic_grassland", "spared_rewetted_organic_grassland",
           "forest", "cropland", "farmable_condition"]


def entry(case, sc, name):
    log = run_case(case)["spared_area_log"]
    rows = log[(log.scenario == sc) & (log.land_use == name)]
    return float(rows.organic_area.sum() + rows.mineral_area.sum())


def grassland(case, farm_id):
    lu = run_case(case)["landuse"]
    return lu[(lu.land_use == "grassland") & (lu.farm_id == farm_id)].iloc[0]


def drained(row):
    return row.area_ha * (row.share_drained_rich_organic + row.share_drained_poor_organic)


def rewet_status(row):
    return row.area_ha * (row.share_rewetted_rich_organic + row.share_rewetted_poor_organic)


class RewettingTarget(unittest.TestCase):
    def test_rewetting_never_exceeds_the_target(self):
        LandCover = classes("national")[0]
        for case in NATIONAL_CASES:
            sc_df, grass, spared, breakdown = CASES[case][1]()
            land = LandCover(CAL, TARGET, sc_df, grass, spared, breakdown)
            for sc in land.scenario_list:
                target = (land.national_class.get_total_spared_area(spared, sc)
                          * land.sc_fetch_class.get_rewetted_proportion(sc))
                with self.subTest(case=case, scenario=sc):
                    self.assertLessEqual(entry(case, sc, "rewet_grassland"), target + 1e-6)

    def test_log_has_the_same_entries_for_every_scenario(self):
        for case in NATIONAL_CASES:
            log = run_case(case)["spared_area_log"]
            for sc in log.scenario.unique():
                with self.subTest(case=case, scenario=sc):
                    self.assertEqual(list(log[log.scenario == sc].land_use), ENTRIES)

    def test_spared_organic_entries_are_organic(self):
        for case in NATIONAL_CASES:
            log = run_case(case)["spared_area_log"]
            organic = log[log.land_use.str.startswith("spared_")]
            self.assertTrue((organic.mineral_area == 0).all(), case)
            self.assertTrue((organic.organic_area >= 0).all(), case)

    def test_no_spared_organic_land_when_the_target_and_mineral_land_suffice(self):
        for case, scenarios in (("national", (0, 1, 2)), ("goblin_lite", (0, 1, 2))):
            for sc in scenarios:
                for name in ("spared_drained_organic_grassland", "spared_rewetted_organic_grassland"):
                    with self.subTest(case=case, scenario=sc, entry=name):
                        self.assertEqual(entry(case, sc, name), 0.0)


class FullSpare(unittest.TestCase):
    """National test scenario 3: all herd grassland spared, rewetted proportion 0."""

    def setUp(self):
        self.base, self.sc3 = grassland("national", -CAL), grassland("national", 3)
        self.herd = input_grassland_area("national", CAL)

    def test_nothing_is_rewetted(self):
        self.assertEqual(entry("national", 3, "rewet_grassland"), 0.0)
        self.assertAlmostEqual(rewet_status(self.sc3), rewet_status(self.base), delta=1e-3)

    def test_drained_land_stays_drained(self):
        self.assertAlmostEqual(drained(self.sc3), drained(self.base), delta=1e-3)

    def test_spared_drained_organic_is_the_herds_drained_land(self):
        herd_drained = self.herd * (self.base.share_drained_rich_organic + self.base.share_drained_poor_organic)
        self.assertAlmostEqual(entry("national", 3, "spared_drained_organic_grassland"), herd_drained, delta=1e-3)
        self.assertAlmostEqual(herd_drained, 126409.57, delta=0.01)

    def test_spared_organic_is_the_herds_organic_land(self):
        """The two entries add up to the herd's organic grassland (herd x share_organic). The rewet-status entry is
        the rest; it includes about 53 ha of organic land that the inventory shares put in neither the drained nor
        the rewet-status pool (inventory rounding)."""
        total = (entry("national", 3, "spared_drained_organic_grassland")
                 + entry("national", 3, "spared_rewetted_organic_grassland"))
        self.assertAlmostEqual(total, self.herd * self.base.share_organic, delta=1e-3)
        self.assertAlmostEqual(entry("national", 3, "spared_rewetted_organic_grassland"), 188230.35, delta=0.01)

    def test_areas_unchanged(self):
        """Total grassland and the farmable condition area are as before the fix."""
        self.assertAlmostEqual(self.sc3.area_ha, 628271.0, delta=1)
        self.assertAlmostEqual(entry("national", 3, "farmable_condition"), 3590236.91, delta=0.01)


if __name__ == "__main__":
    unittest.main()
