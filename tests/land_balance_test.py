import unittest
import pandas as pd
from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.landcover import LandCover
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from landcover_assignment.afforestation import Afforestation
import os

class TestLandCoverSystem(unittest.TestCase):
    def setUp(self):
        self.path = "./data/"

        self.baseline = 2020
        self.target_year = 2050
        self.scenario_dataframe = pd.read_csv(os.path.join(self.path, "scenario_dataframe.csv"), index_col=0)
        self.spared_area = pd.read_csv(os.path.join(self.path, "spared_area.csv"), index_col=0)
        self.spared_area_breakdown = pd.read_csv(os.path.join(self.path, "spared_area_breakdown.csv"), index_col=0)
        self.spared_area.columns = self.spared_area.columns.astype(int)
        self.grassland_area = pd.read_csv(os.path.join(self.path, "total_grassland_area.csv"), index_col=0)
        self.grassland_area.columns = self.grassland_area.columns.astype(int)

        self.transition = TransitionMatrix(
            self.baseline, self.target_year, self.scenario_dataframe, self.grassland_area, self.spared_area, self.spared_area_breakdown
        )

        self.land = LandCover(
            self.baseline, self.target_year, self.scenario_dataframe, self.grassland_area, self.spared_area, self.spared_area_breakdown
        )

        self.fetcher = ScenarioDataFetcher(self.scenario_dataframe)

    def test_transition_matrix_creation(self):
        # Test the creation of the transition matrix
        matrix = self.transition.create_transition_matrix()
        self.assertIsInstance(matrix, pd.DataFrame)  # Example assertion

    def test_land_cover_future_area(self):
        # Test combined future land use area calculation
        future_area = self.land.combined_future_land_use_area()
        self.assertIsInstance(future_area, pd.DataFrame)  # Example assertion


    def test_spared_area(self):
        matrix = self.transition.create_transition_matrix()
        landcover_data = self.land.combined_future_land_use_area()

        rewetted_area_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "grassland")

        for farm_id in matrix.index:
            if farm_id > 0:
                rewetted_area_target_mask = (landcover_data.year == self.target_year) &(landcover_data.farm_id == farm_id) & (landcover_data.land_use == "grassland")

                rewetted_area_target_rich = landcover_data.loc[rewetted_area_target_mask, "area_ha"].item() * landcover_data.loc[rewetted_area_target_mask, "share_rewetted_rich_organic"].item()
                rewetted_area_target_poor = landcover_data.loc[rewetted_area_target_mask, "area_ha"].item() * landcover_data.loc[rewetted_area_target_mask, "share_rewetted_poor_organic"].item()

                rewetted_area_base_rich = landcover_data.loc[rewetted_area_base_mask, "area_ha"].item() * landcover_data.loc[rewetted_area_base_mask, "share_rewetted_rich_organic"].item()
                rewetted_area_base_poor = landcover_data.loc[rewetted_area_base_mask, "area_ha"].item() * landcover_data.loc[rewetted_area_base_mask, "share_rewetted_poor_organic"].item()

                total_rewetted_area_target = (rewetted_area_base_rich + rewetted_area_base_poor)-(rewetted_area_target_rich + rewetted_area_target_poor)
                
                print(f"total_rewetted_area_target: {total_rewetted_area_target}")

                self.assertAlmostEqual(abs(matrix.loc[farm_id, "Grassland_to_Grassland"].item()), (self.spared_area.loc[self.target_year, farm_id].item()+ total_rewetted_area_target))
            
    def test_land_balance(self):
        landcover_data = self.land.combined_future_land_use_area()
        matrix = self.transition.create_transition_matrix()

        for farm_id in landcover_data.farm_id.unique():
            if farm_id > 0:
                grass_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "grassland")
                grass_mask = (landcover_data.farm_id == farm_id) & (landcover_data.land_use == "grassland")
                self.assertAlmostEqual((landcover_data.loc[grass_mask, "area_ha"].item() + abs(matrix.loc[farm_id, "Grassland_to_Grassland"])),landcover_data.loc[grass_base_mask, "area_ha"].item())

                forest_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "forest")
                forest_mask = (landcover_data.farm_id == farm_id) & (landcover_data.land_use == "forest")
                self.assertAlmostEqual((landcover_data.loc[forest_base_mask, "area_ha"].item() + abs(matrix.loc[farm_id, "Grassland_to_Forest"])),landcover_data.loc[forest_mask, "area_ha"].item())

                cropland_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "cropland")
                cropland_mask = (landcover_data.farm_id == farm_id) & (landcover_data.land_use == "cropland")
                self.assertAlmostEqual((landcover_data.loc[cropland_base_mask, "area_ha"].item() + abs(matrix.loc[farm_id, "Grassland_to_Cropland"])),landcover_data.loc[cropland_mask, "area_ha"].item())

                wetland_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "wetland")
                wetland_mask = (landcover_data.farm_id == farm_id) & (landcover_data.land_use == "wetland")
                self.assertAlmostEqual((landcover_data.loc[wetland_base_mask, "area_ha"].item() + abs(matrix.loc[farm_id, "Grassland_to_Wetland"])),landcover_data.loc[wetland_mask, "area_ha"].item())

                farmable_condition_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "farmable_condition")
                farmable_condition_mask = (landcover_data.farm_id == farm_id) & (landcover_data.land_use == "farmable_condition")
                self.assertAlmostEqual((landcover_data.loc[farmable_condition_base_mask, "area_ha"].item() + abs(matrix.loc[farm_id, "Grassland_to_Farmable_Condition"])),landcover_data.loc[farmable_condition_mask, "area_ha"].item())

                settlement_base_mask = (landcover_data.year == self.baseline) & (landcover_data.land_use == "settlement")
                settlement_mask = (landcover_data.farm_id == farm_id) & (landcover_data.land_use == "settlement")
                self.assertAlmostEqual((landcover_data.loc[settlement_base_mask, "area_ha"].item() + abs(matrix.loc[farm_id, "Grassland_to_Settlement"])),landcover_data.loc[settlement_mask, "area_ha"].item())


    def test_proportions(self):
        matrix = self.transition.create_transition_matrix()
        landcover_data = self.land.combined_future_land_use_area()  

        for farm_id in matrix.index:
            if farm_id > 0:

                spared_area = self.spared_area.loc[self.target_year, farm_id].item()

                forest_area = spared_area * self.fetcher.get_forest_proportion(farm_id)

                print(f"forest_area: {forest_area}")

                self.assertAlmostEqual(abs(matrix.loc[farm_id, "Grassland_to_Forest"]), forest_area, places=-1)  # Reduced precision to -1 places
   
    def test_future_land_use_area_balance(self):

        # Generate future land use data using the function
        future_land_use = self.land.combined_future_land_use_area()

        base_sum = future_land_use[future_land_use.farm_id == -self.baseline]["area_ha"].sum()

        # Check that the area_ha balance is the same for the sum of all the land_use data for each unique farm_id
        for farm_id in future_land_use.farm_id.unique()[1:]:

            future_sum = future_land_use[future_land_use.farm_id == farm_id]["area_ha"].sum()

            self.assertAlmostEqual(base_sum, future_sum, places=5)

    def test_afforestation(self):
        matrix = self.transition.create_transition_matrix()
        affor = Afforestation(self.baseline, self.target_year, self.scenario_dataframe, matrix)
        afforestation = affor.gen_cbm_afforestation_dataframe(self.spared_area_breakdown)
        
        for sc in afforestation.scenario.unique():
            if sc > 0:
                afforestation_mask = (afforestation.scenario == sc)
                self.assertAlmostEqual(afforestation.loc[afforestation_mask, "total_area"].sum(), abs(matrix.loc[sc, "Grassland_to_Forest"]))

                
if __name__ == '__main__':
    unittest.main()
