"""Build the national reference dataset of land areas: `data_sources/national_reference_areas.csv`.

It is one table, 1990-2024, holding the national inventory areas in the terms of landcover_assignment's land-use
table, so the package's output can be validated against it. Each row is one (year, land_use, quantity) in
hectares, and names its inventory source.

Quantities, and the land-use table expression each one is compared with:

| land_use | quantity | land-use table | inventory source |
|---|---|---|---|
| forest | area | area_ha | CRT Table4.A 4.A total |
| forest | mineral | area_ha x share_mineral | CRT Table4.A 4.A mineral |
| forest | drained_organic_n_poor | area_ha x share_organic | NID Tables 6.7 + 6.15 drained N-poor |
| forest | drained_organic_n_rich | area_ha x share_organic_mineral | NID Tables 6.7 + 6.15 drained N-rich |
| forest | burnt | area_ha x share_burnt | CRF 2024 Table4(V) A. Forest land |
| cropland | area / mineral / burnt | as forest | CRT 4.B; CRF 2024 Table4(V) B |
| grassland | area | area_ha | CRT 4.C total |
| grassland | mineral | area_ha x share_mineral | CRT 4.C mineral |
| grassland | drained_organic | area_ha x (share_drained_rich_organic + share_drained_poor_organic) | CRT 4(II) 4.C.1 drained |
| grassland | rewet_status_organic | area_ha x (share_rewetted_rich_organic + share_rewetted_poor_organic) | CRT 4(II) 4.C.1 other organic soils |
| grassland | burnt | area_ha x share_burnt | CRF 2024 Table4(V) C |
| wetland | area | area_ha | CRT 4.D total |
| wetland | domestic / industrial / rewetted ... peat extraction | area_ha x share_* | CRT 4.D rows 13-16 (industrial: 4(II) row 48 and 4.D row 14, see D1) |
| wetland | near_natural / unmanaged | area_ha x share_* | CRT 4.D rows 19, 20 |
| wetland | burnt | area_ha x share_burnt | CRF 2024 Table4(V) D |
| settlement | area / mineral / organic | as forest | CRT 4.E |
| all | area | sum of area_ha | CRT Table4.1 final area, all categories |

Usage, from the repo root:
    .venv/bin/python tools/build_national_reference.py
It reads `data_sources/inventory_areas.csv` and `data_sources/nid2026_forest_organic_soils.csv`.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
inv = pd.read_csv(ROOT / "data_sources/inventory_areas.csv")
nid = pd.read_csv(ROOT / "data_sources/nid2026_forest_organic_soils.csv")

KHA = 1000.0   # kha -> ha
HA = 1.0

# (land_use, quantity): (inventory quantity, factor to ha)
CRT = {
    ("forest", "area"): ("4.A.area", KHA),
    ("forest", "mineral"): ("4.A.mineral_area", KHA),
    ("forest", "burnt"): ("burnt_area.4.A", HA),
    ("cropland", "area"): ("4.B.area", KHA),
    ("cropland", "mineral"): ("4.B.mineral_area", KHA),
    ("cropland", "burnt"): ("burnt_area.4.B", HA),
    ("grassland", "area"): ("4.C.area", KHA),
    ("grassland", "area_remaining"): ("4.C.1.area", KHA),
    ("grassland", "mineral"): ("4.C.mineral_area", KHA),
    ("grassland", "drained_organic"): ("4(II).C.1.drained.area", KHA),
    ("grassland", "rewet_status_organic"): ("4(II).C.1.other.area", KHA),
    ("grassland", "burnt"): ("burnt_area.4.C", HA),
    ("wetland", "area"): ("4.D.area", KHA),
    ("wetland", "domestic_peat_extraction"): ("4.D.domestic_peat_extraction.area", KHA),
    ("wetland", "industrial_peat_extraction"): ("4(II).D.industrial_peat_extraction.area", KHA),
    ("wetland", "industrial_peat_extraction_table4D"): ("4.D.industrial_peat_extraction.area", KHA),
    ("wetland", "rewetted_industrial_peat_extraction"): ("4.D.rewetted_industrial_peat_extraction.area", KHA),
    ("wetland", "rewetted_domestic_peat_extraction"): ("4.D.other_domestic_peat_extraction.area", KHA),
    ("wetland", "near_natural"): ("4.D.near_natural_wetlands.area", KHA),
    ("wetland", "unmanaged"): ("4.D.unmanaged_wetlands.area", KHA),
    ("wetland", "burnt"): ("burnt_area.4.D", HA),
    ("settlement", "area"): ("4.E.area", KHA),
    ("settlement", "mineral"): ("4.E.mineral_area", KHA),
    ("settlement", "organic"): ("4.E.organic_area", KHA),
}
TABLE41 = ["forest_managed", "cropland", "grassland_managed", "wetlands_managed", "wetlands_unmanaged", "settlements",
           "other_land"]


def describe(row):
    return f"{row.source} {row.sheet} row {row.row} col {row.column} ('{row.label}')"


def build():
    rows = []
    for (land_use, quantity), (name, factor) in CRT.items():
        for r in inv[inv.quantity == name].itertuples():
            rows.append(dict(year=r.year, land_use=land_use, quantity=quantity,
                             value_ha=r.value * factor if pd.notna(r.value) else None,
                             notation="" if pd.isna(r.notation) else r.notation, source=describe(r)))
    for column, quantity in (("drained_n_poor_organic_kha", "drained_organic_n_poor"),
                             ("drained_n_rich_organo_mineral_kha", "drained_organic_n_rich")):
        both = nid.groupby("year").filter(lambda g: len(g) == 2)        # years printed for both 4.A.1 and 4.A.2
        for year, g in both.groupby("year"):
            rows.append(dict(year=year, land_use="forest", quantity=quantity, value_ha=g[column].sum() * KHA,
                             notation="", source="NID 2026 Table 6.7 p.217 + Table 6.15 p.231 (4.A.1 + 4.A.2)"))
    t41 = inv[inv.quantity.isin([f"4.1.final_area.{c}" for c in TABLE41])]
    for year, g in t41.groupby("year"):
        rows.append(dict(year=year, land_use="all", quantity="area", value_ha=g.value.sum() * KHA, notation="",
                         source="EPA CRT 2026 Table4.1 row 20 'Final area', sum of all categories"))
    return pd.DataFrame(rows).sort_values(["land_use", "quantity", "year"]).reset_index(drop=True)


if __name__ == "__main__":
    df = build()
    out = ROOT / "data_sources/national_reference_areas.csv"
    df.to_csv(out, index=False, lineterminator="\n")
    print(f"{out}: {len(df)} rows; 2020 totals (ha):")
    print(df[(df.year == 2020) & (df.quantity == "area")][["land_use", "value_ha"]].to_string(index=False))
