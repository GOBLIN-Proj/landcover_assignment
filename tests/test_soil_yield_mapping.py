"""D9: the soil group -> yield class table (`forest_soil_yield_mapping`) is the one source of the afforestation
yield classes.

- Its values follow Upton et al. (2013) Table 2 (NFS soil category -> expected Sitka spruce yield class, from the
  Farrelly et al. 2011 productivity model), with the six NFS categories read as three soil groups (inferred pairing,
  to be confirmed): group 1 = YC 24, group 2 = YC 20, group 3 = YC 18 (and 14).
- The zero-area template rows at the top of the afforestation table come from the same table (no second copy).
- Its provenance is recorded in the database.
"""
import re
import sqlite3
import unittest
from pathlib import Path

import pandas as pd

from _helpers import ROOT

from landcover_assignment.afforestation import Afforestation
from landcover_assignment.database import get_database_path
from landcover_assignment.resource_manager.data_loader import Loader
from landcover_assignment.resource_manager.landcover_data_manager import DataManager

UPTON_YC = {1: 24, 2: 20, 3: 18}     # Upton et al. (2013) Table 2, soil categories 1, 3 and 5


def query(sql):
    con = sqlite3.connect(f"file:{get_database_path()}?mode=ro", uri=True)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def band(label):
    low, high = (int(x) for x in re.fullmatch(r"YC(\d+)_(\d+)", label).groups())
    return low, high


class Values(unittest.TestCase):
    def test_table(self):
        mapping = Loader().forest_soil_yield_mapping()
        self.assertEqual(list(mapping.itertuples(index=False, name=None)),
                         [(3, "Sitka", "YC17_20"), (2, "Sitka", "YC20_24"), (1, "Sitka", "YC24_30"),
                          (1, "SGB", "YC6"), (2, "SGB", "YC6"), (3, "SGB", "YC6")])

    def test_sitka_bands_hold_upton_yield_classes(self):
        mapping = Loader().forest_soil_yield_mapping()
        for group, yc in UPTON_YC.items():
            label = mapping[(mapping.species == "Sitka") & (mapping.soil_group == group)].yield_class.item()
            low, high = band(label)
            self.assertTrue(low <= yc <= high, f"group {group}: {label} vs Upton YC {yc}")


class OneSource(unittest.TestCase):
    def expected(self):
        mapping = Loader().forest_soil_yield_mapping()
        return {"scenario": [-1] * len(mapping), "species": list(mapping.species),
                "yield_class": list(mapping.yield_class), "total_area": [0.0] * len(mapping)}

    def test_template_rows_come_from_the_table(self):
        aff = Afforestation(2020, 2050, pd.DataFrame(), pd.DataFrame())
        pd.testing.assert_frame_equal(aff.cbm_dataframe_structure(), pd.DataFrame(self.expected()))

    def test_get_cbm_default_data_comes_from_the_table(self):
        dm = DataManager(2020, 2050)
        self.assertEqual(dm.get_cbm_default_data(), self.expected())
        self.assertEqual(dm.cbm_default_data, self.expected())

    def test_no_hard_coded_yield_classes(self):
        for path in (ROOT / "src/landcover_assignment/resource_manager/landcover_data_manager.py",
                     ROOT / "src/landcover_assignment/afforestation.py"):
            self.assertIsNone(re.search(r'"YC\d', Path(path).read_text()), path.name)


class Provenance(unittest.TestCase):
    def test_metadata(self):
        rows = query("SELECT column_name, source_id, status, decision FROM column_metadata "
                     "WHERE table_name = 'forest_soil_yield_mapping'")
        self.assertEqual({r[0] for r in rows}, {"soil_group", "species", "yield_class"})
        for column, source, status, decision in rows:
            self.assertEqual((source, status), ("UPTON2013", "parameter"), column)
            self.assertTrue(decision.startswith("D9"), column)

    def test_source(self):
        (citation,) = query("SELECT citation FROM sources WHERE source_id = 'UPTON2013'")[0]
        self.assertIn("Upton", citation)
        self.assertIn("Table 2", citation)


if __name__ == "__main__":
    unittest.main()
