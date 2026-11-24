"""Export the managed forest areas and forest fire that landcover_assignment mirrors from cbm_runner (decision D6a).

Source: goblin_cbm_runner 0.6.1 (GitHub main, commit cfc0199), database `cbm_runner_database_0.6.2.db` (the file
name inside the 0.6.1 release). Its historic forest disturbances are aligned with the NID and forest expert judgement
(prepared by the forest consultant who prepared them for the NID). The file's SHA-256 is checked, so a different
database raises an error instead of being exported silently.

cbm_runner models two managed-forest streams, the same in every scenario:
- FM, forest present before 1990: `FM_inventory_2100` (420,417.2 ha at the FM baseline, 2016) and
  `FM_disturbances_2100`, step 1 = 2017;
- AF, forest planted since 1990 (baseline planting continues to 2070): `AF_inventory_2100` and
  `AF_disturbance_2100`, step 1 = 1990 (the AF data line up with the inventory on that basis: step 28 holds the 2017
  planting and fire).

Written (all values in ha, derived from cbm_runner's disturbance events):
- `data_sources/cbm_runner_forest.csv`, one row per year 1990-2070:
  - `fm_area_ha` = FM inventory area - cumulative FM deforestation (DISTID7) to that year (from 2016);
  - `af_area_ha` = cumulative AF afforestation (DISTID4) - cumulative AF deforestation (DISTID7) to that year;
  - `fm_fire_ha`, `af_fire_ha` = FM and AF fire (DISTID3) area in that year; empty where cbm_runner has no fire event.
- `data_sources/cbm_runner_forest_parameters.csv`: the FM and AF inventory areas, which cbm_runner's scenario fire
  rate divides by (`SCDisturbances._calculate_national_fire_rate`).

Usage, from the repo root (the cbm_runner database is passed by path, not committed here):
    .venv/bin/python tools/export_cbm_runner_forest.py \
        ../cbm_runner/src/goblin_cbm_runner/database/cbm_runner_database_0.6.2.db
"""
import hashlib
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SHA256 = "5b03c00186d65a8e0970c7172ab913796dcf368bd7930d7c4896fed1c96724b7"   # cbm_runner 0.6.1, cfc0199
YEARS = range(1990, 2071)
FM_BASELINE, AF_FIRST_STEP_YEAR = 2016, 1990


def by_year(con, table, dist, year_of_step):
    rows = con.execute(f'SELECT Step, SUM(Amount) FROM "{table}" WHERE Dist_Type_ID = ? AND Measurement_type = "A" '
                       "GROUP BY Step", (dist,)).fetchall()
    return {year_of_step(step): amount for step, amount in rows}


def main(db_path):
    digest = hashlib.sha256(Path(db_path).read_bytes()).hexdigest()
    if digest != SHA256:
        raise ValueError(f"{db_path}: SHA-256 {digest} is not the cbm_runner 0.6.1 database")
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        fm_year = lambda step: FM_BASELINE + step
        af_year = lambda step: AF_FIRST_STEP_YEAR - 1 + step
        fm_inventory = con.execute('SELECT SUM(Area) FROM "FM_inventory_2100"').fetchone()[0]
        af_inventory = con.execute('SELECT SUM(Area) FROM "AF_inventory_2100"').fetchone()[0]
        fm_defor = by_year(con, "FM_disturbances_2100", "DISTID7", fm_year)
        af_plant = by_year(con, "AF_disturbance_2100", "DISTID4", af_year)
        af_defor = by_year(con, "AF_disturbance_2100", "DISTID7", af_year)
        fm_fire = by_year(con, "FM_disturbances_2100", "DISTID3", fm_year)
        af_fire = by_year(con, "AF_disturbance_2100", "DISTID3", af_year)
    finally:
        con.close()
    rows, fm_area, af_area = [], fm_inventory, 0.0
    for year in YEARS:
        af_area += af_plant.get(year, 0.0) - af_defor.get(year, 0.0)
        if year > FM_BASELINE:
            fm_area -= fm_defor.get(year, 0.0)
        rows.append(dict(year=year, fm_area_ha=round(fm_area, 6) if year >= FM_BASELINE else None, af_area_ha=round(af_area, 6),
                         fm_fire_ha=fm_fire.get(year), af_fire_ha=af_fire.get(year)))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "data_sources/cbm_runner_forest.csv", index=False, lineterminator="\n")
    source = "goblin_cbm_runner 0.6.1 database cbm_runner_database_0.6.2.db"
    pd.DataFrame([("fm_inventory_area_ha", fm_inventory, "ha", f"{source}, FM_inventory_2100 total Area"),
                  ("af_inventory_area_ha", af_inventory, "ha", f"{source}, AF_inventory_2100 total Area")],
                 columns=["name", "value", "unit", "source"]).to_csv(
        ROOT / "data_sources/cbm_runner_forest_parameters.csv", index=False, lineterminator="\n")
    print(f"cbm_runner_forest.csv: {len(out)} years; FM inventory {fm_inventory} ha, AF inventory {af_inventory} ha")


if __name__ == "__main__":
    main(sys.argv[1])
