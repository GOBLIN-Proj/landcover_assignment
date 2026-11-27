"""Step 6: the package database is built by `tools/build_database.py` from `data_sources/`, and is reproducible.

- The committed database holds exactly what a fresh build gives (same tables, same rows, same values).
- Two builds give byte-identical files.
- Every column of every table the code reads has its unit, source and decision recorded in `column_metadata`;
  `build_info` records the hash of every input file.
- The D-decisions taken so far are in the data (D1, D2, D3, D4, D5, D7); the columns still waiting for a decision say so.
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
from landcover_assignment.resource_manager.units import KHA_TO_HA  # noqa: E402

DATA_TABLES = ("forest_data", "grassland_data", "cropland_data", "wetland_data", "settlement_data")
CODE_TABLES = DATA_TABLES + ("NIR", "forest_soil_yield_mapping", "managed_forest_data", "forest_fire_rate")
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


def rich_fraction(row, year):
    rich, poor = (value("grassland_data", f"{row}_{kind}_organic_kha", year) for kind in ("rich", "poor"))
    return rich / (rich + poor)


def factors():
    df = build_database.read_csv("data_sources/nid2026_grassland_organic_factors.csv")
    return dict(zip(df.name, df.value))


def crt_values(quantity):
    df = build_database.read_csv("data_sources/inventory_areas.csv")
    return df[df.quantity == quantity].set_index("year").value.to_dict()


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
        """Our rewet-status columns hold CRT 4(II).C.1 'Other organic soils' (203.3 kha)."""
        rich, poor = value("grassland_data", "rewetted_rich_organic_kha"), value("grassland_data", "rewetted_poor_organic_kha")
        self.assertAlmostEqual(rich + poor, 203.291, places=3)

    def test_d4_grassland_rich_fraction(self):
        """Rich fraction of each grassland organic row, by year, from its CRT CH4 implied factor and the NID factors."""
        for year, drained, rewet in ((2020, 0.4525, 0.4471), (2024, 0.4493, 0.4493), (1990, 0.5507, 0.4262)):
            with self.subTest(year=year):
                self.assertAlmostEqual(rich_fraction("drained", year), drained, places=4)
                self.assertAlmostEqual(rich_fraction("rewetted", year), rewet, places=4)

    def test_d4_split_reproduces_crt_on_site_carbon(self):
        """Independent check: the rich and poor on-site carbon factors differ, so only the right split reproduces CRT
        Table4.C 4.C.1 organic soil carbon. It does in every year (the fixed 0.45 was 0.3% off in 2020)."""
        f = factors()
        carbon = crt_values("4.C.1.organic_soil_C")
        for year in range(1990, 2025):
            with self.subTest(year=year):
                kt_c = sum(value("grassland_data", f"{row}_{kind}_organic_kha", year) * f[f"ef_co2_{name}_on_site_{kind}"]
                           for row, name in (("drained", "drained"), ("rewetted", "rewet_status"))
                           for kind in ("rich", "poor"))
                self.assertAlmostEqual(kt_c / -carbon[year], 1.0, delta=1e-4)

    def test_d7_cropland_and_settlement(self):
        self.assertAlmostEqual(value("cropland_data", "total_kha"), 747.698, places=3)
        self.assertEqual(value("cropland_data", "organic_kha"), 0.0)                 # CRT: NO
        self.assertAlmostEqual(value("settlement_data", "organic_kha"), 2.0, places=6)

    def test_d1_industrial_peat(self):
        self.assertAlmostEqual(value("wetland_data", "industrial_peat_extraction_kha"), 55.515, places=3)   # 4(II)

    def test_d2_wetland(self):
        self.assertAlmostEqual(value("wetland_data", "total_kha"), 1212.500, places=3)
        self.assertAlmostEqual(value("wetland_data", "unmanaged_wetland_kha"), 108.364, places=3)

    def test_pending_forest_burnt_area(self):
        """forest_data.burnt_kha (read only by the catchment tree, see .artifacts/geo_todo.md G1): CRF 2024 Table4(V)
        4.A.1 wildfires, 1990-2022, 2023-2024 empty. The national forest row uses cbm_runner's fire (D6a)."""
        crf = crf_burnt("A.1.wildfires")
        for year in range(1990, 2023):
            self.assertAlmostEqual(value("forest_data", "burnt_kha", year), crf[year] / KHA_TO_HA, places=15, msg=year)
        self.assertAlmostEqual(value("forest_data", "burnt_kha"), 0.177653407915582, places=12)   # as in 0.4.0
        self.assertIsNone(value("forest_data", "burnt_kha", 2023))
        self.assertIsNone(value("forest_data", "burnt_kha", 2024))
        (source,) = query("SELECT source_id FROM column_metadata WHERE table_name = 'forest_data' "
                          "AND column_name = 'burnt_kha'")[0]
        self.assertEqual(source, "CRF2024")


