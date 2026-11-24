# The package database and its sources

The national areas and soil shares come from a SQLite database shipped with the package,
`src/landcover_assignment/database/land_use_database_0.5.0.db`. The version in the name is the package version that
built it.

## How it is built
`tools/build_database.py` builds the database from the files in `data_sources/`. Two builds give the same file.

| file | made by | holds |
|---|---|---|
| `inventory_areas.csv` | `tools/extract_inventory.py` | EPA CRT 2026 areas, 1990-2024, with sheet, row, column and label for each cell, and notation keys (NO, NA, IE) |
| `nid2026_forest_organic_soils.csv` | `tools/transcribe_nid_forest.py` | NID 2026 Tables 6.7 (p.217) and 6.15 (p.231): forest organic soil areas |
| `legacy_burnt_area.csv`, `legacy_nir_table.csv`, `forest_soil_yield_mapping.csv` | `tools/export_legacy_columns.py` | values kept from the 0.4.0 database until their decision is taken |

The database records its own provenance:

- `column_metadata`: for every column, its unit, meaning, source, cell reference, transformation, decision and status;
- `sources`: the documents behind each source id;
- `inventory_values`: every extracted inventory value, with notation keys;
- `build_info`: the package version and the SHA-256 of every input file.

The tables the code reads (`forest_data`, `grassland_data`, `cropland_data`, `wetland_data`, `settlement_data`,
`NIR`, `forest_soil_yield_mapping`) keep their 0.4.0 names and columns.

**Units.** Values are stored as published (areas in kha), and `column_metadata` names each column's unit. The readers
convert on read, column by column, with `landcover_assignment.resource_manager.units` (kha to ha), the one place
where unit conversions live, as in landcover_lca.

## What each land use takes from the inventory (2020 values)

| land use | area | details |
|---|---|---|
| forest | CRT 4.A, 798.7 kha | mineral share 0.460 (CRT 4.A mineral); organic share 0.360 = drained N-poor and organo-mineral share 0.122 = drained N-rich (NID 2026 Tables 6.7 + 6.15) |
| grassland | CRT 4.C, 4,218.5 kha | the national area for the balance (see [grassland area](grassland_area.md)); drained organic = CRT 4(II).C.1 drained, 136.6 kha; rewet status = CRT 4(II).C.1 "Other organic soils", 203.3 kha |
| cropland | CRT 4.B, 747.7 kha | all mineral (CRT organic: NO) |
| wetland | CRT 4.D total, 1,212.5 kha | domestic peat 88.3, industrial peat 55.5 (4(II)), rewetted industrial 22.9, rewetted domestic 14.4, near-natural 871.3, unmanaged 108.4 kha |
| settlement | CRT 4.E, 126.1 kha | organic 2.0 kha |

### Forest soils
The forest area splits into four parts (2020): mineral soil 367.1 kha (0.460), drained N-poor organic 287.4 kha
(0.360), drained N-rich organo-mineral 97.4 kha (0.122), and open area on organic soil 46.8 kha (0.059). The open
area is never drained, so nothing emits from it and it is in no share; the forest shares add up to about 0.94.

**Interpolated years.** The NID does not print the drained areas for every year:

| table | years printed | years not printed |
|---|---|---|
| Table 6.7 (4.A.1, forest remaining forest) | 1990, 1995, 2000, 2005, 2006-2024 | 1991-1994, 1996-1999, 2001-2004 |
| Table 6.15 (4.A.2, land converted to forest) | 1990, 1995, 2000, 2005, 2010-2024 | 1991-1994, 1996-1999, 2001-2004, 2006-2009 |

For a year that is not printed, each table's drained N-poor and drained N-rich areas are interpolated in a straight
line between the printed years either side (for example 1993 = 1990 + 3/5 of the change to 1995), and the two
tables are then added. Printed years, including the calibration year 2020 and 2022-2024, are the NID values exactly.
The rule is in `tools/build_database.py` (`nid_series`), and each column's `transformation` entry in
`column_metadata` repeats it.

Before 0.5.0 the drained areas were hand-typed values with no source (174.5 and 72.5 kha in 2020), and the mineral
share was 1 minus the drained shares (0.68), which counted undrained organic soil as mineral.

### Industrial peat extraction
CRT Table4.D gives 98.3 kha of industrial peat extraction (2020) and Table4(II) gives 55.5 kha. Every per-hectare
emission (on-site CO2, drainage-water DOC, CH4, N2O) is charged on the 55.5 kha. The other 42.7 kha carries only the
carbon in horticultural peat, which the inventory works out from tonnage, and which landcover_lca adds from export
statistics. The package uses the 4(II) area, so that carbon is not counted twice.

The 42.7 kha is taken to be the estimated area of private (non-Bord na Mona) horticultural peat production: the NID
(s.6.6.3) builds the industrial area from Bord na Mona's area plus an area worked back from horticultural peat sales,
and after Bord na Mona stopped harvesting in 2021 the extra area persists (28 kha in 2024). It is in the wetland
total but in no sub-share. Why the inventory charges no per-hectare emissions on it is not explained in the NID; at
the industrial rates it would be about 345 kt CO2e a year (2020).

## Still waiting for a decision

| column | now | decision |
|---|---|---|
| `burnt_kha` (every land use) | 0.4.0 values (CRF 2024), 1990-2022; 2023-2024 empty | D6: burnt area, averaging window, forest aligned with cbm_runner |
| grassland rich/poor split | 0.45 / 0.55 of the CRT drained and rewet-status areas | D4: split by year from the CRT implied factors |
| `NIR` table | 0.4.0 table (unused by the code) | D8: rebuild from Table4.1 or drop |
| `forest_soil_yield_mapping` | 0.4.0 table | D9: document its source |
