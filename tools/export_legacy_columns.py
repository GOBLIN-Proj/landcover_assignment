"""Export the soil group -> yield class table from the 0.4.0 database (its values are kept, decision D9).

The 0.4.0 database (`land_use_database.db`, CRF 2024 vintage) is read from git at commit 25a83b4, so this script gives
the same files on any checkout. It writes:

- (`data_sources/legacy_burnt_area.csv` is no longer written: its values equal CRF 2024 Table4(V), which the database
  now reads from `data_sources/inventory_areas.csv`.)
- (`data_sources/legacy_nir_table.csv`, the 0.4.0 `NIR` table, is no longer written: D8 rebuilt the table from CRT
  2026 Table4.1.)
- `data_sources/forest_soil_yield_mapping.csv`: the soil group -> yield class table (D9: values kept; source Upton
  et al. 2013 Table 2).

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


def main():
    blob = subprocess.run(["git", "show", f"{COMMIT}:{DB_PATH}"], cwd=ROOT, check=True, capture_output=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "legacy.db"
        db.write_bytes(blob)
        con = sqlite3.connect(db)
        try:
            mapping = pd.read_sql("SELECT soil_group, species, yield_class FROM forest_soil_yield_mapping", con)
        finally:
            con.close()
    out = ROOT / "data_sources"
    mapping.to_csv(out / "forest_soil_yield_mapping.csv", index=False, lineterminator="\n")
    print(f"mapping {len(mapping)} rows -> {out}")


if __name__ == "__main__":
    main()