class Sources(unittest.TestCase):
    def test_no_legacy_inputs(self):
        """Every value comes from a published source: nothing is copied from the 0.4.0 database any more."""
        self.assertFalse(any("legacy" in p for p in build_database.INPUTS))
        self.assertFalse(list((ROOT / "data_sources").glob("legacy_*")))

    def test_every_source_is_used(self):
        used = {r[0] for r in query("SELECT source_id FROM column_metadata UNION SELECT source_id FROM inventory_values")}
        self.assertEqual({r[0] for r in query("SELECT source_id FROM sources")}, used)

    def test_urls(self):
        """Each source has a link to the published document where one has been checked; empty otherwise."""
        urls = dict(query("SELECT source_id, url FROM sources"))
        for source, url in urls.items():
            self.assertTrue(url == "" or url.startswith("https://"), source)
        for source in ("CRT2026", "NID2026", "CRF2024", "CBM061", "PACKAGE"):
            self.assertTrue(urls[source], source)


def crf_burnt(code):
    """CRF 2024 Table4(V) burnt area (ha) by year; a notation key (NO) is 0."""
    df = build_database.read_csv("data_sources/inventory_areas.csv")
    rows = df[df.quantity == f"burnt_area.4.{code}"].set_index("year")
    return {int(y): (0.0 if r.notation else r.value) for y, r in rows.iterrows()}


class BurntAreaD6b(unittest.TestCase):
    """D6b: burnt area of grassland (4.C.1), wetland (4.D.1) and cropland (4.B.1), in kha."""
    CODES = {"grassland_data": ("C.1", "4(IV).C.1.wildfires.ch4"), "wetland_data": ("D.1", "4(IV).D.1.wildfires.ch4"),
             "cropland_data": ("B.1", None)}

    def test_1990_2022_is_crf_2024_with_no_as_zero(self):
        for table, (code, _) in self.CODES.items():
            crf = crf_burnt(code)
            for year in range(1990, 2023):
                with self.subTest(table=table, year=year):
                    self.assertAlmostEqual(value(table, "burnt_kha", year) * KHA_TO_HA, crf[year], places=9)
        self.assertEqual(value("cropland_data", "burnt_kha", 2013), 0.0)        # CRF: NO

    def test_2023_2024_grassland_wetland_from_crt_ch4(self):
        """CRT 2026 wildfire CH4 / mean implied CH4 per ha burnt in 2020-2022."""
        for table in ("grassland_data", "wetland_data"):
            code, ch4_quantity = self.CODES[table]
            crf, ch4 = crf_burnt(code), crt_values(ch4_quantity)
            factor = sum(ch4[y] / crf[y] for y in (2020, 2021, 2022)) / 3
            for year in (2023, 2024):
                with self.subTest(table=table, year=year):
                    self.assertAlmostEqual(value(table, "burnt_kha", year) * KHA_TO_HA, ch4[year] / factor, places=9)
        self.assertAlmostEqual(value("grassland_data", "burnt_kha", 2023) * KHA_TO_HA, 1632.8, places=1)
        self.assertAlmostEqual(value("wetland_data", "burnt_kha", 2023) * KHA_TO_HA, 780.1, places=1)

    def test_2023_2024_cropland_is_the_2020_2022_mean(self):
        """Cropland CH4 per ha burnt is too inconsistent to back-calculate; 2023-2024 = mean CRF area 2020-2022."""
        crf = crf_burnt("B.1")
        mean = sum(crf[y] for y in (2020, 2021, 2022)) / 3
        self.assertAlmostEqual(mean, 42.857, places=3)
        for year in (2023, 2024):
            self.assertAlmostEqual(value("cropland_data", "burnt_kha", year) * KHA_TO_HA, mean, places=9)

    def test_settlement_is_zero(self):
        self.assertEqual({r[0] for r in query("SELECT burnt_kha FROM settlement_data")}, {0.0})

    def test_metadata(self):
        meta = {(t, c): (s, st, d) for t, c, s, st, d in query(
            "SELECT table_name, column_name, source_id, status, decision FROM column_metadata "
            "WHERE column_name = 'burnt_kha'")}
        for table in self.CODES:
            self.assertEqual(meta[(table, "burnt_kha")][:2], ("CRF2024", "derived"), table)
            self.assertTrue(meta[(table, "burnt_kha")][2].startswith("D6b"), table)
        self.assertEqual(meta[("settlement_data", "burnt_kha")][:2], ("PACKAGE", "parameter"))
        (n,) = query("SELECT count(*) FROM inventory_values WHERE quantity LIKE 'burnt_area.%' "
                     "AND source_id != 'CRF2024'")[0]
        self.assertEqual(n, 0)

