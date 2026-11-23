# Where the grassland area comes from

The grassland `area_ha` in the land-use table is **not** an inventory area. It is the `total_grassland` input, which comes from the [grassland_production](https://github.com/GOBLIN-Proj/grassland_production) package: **the area the herd needs to grow its grass**. This is by design.

## How it is calculated
goblin_lite (national) and geo_goblin_py (catchment) run this chain:

1. **The herd.** livestock_generation builds the baseline and scenario animal numbers.
2. **The grassland area.** grassland_production calculates, for each system (dairy, beef, sheep) and year:

   ```text
   grassland area = grass dry matter the herd eats / grass yield per hectare / utilisation rate
   ```

   - The yield is weighted by the mix of grassland types: pasture, silage, hay and rough grazing.
   - The utilisation rate comes from the National Farm Survey. In the target year it rises with the scenario's grass use efficiency (GUE).
3. **The spared area.** This is the calibration-year area minus the target-year area. A scenario frees land only by needing less grass.
4. **landcover_assignment.** It receives the grassland area, the spared area and its soil-group breakdown, and:
   - uses the calibration-year grassland area as grassland `area_ha` (the same for every scenario);
   - takes the grassland **shares** (mineral, drained organic, rewet-status organic, burnt) from the national inventory, through the package database;
   - takes both area and shares from the inventory for forest, cropland, wetland and settlement.

## Why it is done this way
The baseline grassland area and the spared area come from the same herd and diet calculation, so they are consistent. If the baseline used the inventory's grassland area instead, the spared area would no longer reconcile with it.

## What this means for the numbers (2020)

| source | grassland area |
|---|---|
| herd-derived (grassland_production) | 3,904.9 kha |
| CSO grassland (pasture, hay, silage, rough grazing in use) | 4,152.0 kha |
| national inventory, CRT 2026 4.C | 4,218.5 kha |

- **Grassland hectares are lower than the inventory.** Every grassland sub-area (mineral, drained organic, rewet status, burnt) is about 7.4% below the inventory area. Its **share** of grassland matches the inventory.
- **The table doesn't hold all of Ireland's land.** The land-use table totals about 6.78 Mha, against the national 7.11 Mha. The difference is the grassland outside the herd area (about 314 kha), plus other land (8 kha), which the package doesn't model.
- **How the package validates grassland.** `tests/test_national_validation.py` checks the grassland **shares** against the inventory, and checks that grassland `area_ha` equals the input area. It doesn't compare grassland hectares with the inventory.

## A known gap, to be filled
The grassland outside the herd area (about 314 kha nationally) is currently in no land use, so its emissions are counted nowhere. A planned change (0.5.0) will fill the gap at national scale:
- **Balance area:** add a fixed area to the grassland row, equal to the national grassland area minus the herd area in the calibration year.
- **Carried forward unchanged:** the balance stays the same in every scenario and is never available to be spared.
- **Reported:** a separate table will show it.

The national shares then apply to the whole row, so grassland matches the inventory area for area. How to treat catchments is still to be decided.

Do not replace the grassland area with an inventory area. See also [Spared area, rewetting and the grassland row](rewetting.md).
