# The package database and its sources

The national areas and soil shares come from a SQLite database shipped with the package,
`src/landcover_assignment/database/land_use_database_0.5.0.db`. The version in the name is the package version that
built it.

## How it is built
`tools/build_database.py` builds the database from the files in `data_sources/`. Two builds give the same file.

| file | made by | holds |
|---|---|---|
| `inventory_areas.csv` | `tools/extract_inventory.py` | EPA CRT 2026 areas and wildfire emissions, 1990-2024, and CRF 2024 burnt area, 1990-2022, with sheet, row, column and label for each cell, and notation keys (NO, NA, IE) |
| `nid2026_forest_organic_soils.csv` | `tools/transcribe_nid_forest.py` | NID 2026 Tables 6.7 (p.217) and 6.15 (p.231): forest organic soil areas |
| `nid2026_grassland_organic_factors.csv` | transcribed | NID 2026 s.6.5.2 (p.271-272): grassland organic soil emission factors, nutrient rich and nutrient poor |
| `cbm_runner_forest.csv`, `cbm_runner_forest_parameters.csv` | `tools/export_cbm_runner_forest.py` | cbm_runner 0.6.1 managed forest (FM + AF) area and forest fire by year, 1990-2070, and the inventory areas behind its scenario fire rate (derived; see below) |
| `legacy_burnt_area.csv`, `legacy_nir_table.csv`, `forest_soil_yield_mapping.csv` | `tools/export_legacy_columns.py` | values kept from the 0.4.0 database until their decision is taken (of the burnt area, only `forest_data.burnt_kha` is still read) |

The database records its own provenance:

- `column_metadata`: for every column, its unit, meaning, source, cell reference, transformation, decision and status;
- `sources`: the documents behind each source id;
- `inventory_values`: every extracted inventory value, with notation keys;
- `build_info`: the package version and the SHA-256 of every input file.

