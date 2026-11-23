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

## Worked example

National test data (`tests/data`), scenario 0, 2020 to 2050. Spared area: 2,833,798 ha. Rewetted: 28,338 ha.

| | 2020 | 2050, scenario 0 | change |
|---|---:|---:|---|
| grassland row, total | 3,904,877 | 1,099,417 | −2,805,460 |
| … mineral | 3,590,677 | 785,217 | −2,805,460 (forest 1,700,279 + farmable 1,105,181) |
| … organic, drained (rich + poor) | 126,357 | 98,018 | −28,338 |
| … organic, rewet status (rich + poor) | 187,844 | 216,182 | **+28,338** |
| wetland row | 1,225,154 | 1,225,154 | 0 |

Three consequences to keep in mind when reading the outputs:

1. **The grassland row is more than productive grassland.** In 2050 it holds 1,099,417 ha. grassland_production's
   grassland is 1,071,079 ha; the row adds the 28,338 ha of rewetted spared land. The spared area (2,833,798 ha) is
   therefore larger than the fall in the grassland row (2,805,460 ha).
2. **`Grassland_to_Grassland` counts mineral land leaving grassland**, as a negative number (−2,805,460 here).
   **`Grassland_to_Wetland` is always 0.** Neither of these includes rewetting.
3. **The rewetted area is recorded in the spared-area log**, as `land_use = "rewet_grassland"` with the area in
   `organic_area`. In the land-use table it appears only as the change in `share_rewetted_rich_organic` and
   `share_rewetted_poor_organic`.

## Rules the tests enforce

`tests/test_frozen_interface.py` and `tests/test_land_balance.py` check, on every input set, that:

- `Grassland_to_Wetland` is 0 and the wetland row does not grow;
- the logged rewetted area equals the increase in rewet-status grassland, for scenarios where the rewetting fits within the drained organic stock;
- total land area is conserved in every scenario, and each land use balances with the transition matrix.

## Known issue (to be fixed as finding 8)

When a scenario spares more organic grassland than is still drained, the log counts land that already had rewet status
as newly rewetted. In scenario 3, which spares all grassland, the log records 314,200 ha. But only the 126,357 ha
still drained can change status; the other 187,843 ha already had rewet status in 2020. No area is lost (the land
balance holds), but the log overstates new rewetting. An expected failure in `test_frozen_interface.py` marks this
until it is fixed.
