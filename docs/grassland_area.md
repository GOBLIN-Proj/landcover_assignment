# Where the grassland area comes from

The grassland row of the land-use table holds two parts:

- **Herd grassland:** the area the herd needs to grow its grass. It comes from the [grassland_production](https://github.com/GOBLIN-Proj/grassland_production) package as the `total_grassland` input. Only this part can be spared.
- **Other grassland (the balance):** the rest of the country's grassland, which the herd doesn't need. It is fixed at its calibration-year size, is never spared, and is in the table so that its emissions are counted.

The catchment (geo) tree uses the herd grassland only, with no balance. Catchment areas are derived from catchment_data_api, and the balance there needs separate thought.

## Herd grassland
goblin_lite (national) and geo_goblin_py (catchment) run this chain:

1. **The herd.** livestock_generation builds the baseline and scenario animal numbers.
2. **The grassland area.** grassland_production calculates, for each system (dairy, beef, sheep) and year:

   ```text
   herd grassland area = grass dry matter the herd eats / grass yield per hectare / utilisation rate
   ```

   - The yield is weighted by the mix of grassland types: pasture, silage, hay and rough grazing.
   - The utilisation rate comes from the National Farm Survey. In the target year it rises with the scenario's grass use efficiency (GUE).
3. **The spared area.** This is the calibration-year area minus the target-year area. A scenario frees land only by needing less grass.
4. **landcover_assignment.** It receives the herd grassland area, the spared area and its soil-group breakdown.

The baseline and the spared area come from the same herd and diet calculation, so they are consistent.

## Other grassland: the balance (national tree)

```text
balance = national grassland area (calibration year) - herd grassland area (calibration year)
```

- **The calibration year** is whatever year the run uses as its calibration year.
- **National grassland area:** from the package database, `land_use_database.db`, table `grassland_data`, column `total_kha` (EPA CRF 2024, Table 4.C, total grassland, 1990-2022). It becomes the CRT 2026 values when the database is rebuilt. A calibration year that isn't in the database stops the run with an error naming the year.
- **Herd grassland area:** the calibration-year row of the `total_grassland` input.
- **If the herd area is larger than the national area,** the balance is 0 and a warning is logged.

The balance is added to the grassland row in the baseline and in every scenario. The national grassland shares (mineral, drained organic, rewet-status organic, burnt) apply to the whole row, so in the baseline every grassland sub-area equals the inventory area.

The mineral and drained organic areas available to be spared are taken from the herd grassland only. A scenario that spares all herd grassland still keeps the balance.

## How much of the grassland is which
`LandCover.get_grassland_area_breakdown()` (national) reports this for the baseline and each scenario. It is reporting only and doesn't change any output.

| column | meaning |
|---|---|
| `herd_grassland_ha` | grassland the herd needs: the calibration-year area for the baseline; for a scenario, that area minus its spared area |
| `rewetted_spared_ha` | spared organic grassland that is rewetted and stays in the grassland row (see [rewetting](rewetting.md)); 0 in the baseline |
| `other_grassland_ha` | the balance, the same in every row |
| `total_grassland_ha` | the sum, equal to the grassland row's `area_ha` |

## The numbers (2020, test data)

| | grassland area |
|---|---|
| herd grassland (grassland_production) | 3,904.9 kha |
| balance (other grassland) | 324.3 kha |
| **grassland row = national area (package database, CRF 2024 4.C)** | **4,229.1 kha** |
| for comparison: CSO grassland (pasture, hay, silage, rough grazing in use) | 4,152.0 kha |
| for comparison: CRT 2026 4.C | 4,218.5 kha |

Before 0.5.0 the grassland row held the herd grassland only. The other grassland (about 324 kha) was in no land use, and its emissions were counted nowhere.

`tests/test_grassland_balance.py` and `tests/test_national_validation.py` check:
- the mass balance;
- that the balance is constant and never spared;
- the breakdown;
- that grassland matches the national inventory to within 1%, in hectares and in shares.

Do not replace the herd grassland with an inventory area: the spared area must come from the herd calculation.
