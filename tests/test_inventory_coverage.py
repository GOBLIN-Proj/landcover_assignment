"""The land-use database checked against the current inventory (CRT 2026, NID 2026, CRF 2024 for burnt area).

The inventory values come from `data_sources/`, which the scripts in `tools/` build. Each database column is compared
with its inventory source in the calibration year (2020) and in the latest database year (2022), within TOLERANCE.

A known gap is marked as an expected failure and names the decision (D1-D10 in the plan) that resolves it. The step 6
rebuild (tools/build_database.py) closed D1, D2, D3, D5 and D7; burnt area waits for D6.
"""
import sqlite3
import unittest

import pandas as pd

from _helpers import ROOT

from landcover_assignment.database import get_database_path

DB = get_database_path()
TOLERANCE = 0.005          # 0.5 %
YEARS = (2020, 2022)

inventory = pd.read_csv(ROOT / "data_sources/inventory_areas.csv")
nid = pd.read_csv(ROOT / "data_sources/nid2026_forest_organic_soils.csv")


def crt(quantity, scale=1.0):
    d = inventory[inventory.quantity == quantity].set_index("year").value
    return lambda y: d[y] * scale


def nid_sum(column):
    d = nid.groupby("year")[column].sum()
    return lambda y: d[y]


from landcover_assignment.resource_manager.units import KHA_TO_HA  # noqa: E402

HA_TO_KHA = 1 / KHA_TO_HA
# (database expression, inventory value, gap: the decision that resolves it, or None if the column should already agree)
CHECKS = {
    "forest_total": ("forest_data.total_kha", crt("4.A.area"), None),
    "forest_burnt": ("forest_data.burnt_kha", crt("burnt_area.4.A", HA_TO_KHA), "D6: 4.A.1 only"),
    "forest_n_poor": ("forest_data.organic_emitting_kha", nid_sum("drained_n_poor_organic_kha"), None),
    "forest_n_rich": ("forest_data.organo_mineral_emitting_kha", nid_sum("drained_n_rich_organo_mineral_kha"), None),
    "grassland_total": ("grassland_data.total_kha", crt("4.C.area"), None),
    "grassland_mineral": ("grassland_data.mineral_kha", crt("4.C.mineral_area"), None),
    "grassland_organic": ("grassland_data.organic_kha", crt("4.C.organic_area"), None),
    "grassland_drained": ("grassland_data.drained_rich_organic_kha + drained_poor_organic_kha",
                          crt("4(II).C.1.drained.area"), None),
    "grassland_rewet_status": ("grassland_data.rewetted_rich_organic_kha + rewetted_poor_organic_kha",
                               crt("4(II).C.1.other.area"), None),
    "grassland_burnt": ("grassland_data.burnt_kha", crt("burnt_area.4.C", HA_TO_KHA), None),
    "cropland_total": ("cropland_data.total_kha", crt("4.B.area"), None),
    "cropland_burnt": ("cropland_data.burnt_kha", crt("burnt_area.4.B", HA_TO_KHA), None),
    "wetland_total": ("wetland_data.total_kha", crt("4.D.area"), None),
    "wetland_domestic": ("wetland_data.domestic_peat_extraction_kha", crt("4.D.domestic_peat_extraction.area"), None),
    "wetland_industrial": ("wetland_data.industrial_peat_extraction_kha",
                           crt("4(II).D.industrial_peat_extraction.area"), None),
    "wetland_rewetted_industrial": ("wetland_data.rewetted_industrial_peat_kha",
                                    crt("4.D.rewetted_industrial_peat_extraction.area"), None),
    "wetland_rewetted_domestic": ("wetland_data.rewetted_domestic_peat_kha",
                                  crt("4.D.other_domestic_peat_extraction.area"), None),
    "wetland_near_natural": ("wetland_data.near_natural_wetland_kha", crt("4.D.near_natural_wetlands.area"),
                             None),
    "wetland_unmanaged": ("wetland_data.unmanaged_wetland_kha", crt("4.D.unmanaged_wetlands.area"), None),
    "wetland_burnt": ("wetland_data.burnt_kha", crt("burnt_area.4.D", HA_TO_KHA), None),
    "settlement_total": ("settlement_data.total_kha", crt("4.E.area"), None),
}


def db_value(expr, year):
    table, cols = expr.split(".", 1)
    cols = [c.strip() for c in cols.split("+")]
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        row = con.execute(f"SELECT {', '.join(cols)} FROM {table} WHERE year = ?", (year,)).fetchone()
    finally:
        con.close()
    return sum(row)


class InventoryCoverage(unittest.TestCase):
    pass


def make_test(expr, inventory_value, gap):
    def test(self):
        for year in YEARS:
            have, want = db_value(expr, year), inventory_value(year)
            self.assertLessEqual(abs(have - want), TOLERANCE * abs(want),
                                 f"{expr} {year}: database {have:.4f} vs inventory {want:.4f}")
    test.__doc__ = f"{expr}" + (f" (known gap: {gap})" if gap else "")
    return unittest.expectedFailure(test) if gap else test


for name, (expr, value, gap) in CHECKS.items():
    setattr(InventoryCoverage, f"test_{name}", make_test(expr, value, gap))


if __name__ == "__main__":
    unittest.main()
