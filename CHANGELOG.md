# Changelog

## [Unreleased] (0.5.0, in progress)

### Added
- **Characterisation tests** (`tests/test_*.py`): golden outputs for three input sets (national, catchment, goblin_lite's integration inputs), the interface that downstream packages rely on, land balance, the optimiser, and database coverage against CRT 2026 / NID 2026. Known bugs and data gaps are expected failures. See `tests/README.md`.
- **Inventory tooling** (`tools/`): `extract_inventory.py` (CRT 2026, 1990-2024; CRF 2024 burnt area), `transcribe_nid_forest.py` (NID 2026 Tables 6.7 and 6.15) and `build_provenance.py` (database vs inventory audit). Outputs are in `data_sources/`.
- **Documentation**: `docs/rewetting.md` explains how spared area is divided, and that rewetted spared grassland stays grassland with rewet status. The same rule is now in the README and in the docstrings of `calculate_spared_area_allocation`, `grassland_breakdown`, `grassland_distribution` and `create_transition_matrix` (national and catchment). No change in behaviour.

### Removed
- The old print-script tests, and test files that no longer ran. Their land-balance and area checks are now in `tests/test_land_balance.py`.

### Changed
- CI runs the new test suite.

---

## [0.3.2] - 2025.01.15

### Changed
- **Structural Changes**: Moved `DataManager` into the `resource_manager` module for better organization.
- **Code Simplification**: Reduced complexity and redundancy in land distribution logic within `distribution.py` and `geo_distribution.py`.

---

## [0.4.0] - 2025.01.15

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