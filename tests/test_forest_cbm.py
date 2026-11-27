"""D6a: the national forest row mirrors cbm_runner 0.6.1 (managed forest area and forest fire).

cbm_runner models managed forest as FM (forest present before 1990) + AF (forest planted since 1990, with baseline
planting continuing to 2070), the same in every scenario, plus the scenario's own afforestation (SC). Its historic
forest disturbances are aligned with the NID and forest expert judgement. The package mirrors it:

- forest area_ha = FM + AF area in that year (+ the scenario's afforestation in target-year rows);
- drained organic forest = the NID 2026 hectares of the calibration year (Tables 6.7 + 6.15), held fixed; all other
  forest is mineral (the open area and roads that CBM doesn't model are not emitting, as in the NID; AF planting after
  the calibration year is on mineral soil);
- burnt forest = FM fire + AF fire in that year (+ rate x the scenario's afforestation in target-year rows), with
  cbm_runner's scenario fire rate: (mean annual FM fire + mean annual AF fire) / (FM + AF inventory area);
- Grassland_to_Forest (and so the afforestation table cbm_runner plants) stays the scenario's afforestation: the
  managed-forest change between the two years is not a transition from grassland.

Expected values here are computed from `data_sources/cbm_runner_forest*.csv`, not from the package code.
"""
import sqlite3
import unittest
from pathlib import Path

import pandas as pd

from _helpers import CAL, ROOT, TARGET, run_case

from landcover_assignment.database import get_database_path

CBM = pd.read_csv(ROOT / "data_sources/cbm_runner_forest.csv").set_index("year")
PARAMS = pd.read_csv(ROOT / "data_sources/cbm_runner_forest_parameters.csv").set_index("name").value
CBM_DB = ROOT.parent / "cbm_runner/src/goblin_cbm_runner/database/cbm_runner_database_0.6.2.db"
CASES = ("national", "goblin_lite")


def managed(year):
    return CBM.loc[year, "fm_area_ha"] + CBM.loc[year, "af_area_ha"]


def rate():
    return ((CBM.fm_fire_ha.dropna().mean() + CBM.af_fire_ha.dropna().mean())
            / (PARAMS["fm_inventory_area_ha"] + PARAMS["af_inventory_area_ha"]))


def nid_drained_ha(year=CAL):
    con = sqlite3.connect(f"file:{get_database_path()}?mode=ro", uri=True)
    try:
        poor, rich = con.execute("SELECT organic_emitting_kha, organo_mineral_emitting_kha FROM forest_data "
                                 "WHERE year = ?", (year,)).fetchone()
    finally:
        con.close()
    return poor * 1000, rich * 1000


def forest_row(case, farm_id):
    lu = run_case(case)["landuse"]
    return lu[(lu.farm_id == farm_id) & (lu.land_use == "forest")].iloc[0]


def scenario_afforestation(case, sc):
    affor = run_case(case)["afforestation"]
    return affor[affor.scenario == sc].total_area.sum()


def scenarios(case):
    return [sc for sc in run_case(case)["landuse"].farm_id.unique() if sc >= 0]


