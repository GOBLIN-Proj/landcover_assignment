"""Build the package database, `src/landcover_assignment/database/land_use_database_<version>.db`, from `data_sources/`.

Every value the code reads comes from a file in `data_sources/` through a rule written down in this script, and the
database records where it came from:

- `column_metadata`: for every column of every table the code reads, its unit, meaning, source, cell reference,
  transformation, the decision behind it (D1-D10, see the step 6 dossier) and a status (`inventory`, `derived`,
  `parameter`, `pending` or `key`);
- `sources`: the documents behind the source ids;
- `inventory_values`: every inventory value extracted (long format, with notation keys such as NO, NA, IE);
- `build_info`: the package version and the SHA-256 of every input file.

The tables the code reads keep their 0.4.0 names and columns. Areas are in kha, 1990-2024 (CRT 2026 years).

Decided (owner, 2026-11-23/24):
- D1: industrial peat extraction = CRT 4(II) row 48. Table4.D row 14 is 42.7 kha larger (2020); that area carries only
  the tonnage-based horticultural peat carbon (assumed to be private, non-Bord na Mona, horticultural production). It
  stays in the wetland total, in no sub-share.
- D2: wetland total = CRT 4.D total; unmanaged wetland = CRT 4.D row 20.
- D3: forest total and mineral area = CRT 4.A; drained N-poor (`organic_emitting_kha`) and N-rich
  (`organo_mineral_emitting_kha`) = NID 2026 Tables 6.7 + 6.15, 4.A.1 + 4.A.2. Years the NID does not print are
  interpolated linearly per category. The forest mineral share is mineral / total (0.46 in 2020).
- D5: our grassland rewet-status columns keep their names and meaning (NID s.6.5.2) and are filled from CRT 4(II).C.1
  "Other organic soils" (CRT 2026 reports "Rewetted organic soils" as NO).
- D7: cropland and settlement from CRT 4.B and 4.E. A notation key (NO) is stored as 0 in the data tables and kept in
  `inventory_values`.

Pending (values kept from the 0.4.0 database, CRF 2024 vintage; see tools/export_legacy_columns.py):
- D4: the grassland rich/poor split, 0.45/0.55 of the CRT drained and rewet-status areas;
- D6: burnt area (`burnt_kha`), 1990-2022; 2023-2024 empty (NULL);
- D8: the `NIR` table (unused by the code);
- D9: `forest_soil_yield_mapping`.

Two builds give byte-identical files (same SQLite library). Usage, from the repo root:
    .venv/bin/python tools/build_database.py
"""
import hashlib
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.5.0"
OUTPUT = ROOT / f"src/landcover_assignment/database/land_use_database_{VERSION}.db"
YEARS = list(range(1990, 2025))
INPUTS = ("data_sources/inventory_areas.csv", "data_sources/nid2026_forest_organic_soils.csv",
          "data_sources/legacy_burnt_area.csv", "data_sources/legacy_nir_table.csv",
          "data_sources/forest_soil_yield_mapping.csv", "tools/build_database.py")
GRASSLAND_RICH = 0.45      # D4 pending: share of drained and rewet-status grassland organic soil that is nutrient rich

SOURCES = [
    ("CRT2026", "EPA Ireland, Common Reporting Tables 2026 (IRL-CRT-2026-V1.0, one workbook per year, 1990-2024), "
                "extracted by tools/extract_inventory.py into data_sources/inventory_areas.csv"),
    ("NID2026", "EPA Ireland, National Inventory Document 2026, Table 6.7 p.217 (4.A.1) and Table 6.15 p.231 (4.A.2), "
                "transcribed by tools/transcribe_nid_forest.py into data_sources/nid2026_forest_organic_soils.csv"),
    ("LEGACY040", "landcover_assignment 0.4.0 database land_use_database.db (CRF 2024 vintage, git 25a83b4), "
                  "exported by tools/export_legacy_columns.py into data_sources/legacy_*.csv and "
                  "forest_soil_yield_mapping.csv"),
    ("PACKAGE", "landcover_assignment parameter or key, set in tools/build_database.py"),
]

