"""Audit the land-use database against the current inventory (CRT 2026, NID 2026, CRF 2024 for burnt area).

For every column of every table in `land_use_database.db`, this script writes:
- the database value (CRF 2024 vintage);
- the inventory value from `data_sources/`;
- the difference;
- how the database value was produced;
- the decision (D1-D10 in the plan) that the rebuild needs.

It reads only; nothing in the package changes.

Usage, from the repo root:
    .venv/bin/python tools/build_provenance.py <out.md>
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "src/landcover_assignment/database/land_use_database.db"
YEARS = (1990, 2020, 2022)

inv = pd.read_csv(ROOT / "data_sources/inventory_areas.csv")
nid = pd.read_csv(ROOT / "data_sources/nid2026_forest_organic_soils.csv")


def crt(quantity, scale=1.0):
    """Return a year -> value lookup for one inventory quantity (notation keys come back as text)."""
    d = inv[inv.quantity == quantity].set_index("year")
    return lambda y: (d.value[y] * scale if pd.notna(d.value[y]) else d.notation[y]) if y in d.index else "n/a"


def nid_sum(column):
    d = nid.groupby("year")[column].agg(["sum", "count"])
    return lambda y: d.loc[y, "sum"] if y in d.index and d.loc[y, "count"] == 2 else "n/a (not printed for both 4.A.1 and 4.A.2)"


def total(*fns):
    def f(y):
        vals = [fn(y) for fn in fns]
        return sum(vals) if all(isinstance(v, float) for v in vals) else "/".join(map(str, vals))
    return f


KHA_FROM_HA = 1 / 1000
# table.column: (inventory candidate, candidate description, how the DB value was made, status, decision)
MAP = {
    "forest_data.total_kha": (crt("4.A.area"), "CRT Table4.A row 10 col D (4.A total)", "script, CRF Table4.A", "refresh", ""),
    "forest_data.mineral_kha": (crt("4.A.mineral_area"), "CRT Table4.A row 10 col E", "script; not used by the code", "refresh", "D3"),
    "forest_data.organic_kha": (crt("4.A.organic_area"), "CRT Table4.A row 10 col F", "script; not used by the code", "refresh", "D3"),
    "forest_data.burnt_kha": (crt("burnt_area.4.A", KHA_FROM_HA), "CRF 2024 Table4(V) row 9 'A. Forest land' (4.A.1+4.A.2), ha/1000",
                              "**wrong row**: 4.A.1 wildfires only; /1000 by hand", "fix", "D6 (align with cbm_runner)"),
    "forest_data.organic_emitting_kha": (nid_sum("drained_n_poor_organic_kha"), "NID 2026 Tables 6.7 + 6.15, drained N-poor (4.A.1+4.A.2)",
                                         "**no source**: typed in Oct 2023, 2022 copied from 2021", "fix", "D3"),
    "forest_data.organo_mineral_emitting_kha": (nid_sum("drained_n_rich_organo_mineral_kha"), "NID 2026 Tables 6.7 + 6.15, drained N-rich (4.A.1+4.A.2)",
                                                "**no source**: typed in Oct 2023", "fix", "D3"),
    "grassland_data.total_kha": (crt("4.C.area"), "CRT Table4.C row 10 col D (4.C total; 4.C.1 is the alternative)", "script", "refresh", ""),
    "grassland_data.mineral_kha": (crt("4.C.mineral_area"), "CRT Table4.C row 10 col E", "script", "refresh", ""),
    "grassland_data.organic_kha": (crt("4.C.organic_area"), "CRT Table4.C row 10 col F", "script (sum of CRF 4(II) drained + rewetted)", "refresh", ""),
    "grassland_data.drained_rich_organic_kha + drained_poor_organic_kha": (
        crt("4(II).C.1.drained.area"), "CRT Table4(II) row 30 'Drained organic soils' (4.C.1)",
        "script: CRF 4(II) drained, split by a hard-coded 0.45 / 0.55", "refresh", "D4 (split)"),
    "grassland_data.rewetted_rich_organic_kha + rewetted_poor_organic_kha": (
        crt("4(II).C.1.other.area"), "CRT Table4(II) row 33 'Other organic soils' (rewet status; the 'Rewetted' row is NO in the CRT)",
        "script: CRF 4(II) 'Rewetted organic soils', split 0.45 / 0.55", "refresh", "D4, D5"),
    "grassland_data.burnt_kha": (crt("burnt_area.4.C", KHA_FROM_HA), "CRF 2024 Table4(V) row 23 'C. Grassland', ha/1000",
                                 "script read a sub-row ('Controlled burning') equal to the total; /1000 by hand", "refresh", "D6"),
    "cropland_data.total_kha": (crt("4.B.area"), "CRT Table4.B row 10 col D", "script", "refresh", ""),
    "cropland_data.mineral_kha": (crt("4.B.mineral_area"), "CRT Table4.B row 10 col E", "script", "refresh", ""),
    "cropland_data.organic_kha": (crt("4.B.organic_area"), "CRT Table4.B row 10 col F (notation NO)", "hard-coded 0", "refresh", "D7"),
    "cropland_data.burnt_kha": (crt("burnt_area.4.B", KHA_FROM_HA), "CRF 2024 Table4(V) row 16 'B. Cropland', ha/1000",
                                "script read the 'remaining' sub-row (equal to the total); /1000 by hand", "refresh", "D6"),
    "wetland_data.total_kha": (crt("4.D.area"), "CRT Table4.D row 10 col D (4.D total; 4.D.1 is the alternative)", "script", "refresh", "D2"),
    "wetland_data.mineral_kha": (crt("4.D.mineral_area"), "CRT Table4.D row 10 col E", "script", "refresh", "D2"),
    "wetland_data.organic_kha": (crt("4.D.organic_area"), "CRT Table4.D row 10 col F", "script", "refresh", "D2"),
    "wetland_data.domestic_peat_extraction_kha": (crt("4.D.domestic_peat_extraction.area"), "CRT Table4.D row 13 (= 4(II) row 47)", "script", "refresh", ""),
    "wetland_data.industrial_peat_extraction_kha": (crt("4.D.industrial_peat_extraction.area"),
                                                    "CRT Table4.D row 14; **4(II) row 48 differs** (see the D1 table)", "script, CRF Table4.D", "refresh", "D1"),
    "wetland_data.rewetted_industrial_peat_kha": (crt("4.D.rewetted_industrial_peat_extraction.area"), "CRT Table4.D row 15 (= 4(II) row 50)", "script", "refresh", ""),
    "wetland_data.rewetted_domestic_peat_kha": (crt("4.D.other_domestic_peat_extraction.area"), "CRT Table4.D row 16 'Other Domestic Peat Extraction'", "script", "refresh", ""),
    "wetland_data.rewetted_mineral_kha": (crt("4.D.2.mineral_area"), "CRT Table4.D row 21 col E: **land converted to wetland**, not rewetting",
                                          "script read '2. Land converted to wetlands' under a 'rewetted' name", "fix (rename or drop)", "D2"),
    "wetland_data.rewetted_organic_kha": (crt("4.D.2.organic_area"), "CRT Table4.D row 21 col F: **land converted to wetland**",
                                          "as above", "fix (rename or drop)", "D2"),
    "wetland_data.near_natural_wetland_kha": (crt("4.D.near_natural_wetlands.area"), "CRT Table4.D row 19 (= 4(II) row 75)", "script", "refresh", ""),
    "wetland_data.unmanaged_wetland_kha": (crt("4.D.unmanaged_wetlands.area"), "CRT Table4.D row 20", "script (CRF: constant 126.78)", "refresh", "D2"),
    "wetland_data.burnt_kha": (crt("burnt_area.4.D", KHA_FROM_HA), "CRF 2024 Table4(V) row 30 'D. Wetlands', ha/1000",
                               "script read a sub-row equal to the total; /1000 by hand", "refresh", "D6"),
    "settlement_data.total_kha": (crt("4.E.area"), "CRT Table4.E row 10 col D", "script", "refresh", "D7"),
    "settlement_data.mineral_kha": (crt("4.E.mineral_area"), "CRT Table4.E row 10 col E", "script", "refresh", "D7"),
    "settlement_data.organic_kha": (crt("4.E.organic_area"), "CRT Table4.E row 10 col F", "script", "refresh", "D7"),
    "settlement_data.burnt_kha": (lambda y: "not reported", "none (CRF Table4(V) has no settlement row)", "hard-coded 0", "keep 0, documented", "D7"),
}


def db_value(con, key, year):
    table, cols = key.split(".", 1)
    cols = [c.strip() for c in cols.replace(table + ".", "").split("+")]
    row = con.execute(f"SELECT {', '.join(cols)} FROM {table} WHERE year = ?", (year,)).fetchone()
    return sum(row) if row else "n/a"


def fmt(v):
    if isinstance(v, (int, float)):
        return f"{v:,.3f}" if abs(v) >= 1 else f"{v:.4f}"
    return str(v)


def diff(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b:
        return f"{(a - b) / b:+.1%}"
    return ""


def main(out_path):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    lines = [
        "# Data provenance audit: land_use_database.db against CRT 2026 / NID 2026",
        "",
        "Generated by `tools/build_provenance.py` from `data_sources/inventory_areas.csv` (`tools/extract_inventory.py`) and "
        "`data_sources/nid2026_forest_organic_soils.csv` (`tools/transcribe_nid_forest.py`).",
        "",
        "- **Units:** all values are kha. The database tables hold CRF 2024 values (submission 2024, years 1990-2022). The code multiplies them by 1000 on reading.",
        "- **Year coverage:** CRT 2026 covers 1990-2024. Burnt area exists only in CRF 2024 Table4(V), 1990-2022; the CRT leaves it blank.",
        "- **Diff:** (database - inventory) / inventory.",
        "- **Decisions:** 'Decision' refers to D1-D10 in the plan. Nothing here is changed until the owner decides.",
        "",
        "## Column by column",
        "",
    ]
    for key, (cand, cand_desc, how, status, decision) in MAP.items():
        lines += [f"### `{key}`", f"- **Inventory source:** {cand_desc}", f"- **How the database value was made:** {how}",
                  f"- **Status:** {status}" + (f"; decision: {decision}" if decision else ""), "",
                  "| year | database | inventory | diff |", "|---|---|---|---|"]
        for y in YEARS:
            a, b = db_value(con, key, y), cand(y)
            lines.append(f"| {y} | {fmt(a)} | {fmt(b)} | {diff(a, b)} |")
        lines.append(f"| 2024 | n/a | {fmt(cand(2024))} | |")
        lines.append("")

    # D1: the two industrial peat figures side by side
    d4, d2 = crt("4.D.industrial_peat_extraction.area"), crt("4(II).D.industrial_peat_extraction.area")
    lines += ["## D1: industrial peat extraction, Table4.D vs Table4(II)", "",
              "| year | database | CRT Table4.D row 14 | CRT Table4(II) row 48 |", "|---|---|---|---|"]
    for y in (1990, 2010, 2020, 2022, 2024):
        lines.append(f"| {y} | {fmt(db_value(con, 'wetland_data.industrial_peat_extraction_kha', y))} | {fmt(d4(y))} | {fmt(d2(y))} |")

    # D6: forest burnt series and rate options
    a_tot, a1 = crt("burnt_area.4.A"), crt("burnt_area.4.A.1.wildfires")
    lines += ["", "## D6: forest burnt area (ha), CRF 2024 Table4(V)", "",
              "| year | 4.A.1 wildfires (in the database) | 4.A total |", "|---|---|---|"]
    for y in range(2010, 2023):
        lines.append(f"| {y} | {fmt(a1(y))} | {fmt(a_tot(y))} |")

    lines += ["", "## Other tables", "",
              "- **`forest_soil_yield_mapping`:** no script; added by hand in February 2024. The only source cited is Farrelly & Gallagher (2015), in the README. It is duplicated in `landcover_data_manager.py` (`cbm_default_data`). Decision D9.",
              "- **`NIR`:** the year assigned to each row is wrong (a counter over unsorted `os.listdir`), and it holds Table4.1 'Initial area'. Nothing in the package uses it. Decision D8.",
              "", "## Not inventory data", "",
              "- **Grassland area** (`area_ha` of the grassland row) comes from grassland_production's input (`total_grassland`). The database supplies only the shares.",
              "- **Rewetted spared grassland stays grassland** (protected design rule): it moves into `share_rewetted_rich/poor_organic`, never into the wetland row."]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1])
