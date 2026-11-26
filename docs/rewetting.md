# Spared area, rewetting and the grassland row

This page explains how landcover_assignment divides the grassland spared by a scenario, and why spared grassland that
is rewetted **stays in the grassland row**.

## The rule

Rewetted organic grassland is still grassland. When a scenario rewets spared organic grassland, the area does not move
to wetland. It stays in the `grassland` row of the land-use table, and its status changes from *drained* to *rewet
status*.

This follows the national inventory:
- CRT 2026 reports "grassland remaining grassland" (4.C.1) organic soil as drained organic soil plus "Other organic
  soils", which is the NID 2026 s.6.5.2 rewet status.
- In 2020 that is 136.562 + 203.291 = 339.854 kha, which is exactly the 4.C.1 organic area. The separate "Rewetted
  organic soils" row is reported as NO.
- Rewetting therefore changes the status of land inside grassland remaining grassland. It is not a land-use
  conversion.

Downstream, landcover_lca charges rewet-status grassland with its *grassland* rewetting factors
(`rewetting_co2_organic_soils_in_grassland`, `rewetting_ch4_organic_soils_in_grassland`), which differ from the
wetland factors. Moving the area to the wetland row would apply the wrong factors.

## How a scenario's spared area is divided

```text
spared grassland (from grassland_production)
├── rewetted organic soil      rewetted proportion × spared area, capped by the drained organic grassland available
│     stays in the GRASSLAND row: drained share → rewet-status share
│     logged as "rewet_grassland" in the spared-area log
└── mineral soil               the rest, capped by the mineral grassland available
      allocated by the optimiser (Pyomo, HiGHS)
      ├── forest               target: forest proportion × spared area
      ├── cropland             target: crop proportion × spared area
      └── farmable_condition   whatever is not allocated to a target
```

Code: `LandCover.calculate_spared_area_allocation` (`landcover.py`), `LandDistribution.grassland_distribution`
(`distribution.py`). The catchment tree (`geo_landcover_assignment/`) follows the same rule, but it tracks organic and
organo-mineral pools (`share_rewetted_in_organic`, `share_rewetted_in_organic_mineral`) instead of the drained rich/poor
split.

## Farmable condition is mineral soil only

`farmable_condition` is spared grassland that leaves production in unchanged condition (no animals, no new land use).
It only ever receives mineral soil: its rows have `share_mineral` = 1. Spared organic grassland that is rewetted is not
farmable condition: it stays grassland with rewet status (above). Rewetted land is reported in aggregate in the
grassland row, so the rewet-status shares hold the rewet-status area of the calibration year (CRT "Other organic
soils") plus the rewetted spared area.

## Worked example

National test data (`tests/data`), scenario 0, 2020 to 2050. Spared area: 2,833,798 ha. Rewetted: 28,338 ha.

| | 2020 | 2050, scenario 0 | change |
|---|---:|---:|---|
| grassland row, total | 4,218,508 | 1,413,048 | −2,805,460 |
| … mineral | 3,878,597 | 1,073,137 | −2,805,460 (forest 1,700,279 + farmable 1,105,181) |
| … organic, drained (rich + poor) | 136,562 | 108,225 | −28,338 |
| … organic, rewet status (rich + poor) | 203,291 | 231,629 | **+28,338** |
| wetland row | 1,212,500 | 1,212,500 | 0 |

The grassland row includes the national balance (313,631 ha, `docs/grassland_area.md`), which is never spared.

Three consequences to keep in mind when reading the outputs:

1. **The grassland row is more than productive grassland.** In 2050 it holds 1,413,048 ha: grassland_production's
   grassland (1,071,079 ha), the balance (313,631 ha) and the 28,338 ha of rewetted spared land
   (`LandCover.get_grassland_area_breakdown()` reports the three parts). The spared area (2,833,798 ha) is therefore
   larger than the fall in the grassland row (2,805,460 ha).
2. **`Grassland_to_Grassland` counts mineral land leaving grassland**, as a negative number (−2,805,460 here).
   **`Grassland_to_Wetland` is always 0.** Neither of these includes rewetting.
3. **The rewetted area is recorded in the spared-area log**, as `land_use = "rewet_grassland"` with the area in
   `organic_area`. In the land-use table it appears only as the change in `share_rewetted_rich_organic` and
   `share_rewetted_poor_organic`.

## Transitions by soil group

Afforestation needs the soil group of each new forest hectare (it sets the yield class). `TransitionDataFetcher`
splits each scenario's transitions across soil groups 1, 2 and 3, using the spared area by soil group from
grassland_production: soil group 1 first, then 2, then 3; in each group cropland, then forest, then farmable condition,
each capped by what is left in the group. The spared area the transition matrix does not account for is the rewetted
area; it stays grassland and is placed in soil group 3 (`Grassland_Rewetted`,
`get_grassland_rewetted_soil_group_areas`). Scenario 0:

| soil group | forest | farmable condition | rewetted (stays grassland) |
|---|---:|---:|---:|
| 1 | 1,133,531 | 0 | 0 |
| 2 | 566,748 | 806,039 | 0 |
| 3 | 0 | 299,143 | 28,338 |

Before 0.5.0 farmable condition took everything left in each group, including the rewetted area, so farmable by soil
group added up to more than `Grassland_to_Farmable_Condition` (scenario 0: 1,133,519 ha against 1,105,181; finding 3).

## Rules the tests enforce

`tests/test_frozen_interface.py` and `tests/test_land_balance.py` check, on every input set, that:

- `Grassland_to_Wetland` is 0 and the wetland row does not grow;
- the logged rewetted area equals the increase in rewet-status grassland, for scenarios where the rewetting fits within the drained organic stock;
- total land area is conserved in every scenario, and each land use balances with the transition matrix;
- the transitions by soil group add up to the transition matrix, and each soil group's transitions plus its rewetted
  area add up to its spared area.

## Known issue (to be fixed as finding 8)

When a scenario spares more organic grassland than is still drained, the log counts land that already had rewet status
as newly rewetted. In scenario 3, which spares all grassland, the log records 314,640 ha. But only the 126,410 ha
still drained can change status; the other 188,230 ha already had rewet status in 2020. No area is lost (the land
balance holds), but the log overstates new rewetting. An expected failure in `test_frozen_interface.py` marks this
until it is fixed.
