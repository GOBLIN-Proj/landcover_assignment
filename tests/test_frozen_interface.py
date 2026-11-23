"""The interface that goblin_lite, geo_goblin_py, landcover_lca and cbm_runner rely on.

The full list is in `.goblin-context/interfaces/landcover_assignment.md`. Changing anything tested here needs a
gated, coordinated change across those packages.
"""
import inspect
import itertools
import unittest

from _helpers import CAL, classes, run_case

SIX = ["calibration_year", "target_year", "scenario_inputs_df", "total_grassland", "total_spared_area",
       "spared_area_breakdown"]
LAND_USES = {"national": ["grassland", "wetland", "cropland", "forest", "settlement", "farmable_condition"],
             "geo": ["grassland", "wetland", "cropland", "forest", "farmable_condition"]}
SHARES = {
    "national": ["share_mineral", "share_organic", "share_drained_rich_organic", "share_drained_poor_organic",
                 "share_rewetted_rich_organic", "share_rewetted_poor_organic", "share_organic_mineral",
                 "share_rewetted_in_organic", "share_rewetted_in_mineral", "share_domestic_peat_extraction",
                 "share_industrial_peat_extraction", "share_rewetted_industrial_peat_extraction",
                 "share_rewetted_domestic_peat_extraction", "share_near_natural_wetland", "share_unmanaged_wetland",
                 "share_burnt"],
    "geo": ["share_mineral", "share_organic", "share_organic_mineral", "share_rewetted_in_organic",
            "share_rewetted_in_mineral", "share_rewetted_in_organic_mineral", "share_peat_extraction", "share_burnt"],
}
# landcover_lca reads these transition columns and raises KeyError if one is missing
LCA_TRANSITIONS = ["Grassland_to_Grassland", "Grassland_to_Cropland", "Wetland_to_Wetland", "Cropland_to_Grassland",
                   "Cropland_to_Cropland", "Forest_to_Grassland", "Forest_to_Cropland", "Forest_to_Forest"]


def params(func):
    return [p for p in inspect.signature(func).parameters if p != "self"]


class Signatures(unittest.TestCase):
    def test_constructors_and_methods(self):
        for tree in ("national", "geo"):
            LandCover, TransitionMatrix, Afforestation = classes(tree)
            with self.subTest(tree=tree):
                self.assertEqual(params(LandCover.__init__), SIX)
                self.assertEqual(params(TransitionMatrix.__init__), SIX)
                self.assertEqual(params(Afforestation.__init__),
                                 ["calibration_year", "target_year", "scenario_inputs_df", "transition_matrix"])
                self.assertEqual(params(LandCover.combined_future_land_use_area), [])
                self.assertEqual(params(LandCover.get_spared_area_log), [])
                self.assertEqual(params(TransitionMatrix.create_transition_matrix), [])
                self.assertEqual(params(Afforestation.gen_cbm_afforestation_dataframe), ["spared_area_breakdown"])


class Tables(unittest.TestCase):
    def check_landuse(self, case, tree):
        df = run_case(case)["landuse"]
        self.assertEqual(list(df.columns), ["farm_id", "year", "land_use", "area_ha"] + SHARES[tree])
        base = df[df.farm_id == -CAL]
        self.assertTrue((base.year == CAL).all())
        self.assertEqual(sorted(base.land_use), sorted(LAND_USES[tree]))
        scen = df[df.farm_id >= 0]
        self.assertTrue((scen.year == 2050).all())
        self.assertTrue(set(df.land_use) <= set(LAND_USES[tree]))

    def check_matrix(self, case, tree):
        tm = run_case(case)["transition_matrix"]
        uses = LAND_USES[tree]
        names = [f"{a.title()}_to_{b.title()}" for a, b in itertools.product(uses, uses)]
        self.assertEqual(sorted(tm.columns), sorted(names))
        self.assertIn(-CAL, list(tm.index))
        self.assertTrue(all(isinstance(i, int) or float(i).is_integer() for i in tm.index))
        self.assertTrue(set(LCA_TRANSITIONS) <= set(tm.columns))

    def check_afforestation(self, case):
        df = run_case(case)["afforestation"]
        self.assertEqual(list(df.columns), ["scenario", "species", "yield_class", "total_area"])
        self.assertTrue(set(df.species) <= {"Sitka", "SGB"})
        self.assertTrue(set(df.yield_class) <= {"YC6", "YC17_20", "YC20_24", "YC24_30"})

    def test_national(self):
        for case in ("national", "goblin_lite"):
            with self.subTest(case=case):
                self.check_landuse(case, "national")
                self.check_matrix(case, "national")
                self.check_afforestation(case)

    def test_geo(self):
        self.check_landuse("geo", "geo")
        self.check_matrix("geo", "geo")
        self.check_afforestation("geo")


class RewettedGrasslandStaysGrassland(unittest.TestCase):
    """Protected design rule (owner, 2026-11-23): rewetted organic grassland is not wetland.

    It stays in the grassland row (share_rewetted_rich/poor_organic), and landcover_lca charges it with the grassland
    rewetting factors. Grassland_to_Wetland is therefore 0, and the rewetted area is recorded in the spared-area log.
    """

    @staticmethod
    def rewetting(case="national"):
        """Return the logged rewetted area per scenario and the area added to the grassland rewetted shares."""
        out = run_case(case)
        log = out["spared_area_log"]
        logged = log[log.land_use == "rewet_grassland"].set_index("scenario").organic_area
        grass = out["landuse"][out["landuse"].land_use == "grassland"].set_index("farm_id")
        held = grass.area_ha * (grass.share_rewetted_rich_organic + grass.share_rewetted_poor_organic)
        return out, logged, held - held[-CAL]

    def test_rewetting_stays_in_grassland(self):
        out, logged, added = self.rewetting()
        self.assertTrue((logged > 0).any())
        self.assertTrue((out["transition_matrix"]["Grassland_to_Wetland"] == 0).all())
        lu = out["landuse"]
        wetland = lu[lu.land_use == "wetland"].set_index("farm_id").area_ha
        for sc in logged.index:
            with self.subTest(scenario=sc):
                self.assertAlmostEqual(wetland[sc], wetland[-CAL], places=6)   # the wetland row does not grow
                self.assertGreater(added[sc], 0)                               # the grassland rewetted shares do

    def test_logged_rewetting_is_in_grassland_without_spillover(self):
        _, logged, added = self.rewetting()
        for sc in (0, 1, 2):        # scenarios whose rewetting fits within the drained organic stock
            with self.subTest(scenario=sc):
                self.assertAlmostEqual(added[sc], logged[sc], delta=1e-3)

    @unittest.expectedFailure
    def test_logged_rewetting_is_in_grassland_with_spillover(self):
        """Finding 8: spillover past the drained organic stock is logged, not applied.

        In scenario 3 (all grassland spared), 314,200 ha is logged as rewetted but only 126,357 ha is added to the
        grassland rewetted shares (187,843 ha spillover).
        """
        _, logged, added = self.rewetting()
        self.assertAlmostEqual(added[3], logged[3], delta=1e-3)


if __name__ == "__main__":
    unittest.main()