The tables the code reads (`forest_data`, `grassland_data`, `cropland_data`, `wetland_data`, `settlement_data`,
`NIR`, `forest_soil_yield_mapping`) keep their 0.4.0 names and columns. Two tables are new in 0.5.0:
`managed_forest_data` and `forest_fire_rate` (cbm_runner's managed forest and forest fire, decision D6a).

**Units.** Values are stored as published (areas in kha), and `column_metadata` names each column's unit. The readers
convert on read, column by column, with `landcover_assignment.resource_manager.units` (kha to ha), the one place
where unit conversions live, as in landcover_lca.

## What each land use takes from the inventory (2020 values)

| land use | area | details |
|---|---|---|
| forest | cbm_runner managed forest (FM + AF), 730.1 kha (CRT 4.A: 798.7 kha) | drained N-poor 287.4 kha (share 0.394) and N-rich 97.4 kha (0.133), NID 2026 Tables 6.7 + 6.15; the rest mineral (0.473); burnt 305 ha (cbm_runner FM + AF fire). See below |
| grassland | CRT 4.C, 4,218.5 kha | the national area for the balance (see [grassland area](grassland_area.md)); drained organic = CRT 4(II).C.1 drained, 136.6 kha (rich 0.4525); rewet status = CRT 4(II).C.1 "Other organic soils", 203.3 kha (rich 0.4471) |
| cropland | CRT 4.B, 747.7 kha | all mineral (CRT organic: NO) |
| wetland | CRT 4.D total, 1,212.5 kha | domestic peat 88.3, industrial peat 55.5 (4(II)), rewetted industrial 22.9, rewetted domestic 14.4, near-natural 871.3, unmanaged 108.4 kha |
| settlement | CRT 4.E, 126.1 kha | organic 2.0 kha |

### Forest area and fire: mirroring cbm_runner (D6a)
The forest row mirrors cbm_runner 0.6.1, so that landcover_lca and cbm_runner work on the same forest area and the
same burnt area. cbm_runner's historic forest disturbances are aligned with the NID and forest expert judgement: they
were prepared by the forest consultant who prepared them for the NID. Every value is **derived** from cbm_runner's
database (`cbm_runner_database_0.6.2.db`, the file inside the 0.6.1 release) by `tools/export_cbm_runner_forest.py`,
and the database records it with source `CBM061` and status `derived`.

cbm_runner models managed forest in two streams, the same in every scenario, plus the scenario's own afforestation:

- **FM**, forest present before 1990: 420,417.2 ha at its 2016 baseline, less about 1,000 ha/yr of deforestation;
- **AF**, forest planted since 1990: the planting record, with baseline planting continuing to 2070;
- **SC**, the scenario's afforestation, which is what this package's afforestation table gives cbm_runner.

The package's forest row is built the same way:

| | rule |
|---|---|
| area | FM + AF in that year (`managed_forest_data.total_ha`); target-year rows add the scenario's afforestation |
| drained organic | the NID calibration-year hectares (287.4 kha N-poor, 97.4 kha N-rich in 2020), held fixed |
| mineral | the rest. The open area on organic soil and roads that CBM doesn't model are not emitting (as in the NID), and AF planting after the calibration year is on mineral soil |
| burnt | FM fire + AF fire in that year (`managed_forest_data.burnt_ha`); target-year rows add rate x the scenario's afforestation |

**The scenario fire rate** is cbm_runner's (`SCDisturbances._calculate_national_fire_rate`): mean annual FM fire
(9,826 ha over 2017-2070 = 182.0 ha/yr) plus mean annual AF fire (6,872 ha over 2008-2070 = 109.1 ha/yr), divided by
the FM and AF inventory areas (420,417.2 + 612,488.4 ha): 2.8177e-4 per year (`forest_fire_rate.rate_per_year`).
cbm_runner plants the scenario's afforestation evenly up to its afforestation end year and each year burns rate x the
area planted so far, so in the target year it burns rate x all of it.

**Worked example** (national test data, 2050; scenario 0 afforests 1,700,279 ha, scenario 2 nothing):

| | 2020 | 2050, scenario 2 | 2050, scenario 0 |
|---|---|---|---|
| FM area | 417,617 | 387,827 | 387,827 |
| AF area | 312,482 | 483,664 | 483,664 |
| scenario afforestation | 0 | 0 | 1,700,279 |
| **forest area** | **730,099** | **871,492** | **2,571,770** |
| drained N-poor + N-rich | 384,800 | 384,800 | 384,800 |
| FM + AF fire | 177 + 128 | 169 + 81 | 169 + 81 |
| scenario fire (2.8177e-4 x afforestation) | 0 | 0 | 479 |
| **burnt area** | **305** | **250** | **729** |

Before 0.5.0 the forest area was the inventory area held constant (plus the scenario's afforestation), and the burnt
area was 178 ha in every scenario and year (CRF 4.A.1 only; new forest never burned).

**The transition matrix and the afforestation table do not change.** Between 2020 and 2050 managed forest grows by
141,393 ha in every scenario (AF baseline planting less FM deforestation). cbm_runner plants and burns that itself, so
it is not a transition from grassland: `Grassland_to_Forest` is the forest row's change less the managed-forest
change, which is the scenario's afforestation. Otherwise cbm_runner would plant it a second time. For the same
reason the target-year land-use table's total is the baseline total plus the managed-forest change.

**Against the inventory (2020).** CRT 4.A is 798,747 ha, 68,648 ha more than CBM's managed forest: the NID open area
on organic soil (46,810 ha) and roads and other areas that CBM doesn't model. None of it emits, so landcover_lca's
forest drainage is charged on the same NID hectares as before. CBM's 305 ha burnt compares with CRF 2024 4.A 300 ha.
The calibration year must be 2017 or later (cbm_runner's FM fire starts in 2017).

### Forest soils
The forest area splits into four parts (2020): mineral soil 367.1 kha (0.460), drained N-poor organic 287.4 kha
(0.360), drained N-rich organo-mineral 97.4 kha (0.122), and open area on organic soil 46.8 kha (0.059). The open
area is never drained, so nothing emits from it. These are the inventory's (CRT 4.A) parts; the package's forest row
uses the NID drained hectares on cbm_runner's managed forest area (above), so its shares are 0.394 / 0.133 / 0.473.

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

### Grassland organic soils: nutrient rich and nutrient poor
The NID charges nutrient-rich and nutrient-poor organic grassland soil at different rates but publishes no area for
each. The package works out the split for each year from the inventory itself. The CRT gives, for each grassland
organic row (drained, and rewet status), the CH4 emitted per hectare. That figure is a mix of the NID rich and poor
factors, weighted by area, so

    rich fraction = (CRT CH4 per hectare - poor factor) / (rich factor - poor factor)

| row | poor factor | rich factor | rich fraction 2020 | 2022-2024 |
|---|---|---|---|---|
| drained | 0.95 x 11.76 + 0.05 x 1165 = 69.42 kg CH4/ha | 0.95 x 16.0 + 0.05 x 1165 = 73.45 kg CH4/ha | 0.4525 | 0.449 |
| rewet status | 68.1 kg CH4-C/ha = 90.8 kg CH4/ha | 216 kg CH4-C/ha = 288.0 kg CH4/ha | 0.4471 | 0.449 |

The drained factors combine the field and ditch factors, with 5% of the area in ditches (NID p.271). The rewet-status
factors are printed in kg CH4-C and converted to kg CH4 (x 16/12, `units.CH4_C_TO_CH4`). The factors are in
`data_sources/nid2026_grassland_organic_factors.csv`, the rule in `tools/build_database.py`
(`grassland_rich_fraction`), and each column's `transformation` entry repeats it. In earlier years the drained land
was richer (0.551 in 1990).

**Checks.** The rich and poor soils also lose carbon at different rates (drained 6.1 and 1.3 t C/ha, rewet status
0.5 and 0.85). With the split above, the package areas reproduce the CRT grassland organic soil carbon (Table4.C,
4.C.1) in every year, 1990-2024 (`tests/test_database_build.py`). The CRT N2O per hectare for drained grassland
(Table3.D) gives the same drained fraction (0.4525 in 2020).

**Scenarios.** The future split is not projected on its own. Drained land that stays drained keeps the
calibration year's rich fraction; rewetted land carries that fraction into the rewet-status pool.

Before 0.5.0 both rows were split 0.45 / 0.55 every year, with no recorded source. landcover_lca's inventory tests
use the same rule as above.

### Burnt area of grassland, wetland and cropland (D6b)
Calibration-year rows carry that year's inventory burnt area (as a share of the land use's area). The data:

| years | grassland, wetland | cropland |
|---|---|---|
| 1990-2022 | CRF 2024 Table4(V) area burnt (4.C.1, 4.D.1) | CRF 2024 Table4(V) (4.B.1); years reported NO are 0 |
| 2023-2024 (derived) | CRT 2026 Table4(IV) wildfire CH4 / the mean implied CH4 per ha burnt in 2020-2022 (CRT CH4 / CRF area: grassland 0.226, wetland 2.48 t CH4/ha) | the mean CRF burnt area 2020-2022, 42.9 ha |

The CRF stops at 2022 and the CRT reports no burnt area, hence the derived years. Cropland's implied CH4 per ha
varies too much (0.005-0.011 t/ha, and the CRT reports NO in 2020 where the CRF has 14.3 ha) to back-calculate, so
its 2023-2024 take the 3-year average instead. Settlement: 0 (no inventory burnt area).

| ha | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| grassland | 435.7 | 321.4 | 321.4 | 1,632.8 | 114.0 |
| wetland | 335.7 | 135.7 | 135.7 | 780.1 | 31.2 |
| cropland | 14.3 | 57.1 | 57.1 | 42.9 | 42.9 |

**Target-year rows** burn at the 3-year rate over 2022-2024 (sum of burnt area / sum of area;
`NationalLandCover.get_burnt_rate`, `BURNT_RATE_YEARS`), applied to the whole row, so land a scenario adds to wetland
or cropland burns too: grassland 1.64e-4, wetland 2.61e-4, cropland 6.4e-5 per year. Before 0.5.0 they carried the
calibration-year share (2020, a low fire year), and added land burnt nothing. National test scenario 0, 2050:
grassland 146 -> 231 ha, wetland 336 -> 316 ha, cropland 14 -> 48 ha.

The catchment tree keeps its own rule (the all-years average), which now covers 1990-2024; its forest still reads
`forest_data.burnt_kha`. Both are on the catchment to-do list for later.

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
| `forest_data.burnt_kha` (read only by the catchment tree) | 0.4.0 values (CRF 2024 4.A.1), 1990-2022; 2023-2024 empty | catchment forest burnt area (the national forest row uses cbm_runner's fire, D6a) |
| `NIR` table | 0.4.0 table (unused by the code) | D8: rebuild from Table4.1 or drop |
| `forest_soil_yield_mapping` | 0.4.0 table | D9: document its source |
