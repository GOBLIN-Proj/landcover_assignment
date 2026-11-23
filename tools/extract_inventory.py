"""Extract the land-use areas landcover_assignment needs from Ireland's inventory workbooks.

Sources:
- **EPA CRT 2026** (submission 2026), one workbook per year, 1990-2024: land areas
  (Table4.1, Table4.A-F), organic soils (Table4(II)), and biomass-burning emissions (Table4(IV)).
  The CRT leaves "area burned" blank.
- **EPA CRF 2024** (submission 2024), 1990-2022: area burnt, Table4(V). This is the last submission that
  reports burnt area.

Each value is read from a fixed (sheet, row, column). The row label, and for Table4.1 the column header, are checked
against the expected text, so a change in layout raises an error instead of reading the wrong cell. CRT notation
keys (NO, IE, NA, NE, ...) are kept as text in the `notation` column; they are never turned into 0. The pattern
follows landcover_lca's `tools/extract_inventory_fixtures.py`.

Output: one long-format CSV, one row per (year, quantity), with columns
    year, quantity, value, unit, notation, source, sheet, row, label, column

Usage, from the repo root:
    .venv/bin/python tools/extract_inventory.py \
        .artifacts/data/national-inventory-2026/IRL-CRT-2026-V1.0 \
        .artifacts/data/NIR/NIR_2024/IRL_2024__12032024_130024_started \
        data_sources/inventory_areas.csv

The workbooks themselves are not committed; pass their folders by path.
"""
import glob
import os
import sys
import warnings

import openpyxl
import pandas as pd

warnings.filterwarnings("ignore")

CRT_YEARS = range(1990, 2025)
CRF_YEARS = range(1990, 2023)
COL = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTU")}

AREA = {"area": ("D", "kha"), "mineral_area": ("E", "kha"), "organic_area": ("F", "kha")}
AREA_ONLY = {"area": ("D", "kha")}
II = {"area": ("D", "kha"), "ief_co2": ("E", "kg CO2/ha"), "ief_n2o_n": ("F", "kg N2O-N/ha"),
      "ief_ch4": ("G", "kg CH4/ha")}
IV = {"co2": ("J", "kt CO2"), "ch4": ("K", "kt CH4"), "n2o": ("L", "kt N2O")}

# quantity prefix: (sheet, row, expected label start, {quantity suffix: (column, unit)})
CRT_SPEC = {
    # areas by category, with mineral/organic split
    "4.A": ("Table4.A", 10, "4.A. Total forest land", AREA),
    "4.A.1": ("Table4.A", 11, "4.A.1.", AREA),
    "4.A.2": ("Table4.A", 12, "4.A.2.", AREA),
    "4.B": ("Table4.B", 10, "4.B. Total cropland", AREA),
    "4.C": ("Table4.C", 10, "4.C. Total grassland", AREA),
    "4.C.1": ("Table4.C", 11, "4.C.1.", AREA),
    "4.C.2": ("Table4.C", 12, "4.C.2.", AREA),
    "4.D": ("Table4.D", 10, "4.D. Total wetlands", AREA),
    "4.D.1": ("Table4.D", 11, "4.D.1.", AREA),
    "4.D.domestic_peat_extraction": ("Table4.D", 13, "Domestic Peat Extraction", AREA),
    "4.D.industrial_peat_extraction": ("Table4.D", 14, "Industrial Peat Extraction", AREA),
    "4.D.rewetted_industrial_peat_extraction": ("Table4.D", 15, "Rewetted Industrial Peat Extraction", AREA),
    "4.D.other_domestic_peat_extraction": ("Table4.D", 16, "Other Domestic Peat Extraction", AREA),
    "4.D.near_natural_wetlands": ("Table4.D", 19, "Near Natural Wetlands", AREA),
    "4.D.unmanaged_wetlands": ("Table4.D", 20, "Unmanaged Wetlands", AREA),
    "4.D.2": ("Table4.D", 21, "4.D.2.", AREA),
    "4.E": ("Table4.E", 10, "4.E.  Total settlements", AREA),
    "4.F": ("Table4.F", 10, "4.F. Total other land", AREA),
    # organic soils: drained / rewetted / other, with implied emission factors
    "4(II).A.1.drained": ("Table4(II)", 14, "Drained organic soils", II),
    "4(II).A.2.drained": ("Table4(II)", 18, "Drained organic soils", II),
    "4(II).C.1.drained": ("Table4(II)", 30, "Drained organic soils", II),
    "4(II).C.1.rewetted": ("Table4(II)", 31, "Rewetted organic soils", II),
    "4(II).C.1.other": ("Table4(II)", 33, "Other organic soils", II),
    "4(II).D.domestic_peat_extraction": ("Table4(II)", 47, "Domestic Peat Extraction", II),
    "4(II).D.industrial_peat_extraction": ("Table4(II)", 48, "Industrial Peat Extraction", II),
    "4(II).D.rewetted_industrial_peat_extraction": ("Table4(II)", 50, "Rewetted Industrial Peat Extraction", II),
    "4(II).D.other_domestic_peat_extraction": ("Table4(II)", 52, "Other Domestic Peat Extraction", II),
    "4(II).D.near_natural_wetlands": ("Table4(II)", 75, "Near Natural Wetlands", II),
    # biomass burning emissions (area column is blank in the CRT; kept to back-calculate burnt area)
    "4(IV).A": ("Table4(IV)", 11, "4(IV).A. Forest land", IV),
    "4(IV).A.1.wildfires": ("Table4(IV)", 14, "4(IV).A.1.b. Wildfires", IV),
    "4(IV).A.2.wildfires": ("Table4(IV)", 17, "4(IV).A.2.b. Wildfires", IV),
    "4(IV).B.1.wildfires": ("Table4(IV)", 21, "4(IV).B.1.b. Wildfires", IV),
    "4(IV).C.1.wildfires": ("Table4(IV)", 28, "4(IV).C.1.b. Wildfires", IV),
    "4(IV).D.1.wildfires": ("Table4(IV)", 35, "4(IV).D.1.b. Wildfires", IV),
}

