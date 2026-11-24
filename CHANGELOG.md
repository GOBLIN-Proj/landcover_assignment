# Changelog

## [Unreleased] (0.5.0, in progress)

### Added
- **Unit conversions in one place** (`resource_manager/units.py`, the landcover_lca pattern): the database readers convert each column from the unit recorded in `column_metadata` (kha to ha) instead of a hard-coded `* 1000` in each reader; `tools/` and the tests use the same constants. Outputs are bit-identical.
- **Characterisation tests** (`tests/test_*.py`): golden outputs for three input sets (national, catchment, goblin_lite's integration inputs), the interface that downstream packages rely on, land balance, the optimiser, and database coverage against CRT 2026 / NID 2026. Known bugs and data gaps are expected failures. See `tests/README.md`.
- **Inventory tooling** (`tools/`): `extract_inventory.py` (CRT 2026, 1990-2024; CRF 2024 burnt area), `transcribe_nid_forest.py` (NID 2026 Tables 6.7 and 6.15) and `build_provenance.py` (database vs inventory audit). Outputs are in `data_sources/`.
- **Documentation**: `docs/rewetting.md` explains how spared area is divided, and that rewetted spared grassland stays grassland with rewet status. The same rule is now in the README and in the docstrings of `calculate_spared_area_allocation`, `grassland_breakdown`, `grassland_distribution` and `create_transition_matrix` (national and catchment). No change in behaviour.
- **National reference areas**: `data_sources/national_reference_areas.csv` (`tools/build_national_reference.py`) holds national land areas for 1990-2024, from CRT 2026, NID 2026 and CRF 2024 (burnt area), in the land-use table's terms. `tests/test_national_validation.py` checks the 2020 land-use table against it.
- **Documentation**: `docs/grassland_area.md` and a README section explain where the grassland area comes from: herd grassland from grassland_production, plus the national balance.
- **`LandCover.get_grassland_area_breakdown()`** (national): herd, rewetted spared and other (balance) grassland for the baseline and each scenario, adding up to the grassland row. Reporting only.
- **Optimiser extensibility**: `optimise_mineral_spared_area_distribution(..., extra_constraints=[...])` takes functions that add constraints to the Pyomo model. New land uses only need an entry in `target_areas`.

### Changed
- **Database rebuilt from CRT 2026 (changes results; step 6a).** `tools/build_database.py` builds `land_use_database_0.5.0.db` from `data_sources/` (CRT 2026 and NID 2026, 1990-2024); two builds give the same file. It replaces `land_use_database.db` (CRF 2024, 1990-2022, partly hand-made). The database now records its sources: `column_metadata` (unit, source, cell, transformation, decision for every column), `sources`, `inventory_values` (with notation keys) and `build_info` (input hashes). Table and column names the code reads are unchanged. See `docs/data_sources.md`.
  - **Forest (D3):** area 776.4 -> 798.7 kha (CRT 4.A); `share_mineral` 0.682 -> 0.460 (CRT mineral area; was 1 - drained shares); `share_organic` (drained N-poor) 0.225 -> 0.360 and `share_organic_mineral` (drained N-rich) 0.093 -> 0.122 (NID Tables 6.7 + 6.15; the old values had no source). landcover_lca's forest drainage emissions move from about 0.63x to about 1.0x the inventory.
  - **Grassland (D5):** national area 4,229.1 -> 4,218.5 kha, so the balance is 313.6 kha (was 324.3). The rewet-status columns keep their names and are filled from CRT 4(II) "Other organic soils" (203.3 kha). Rich/poor split still 0.45/0.55 (D4 pending).
  - **Wetland (D1, D2):** area 1,225.2 -> 1,212.5 kha (CRT 4.D total); industrial peat extraction 77.8 -> 55.5 kha (CRT 4(II), the area charged per-hectare emissions; the other 42.7 kha in Table4.D carries only horticultural peat carbon, taken from exports downstream); rewetted industrial 37.4 -> 22.9 kha; unmanaged 126.8 -> 108.4 kha.
  - **Cropland and settlement (D7):** CRT 4.B and 4.E (settlement organic 3.2 -> 2.0 kha).
  - **Burnt area unchanged (D6 pending):** 0.4.0 values for 1990-2022, empty for 2023-2024. The all-years burnt average (catchment tree) now uses only years with a burnt area.
  - **Effect on scenarios:** small. The grassland shares barely move (mineral 0.91954 -> 0.91945), so where the spareable caps bind, 53 ha (scenarios 1-2) to 440 ha (scenario 3, national test data) that went to farmable condition stays as rewet-status grassland. Afforestation is unchanged. Catchment outputs change only in `share_burnt` (the national average now uses CRT areas).
- **Grassland balance (national tree; changes results).** The grassland row now holds the herd-derived grassland from grassland_production plus the national grassland the herd doesn't need (the balance):
  - **Balance:** the national area (package database, `grassland_data.total_kha`) minus the herd area, in the calibration year.
  - **Fixed:** it is the same in the baseline and every scenario, and it is never available to be spared.
  - **Effect:** baseline grassland equals the national area (2020: 3,904.9 + 324.3 = 4,229.1 kha), so grassland emissions are counted for all national grassland.
  - Every grassland row gains the same hectares in each sub-area. Scenario-minus-baseline differences, the transition matrix, afforestation and the spared-area log are unchanged.
  - The catchment tree is unchanged.
  - See `docs/grassland_area.md`.
- **Open-source solver**: the optimiser uses HiGHS (Pyomo `"highs"`, through `highspy`) by default, not CPLEX (`"cplex_direct"`). The objective is strictly convex, so results are unchanged (checked against the golden outputs). Dependencies: `cplex` is removed, `highspy >=1.7.2` is added, and the Pyomo floor rises to 6.9.4, the first version whose `"highs"` interface accepts the quadratic objective. Pyomo's `"appsi_highs"` interface does not.
- **Optimiser structure**: the model is documented (sets, parameters, variables, objective, constraints). Its rules are named functions. It checks that the solver is available and that the solution is optimal, and it logs instead of printing.
- **Dependencies widened** (phase 1 of the GOBLIN upgrade plan):
  - pins: `pandas >=2.1.4,<4`, `numpy >=1.25,<3`, `sqlalchemy >=1.4,<3`, `pyomo >=6.9.4,<7`, `python >=3.9,<4`;
  - `requirements.txt` now matches `pyproject.toml`.
  - Results are identical on the oldest set (pandas 2.1.4, numpy 1.26, SQLAlchemy 1.4) and the latest (pandas 3.1, numpy 2.5, SQLAlchemy 2.1).
  - `catchment_data_api` 0.1.3 still pins the oldest set itself, so a plain install resolves to it. The latest set needs that package installed with `--no-deps`.
- **CI** runs the full test suite on the oldest and latest sets, with warnings as errors, and builds the docs with warnings as errors. The required `ci` check passes only if every job passes.
- **Docs**:
  - Read the Docs configuration (`.readthedocs.yaml`, `docs/requirements.txt`);
  - docs dependency group in `pyproject.toml`;
  - the build is now free of warnings. Docstrings no longer repeat what AutoAPI generates; the duplicate descriptions and the ambiguous `DataManager` / `LandDistribution` references are fixed.
- **Spelling**: misspelt public names are renamed. The old names keep working for one release, with a `DeprecationWarning`:
  - `data_engine_creater` → `data_engine_creator`;
  - `get_national_rich_drained_orgainc_grassland` → `get_national_rich_drained_organic_grassland`;
  - geo `LandCover.catchemnt_class` → `catchment_class`;
  - the `spared_area_breakdown` keyword `intial_spared_area` → `initial_spared_area`.
  - README typos are fixed. `tests/test_spelling.py` stops them coming back.
- CI runs the new test suite.
- **Simplification (results unchanged, outputs bit-identical):**
  - **National shares:** the national land-use rows are built from one share table (`national_landcover.SHARE_SOURCES`); 1,833 → 481 lines. The `get_share_*` / `get_national_*` names remain as one-line wrappers.
  - **`Loader`:** `Loader.national_*_areas` return the tables, not bound methods.
  - **One allocation per instance:** `combined_future_land_use_area()` builds the table once per `LandCover` instance and returns copies.
  - **Catchment `Afforestation`:** a subclass of the national one that validates the scenario table; the import path and constructor are unchanged.
- **National validation of grassland**: with the balance, grassland is checked in hectares and in shares against the national inventory. The total-land check compares the table with the national total less other land.

### Fixed
- **Zero mineral area**: when no spared mineral area is available (all of it rewetted, or no mineral grassland left), the optimiser returns zeros. Before, it raised `ZeroDivisionError`.

### Removed
- Dead code:
  - the catchment `combined_future_land_use_area_old`;
  - the crop-type lookups in `CatchmentLandCover`, which called each other forever if used, and their unused `Crops()` object;
  - the unused `LandCover.data_loader_class` and `DataManager.landuse_dict` / `get_landuse_dict`.
- The built HTML docs (`docs/html`, `docs/index.html`, `docs/.nojekyll`) are no longer committed. The docs are built by Read the Docs (`.readthedocs.yaml`) and checked by CI.
- The old print-script tests, and test files that no longer ran. Their land-balance and area checks are now in `tests/test_land_balance.py`.

---

## [0.4.0] - 2025.01.24

### Added
- **New Features**: Introduced `landcover_optimisation` class, used to categorize the spared area with an optimizer, Pyomo. This is used alongside the parameters and constraints to calculate the optimum land use change for each category.
  - Note that this is not always the same as the requested spared area due to the constraints.
  - Added additional functionality to output the actual areas achieved from spared area alone.
  - Optimization has been built into both the default and geo goblin models.
- **Caching**: Introduced caching, which significantly speeds up performance.

### Fixed
- **Bug Fixes**: Fixed various bugs in the land distribution and optimization logic.
- **Performance**: Improved the performance of the land distribution algorithm.

### Testing
- **Additional Testing**: Added comprehensive tests for the new `landcover_optimisation` class and related functionalities.

---

## [0.3.2] - 2025.01.15

### Changed
- **Structural Changes**: Moved `DataManager` into the `resource_manager` module for better organization.
- **Code Simplification**: Reduced complexity and redundancy in land distribution logic within `distribution.py` and `geo_distribution.py`.
