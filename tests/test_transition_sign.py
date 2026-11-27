"""Step 7, item 14 (LA1): the transition matrix keeps the sign of each change.

Only ``Grassland_to_<X>`` cells are filled, so a land use other than grassland that shrinks can't be recorded there.
Today none can (dossier S7_item14_transition_sign); if one ever does, the matrix raises instead of writing the loss as
a gain from grassland (the old ``abs()``).
"""
import math
import unittest

from _helpers import CAL, TARGET, load_national
from landcover_assignment.transition_matrix import TransitionMatrix


def matrix_with_target_change(land_use, change_ha, scenario=0):
    """National test inputs, with the target-year area of one land use in one scenario set to its calibration-year
    area + change_ha (for forest, also + the managed-forest change, which the matrix takes out; decision D6a)."""
    sc, grass, spared, breakdown = load_national()
    tm = TransitionMatrix(CAL, TARGET, sc, grass, spared, breakdown)
    land_use_df = tm.land_cover_class.combined_future_land_use_area()
    row = (land_use_df["farm_id"] == scenario) & (land_use_df["year"] == TARGET) & (land_use_df["land_use"] == land_use)
    calibration = land_use_df.loc[(land_use_df["year"] == CAL) & (land_use_df["land_use"] == land_use), "area_ha"].item()
    if land_use == "forest":
        calibration += tm.land_cover_class.national_class.get_managed_forest_change(CAL, TARGET)
    land_use_df.loc[row, "area_ha"] = calibration + change_ha
    tm.land_cover_class.combined_future_land_use_area = lambda: land_use_df
    return tm


class TransitionSign(unittest.TestCase):
    def test_shrinking_land_use_raises(self):
        for land_use in ("cropland", "wetland", "settlement", "forest", "farmable_condition"):
            with self.subTest(land_use=land_use):
                tm = matrix_with_target_change(land_use, -1_000.0)
                with self.assertRaisesRegex(ValueError, land_use):
                    tm.create_transition_matrix()

    def test_growing_land_use_is_written_as_a_gain(self):
        tm = matrix_with_target_change("cropland", 1_000.0)
        self.assertAlmostEqual(tm.create_transition_matrix().loc[0, "Grassland_to_Cropland"], 1_000.0, delta=1e-6)

    def test_no_change_is_written_as_zero_not_minus_zero(self):
        """A land use whose area doesn't change gets 0.0, not -0.0 (which prints as "-0.0")."""
        sc, grass, spared, breakdown = load_national()
        matrix = TransitionMatrix(CAL, TARGET, sc, grass, spared, breakdown).create_transition_matrix()
        negative_zeros = [(i, c) for i in matrix.index for c in matrix.columns
                          if matrix.at[i, c] == 0 and math.copysign(1.0, matrix.at[i, c]) < 0]
        self.assertEqual(negative_zeros, [])


if __name__ == "__main__":
    unittest.main()