# Table4.1 land transition matrix: final area (row 20) by destination column; header checked in row 8.
T41_FINAL = {
    "forest_managed": ("C", "Forest land (managed)"),
    "cropland": ("E", "Cropland"),
    "grassland_managed": ("F", "Grassland (managed)"),
    "wetlands_managed": ("H", "Wetlands (managed)"),
    "wetlands_unmanaged": ("I", "Wetlands (unmanaged)"),
    "settlements": ("J", "Settlements"),
    "other_land": ("K", "Other land"),
}

# CRF 2024 Table4(V): area burnt, column E (ha); label in column A. (row, expected label, parent row, parent label)
CRF_SPEC = {
    "4.A": (9, "A. Forest land", None, None),
    "4.A.1.wildfires": (12, "Wildfires", 10, "1. Forest land remaining"),
    "4.A.2.wildfires": (15, "Wildfires", 13, "2. Land converted to forest"),
    "4.B": (16, "B. Cropland", None, None),
    "4.B.1": (17, "1.  Cropland remaining cropland", None, None),
    "4.C": (23, "C. Grassland", None, None),
    "4.C.1": (24, "1. Grassland remaining grassland", None, None),
    "4.D": (30, "D. Wetlands", None, None),
    "4.D.1": (31, "1. Wetlands remaining wetlands", None, None),
}


def _text(v):
    return str(v or "").strip()


def _value(v):
    if isinstance(v, (int, float)):
        return float(v), ""
    s = _text(v)
    try:
        return float(s), ""
    except ValueError:
        return None, s


def _rows(ws, max_row):
    return {i: r for i, r in enumerate(ws.iter_rows(min_row=1, max_row=max_row, values_only=True), start=1)}


def _check(label, expect, where):
    if not label.startswith(expect):
        raise ValueError(f"{where}: expected label starting '{expect}', found '{label}'")


def extract_crt(folder):
    out = []
    for year in CRT_YEARS:
        path = os.path.join(folder, f"IRL-CRT-2026-V1.0-{year}.xlsx")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        cache = {}
        for prefix, (sheet, rnum, expect, quantities) in CRT_SPEC.items():
            if sheet not in cache:
                cache[sheet] = _rows(wb[sheet], 110)
            label = _text(cache[sheet][rnum][COL["B"]])
            _check(label, expect, f"CRT {year} {sheet} row {rnum}")
            for suffix, (col, unit) in quantities.items():
                value, notation = _value(cache[sheet][rnum][COL[col]])
                out.append(dict(year=year, quantity=f"{prefix}.{suffix}", value=value, unit=unit, notation=notation,
                                source="EPA CRT 2026", sheet=sheet, row=rnum, label=label, column=col))
        t41 = _rows(wb["Table4.1"], 25)
        _check(_text(t41[20][COL["B"]]), "Final area", f"CRT {year} Table4.1 row 20")
        for name, (col, header) in T41_FINAL.items():
            _check(_text(t41[8][COL[col]]), header, f"CRT {year} Table4.1 header {col}8")
            value, notation = _value(t41[20][COL[col]])
            out.append(dict(year=year, quantity=f"4.1.final_area.{name}", value=value, unit="kha", notation=notation,
                            source="EPA CRT 2026", sheet="Table4.1", row=20, label=f"Final area / {header}",
                            column=col))
        wb.close()
    return out


def extract_crf_burnt(folder):
    out = []
    for year in CRF_YEARS:
        path = glob.glob(os.path.join(folder, f"IRL_2024_{year}_*.xlsx"))[0]
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        rows = _rows(wb["Table4(V)"], 40)
        for name, (rnum, expect, parent, parent_expect) in CRF_SPEC.items():
            label = _text(rows[rnum][COL["A"]])
            _check(label, expect, f"CRF {year} Table4(V) row {rnum}")
            if parent:
                _check(_text(rows[parent][COL["A"]]), parent_expect, f"CRF {year} Table4(V) row {parent}")
            if _text(rows[rnum][COL["D"]]) != "ha":
                raise ValueError(f"CRF {year} Table4(V) row {rnum}: unit is not ha")
            value, notation = _value(rows[rnum][COL["E"]])
            out.append(dict(year=year, quantity=f"burnt_area.{name}", value=value, unit="ha", notation=notation,
                            source="EPA CRF 2024", sheet="Table4(V)", row=rnum, label=label, column="E"))
        wb.close()
    return out


def main(crt_folder, crf_folder, out_path):
    df = pd.DataFrame(extract_crt(crt_folder) + extract_crf_burnt(crf_folder))
    df = df.sort_values(["quantity", "year"], kind="stable").reset_index(drop=True)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False, lineterminator="\n")
    print(f"{out_path}: {len(df)} rows, {df['quantity'].nunique()} quantities, years {df.year.min()}-{df.year.max()}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