# Column recipes. Each entry: column -> (kind, argument, unit, description, decision)
#   crt: CRT quantity in data_sources/inventory_areas.csv (notation key -> 0)
#   crt_share: (CRT quantity, factor)
#   nid: NID column, 4.A.1 + 4.A.2, interpolated between printed years
#   legacy_burnt: data_sources/legacy_burnt_area.csv
REFRESH = "refresh: CRF 2024 -> CRT 2026"
D6 = "pending D6: burnt area (CRF 2024 vintage, 1990-2022; 2023-2024 NULL)"
TABLES = {
    "forest_data": {
        "total_kha": ("crt", "4.A.area", "kha", "forest land, total area", "D3"),
        "mineral_kha": ("crt", "4.A.mineral_area", "kha", "forest land on mineral soil (incl. its open area)", "D3"),
        "organic_kha": ("crt", "4.A.organic_area", "kha", "forest land on organic soil (drained N-poor, drained N-rich "
                        "and open area); not read by the code", "D3"),
        "burnt_kha": ("legacy_burnt", "forest_data", "kha", "burnt forest area (CRF 2024 Table4(V) 4.A.1 wildfires)", D6),
        "organic_emitting_kha": ("nid", "drained_n_poor_organic_kha", "kha",
                                 "drained N-poor organic forest soil (emits from drainage); forest share_organic", "D3"),
        "organo_mineral_emitting_kha": ("nid", "drained_n_rich_organo_mineral_kha", "kha",
                                        "drained N-rich organo-mineral forest soil (emits from drainage); forest "
                                        "share_organic_mineral", "D3"),
    },
    "grassland_data": {
        "total_kha": ("crt", "4.C.area", "kha", "grassland, total area (national; the grassland row is the herd area "
                      "plus the balance to this, docs/grassland_area.md)", REFRESH),
        "mineral_kha": ("crt", "4.C.mineral_area", "kha", "grassland on mineral soil", REFRESH),
        "organic_kha": ("crt", "4.C.organic_area", "kha", "grassland on organic soil", REFRESH),
        "drained_rich_organic_kha": ("crt_share", ("4(II).C.1.drained.area", GRASSLAND_RICH), "kha",
                                     "drained nutrient-rich organic grassland soil",
                                     "pending D4: rich share 0.45 of CRT 4(II).C.1 drained"),
        "drained_poor_organic_kha": ("crt_share", ("4(II).C.1.drained.area", 1 - GRASSLAND_RICH), "kha",
                                     "drained nutrient-poor organic grassland soil",
                                     "pending D4: poor share 0.55 of CRT 4(II).C.1 drained"),
        "rewetted_rich_organic_kha": ("crt_share", ("4(II).C.1.other.area", GRASSLAND_RICH), "kha",
                                      "nutrient-rich organic grassland soil with rewet status (NID s.6.5.2; CRT 2026 "
                                      "'Other organic soils')", "D5; pending D4: rich share 0.45"),
        "rewetted_poor_organic_kha": ("crt_share", ("4(II).C.1.other.area", 1 - GRASSLAND_RICH), "kha",
                                      "nutrient-poor organic grassland soil with rewet status (NID s.6.5.2; CRT 2026 "
                                      "'Other organic soils')", "D5; pending D4: poor share 0.55"),
        "burnt_kha": ("legacy_burnt", "grassland_data", "kha", "burnt grassland area", D6),
    },
    "cropland_data": {
        "total_kha": ("crt", "4.B.area", "kha", "cropland, total area", "D7"),
        "mineral_kha": ("crt", "4.B.mineral_area", "kha", "cropland on mineral soil", "D7"),
        "organic_kha": ("crt", "4.B.organic_area", "kha", "cropland on organic soil (CRT: NO -> 0)", "D7"),
        "burnt_kha": ("legacy_burnt", "cropland_data", "kha", "burnt cropland area", D6),
    },
    "wetland_data": {
        "total_kha": ("crt", "4.D.area", "kha", "wetland, total area (managed + unmanaged; = CRT Table4.1)", "D2"),
        "mineral_kha": ("crt", "4.D.mineral_area", "kha", "wetland on mineral soil", "D2"),
        "organic_kha": ("crt", "4.D.organic_area", "kha", "wetland on organic soil", "D2"),
        "domestic_peat_extraction_kha": ("crt", "4(II).D.domestic_peat_extraction.area", "kha",
                                         "drained domestic peat extraction", REFRESH),
        "industrial_peat_extraction_kha": ("crt", "4(II).D.industrial_peat_extraction.area", "kha",
                                           "drained industrial peat extraction, the area charged per-hectare drainage "
                                           "emissions. Table4.D row 14 is larger (2020: 98.3 vs 55.5 kha); the "
                                           "difference, assumed private horticultural production, carries only "
                                           "tonnage-based carbon and is in the total but in no sub-share", "D1"),
        "rewetted_domestic_peat_kha": ("crt", "4.D.other_domestic_peat_extraction.area", "kha",
                                       "rewetted domestic peat extraction (CRT 'Other Domestic Peat Extraction')",
                                       REFRESH),
        "rewetted_industrial_peat_kha": ("crt", "4.D.rewetted_industrial_peat_extraction.area", "kha",
                                         "rewetted industrial peat extraction", REFRESH),
        "rewetted_mineral_kha": ("crt", "4.D.2.mineral_area", "kha",
                                 "land converted to wetland, mineral soil (CRT 4.D.2; the column name says "
                                 "'rewetted', the 0.4.0 values were also 4.D.2)", REFRESH),
        "rewetted_organic_kha": ("crt", "4.D.2.organic_area", "kha",
                                 "land converted to wetland, organic soil (CRT 4.D.2; see rewetted_mineral_kha)",
                                 REFRESH),
        "near_natural_wetland_kha": ("crt", "4.D.near_natural_wetlands.area", "kha", "near-natural wetland", "D2"),
        "unmanaged_wetland_kha": ("crt", "4.D.unmanaged_wetlands.area", "kha", "unmanaged wetland", "D2"),
        "burnt_kha": ("legacy_burnt", "wetland_data", "kha", "burnt wetland area", D6),
    },
    "settlement_data": {
        "total_kha": ("crt", "4.E.area", "kha", "settlement, total area", "D7"),
        "mineral_kha": ("crt", "4.E.mineral_area", "kha", "settlement on mineral soil", "D7"),
        "organic_kha": ("crt", "4.E.organic_area", "kha", "settlement on organic soil (NO in some years -> 0)", "D7"),
        "burnt_kha": ("legacy_burnt", "settlement_data", "kha", "burnt settlement area (0 in 0.4.0)", D6),
    },
}
OTHER_COLUMNS = [   # (table, column, unit, description, source, transformation, decision, status)
    ("NIR", "Year", "year", "inventory year", "LEGACY040", "copied", "pending D8: rebuild from Table4.1 or drop",
     "pending"),
    ("NIR", "Land_cover", "label", "Table4.1 land category label", "LEGACY040", "copied",
     "pending D8: rebuild from Table4.1 or drop", "pending"),
    ("NIR", "Area_kha", "kha", "Table4.1 area (scrambled years in 0.4.0; unused by the code)", "LEGACY040", "copied",
     "pending D8: rebuild from Table4.1 or drop", "pending"),
    ("forest_soil_yield_mapping", "soil_group", "group", "spared-area soil group (1-3)", "LEGACY040", "copied",
     "pending D9: document source (Farrelly & Gallagher 2015)", "pending"),
    ("forest_soil_yield_mapping", "species", "label", "tree species (Sitka spruce, SGB)", "LEGACY040", "copied",
     "pending D9: document source (Farrelly & Gallagher 2015)", "pending"),
    ("forest_soil_yield_mapping", "yield_class", "label", "CBM yield class", "LEGACY040", "copied",
     "pending D9: document source (Farrelly & Gallagher 2015)", "pending"),
]


