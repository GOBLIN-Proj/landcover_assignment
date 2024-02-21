import unittest
import pandas as pd
import shutil
import os
from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.resource_manager.transition_data_fetcher import TransitionDataFetcher
from landcover_assignment.afforestation import Afforestation

class TestTransitions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up method to prepare the environment before running tests."""
        cls.path = "./data/"

        cls.baseline = 2020
        cls.target_year = 2050
        cls.scenario_dataframe = pd.read_csv(os.path.join(cls.path, "scenario_dataframe.csv"), index_col=0)
        cls.spared_area = pd.read_csv(os.path.join(cls.path, "spared_area.csv"), index_col=0)
        cls.spared_area_breakdown = pd.read_csv(os.path.join(cls.path, "spared_area_breakdown.csv"), index_col=0)
        cls.spared_area.columns = cls.spared_area.columns.astype(int)
        cls.grassland_area = pd.read_csv(os.path.join(cls.path, "total_grassland_area.csv"), index_col=0)
        cls.grassland_area.columns = cls.grassland_area.columns.astype(int)


        cls.transition = TransitionMatrix(
            cls.baseline, cls.target_year, cls.scenario_dataframe, cls.grassland_area, cls.spared_area, cls.spared_area_breakdown
        )

        cls.transition_matrix = cls.transition.create_transition_matrix()
        cls.t_class = TransitionDataFetcher(cls.transition_matrix)

        cls.transition_breakdown = cls.t_class.get_grassland_to_landuse_soil_group_area(cls.spared_area_breakdown)

        cls.cols = ["Grassland_to_Forest", "Grassland_to_Wetland", "Grassland_to_Cropland", "Grassland_to_Farmable_Condition"]

        cls.affor_class = Afforestation(cls.baseline, cls.target_year, cls.scenario_dataframe, cls.transition_matrix)



    def test_transition_area_validation(self):
        """Test if transition areas are equal."""
        transition_area_breakdown = self.transition_breakdown.groupby('scenario').sum()

        ## Calculate the sum of breakdown areas
        for sc in transition_area_breakdown.index:
            for col in self.cols:
                transition_area = self.transition_matrix.at[sc,col]
                total_breakdown_area = transition_area_breakdown.loc[sc, col]
                
                self.assertAlmostEqual(transition_area, total_breakdown_area, places=2, msg="Breakdown area sum for scenario {col} does not match spared area.")
           

    def test_afforestation_transition(self):
        """Test if afforestation transition areas are equal."""
        afforstation_output = self.affor_class.gen_cbm_afforestation_dataframe(self.spared_area_breakdown)[["scenario", "total_area"]].groupby('scenario').sum()
        new_forest_area = self.t_class.get_grassland_to_forest_soil_group_areas(self.spared_area_breakdown)[["scenario","Grassland_to_Forest"]].groupby('scenario').sum()

        for index in new_forest_area.index:

            afforestation_area = afforstation_output.loc[index, "total_area"]
            transition_area = new_forest_area.loc[index, "Grassland_to_Forest"]

            self.assertAlmostEqual(afforestation_area, transition_area, places=2, msg="Breakdown area sum for afforestation does not match spared area.")


    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        #if os.path.exists("./test_data"):
            #shutil.rmtree("./test_data")

if __name__ == '__main__':
    unittest.main()