class NIRTableD8(unittest.TestCase):
    """D8: the `NIR` table is Table4.1 final area by land category, CRT 2026, 1990-2024, in kha (0.4.0 held the
    CRF 2024 'Initial area' under scrambled years). Columns and labels are unchanged."""
    LABELS = {"Forest land (managed)(2)": "forest_managed", "Cropland(2)": "cropland",
              "Grassland (managed)(2)": "grassland_managed", "Wetlands (managed)(2)": "wetlands_managed",
              "Wetlands (unmanaged)(2)": "wetlands_unmanaged", "Settlements(2)": "settlements",
              "Other land(2)": "other_land"}

    def test_shape(self):
        rows = query('SELECT "Year", "Land_cover" FROM "NIR" ORDER BY rowid')
        self.assertEqual(len(rows), 35 * 7)
        self.assertEqual(sorted({y for y, _ in rows}), list(range(1990, 2025)))
        self.assertEqual([l for y, l in rows if y == 1990], list(self.LABELS))

    def test_values_are_crt_2026_final_area(self):
        for label, name in self.LABELS.items():
            crt = crt_values(f"4.1.final_area.{name}")
            have = dict(query('SELECT "Year", "Area_kha" FROM "NIR" WHERE "Land_cover" = ?', label))
            for year in range(1990, 2025):
                with self.subTest(label=label, year=year):
                    self.assertEqual(have[year], crt[year])

    def test_known_values(self):
        def area(label, year):
            return query('SELECT "Area_kha" FROM "NIR" WHERE "Land_cover" = ? AND "Year" = ?', label, year)[0][0]
        self.assertAlmostEqual(area("Forest land (managed)(2)", 2020), 798.747, places=3)    # = forest_data 2020
        self.assertAlmostEqual(area("Grassland (managed)(2)", 2020), 4218.508, places=3)
        self.assertAlmostEqual(area("Wetlands (unmanaged)(2)", 2020), 108.364, places=3)
        # Table4.1 and Table4.A agree to rounding (1e-7 kha)
        self.assertAlmostEqual(area("Forest land (managed)(2)", 2020), value("forest_data", "total_kha"), places=6)

    def test_total_land_is_constant(self):
        totals = query('SELECT "Year", SUM("Area_kha") FROM "NIR" GROUP BY "Year"')
        for year, total in totals:
            self.assertAlmostEqual(total, 7111.78536, places=4, msg=year)

    def test_metadata(self):
        meta = query("SELECT column_name, source_id, status, decision FROM column_metadata WHERE table_name = 'NIR'")
        self.assertEqual({c for c, *_ in meta}, {"Year", "Land_cover", "Area_kha"})
        for column, source, status, decision in meta:
            self.assertEqual((source, status), ("CRT2026", "inventory"), column)
            self.assertTrue(decision.startswith("D8"), column)


if __name__ == "__main__":
    unittest.main()
