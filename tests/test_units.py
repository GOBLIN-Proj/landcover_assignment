"""Unit conversions live in one place, `landcover_assignment.resource_manager.units` (the landcover_lca pattern).

The database stores every value in its published unit (CRT areas in kha) and names that unit in `column_metadata`.
The readers convert on read, column by column, using that unit and the `UNITS` table.
"""
import sqlite3
import unittest

import pandas as pd

from landcover_assignment.database import get_database_path
from landcover_assignment.resource_manager import units
from landcover_assignment.resource_manager.database_manager import DataManager


def metadata_units():
    con = sqlite3.connect(f"file:{get_database_path()}?mode=ro", uri=True)
    try:
        return con.execute("SELECT table_name, column_name, unit FROM column_metadata").fetchall()
    finally:
        con.close()


def raw(table):
    con = sqlite3.connect(f"file:{get_database_path()}?mode=ro", uri=True)
    try:
        return pd.read_sql(f'SELECT * FROM "{table}"', con)
    finally:
        con.close()


class Units(unittest.TestCase):
    def test_every_database_unit_is_known(self):
        for table, column, unit in metadata_units():
            self.assertTrue(unit in units.UNITS or unit in units.NOT_CONVERTED, f"{table}.{column}: {unit!r}")

    def test_conversions(self):
        self.assertEqual(units.to_model_units(1.5, "kha"), 1500.0)
        self.assertEqual(units.model_unit("kha"), "ha")
        self.assertEqual(units.to_model_units(2.0, "ha"), 2.0)
        with self.assertRaises(KeyError):
            units.to_model_units(1.0, "acre")

    def test_ch4_c_to_ch4(self):
        """The NID prints the grassland rewet-status CH4 factors in kg CH4-C (D4 converts them to kg CH4)."""
        self.assertEqual(units.CH4_C_TO_CH4, 16.0 / 12.0)

    def test_readers_convert_by_the_recorded_unit(self):
        """Each area column comes back in ha: the database value (kha) x 1000, the same bits as before."""
        dm = DataManager()
        readers = {"forest_data": dm.get_national_forest_areas, "grassland_data": dm.get_national_grassland_areas,
                   "cropland_data": dm.get_national_cropland_areas, "wetland_data": dm.get_national_wetland_areas,
                   "settlement_data": dm.get_national_settlement_areas}
        for table, read in readers.items():
            have, db = read(), raw(table).set_index("year")
            for column in db.columns:
                pd.testing.assert_series_equal(have[column], db[column] * 1000, check_exact=True, obj=column)
        nir = dm.get_national_inventory_areas()
        pd.testing.assert_series_equal(nir["Area_kha"], raw("NIR").set_index("Year")["Area_kha"] * 1000,
                                       check_exact=True)


if __name__ == "__main__":
    unittest.main()