NUMERIC = {"year", "Year", "value", "Area_kha", "soil_group", "total_area_kha", "mineral_kha", "organic_kha",
           "open_area_kha", "drained_n_poor_organic_kha", "drained_n_rich_organo_mineral_kha"}


def read_csv(path):
    """Read a data_sources CSV. Numbers are parsed with Python's float(), which is exact (shortest round-trip repr)
    on every pandas version; empty cells become NaN in numeric columns and "" elsewhere."""
    df = pd.read_csv(ROOT / path, dtype=str, keep_default_na=False)
    for column in df.columns:
        if column in NUMERIC:
            df[column] = [float(v) if v != "" else float("nan") for v in df[column]]
    return df


def sha256(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def crt_series(inventory, quantity):
    rows = inventory[inventory.quantity == quantity].set_index("year")
    if list(rows.index) != YEARS:
        raise ValueError(f"{quantity}: years {list(rows.index)[:3]}... are not 1990-2024")
    missing = rows.value.isna() & (rows.notation == "")
    if missing.any():
        raise ValueError(f"{quantity}: no value and no notation key in {list(rows.index[missing])}")
    return rows.value.fillna(0.0).astype(float)


def crt_reference(inventory, quantity):
    r = inventory[(inventory.quantity == quantity) & (inventory.year == 2020)].iloc[0]
    return f"{r.sheet} row {r.row} col {r.column} ('{r.label.strip()}')"


def nid_series(nid, column):
    """4.A.1 + 4.A.2, each interpolated linearly between the years the NID prints."""
    total = 0.0
    for _, g in nid.groupby("category"):
        s = g.set_index("year")[column].astype(float)
        full = s.reindex(YEARS).interpolate(method="index", limit_area="inside")
        if full.isna().any():
            raise ValueError(f"NID {column}: years outside the printed range")
        total = total + full
    return total


def build_tables():
    inventory = read_csv("data_sources/inventory_areas.csv")
    nid = read_csv("data_sources/nid2026_forest_organic_soils.csv")
    burnt = read_csv("data_sources/legacy_burnt_area.csv")
    tables, metadata = {}, []
    for table, columns in TABLES.items():
        data = {"year": YEARS}
        metadata.append((table, "year", "year", "inventory year", "PACKAGE", "", "", "1990-2024", "key"))
        for column, (kind, arg, unit, description, decision) in columns.items():
            if kind == "crt":
                values = crt_series(inventory, arg)
                source, reference, transformation, status = "CRT2026", crt_reference(inventory, arg), \
                    "kha as reported; notation key -> 0", "inventory"
            elif kind == "crt_share":
                quantity, factor = arg
                values = crt_series(inventory, quantity) * factor
                source, reference, transformation, status = "CRT2026", crt_reference(inventory, quantity), \
                    f"x {factor:.2f}", "derived"
            elif kind == "nid":
                values = nid_series(nid, arg)
                printed = sorted({int(y) for y in nid.year})
                source, reference, status = "NID2026", f"Table 6.7 + Table 6.15, column {arg}", "derived"
                transformation = ("4.A.1 + 4.A.2; years not printed interpolated linearly per category "
                                  f"(printed: {printed[0]}-{printed[-1]}, gaps 1991-94, 1996-99, 2001-04, "
                                  "and 2006-09 for 4.A.2)")
            elif kind == "legacy_burnt":
                s = burnt[burnt.table == arg].set_index("year").value.astype(float)
                values = s.reindex(YEARS)
                source, reference, transformation, status = "LEGACY040", f"{arg}.burnt_kha", \
                    "copied 1990-2022; 2023-2024 NULL", "pending"
            else:
                raise ValueError(kind)
            data[column] = [None if pd.isna(v) else float(v) for v in values]
            metadata.append((table, column, unit, description, source, reference, transformation, decision, status))
        tables[table] = (columns, pd.DataFrame(data))
    for table, column, unit, description, source, transformation, decision, status in OTHER_COLUMNS:
        metadata.append((table, column, unit, description, source, f"{table}.{column}", transformation, decision,
                         status))
    return inventory, nid, tables, metadata


def build(path=OUTPUT):
    """Write the database to ``path`` (overwritten). Returns the path."""
    path = Path(path)
    inventory, nid, tables, metadata = build_tables()
    nir = read_csv("data_sources/legacy_nir_table.csv")
    mapping = read_csv("data_sources/forest_soil_yield_mapping.csv")
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    try:
        cur = con.cursor()
        for table, (columns, df) in tables.items():
            cols = ", ".join(['"year" INTEGER'] + [f'"{c}" REAL' for c in columns])
            cur.execute(f'CREATE TABLE "{table}" ({cols})')
            cur.executemany(f'INSERT INTO "{table}" VALUES ({", ".join("?" * len(df.columns))})',
                            [tuple(int(v) if i == 0 else v for i, v in enumerate(row))
                             for row in df.itertuples(index=False, name=None)])
        cur.execute('CREATE TABLE "NIR" ("Year" INTEGER, "Land_cover" TEXT, "Area_kha" REAL)')
        cur.executemany('INSERT INTO "NIR" VALUES (?, ?, ?)',
                        [(int(y), str(l), float(a)) for y, l, a in nir.itertuples(index=False, name=None)])
        cur.execute('CREATE TABLE "forest_soil_yield_mapping" ("soil_group" INTEGER, "species" TEXT, '
                    '"yield_class" TEXT)')
        cur.executemany('INSERT INTO "forest_soil_yield_mapping" VALUES (?, ?, ?)',
                        [(int(g), str(s), str(y)) for g, s, y in mapping.itertuples(index=False, name=None)])

        cur.execute('CREATE TABLE "sources" ("source_id" TEXT PRIMARY KEY, "citation" TEXT)')
        cur.executemany('INSERT INTO "sources" VALUES (?, ?)', SOURCES)
        cur.execute('CREATE TABLE "column_metadata" ("table_name" TEXT, "column_name" TEXT, "unit" TEXT, '
                    '"description" TEXT, "source_id" TEXT, "reference" TEXT, "transformation" TEXT, '
                    '"decision" TEXT, "status" TEXT)')
        cur.executemany('INSERT INTO "column_metadata" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', metadata)
        cur.execute('CREATE TABLE "inventory_values" ("year" INTEGER, "quantity" TEXT, "value" REAL, "unit" TEXT, '
                    '"notation" TEXT, "source_id" TEXT, "reference" TEXT)')
        rows = [(int(r.year), r.quantity, None if pd.isna(r.value) else float(r.value), r.unit, r.notation or "",
                 "CRT2026", f"{r.sheet} row {r.row} col {r.column} ('{str(r.label).strip()}')")
                for r in inventory.fillna({"notation": ""}).itertuples()]
        for r in nid.itertuples():
            for column in ("total_area_kha", "mineral_kha", "organic_kha", "open_area_kha",
                           "drained_n_poor_organic_kha", "drained_n_rich_organo_mineral_kha"):
                rows.append((int(r.year), f"NID.{r.category}.{column}", float(getattr(r, column)), "kha", "",
                             "NID2026", r.source))
        rows.sort(key=lambda x: (x[1], x[0]))
        cur.executemany('INSERT INTO "inventory_values" VALUES (?, ?, ?, ?, ?, ?, ?)', rows)
        cur.execute('CREATE TABLE "build_info" ("key" TEXT PRIMARY KEY, "value" TEXT)')
        info = [("package_version", VERSION), ("built_by", "tools/build_database.py"), ("years", "1990-2024"),
                ("units", "areas in kha")] + [(f"sha256:{p}", sha256(p)) for p in INPUTS]
        cur.executemany('INSERT INTO "build_info" VALUES (?, ?)', info)
        con.commit()
        con.execute("VACUUM")
    finally:
        con.close()
    return path


if __name__ == "__main__":
    out = build(Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT)
    print(f"{out}: {hashlib.sha256(out.read_bytes()).hexdigest()}")
