"""Validate the package's calibration-year (2020) land-use table against the national inventory areas.

The reference is `data_sources/national_reference_areas.csv`, built by `tools/build_national_reference.py` from
CRT 2026, NID 2026 and CRF 2024 (burnt area). Every area the package implies (area_ha, or area_ha x share) is compared
with its national counterpart, within TOLERANCE.

Known gaps are expected failures, and each names its cause: a data decision (D1-D10), or LA2 (the grassland area
comes from grassland_production, not the inventory). A gap that is fixed turns its test into an unexpected success,
and its marker must then be removed.

The comparison covers two input sets: this repo's national test data, and goblin_lite's integration inputs.
"""
import unittest

import pandas as pd

from _helpers import CAL, ROOT, run_case

TOLERANCE = 0.01          # 1 %
reference = pd.read_csv(ROOT / "data_sources/national_reference_areas.csv")
reference = reference[reference.year == CAL].set_index(["land_use", "quantity"]).value_ha

LA2 = "LA2: grassland area comes from grassland_production (3.90 Mha), not CRT 4.C (4.22 Mha); every grassland sub-area scales with it"
# (land_use, quantity): (shares multiplied by area_ha (none = area itself), known gap or None)
CHECKS = {
    ("forest", "area"): ([], "refresh: CRF 2024 776.4 kha -> CRT 2026 798.7 kha"),
    ("forest", "mineral"): (["share_mineral"], "D3: forest mineral share = 1 - emitting shares (0.68), CRT 0.46"),
    ("forest", "drained_organic_n_poor"): (["share_organic"], "D3: 174.5 kha has no source; NID 287.4 kha"),
    ("forest", "drained_organic_n_rich"): (["share_organic_mineral"], "D3: 72.5 kha has no source; NID 97.4 kha"),
    ("forest", "burnt"): (["share_burnt"], "D6: 4.A.1 only (177.7 of 300 ha)"),
    ("cropland", "area"): ([], None),
    ("cropland", "mineral"): (["share_mineral"], None),
    ("cropland", "burnt"): (["share_burnt"], None),
    ("grassland", "area"): ([], LA2),
    ("grassland", "mineral"): (["share_mineral"], LA2),
    ("grassland", "drained_organic"): (["share_drained_rich_organic", "share_drained_poor_organic"], LA2),
    ("grassland", "rewet_status_organic"): (["share_rewetted_rich_organic", "share_rewetted_poor_organic"], LA2),
    ("grassland", "burnt"): (["share_burnt"], LA2),
    ("wetland", "area"): ([], "D2: CRF 2024 1225.2 kha -> CRT 2026 1212.5 kha"),
    ("wetland", "domestic_peat_extraction"): (["share_domestic_peat_extraction"], None),
    ("wetland", "industrial_peat_extraction"): (["share_industrial_peat_extraction"], "D1: CRF 2024 77.8 kha; CRT 4(II) 55.5, 4.D 98.3"),
    ("wetland", "rewetted_industrial_peat_extraction"): (["share_rewetted_industrial_peat_extraction"], "D1/D2: CRF 2024 37.4 kha -> CRT 22.9 kha"),
    ("wetland", "rewetted_domestic_peat_extraction"): (["share_rewetted_domestic_peat_extraction"], "refresh: CRF 2024 14.24 -> CRT 14.41 kha"),
    ("wetland", "near_natural"): (["share_near_natural_wetland"], None),
    ("wetland", "unmanaged"): (["share_unmanaged_wetland"], "D2: CRF 2024 126.8 kha -> CRT 108.4 kha"),
    ("wetland", "burnt"): (["share_burnt"], None),
    ("settlement", "area"): ([], None),
    ("settlement", "mineral"): (["share_mineral"], None),
    ("settlement", "organic"): (["share_organic"], "D7: CRF 2024 3.2 kha -> CRT 2.0 kha"),
}


def package_area(case, land_use, shares):
    lu = run_case(case)["landuse"]
    row = lu[(lu.farm_id == -CAL) & (lu.land_use == land_use)].iloc[0]
    return row.area_ha * (sum(row[s] for s in shares) if shares else 1.0)


class NationalValidation(unittest.TestCase):
    @unittest.expectedFailure
    def test_total_land_area(self):
        """All land in the 2020 table vs the national total (CRT Table4.1, 7,111,785 ha). Known gap: LA2, the data
        refresh, and other land (8.2 kha), which the package does not model."""
        for case in ("national", "goblin_lite"):
            lu = run_case(case)["landuse"]
            total = lu[lu.farm_id == -CAL].area_ha.sum()
            self.assertLessEqual(abs(total - reference[("all", "area")]), TOLERANCE * reference[("all", "area")])


def make_test(land_use, quantity, shares, gap):
    def test(self):
        want = reference[(land_use, quantity)]
        for case in ("national", "goblin_lite"):
            have = package_area(case, land_use, shares)
            self.assertLessEqual(abs(have - want), TOLERANCE * abs(want),
                                 f"{case} {land_use} {quantity}: package {have:,.1f} ha vs national {want:,.1f} ha "
                                 f"({(have - want) / want:+.1%})")
    test.__doc__ = f"{land_use} {quantity}" + (f" (known gap: {gap})" if gap else "")
    return unittest.expectedFailure(test) if gap else test


for (land_use, quantity), (shares, gap) in CHECKS.items():
    setattr(NationalValidation, f"test_{land_use}_{quantity}", make_test(land_use, quantity, shares, gap))


if __name__ == "__main__":
    unittest.main()
