# Peat extraction in scenarios

This page sets out the **modelling assumption** landcover_assignment makes about peat extraction in scenario
(target) years (decision D10). Peat extraction emissions are counted, but they are not the focus of the model, so the
rule is kept simple.

## The assumption

**All peat extraction, industrial and domestic, ends in 2040.** Between the calibration year and 2040 it falls in a
straight line, and the land that stops being extracted is rewetted.

In a target-year wetland row:

```text
remaining = (2040 - target year) / (2040 - calibration year), between 0 and 1
share_industrial_peat_extraction           = calibration share x remaining
share_rewetted_industrial_peat_extraction  = calibration share + calibration industrial share x (1 - remaining)
```

The same applies to domestic extraction (`share_domestic_peat_extraction` -> `share_rewetted_domestic_peat_extraction`).

- The wetland area does not change, and nor does any other share (near-natural, unmanaged, burnt, ...).
- Calibration-year rows are the inventory (CRT 2026 4(II)), unchanged.
- Target years from 2040 on have no peat extraction. With a 2020 calibration year, a 2030 target year has half the 2020
  extraction.
- The year is a constant, `national_landcover.PEAT_PHASE_OUT_YEAR`. The function is
  `NationalLandCover.get_peat_extraction_remaining`.
- National tree only. The catchment tree keeps its calibration-year peat share.

## Why

- **Industrial:** Bord na Móna stopped harvesting peat in 2021, and its drained area is moving into rewetted land:
  55.5 kha drained in 2020, 34.7 kha in 2024 (CRT 2026 4(II)). At that pace it reaches zero around 2031, so a straight
  line to 2040 is conservative.
- **Domestic:** there is no agreed end date, and the inventory decline is slower (88.3 kha drained in 2020, 84.3 kha in
  2024). Ending it by 2040 is a scenario assumption, chosen for simplicity and consistency with industrial extraction.
- Before this change, every scenario extracted peat at the calibration-year rate in every target year.

The 2020 inventory and the target-year rows (wetland area 1,212.5 kha):

| part (kha) | 2020 | 2030 | 2050 |
|---|---:|---:|---:|
| industrial drained | 55.5 | 27.8 | 0 |
| industrial rewetted | 22.9 | 50.7 | 78.4 |
| domestic drained | 88.3 | 44.2 | 0 |
| domestic rewetted | 14.4 | 58.6 | 102.7 |

## Downstream

The output columns are unchanged, so no other package needs a change. landcover_lca charges the rewetted area with its
rewetted-peat factors instead of the extraction factors.

landcover_lca computes off-site CO2 from horticultural peat (`horticulture_co2_peat_export`) from peat export
tonnage, not from this area. For years after its export data it uses the mean of the last three years. So in a
scenario year after 2040, that off-site CO2 is still counted although this package has no industrial extraction.
This is a known difference between the two packages, recorded here; it is not changed.
