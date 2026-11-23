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
| `test_land_balance.py` | Land is conserved in every scenario. The land-use table, transition matrix, spared-area log, soil-group split and afforestation table must agree. |
| `test_optimisation.py` | The spared mineral-area allocation (Pyomo with HiGHS). |
| `test_national_validation.py` | The package's 2020 land-use table against the **national reference areas** (`data_sources/national_reference_areas.csv`: CRT 2026 / NID 2026 / CRF 2024 burnt area, 1990-2024, in hectares, in the land-use table's terms), within 1%. Grassland is checked as **shares** of the national area, and its `area_ha` against the input: the grassland area is herd-derived by design (`docs/grassland_area.md`). Each known gap names its cause (D1-D10). |
| `test_inventory_coverage.py` | `land_use_database.db` against CRT 2026 / NID 2026 (`data_sources/`), within 0.5%. |
| `test_spelling.py` | No misspelt names in the source, README or docs pages. The renamed public names still work, with a `DeprecationWarning`. |
| `_helpers.py` | Paths, input loaders, and a cached pipeline run. |

## Input sets
- **`data/`** (national): `scenario_dataframe.csv`, `total_grassland_area.csv`, `spared_area.csv`, `spared_area_breakdown.csv`. `docs/example.ipynb` also uses them.
- **`data/goblin_lite_input/`**: a copy of `goblin_lite/tests/data/integration/input/`. The tests read these files the way goblin_lite's integration test does: no `index_col`, string scenario columns.
- **`geo_data/`** (catchment): `scenario_input_dataframe.csv`, `grassland_area.csv`, `spared_area.csv`, `spared_area_breakdown.csv`.
  - These were made with grassland_production's `geo_grassland_production.geo_grassland_output.GrasslandOutput("ireland", 2020, 2050, scenario_input_dataframe, future_animals, past_animals)`, through its `total_grassland_area()`, `total_spared_area()` and `total_spared_area_breakdown()`.
  - The animal input files and the script (`geo_integrations/geo_example.py`) are in git history at commit c0d03eb.
  - geo_goblin_py keeps no stored inputs, so this set is the catchment safety net.

## Golden files
`golden/<case>_<table>.csv` was made from landcover_assignment 0.4.0 at c0d03eb, solved with HiGHS (2026-11-23). It gives identical results on pandas 2.1.4 / numpy 1.26 / SQLAlchemy 1.4 and on pandas 3.1 / numpy 2.5 / SQLAlchemy 2.1.
