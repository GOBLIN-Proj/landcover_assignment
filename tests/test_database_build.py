"""Step 6: the package database is built by `tools/build_database.py` from `data_sources/`, and is reproducible.

- The committed database holds exactly what a fresh build gives (same tables, same rows, same values).
- Two builds give byte-identical files.
- Every column of every table the code reads has its unit, source and decision recorded in `column_metadata`;
  `build_info` records the hash of every input file.
- The D-decisions taken so far are in the data (D1, D2, D3, D5, D7); the columns still waiting for a decision say so.
"""
import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from _helpers import ROOT

sys.path.insert(0, str(ROOT / "tools"))
import build_database  # noqa: E402

from landcover_assignment.database import DATABASE_FILE, get_database_path  # noqa: E402

DATA_TABLES = ("forest_data", "grassland_data", "cropland_data", "wetland_data", "settlement_data")
CODE_TABLES = DATA_TABLES + ("NIR", "forest_soil_yield_mapping")
META_TABLES = ("build_info", "sources", "column_metadata", "inventory_values")


def dump(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return list(con.iterdump())
    finally:
        con.close()


def query(sql, *args, path=None):
    con = sqlite3.connect(f"file:{path or get_database_path()}?mode=ro", uri=True)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.first = Path(cls.tmp.name) / "a.db"
        cls.second = Path(cls.tmp.name) / "b.db"
        build_database.build(cls.first)
        build_database.build(cls.second)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_file_name_carries_the_version(self):
        self.assertEqual(DATABASE_FILE, f"land_use_database_{build_database.VERSION}.db")
        self.assertTrue(Path(get_database_path()).is_file())

    def test_committed_database_is_the_build(self):
        self.assertEqual(dump(get_database_path()), dump(self.first))

    def test_reproducible(self):
        self.assertEqual(hashlib.sha256(self.first.read_bytes()).hexdigest(),
                         hashlib.sha256(self.second.read_bytes()).hexdigest())

    def test_tables(self):
        names = {r[0] for r in query("SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertEqual(names, set(CODE_TABLES) | set(META_TABLES))

    def test_years(self):
        for table in DATA_TABLES:
            years = [r[0] for r in query(f"SELECT year FROM {table} ORDER BY year")]
            self.assertEqual(years, list(range(1990, 2025)), table)

    def test_every_column_has_metadata(self):
        meta = {(t, c): (unit, source, decision, status) for t, c, unit, source, decision, status in query(
            "SELECT table_name, column_name, unit, source_id, decision, status FROM column_metadata")}
        sources = {r[0] for r in query("SELECT source_id FROM sources")}
        for table in CODE_TABLES:
            for _, column, *_ in query(f"PRAGMA table_info({table})"):
                self.assertIn((table, column), meta, f"{table}.{column}")
                unit, source, decision, status = meta[(table, column)]
                self.assertTrue(unit, f"{table}.{column} unit")
                self.assertIn(source, sources, f"{table}.{column} source")
                self.assertIn(status, ("inventory", "derived", "pending", "key", "parameter"), f"{table}.{column}")
                if status == "pending":
                    self.assertTrue(decision.startswith("pending D"), f"{table}.{column}: {decision}")

    def test_build_info_hashes_the_inputs(self):
        info = dict(query("SELECT key, value FROM build_info"))
        self.assertEqual(info["package_version"], build_database.VERSION)
        for path in build_database.INPUTS:
            self.assertEqual(info[f"sha256:{path}"], hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), path)

    def test_inventory_values_keep_notation_keys(self):
        (n,) = query("SELECT count(*) FROM inventory_values WHERE quantity = '4.B.organic_area' AND notation = 'NO'")[0]
        self.assertEqual(n, 35)


def value(table, column, year=2020):
    return query(f"SELECT {column} FROM {table} WHERE year = ?", year)[0][0]


class Decisions(unittest.TestCase):
    def test_d3_forest(self):
        """Forest: CRT 4.A total and mineral; NID 6.7 + 6.15 drained N-poor and N-rich."""
        total = value("forest_data", "total_kha")
        self.assertAlmostEqual(total, 798.747, places=3)
        self.assertAlmostEqual(value("forest_data", "mineral_kha") / total, 0.4596, places=4)
        self.assertAlmostEqual(value("forest_data", "organic_emitting_kha"), 178.4 + 109.0, places=6)
        self.assertAlmostEqual(value("forest_data", "organo_mineral_emitting_kha"), 63.5 + 33.9, places=6)

    def test_d3_forest_interpolated_years(self):
        """Years the NID doesn't print (e.g. 1993) are interpolated linearly between printed years, per category."""
        poor_1990, poor_1995 = 67.4 + 155.8, value("forest_data", "organic_emitting_kha", 1995)
        have = value("forest_data", "organic_emitting_kha", 1993)
        self.assertAlmostEqual(have, poor_1990 + (poor_1995 - poor_1990) * 3 / 5, places=6)

    def test_d5_grassland_rewet_status(self):
        """Our rewet-status columns hold CRT 4(II).C.1 'Other organic soils' (203.3 kha); rich/poor 0.45/0.55 (D4)."""
        rich, poor = value("grassland_data", "rewetted_rich_organic_kha"), value("grassland_data", "rewetted_poor_organic_kha")
        self.assertAlmostEqual(rich + poor, 203.291, places=3)
        self.assertAlmostEqual(rich / (rich + poor), 0.45, places=12)

    def test_d7_cropland_and_settlement(self):
        self.assertAlmostEqual(value("cropland_data", "total_kha"), 747.698, places=3)
        self.assertEqual(value("cropland_data", "organic_kha"), 0.0)                 # CRT: NO
        self.assertAlmostEqual(value("settlement_data", "organic_kha"), 2.0, places=6)

    def test_d1_industrial_peat(self):
        self.assertAlmostEqual(value("wetland_data", "industrial_peat_extraction_kha"), 55.515, places=3)   # 4(II)

    def test_d2_wetland(self):
        self.assertAlmostEqual(value("wetland_data", "total_kha"), 1212.500, places=3)
        self.assertAlmostEqual(value("wetland_data", "unmanaged_wetland_kha"), 108.364, places=3)

    def test_pending_burnt_area(self):
        """Burnt area waits for D6: 1990-2022 as in 0.4.0 (CRF 2024), 2023-2024 empty."""
        self.assertAlmostEqual(value("forest_data", "burnt_kha"), 0.177653407915582, places=15)
        self.assertIsNone(value("forest_data", "burnt_kha", 2024))


if __name__ == "__main__":
    unittest.main()
