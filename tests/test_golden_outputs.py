"""Golden-output regression: every output table must match the recorded baseline.

The baseline is landcover_assignment 0.4.0 at c0d03eb, run with HiGHS (2026-11-23), and it is stored in `tests/golden/`.
It covers three input sets:
- `national`: tests/data;
- `geo`: tests/geo_data;
- `goblin_lite`: goblin_lite's integration inputs, read the way goblin_lite reads them.

A result may change only through an approved dossier. When one is approved, regenerate the affected golden files
in the same commit, and record the before and after numbers in the dossier.
"""
import unittest

import pandas as pd

from _helpers import CASES, GOLDEN, roundtrip, run_case

TABLES = ("landuse", "transition_matrix", "afforestation", "spared_area_log")


class GoldenOutputs(unittest.TestCase):
    def test_outputs_match_baseline(self):
        for case in CASES:
            out = run_case(case)
            for table in TABLES:
                with self.subTest(case=case, table=table):
                    expected = pd.read_csv(GOLDEN / f"{case}_{table}.csv", index_col=0)
                    pd.testing.assert_frame_equal(roundtrip(out[table]), expected, check_exact=False,
                                                  rtol=1e-9, atol=1e-6)


if __name__ == "__main__":
    unittest.main()
