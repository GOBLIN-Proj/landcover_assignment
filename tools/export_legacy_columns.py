"""Export the values that the database rebuild (step 6) still takes from the 0.4.0 database, pending a decision.

The 0.4.0 database (`land_use_database.db`, CRF 2024 vintage) is read from git at commit 25a83b4, so this script gives
the same files on any checkout. It writes:

- `data_sources/legacy_burnt_area.csv`: `burnt_kha` of every land-use table, 1990-2022 (pending D6, burnt area);
- (`data_sources/legacy_nir_table.csv`, the 0.4.0 `NIR` table, is no longer written: D8 rebuilt the table from CRT
  2026 Table4.1.)
- `data_sources/forest_soil_yield_mapping.csv`: the soil group -> yield class table (pending D9).

Floats are written with Python's shortest round-trip repr, so the rebuilt database holds the same values bit for bit.

Usage, from the repo root:
    .venv/bin/python tools/export_legacy_columns.py
"""
import sqlite3
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "25a83b4"
DB_PATH = "src/landcover_assignment/database/land_use_database.db"
TABLES = ("forest_data", "grassland_data", "cropland_data", "wetland_data", "settlement_data")


def main():
    blob = subprocess.run(["git", "show", f"{COMMIT}:{DB_PATH}"], cwd=ROOT, check=True, capture_output=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "legacy.db"
        db.write_bytes(blob)
        con = sqlite3.connect(db)
        try:
            burnt = pd.concat([pd.read_sql(f"SELECT year, burnt_kha AS value FROM {t} ORDER BY year", con).assign(table=t)
                               for t in TABLES])
            mapping = pd.read_sql("SELECT soil_group, species, yield_class FROM forest_soil_yield_mapping", con)
        finally:
            con.close()
    out = ROOT / "data_sources"
    burnt[["table", "year", "value"]].to_csv(out / "legacy_burnt_area.csv", index=False, lineterminator="\n")
    mapping.to_csv(out / "forest_soil_yield_mapping.csv", index=False, lineterminator="\n")
    print(f"burnt {len(burnt)} rows, mapping {len(mapping)} rows -> {out}")


if __name__ == "__main__":
    main()