class CbmRunnerData(unittest.TestCase):
    def test_rate_mirrors_cbm_runner(self):
        """(9,826 / 54 + 6,872 / 63) / (420,417.2 + 612,488.4) = 2.8177e-4 per year."""
        self.assertAlmostEqual(rate(), (9826 / 54 + 6872 / 63) / (420417.2 + 612488.4), places=15)
        self.assertAlmostEqual(rate(), 2.8177e-4, delta=5e-9)

    @unittest.skipUnless(CBM_DB.is_file(), "cbm_runner database not checked out next to this repo")
    def test_rate_from_the_cbm_runner_database(self):
        """The same rate, computed from cbm_runner's own tables the way SCDisturbances._calculate_national_fire_rate
        does (mean over the steps that have fire, per stream)."""
        con = sqlite3.connect(f"file:{CBM_DB}?mode=ro", uri=True)
        try:
            mean = lambda t: con.execute(f'SELECT AVG(s) FROM (SELECT SUM(Amount) s FROM "{t}" '
                                         "WHERE Dist_Type_ID = 'DISTID3' GROUP BY Step)").fetchone()[0]
            area = lambda t: con.execute(f'SELECT SUM(Area) FROM "{t}"').fetchone()[0]
            want = ((mean("FM_disturbances_2100") + mean("AF_disturbance_2100"))
                    / (area("FM_inventory_2100") + area("AF_inventory_2100")))
        finally:
            con.close()
        self.assertAlmostEqual(rate(), want, places=15)

    def test_managed_forest_2020_and_2050(self):
        self.assertAlmostEqual(managed(2020), 417617.2 + 312481.6, places=6)
        self.assertAlmostEqual(managed(2050), 387827.2 + 483664.4, places=6)

    def test_database_holds_the_cbm_data_as_derived(self):
        con = sqlite3.connect(f"file:{get_database_path()}?mode=ro", uri=True)
        try:
            meta = con.execute("SELECT column_name, source_id, status FROM column_metadata WHERE table_name IN "
                               "('managed_forest_data', 'forest_fire_rate') AND status != 'key'").fetchall()
            citation = con.execute("SELECT citation FROM sources WHERE source_id = 'CBM061'").fetchone()[0]
            area = con.execute("SELECT fm_area_ha + af_area_ha FROM managed_forest_data WHERE year = 2050").fetchone()[0]
            stored_rate = con.execute("SELECT rate_per_year FROM forest_fire_rate").fetchone()[0]
        finally:
            con.close()
        self.assertTrue(meta)
        for column, source, status in meta:
            self.assertEqual((source, status), ("CBM061", "derived"), column)
        self.assertIn("NID and forest expert judgement", citation)
        self.assertAlmostEqual(area, managed(2050), places=6)
        self.assertAlmostEqual(stored_rate, rate(), places=15)


class ForestRow(unittest.TestCase):
    def test_calibration_row(self):
        poor, rich = nid_drained_ha()
        for case in CASES:
            with self.subTest(case=case):
                row = forest_row(case, -CAL)
                self.assertAlmostEqual(row.area_ha, managed(CAL), delta=1e-6)
                self.assertAlmostEqual(row.area_ha * row.share_organic, poor, delta=1e-6)
                self.assertAlmostEqual(row.area_ha * row.share_organic_mineral, rich, delta=1e-6)
                self.assertAlmostEqual(row.share_mineral, 1 - row.share_organic - row.share_organic_mineral, places=12)
                self.assertAlmostEqual(row.area_ha * row.share_burnt, 177 + 128, delta=1e-6)

    def test_target_rows(self):
        poor, rich = nid_drained_ha()
        for case in CASES:
            for sc in scenarios(case):
                with self.subTest(case=case, scenario=sc):
                    row, affor = forest_row(case, sc), scenario_afforestation(case, sc)
                    self.assertAlmostEqual(row.area_ha, managed(TARGET) + affor, delta=1e-6)
                    self.assertAlmostEqual(row.area_ha * row.share_organic, poor, delta=1e-6)
                    self.assertAlmostEqual(row.area_ha * row.share_organic_mineral, rich, delta=1e-6)
                    self.assertAlmostEqual(row.share_mineral, 1 - row.share_organic - row.share_organic_mineral,
                                           places=12)
                    burnt = CBM.loc[TARGET, "fm_fire_ha"] + CBM.loc[TARGET, "af_fire_ha"] + rate() * affor
                    self.assertAlmostEqual(row.area_ha * row.share_burnt, burnt, delta=1e-6)

    def test_grassland_to_forest_is_the_scenario_afforestation(self):
        """Target - baseline forest includes the managed-forest change (CBM's own AF planting less FM
        deforestation, 141,392.8 ha by 2050); the transition, which feeds the afforestation table, leaves it out."""
        for case in CASES:
            tm = run_case(case)["transition_matrix"]
            for sc in scenarios(case):
                with self.subTest(case=case, scenario=sc):
                    affor = scenario_afforestation(case, sc)
                    self.assertAlmostEqual(tm.loc[sc, "Grassland_to_Forest"], affor, delta=1e-2)
                    change = forest_row(case, sc).area_ha - forest_row(case, -CAL).area_ha
                    self.assertAlmostEqual(change - (managed(TARGET) - managed(CAL)), affor, delta=1e-2)


if __name__ == "__main__":
    unittest.main()
