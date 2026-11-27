"""Names are spelt correctly in the source, the README and the docs pages.

Misspellings found in the 0.5.0 sweep are listed in MISSPELT; none may come back. Lines that keep an old name
working on purpose carry the marker DEPRECATED_NAME. The public names that changed keep working for one release,
with a DeprecationWarning:
- resource_manager.database_manager.DataManager.data_engine_creater -> data_engine_creator
- NationalLandCover.get_national_rich_drained_orgainc_grassland -> get_national_rich_drained_organic_grassland
- geo LandCover.catchemnt_class -> catchment_class
- LandCover.spared_area_breakdown(..., intial_spared_area=...) -> initial_spared_area (national and geo)
"""
import re
import unittest
import warnings

from _helpers import ROOT


def call_warns(test, func, *args, **kwargs):
    """Call func and check it raised a DeprecationWarning. (unittest's assertWarns scans every loaded module, which
    trips Pyomo's deferred optional imports, so the warnings are recorded directly.)"""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = func(*args, **kwargs)
    test.assertTrue(any(issubclass(w.category, DeprecationWarning) for w in caught), "no DeprecationWarning")
    return result

MISSPELT = ["creater", "intial", "orgainc", "catchemnt", "conditon", "invetory"]
PATTERN = re.compile("|".join(MISSPELT), re.IGNORECASE)


def hits_in(paths):
    hits = []
    for path in paths:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PATTERN.search(line) and "DEPRECATED_NAME" not in line:
                hits.append(f"{path.relative_to(ROOT)}:{n}")
    return hits


class NoMisspellings(unittest.TestCase):
    def test_source(self):
        self.assertEqual(hits_in(sorted((ROOT / "src").rglob("*.py"))), [])

    def test_readme_and_docs(self):
        pages = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        self.assertEqual(hits_in(pages), [])


class OldNamesStillWork(unittest.TestCase):
    def test_data_engine_creater(self):
        from landcover_assignment.resource_manager.database_manager import DataManager
        dm = DataManager()
        engine = call_warns(self, dm.data_engine_creater)
        self.assertEqual(str(engine.url), str(dm.data_engine_creator().url))

    def test_rich_drained_organic_grassland(self):
        from landcover_assignment.national_landcover import NationalLandCover
        nlc = NationalLandCover()
        old = call_warns(self, nlc.get_national_rich_drained_orgainc_grassland, "grassland", 2020)
        self.assertEqual(old, nlc.get_national_rich_drained_organic_grassland("grassland", 2020))

    def test_catchemnt_class(self):
        from landcover_assignment.geo_landcover_assignment.geo_landcover import LandCover
        from _helpers import load_geo
        land = LandCover(2020, 2050, *load_geo())
        self.assertIs(call_warns(self, getattr, land, "catchemnt_class"), land.catchment_class)

    def test_intial_spared_area_keyword(self):
        from landcover_assignment.landcover import LandCover
        from _helpers import load_national
        land = LandCover(2020, 2050, *load_national())
        args = dict(scenario=0, actual_rewetted_area=0.0, actual_mineral_area=1000.0)
        new = land.spared_area_breakdown(initial_spared_area=1000.0, **args)
        old = call_warns(self, land.spared_area_breakdown, intial_spared_area=1000.0, **args)
        self.assertEqual(old, new)


if __name__ == "__main__":
    unittest.main()
