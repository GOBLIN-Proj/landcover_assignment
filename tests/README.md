# Tests

Run everything from the repo root (any folder works; paths are absolute):

```bash
python -m unittest discover -s tests -p "test_*.py"
```

CI runs the same command with warnings as errors, on the oldest and the latest dependency sets (`.github/workflows/main.yml`):

```bash
python -W error -W "ignore:::catchment_data_api.catchment_data_api" -m unittest discover -s tests -p "test_*.py"
```

No test writes into a data folder. Expected failures mark known bugs and data gaps; each one names the finding
(1-14) or data decision (D1-D10) in the 0.5.0 plan that removes it.

| file | what it guards |
|---|---|
| `test_golden_outputs.py` | Every output table must match the recorded baseline (`golden/`) for three input sets. Results change only through an approved change, which regenerates the affected golden files in the same commit. |
| `test_frozen_interface.py` | The import paths, signatures, table columns and index conventions that goblin_lite, geo_goblin_py, landcover_lca and cbm_runner use. Also checks the rule that **rewetted grassland stays grassland** (see `docs/rewetting.md`). |
| `test_land_balance.py` | Land is conserved in every scenario. The land-use table, transition matrix, spared-area log, soil-group split and afforestation table must agree. Each soil group's transitions plus its spared organic area (stays grassland, soil group 3) add up to its spared area (finding 3). |
| `test_optimisation.py` | The spared mineral-area allocation (Pyomo with HiGHS). When mineral land is short, every target is cut by the same percentage (step 7, item 13), also through the whole pipeline. |
| `test_national_validation.py` | The package's 2020 land-use table against the **national reference areas** (`data_sources/national_reference_areas.csv`: CRT 2026 / NID 2026 / CRF 2024 burnt area, 1990-2024, in hectares, in the land-use table's terms), within 1%. Grassland (herd + balance) is checked in hectares and shares. Each known gap names its cause (D1-D10). |
| `test_inventory_coverage.py` | The package database against CRT 2026 / NID 2026 (`data_sources/`), within 0.5%. |
| `test_forest_cbm.py` | D6a: the national forest row mirrors cbm_runner 0.6.1 (managed forest area FM + AF, NID drained hectares, FM + AF fire plus the scenario fire rate), the rate matches cbm_runner's formula (and its database, when checked out next to this repo), and `Grassland_to_Forest` stays the scenario's afforestation. |
| `test_database_build.py` | The package database is what `tools/build_database.py` builds from `data_sources/` (same rows; two builds byte-identical); every column has unit, source and decision in `column_metadata`; every source is used, has a checked link where one is recorded, and nothing is read from the 0.4.0 database; the D-decisions taken are in the data, and the D4 grassland rich/poor split reproduces the CRT organic soil carbon in every year. |
| `test_burnt_area.py` | D6b: grassland, wetland and cropland target-year rows burn at the 3-year rate over 2022-2024 (sum burnt / sum area) on the whole row; calibration rows keep the year's inventory share; settlement and farmable_condition 0. |
| `test_grassland_balance.py` | Dossier LA2: grassland row = herd grassland + national balance (calibration year). The balance is constant in every scenario and never spared. `get_grassland_area_breakdown()` adds up and its spared organic columns match the spared-area log. Edge cases: other calibration years, a negative balance, a year missing from the database. |
| `test_soil_yield_mapping.py` | D9: the soil group -> yield class table follows Upton et al. (2013) Table 2 (each Sitka band holds the Table 2 yield class), is the only source of the afforestation template rows (`cbm_default_data` built from it, no hard-coded yield classes), and records its source in the database. |
| `test_spared_area_edge_cases.py` | Step 7, findings 4 and 5 (national tree): a scenario with zero spared area runs (grassland unchanged, no transitions, nothing planted); a spared-area column with more than one non-zero value, or a scenario missing from the spared-area breakdown, raises a clear `ValueError`; a scenario with no soil group 3 has no organic potential and runs. |
| `test_rewetting_target.py` | Step 7, finding 8: rewetting never exceeds the scenario's target (rewetted proportion x spared area); organic land spared beyond it stays in its current condition (national scenario 3: drained hectares unchanged, `spared_drained_organic_grassland` 126,410 ha, `spared_rewetted_organic_grassland` 188,230 ha); every scenario has the same six log entries. |
| `test_transition_sign.py` | Step 7, item 14 (LA1): the transition matrix writes the signed change; a land use other than grassland that shrinks raises `ValueError` (the matrix only records conversions from grassland). |
| `test_peat_phase_out.py` | D10: target-year wetland rows phase out industrial and domestic peat extraction linearly to 0 in 2040, the stopped share moving to rewetted (2050: none left; 2030: half); wetland area and other shares unchanged; calibration rows are the inventory. |
| `test_example.py` | The usage example `example.py` (not a test itself) runs on `data/`, and the README's usage section is an exact copy of it. |
| `test_spelling.py` | No misspelt names in the source, README or docs pages. The renamed public names still work, with a `DeprecationWarning`. |
| `_helpers.py` | Paths, input loaders, and a cached pipeline run. |

## Input sets
- **`data/`** (national): `scenario_dataframe.csv`, `total_grassland_area.csv`, `spared_area.csv`, `spared_area_breakdown.csv`. `example.py` and `docs/example.ipynb` also use them.
- **`data/goblin_lite_input/`**: a copy of `goblin_lite/tests/data/integration/input/`. The tests read these files the way goblin_lite's integration test does: no `index_col`, string scenario columns.
- **`geo_data/`** (catchment): `scenario_input_dataframe.csv`, `grassland_area.csv`, `spared_area.csv`, `spared_area_breakdown.csv`.
  - These were made with grassland_production's `geo_grassland_production.geo_grassland_output.GrasslandOutput("ireland", 2020, 2050, scenario_input_dataframe, future_animals, past_animals)`, through its `total_grassland_area()`, `total_spared_area()` and `total_spared_area_breakdown()`.
  - The animal input files and the script (`geo_integrations/geo_example.py`) are in git history at commit c0d03eb.
  - geo_goblin_py keeps no stored inputs, so this set is the catchment safety net.

## Golden files
`golden/<case>_<table>.csv` was made from landcover_assignment 0.4.0 at c0d03eb, solved with HiGHS (2026-11-23). It gives identical results on pandas 2.1.4 / numpy 1.26 / SQLAlchemy 1.4 and on pandas 3.1 / numpy 2.5 / SQLAlchemy 2.1.

Changes since then, each made by an approved dossier in the same commit:
- **LA2, grassland balance:** the grassland rows of `national_landuse.csv` and `goblin_lite_landuse.csv` (each grassland sub-area + the balance). The geo files and all other tables are unchanged.
- **Step 6a, database rebuilt from CRT 2026:** `national_` and `goblin_lite_` `landuse`, `transition_matrix` and `spared_area_log`, and `geo_landuse` (`share_burnt`).
- **D6a, forest mirrors cbm_runner:** the forest rows of `national_landuse.csv` and `goblin_lite_landuse.csv` (area, shares). Transition matrix, afforestation, spared-area log and geo files unchanged.
- **D4, grassland rich/poor split:** the grassland rows of `national_landuse.csv` and `goblin_lite_landuse.csv` (the four organic shares). The spared-area log moved by float noise only (1.5e-11 ha) and was kept.
