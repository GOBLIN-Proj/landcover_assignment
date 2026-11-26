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
- D4: the grassland nutrient-rich / nutrient-poor split, by year, for the drained and the rewet-status rows: rich
  fraction = (CRT 4(II).C.1 CH4 implied factor - EF poor) / (EF rich - EF poor), with the NID 2026 s.6.5.2 factors in
  data_sources/nid2026_grassland_organic_factors.csv (rewet-status factors converted from kg CH4-C to kg CH4). 2020:
  drained 0.4525, rewet status 0.4471 (0.45 before). The split reproduces CRT Table4.C 4.C.1 organic soil carbon in
  every year (tests/test_database_build.py).
- D6a: the national forest row mirrors cbm_runner 0.6.1 (historic forest disturbances aligned with the NID and forest
  expert judgement): `managed_forest_data` holds cbm_runner's managed forest area (FM + AF) and forest fire by year,
  1990-2070, and `forest_fire_rate` its scenario fire rate, all derived from cbm_runner's disturbance events and
  inventories (data_sources/cbm_runner_forest*.csv, tools/export_cbm_runner_forest.py). `forest_data` keeps the
  inventory forest (CRT, NID) for the audit and for the drained hectares.
- D5: our grassland rewet-status columns keep their names and meaning (NID s.6.5.2) and are filled from CRT 4(II).C.1
  "Other organic soils" (CRT 2026 reports "Rewetted organic soils" as NO).
- D7: cropland and settlement from CRT 4.B and 4.E. A notation key (NO) is stored as 0 in the data tables and kept in
  `inventory_values`.

- D6b (owner, 2026-11-25): burnt area (`burnt_kha`) of grassland, wetland and cropland. 1990-2022 = CRF 2024
  Table4(V) (4.C.1, 4.D.1, 4.B.1; notation key NO -> 0). The CRF has no 2023-2024 and the CRT reports no burnt area,
  so 2023-2024 are derived: grassland and wetland = CRT 2026 Table4(IV) wildfire CH4 / the mean implied CH4 per ha
  burnt in 2020-2022; cropland = the mean CRF burnt area 2020-2022 (its implied CH4 per ha is too inconsistent to
  back-calculate). Settlement: 0 (no inventory burnt area).
- D8 (owner, 2026-11-25): the `NIR` table is rebuilt, not dropped (a national land-area table for quick validation
  and other users of the package): Table4.1 final area by land category, CRT 2026, 1990-2024, taken from the same
  extracted rows as `inventory_values` (`4.1.final_area.*`). Columns and 0.4.0 labels are kept. 0.4.0 held the
  CRF 2024 "Initial area" under scrambled years.
- D9 (owner, 2026-11-26): `forest_soil_yield_mapping` keeps its 0.4.0 values; source Upton et al. (2013) Table 2
  (NFS soil category -> Sitka yield class), the six categories grouped as the Teagasc NFS soil groups (1-2, 3-4, 5-6; owner confirmed).
  It is the only source of the afforestation yield classes (the CBM template rows are built from it).

