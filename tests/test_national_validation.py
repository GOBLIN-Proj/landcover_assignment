"""Validate the package's calibration-year (2020) land-use table against the national inventory areas.

The reference is `data_sources/national_reference_areas.csv`, built by `tools/build_national_reference.py` from
CRT 2026, NID 2026 and CRF 2024 (burnt area). Every area the package implies (area_ha, or area_ha x share) is compared
with its national counterpart, within TOLERANCE.

Grassland: the herd-derived area from grassland_production (the area the herd needs for its grass) plus the national
balance (the grassland the herd doesn't need, dossier LA2) equals the national grassland area, so grassland is checked
in hectares like the other land uses, and its shares are checked too. See docs/grassland_area.md and the shared
context .goblin-context/pipeline/goblin_lite-land-flow.md.

Known gaps are expected failures, and each names its cause, a data decision (D1-D10). A gap that is fixed turns its
test into an unexpected success, and its marker must then be removed.

The comparison covers two input sets: this repo's national test data, and goblin_lite's integration inputs.
"""
import unittest

import pandas as pd

from _helpers import CAL, ROOT, input_grassland_area, load_goblin_lite, load_national, national_grassland_area, run_case

TOLERANCE = 0.01          # 1 %
reference = pd.read_csv(ROOT / "data_sources/national_reference_areas.csv")
reference = reference[reference.year == CAL].set_index(["land_use", "quantity"]).value_ha

# (land_use, quantity): (shares multiplied by area_ha (none = area itself), known gap or None).
CHECKS = {
    ("forest", "area"): ([], None),
    ("forest", "mineral"): (["share_mineral"], None),
    ("forest", "drained_organic_n_poor"): (["share_organic"], None),
    ("forest", "drained_organic_n_rich"): (["share_organic_mineral"], None),
    ("forest", "burnt"): (["share_burnt"], "D6: 4.A.1 only (177.7 of 300 ha)"),
    ("cropland", "area"): ([], None),
    ("cropland", "mineral"): (["share_mineral"], None),
    ("cropland", "burnt"): (["share_burnt"], None),
    ("grassland", "area"): ([], None),
    ("grassland", "mineral"): (["share_mineral"], None),
    ("grassland", "drained_organic"): (["share_drained_rich_organic", "share_drained_poor_organic"], None),
    ("grassland", "rewet_status_organic"): (["share_rewetted_rich_organic", "share_rewetted_poor_organic"], None),
    ("grassland", "burnt"): (["share_burnt"], None),
    ("wetland", "area"): ([], None),
    ("wetland", "domestic_peat_extraction"): (["share_domestic_peat_extraction"], None),
    ("wetland", "industrial_peat_extraction"): (["share_industrial_peat_extraction"], None),
    ("wetland", "rewetted_industrial_peat_extraction"): (["share_rewetted_industrial_peat_extraction"], None),
    ("wetland", "rewetted_domestic_peat_extraction"): (["share_rewetted_domestic_peat_extraction"], None),
    ("wetland", "near_natural"): (["share_near_natural_wetland"], None),
    ("wetland", "unmanaged"): (["share_unmanaged_wetland"], None),
    ("wetland", "burnt"): (["share_burnt"], None),
    ("settlement", "area"): ([], None),
    ("settlement", "mineral"): (["share_mineral"], None),
    ("settlement", "organic"): (["share_organic"], None),
}

# Grassland sub-areas as a share of all grassland: the package's shares vs national quantity / 4.C area.
GRASSLAND_SHARES = {
    "mineral": ["share_mineral"],
    "drained_organic": ["share_drained_rich_organic", "share_drained_poor_organic"],
    "rewet_status_organic": ["share_rewetted_rich_organic", "share_rewetted_poor_organic"],
    "burnt": ["share_burnt"],
}
LAND_USES = ("forest", "cropland", "grassland", "wetland", "settlement")
CASES = {"national": load_national, "goblin_lite": load_goblin_lite}


def baseline_row(case, land_use):
    lu = run_case(case)["landuse"]
    return lu[(lu.farm_id == -CAL) & (lu.land_use == land_use)].iloc[0]


def package_area(case, land_use, shares):
    row = baseline_row(case, land_use)
    return row.area_ha * (sum(row[s] for s in shares) if shares else 1.0)


class NationalValidation(unittest.TestCase):
    def test_grassland_area_is_herd_plus_balance(self):
        """Grassland area_ha = grassland_production's herd-derived area + the national balance = the national
        grassland area in the package database (dossier LA2)."""
        for case in CASES:
            herd = input_grassland_area(case, CAL)
            balance = national_grassland_area(CAL) - herd
            self.assertGreater(balance, 0)
            self.assertAlmostEqual(baseline_row(case, "grassland").area_ha, herd + balance, delta=1e-3)

    def test_total_land_area(self):
        """All land in the 2020 table equals the national total (CRT Table4.1, 7,111,785 ha) less other land, which the
        package does not model."""
        national_total = reference[("all", "area")]
        other_land = national_total - sum(reference[(lu, "area")] for lu in LAND_USES)
        for case in CASES:
            lu = run_case(case)["landuse"]
            have = lu[lu.farm_id == -CAL].area_ha.sum()
            self.assertLessEqual(abs(have - (national_total - other_land)), TOLERANCE * national_total,
                                 f"{case}: {have:,.0f} ha vs {national_total - other_land:,.0f} ha")


def make_test(land_use, quantity, shares, gap):
    def test(self):
        want = reference[(land_use, quantity)]
        for case in CASES:
            have = package_area(case, land_use, shares)
            self.assertLessEqual(abs(have - want), TOLERANCE * abs(want),
                                 f"{case} {land_use} {quantity}: package {have:,.1f} ha vs national {want:,.1f} ha "
                                 f"({(have - want) / want:+.1%})")
    test.__doc__ = f"{land_use} {quantity}" + (f" (known gap: {gap})" if gap else "")
    return unittest.expectedFailure(test) if gap else test


def make_grassland_share_test(quantity, shares):
    def test(self):
        want = reference[("grassland", quantity)] / reference[("grassland", "area")]
        for case in CASES:
            row = baseline_row(case, "grassland")
            have = sum(row[s] for s in shares)
            self.assertLessEqual(abs(have - want), TOLERANCE * abs(want),
                                 f"{case} grassland {quantity} share: package {have:.5f} vs national {want:.5f}")
    test.__doc__ = f"grassland {quantity}, as a share of all grassland"
    return test


for (land_use, quantity), (shares, gap) in CHECKS.items():
    setattr(NationalValidation, f"test_{land_use}_{quantity}", make_test(land_use, quantity, shares, gap))
for quantity, shares in GRASSLAND_SHARES.items():
    setattr(NationalValidation, f"test_grassland_{quantity}_share", make_grassland_share_test(quantity, shares))


if __name__ == "__main__":
    unittest.main()
