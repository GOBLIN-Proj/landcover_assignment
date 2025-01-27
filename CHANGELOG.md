# Changelog

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