Pending (values kept from the 0.4.0 database, CRF 2024 vintage; see tools/export_legacy_columns.py):
- `forest_data.burnt_kha` (CRF 2024 4.A.1, 1990-2022; 2023-2024 empty), read only by the catchment tree (geo to-do;
  the national forest row uses cbm_runner's fire, D6a);

Two builds give byte-identical files (same SQLite library). Usage, from the repo root:
    .venv/bin/python tools/build_database.py
"""
import hashlib
import sqlite3
import sys
from pathlib import Path

import pandas as pd

from landcover_assignment.resource_manager.units import CH4_C_TO_CH4, HA_TO_KHA

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.5.0"
OUTPUT = ROOT / f"src/landcover_assignment/database/land_use_database_{VERSION}.db"
YEARS = list(range(1990, 2025))
INPUTS = ("data_sources/inventory_areas.csv", "data_sources/nid2026_forest_organic_soils.csv",
          "data_sources/legacy_burnt_area.csv",
          "data_sources/forest_soil_yield_mapping.csv", "data_sources/nid2026_grassland_organic_factors.csv",
          "data_sources/cbm_runner_forest.csv", "data_sources/cbm_runner_forest_parameters.csv",
          "tools/build_database.py")
CBM_YEARS = list(range(1990, 2071))

SOURCES = [
    ("CRT2026", "EPA Ireland, Common Reporting Tables 2026 (IRL-CRT-2026-V1.0, one workbook per year, 1990-2024), "
                "extracted by tools/extract_inventory.py into data_sources/inventory_areas.csv"),
    ("NID2026", "EPA Ireland, National Inventory Document 2026, Table 6.7 p.217 (4.A.1) and Table 6.15 p.231 (4.A.2), "
                "transcribed by tools/transcribe_nid_forest.py into data_sources/nid2026_forest_organic_soils.csv; "
                "s.6.5.2 p.271-272 grassland organic soil emission factors, transcribed into "
                "data_sources/nid2026_grassland_organic_factors.csv"),
    ("CRF2024", "EPA Ireland, Common Reporting Format 2024 submission, Table4(V) biomass burning: area burnt "
                "(1990-2022), extracted by tools/extract_inventory.py into data_sources/inventory_areas.csv"),
    ("LEGACY040", "landcover_assignment 0.4.0 database land_use_database.db (CRF 2024 vintage, git 25a83b4), "
                  "exported by tools/export_legacy_columns.py into data_sources/legacy_*.csv and "
                  "forest_soil_yield_mapping.csv"),
    ("UPTON2013", "Upton, V., Ryan, M., Farrelly, N. and O'Donoghue, C. (2013) The potential economic returns of "
                  "converting agricultural land to forestry: an analysis of system and soil effects from 1995 to 2009. "
                  "Irish Forestry 70: 61-74. Table 2 (p.5): National Farm Survey soil category -> expected Sitka "
                  "spruce yield class (Farrelly et al. 2011 productivity model): 1 Wide 24, 2 Moderately wide 24, "
                  "3 Somewhat limited 20, 4 Limited 20, 5 Very limited 18, 6 Extremely limited 14"),
    ("CBM061", "goblin_cbm_runner 0.6.1 (GitHub GOBLIN-Proj/goblin_cbm_runner main, cfc0199), database "
               "cbm_runner_database_0.6.2.db: FM and AF inventories and disturbance events. Historic forest "
               "disturbances aligned with the NID and forest expert judgement (prepared by the forest consultant who "
               "prepared them for the NID). Exported by tools/export_cbm_runner_forest.py into "
               "data_sources/cbm_runner_forest.csv and cbm_runner_forest_parameters.csv"),
    ("PACKAGE", "landcover_assignment parameter or key, set in tools/build_database.py"),
]

# Column recipes. Each entry: column -> (kind, argument, unit, description, decision)
#   crt: CRT quantity in data_sources/inventory_areas.csv (notation key -> 0)
#   crt_rich: (CRT 4(II).C.1 row, "rich" or "poor"): the row's area x its rich (or poor) fraction (D4)
#   nid: NID column, 4.A.1 + 4.A.2, interpolated between printed years
#   legacy_burnt: data_sources/legacy_burnt_area.csv
#   burnt: (CRF burnt area code, CRT wildfire CH4 quantity or None): D6b, see burnt_series
#   zero: 0 in every year (PACKAGE parameter)
REFRESH = "refresh: CRF 2024 -> CRT 2026"
D6 = ("pending D6, geo to-do G1: catchment forest burnt area (CRF 2024 4.A.1, 1990-2022; 2023-2024 NULL); the "
      "national forest row uses cbm_runner fire (D6a)")
D6B = "D6b: inventory burnt area"
BURNT_FACTOR_YEARS = (2020, 2021, 2022)
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
        "drained_rich_organic_kha": ("crt_rich", ("drained", "rich"), "kha",
                                     "drained nutrient-rich organic grassland soil", "D4"),
        "drained_poor_organic_kha": ("crt_rich", ("drained", "poor"), "kha",
                                     "drained nutrient-poor organic grassland soil", "D4"),
        "rewetted_rich_organic_kha": ("crt_rich", ("other", "rich"), "kha",
                                      "nutrient-rich organic grassland soil with rewet status (NID s.6.5.2; CRT 2026 "
                                      "'Other organic soils')", "D5, D4"),
        "rewetted_poor_organic_kha": ("crt_rich", ("other", "poor"), "kha",
                                      "nutrient-poor organic grassland soil with rewet status (NID s.6.5.2; CRT 2026 "
                                      "'Other organic soils')", "D5, D4"),
        "burnt_kha": ("burnt", ("C.1", "4(IV).C.1.wildfires.ch4"), "kha", "burnt grassland area (wildfires)", D6B),
    },
    "cropland_data": {
        "total_kha": ("crt", "4.B.area", "kha", "cropland, total area", "D7"),
        "mineral_kha": ("crt", "4.B.mineral_area", "kha", "cropland on mineral soil", "D7"),
        "organic_kha": ("crt", "4.B.organic_area", "kha", "cropland on organic soil (CRT: NO -> 0)", "D7"),
        "burnt_kha": ("burnt", ("B.1", None), "kha", "burnt cropland area", D6B),
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
        "burnt_kha": ("burnt", ("D.1", "4(IV).D.1.wildfires.ch4"), "kha", "burnt wetland area (wildfires)", D6B),
    },
    "settlement_data": {
        "total_kha": ("crt", "4.E.area", "kha", "settlement, total area", "D7"),
        "mineral_kha": ("crt", "4.E.mineral_area", "kha", "settlement on mineral soil", "D7"),
        "organic_kha": ("crt", "4.E.organic_area", "kha", "settlement on organic soil (NO in some years -> 0)", "D7"),
        "burnt_kha": ("zero", None, "kha", "burnt settlement area: 0 (no inventory burnt area)", D6B),
    },
}
D9 = "D9: soil group -> yield class from Upton et al. (2013) Table 2 (values unchanged from 0.4.0)"
D8 = "D8: Table4.1 final area by land category (rebuilt; was CRF 2024 initial area under scrambled years)"
NIR_LABELS = {   # 0.4.0 label -> 4.1.final_area quantity in inventory_values; order as in 0.4.0
    "Forest land (managed)(2)": "forest_managed", "Cropland(2)": "cropland",
    "Grassland (managed)(2)": "grassland_managed", "Wetlands (managed)(2)": "wetlands_managed",
    "Wetlands (unmanaged)(2)": "wetlands_unmanaged", "Settlements(2)": "settlements", "Other land(2)": "other_land",
}
OTHER_COLUMNS = [   # (table, column, unit, description, source, transformation, decision, status)
    ("NIR", "Year", "year", "inventory year", "CRT2026", "Table4.1, one workbook per year", D8, "inventory"),
    ("NIR", "Land_cover", "label", "Table4.1 land category (0.4.0 label)", "CRT2026",
     "Table4.1 column header, with the 0.4.0 label", D8, "inventory"),
    ("NIR", "Area_kha", "kha", "Table4.1 final area of the land category", "CRT2026",
     "Table4.1 row 20 'Final area' (NO -> 0)", D8, "inventory"),
    ("forest_soil_yield_mapping", "soil_group", "group", "spared-area soil group (1 best - 3 poorest farm soil)",
     "UPTON2013", "Table 2 soil categories grouped as the Teagasc NFS soil groups: 1 = SC1-2, 2 = SC3-4, "
     "3 = SC5-6", D9, "parameter"),
    ("forest_soil_yield_mapping", "species", "label", "tree species (Sitka spruce; SGB = slow-growing broadleaf)",
     "UPTON2013", "Table 2 is for Sitka spruce; SGB is a single class (YC6) for every group", D9, "parameter"),
    ("forest_soil_yield_mapping", "yield_class", "label", "cbm_runner yield class label", "UPTON2013",
     "Sitka band holding the Table 2 yield class: group 1 YC 24 -> YC24_30, group 2 YC 20 -> YC20_24, group 3 "
     "YC 18 -> YC17_20 (SC6 YC 14 not used: below the grant threshold, hill land)", D9, "parameter"),
]


NUMERIC = {"year", "Year", "value", "Area_kha", "soil_group", "total_area_kha", "mineral_kha", "organic_kha",
           "open_area_kha", "drained_n_poor_organic_kha", "drained_n_rich_organo_mineral_kha",
           "fm_area_ha", "af_area_ha", "fm_fire_ha", "af_fire_ha"}

D6A = "D6a: mirror cbm_runner 0.6.1"
CBM_AREA_RULE = ("cumulative from cbm_runner's disturbance events, FM step 1 = 2017, AF step 1 = 1990 (DISTID4 "
                 "afforestation, DISTID7 deforestation, area-based)")
# managed_forest_data: column -> (unit, description, transformation)
MANAGED_FOREST = {
    "fm_area_ha": ("ha", "cbm_runner FM forest (present before 1990), from 2016",
                   "FM inventory area (FM_inventory_2100, 420,417.2 ha at 2016) - cumulative FM deforestation; "
                   + CBM_AREA_RULE),
    "af_area_ha": ("ha", "cbm_runner AF forest (planted since 1990; baseline planting continues to 2070)",
                   "cumulative AF afforestation - cumulative AF deforestation; " + CBM_AREA_RULE),
    "total_ha": ("ha", "managed forest = FM + AF: the national forest row's area (scenario rows add the scenario's "
                       "afforestation)", "fm_area_ha + af_area_ha; NULL before 2016"),
    "fm_fire_ha": ("ha", "cbm_runner FM forest fire (DISTID3) in the year",
                   "sum of FM_disturbances_2100 DISTID3 Amount for the step (FM step 1 = 2017); NULL = no event"),
    "af_fire_ha": ("ha", "cbm_runner AF forest fire (DISTID3) in the year",
                   "sum of AF_disturbance_2100 DISTID3 Amount for the step (AF step 1 = 1990); NULL = no event"),
    "burnt_ha": ("ha", "managed forest burnt area: the national forest row's burnt area (scenario rows add rate x "
                       "the scenario's afforestation, forest_fire_rate)",
                 "fm_fire_ha + af_fire_ha; NULL where either is NULL"),
}
# forest_fire_rate (one row): column -> (unit, description, transformation)
FIRE_RATE = {
    "fm_mean_fire_ha": ("ha/yr", "mean annual FM fire over the years with an FM fire event (2017-2070)",
                        "mean of fm_fire_ha (non-NULL)"),
    "af_mean_fire_ha": ("ha/yr", "mean annual AF fire over the years with an AF fire event (2008-2070)",
                        "mean of af_fire_ha (non-NULL)"),
    "fm_inventory_area_ha": ("ha", "FM inventory area (FM_inventory_2100 total Area)", "copied"),
    "af_inventory_area_ha": ("ha", "AF inventory area (AF_inventory_2100 total Area: all AF planting 1990-2070)",
                             "copied"),
    "rate_per_year": ("1/yr", "scenario forest fire rate: burnt ha per ha of scenario afforestation per year "
                              "(cbm_runner SCDisturbances._calculate_national_fire_rate)",
                      "(fm_mean_fire_ha + af_mean_fire_ha) / (fm_inventory_area_ha + af_inventory_area_ha)"),
}


def managed_forest_tables():
    """D6a: the cbm_runner managed forest table (by year) and its scenario fire rate (one row)."""
    cbm = read_csv("data_sources/cbm_runner_forest.csv").set_index("year")
    if [int(y) for y in cbm.index] != CBM_YEARS:
        raise ValueError("cbm_runner_forest.csv: years are not 1990-2070")
    params = read_csv("data_sources/cbm_runner_forest_parameters.csv").set_index("name").value
    cbm["total_ha"] = cbm.fm_area_ha + cbm.af_area_ha
    cbm["burnt_ha"] = cbm.fm_fire_ha + cbm.af_fire_ha
    forest = cbm[list(MANAGED_FOREST)]
    fm_mean, af_mean = cbm.fm_fire_ha.dropna().mean(), cbm.af_fire_ha.dropna().mean()
    inventory = params["fm_inventory_area_ha"] + params["af_inventory_area_ha"]
    rate = {"fm_mean_fire_ha": fm_mean, "af_mean_fire_ha": af_mean,
            "fm_inventory_area_ha": params["fm_inventory_area_ha"],
            "af_inventory_area_ha": params["af_inventory_area_ha"], "rate_per_year": (fm_mean + af_mean) / inventory}
    metadata = [("managed_forest_data", "year", "year", "year", "PACKAGE", "", "", "1990-2070", "key")]
    metadata += [("managed_forest_data", c, u, d, "CBM061", "cbm_runner_database_0.6.2.db", t, D6A, "derived")
                 for c, (u, d, t) in MANAGED_FOREST.items()]
    metadata += [("forest_fire_rate", c, u, d, "CBM061", "cbm_runner_database_0.6.2.db", t, D6A, "derived")
                 for c, (u, d, t) in FIRE_RATE.items()]
    return forest, rate, metadata


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


def burnt_series(inventory, code, ch4_quantity):
    """D6b: burnt area (kha), 1990-2024. 1990-2022 = CRF 2024 Table4(V) `burnt_area.4.<code>` (ha; notation key
    -> 0). 2023-2024: with a CRT CH4 quantity, CRT 2026 wildfire CH4 / mean implied CH4 per ha burnt over
    BURNT_FACTOR_YEARS; without one (cropland), the mean CRF burnt area over BURNT_FACTOR_YEARS."""
    rows = inventory[inventory.quantity == f"burnt_area.4.{code}"].set_index("year")
    if list(rows.index) != YEARS[:-2]:
        raise ValueError(f"burnt_area.4.{code}: years are not 1990-2022")
    missing = rows.value.isna() & (rows.notation == "")
    if missing.any():
        raise ValueError(f"burnt_area.4.{code}: no value and no notation key in {list(rows.index[missing])}")
    ha = rows.value.fillna(0.0).astype(float)
    if ch4_quantity is None:
        later = {y: ha[list(BURNT_FACTOR_YEARS)].mean() for y in (2023, 2024)}
    else:
        ch4 = crt_series(inventory, ch4_quantity)
        factor = (ch4[list(BURNT_FACTOR_YEARS)] / ha[list(BURNT_FACTOR_YEARS)]).mean()
        later = {y: ch4[y] / factor for y in (2023, 2024)}
    ha = pd.concat([ha, pd.Series(later)])
    ha.index = ha.index.astype(int)
    return ha.reindex(YEARS) * HA_TO_KHA


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


def grassland_rich_fraction(inventory, factors, row):
    """D4: nutrient-rich fraction of CRT 4(II).C.1 `row` ("drained" or "other", i.e. rewet status), by year.

    The CRT CH4 implied factor of the row is the area-weighted mix of the NID rich and poor factors, so
        rich fraction = (implied factor - EF poor) / (EF rich - EF poor).
    Drained: EF = (1 - Frac_ditch) x EF_land + Frac_ditch x EF_ditch (NID s.6.5.2 p.271). Rewet status: the NID factors
    are in kg CH4-C, converted to kg CH4 like the CRT (p.272)."""
    if row == "drained":
        ditch = factors["frac_ditch"] * factors["ef_ch4_drained_ditch"]
        poor = (1 - factors["frac_ditch"]) * factors["ef_ch4_drained_land_poor"] + ditch
        rich = (1 - factors["frac_ditch"]) * factors["ef_ch4_drained_land_rich"] + ditch
    else:
        poor = factors["ef_ch4_rewet_status_poor"] * CH4_C_TO_CH4
        rich = factors["ef_ch4_rewet_status_rich"] * CH4_C_TO_CH4
    fraction = (crt_series(inventory, f"4(II).C.1.{row}.ief_ch4") - poor) / (rich - poor)
    if ((fraction < 0) | (fraction > 1)).any():
        raise ValueError(f"4(II).C.1.{row}: rich fraction outside 0-1")
    return fraction, poor, rich


def build_tables():
    inventory = read_csv("data_sources/inventory_areas.csv")
    nid = read_csv("data_sources/nid2026_forest_organic_soils.csv")
    burnt = read_csv("data_sources/legacy_burnt_area.csv")
    f = read_csv("data_sources/nid2026_grassland_organic_factors.csv")
    factors = dict(zip(f.name, f.value))
    tables, metadata = {}, []
    for table, columns in TABLES.items():
        data = {"year": YEARS}
        metadata.append((table, "year", "year", "inventory year", "PACKAGE", "", "", "1990-2024", "key"))
        for column, (kind, arg, unit, description, decision) in columns.items():
            if kind == "crt":
                values = crt_series(inventory, arg)
                source, reference, transformation, status = "CRT2026", crt_reference(inventory, arg), \
                    "kha as reported; notation key -> 0", "inventory"
            elif kind == "crt_rich":
                row, part = arg
                fraction, poor, rich = grassland_rich_fraction(inventory, factors, row)
                area = f"4(II).C.1.{row}.area"
                values = crt_series(inventory, area) * (fraction if part == "rich" else 1 - fraction)
                source, status = "CRT2026", "derived"
                reference = (f"{crt_reference(inventory, area)}; rich fraction from "
                             f"{crt_reference(inventory, f'4(II).C.1.{row}.ief_ch4')} and NID 2026 s.6.5.2")
                transformation = (f"area x {part} fraction; rich fraction = (CH4 implied factor - {poor:.2f}) / "
                                  f"({rich:.2f} - {poor:.2f}) kg CH4/ha (NID nutrient-poor and nutrient-rich factors, "
                                  f"data_sources/nid2026_grassland_organic_factors.csv); 2020: "
                                  f"{fraction[2020]:.4f}")
            elif kind == "nid":
                values = nid_series(nid, arg)
                printed = sorted({int(y) for y in nid.year})
                source, reference, status = "NID2026", f"Table 6.7 + Table 6.15, column {arg}", "derived"
                transformation = ("4.A.1 + 4.A.2; years not printed interpolated linearly per category "
                                  f"(printed: {printed[0]}-{printed[-1]}, gaps 1991-94, 1996-99, 2001-04, "
                                  "and 2006-09 for 4.A.2)")
            elif kind == "burnt":
                code, ch4_quantity = arg
                values = burnt_series(inventory, code, ch4_quantity)
                years = "-".join(str(y) for y in (BURNT_FACTOR_YEARS[0], BURNT_FACTOR_YEARS[-1]))
                source, status = "CRF2024", "derived"
                reference = f"Table4(V) burnt_area.4.{code} (ha)" + (
                    f"; 2023-2024 from CRT 2026 {ch4_quantity}" if ch4_quantity else "")
                transformation = "ha / 1000; 1990-2022 as reported (notation key NO -> 0); 2023-2024 " + (
                    f"= CRT 2026 wildfire CH4 / mean implied CH4 per ha burnt {years} (CRT CH4 / CRF area)"
                    if ch4_quantity else
                    f"= mean CRF burnt area {years} (implied CH4 per ha too inconsistent to back-calculate)")
            elif kind == "zero":
                values = pd.Series(0.0, index=YEARS)
                source, reference, transformation, status = "PACKAGE", "", "0 in every year", "parameter"
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


def nir_table(inventory):
    """The `NIR` table (D8): Table4.1 final area (kha) by year and land category, from the extracted CRT rows."""
    series = {label: crt_series(inventory, f"4.1.final_area.{name}") for label, name in NIR_LABELS.items()}
    return [(year, label, float(series[label][year])) for year in YEARS for label in NIR_LABELS]


def build(path=OUTPUT):
    """Write the database to ``path`` (overwritten). Returns the path."""
    path = Path(path)
    inventory, nid, tables, metadata = build_tables()
    managed_forest, fire_rate, cbm_metadata = managed_forest_tables()
    metadata = metadata + cbm_metadata
    nir = nir_table(inventory)
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
        cols = ", ".join(['"year" INTEGER'] + [f'"{c}" REAL' for c in MANAGED_FOREST])
        cur.execute(f'CREATE TABLE "managed_forest_data" ({cols})')
        cur.executemany(f'INSERT INTO "managed_forest_data" VALUES ({", ".join("?" * (len(MANAGED_FOREST) + 1))})',
                        [(int(y), *(None if pd.isna(v) else float(v) for v in row))
                         for y, row in zip(managed_forest.index, managed_forest.itertuples(index=False, name=None))])
        cur.execute(f'CREATE TABLE "forest_fire_rate" ({", ".join(f"{chr(34)}{c}{chr(34)} REAL" for c in FIRE_RATE)})')
        cur.execute(f'INSERT INTO "forest_fire_rate" VALUES ({", ".join("?" * len(FIRE_RATE))})',
                    tuple(float(fire_rate[c]) for c in FIRE_RATE))
        cur.execute('CREATE TABLE "NIR" ("Year" INTEGER, "Land_cover" TEXT, "Area_kha" REAL)')
        cur.executemany('INSERT INTO "NIR" VALUES (?, ?, ?)',
                        nir)
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
                 "CRF2024" if r.source == "EPA CRF 2024" else "CRT2026", f"{r.sheet} row {r.row} col {r.column} ('{str(r.label).strip()}')")
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
