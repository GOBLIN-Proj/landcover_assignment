import unittest
import os
from tempfile import TemporaryDirectory
import pandas as pd
from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.landcover import LandCover
from landcover_assignment.afforestation import Afforestation

class TestGenerateData(unittest.TestCase):
    def test_generate_scenario_dataframe_creates_file(self):
        # Use a temporary directory
        with TemporaryDirectory() as tmp_dir:

            path = "./data/"

            baseline = 2020
            target_year = 2050
            scenario_dataframe = pd.read_csv(os.path.join(path, "scenario_dataframe.csv"), index_col=0)
            spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
            spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
            spared_area.columns = spared_area.columns.astype(int)
            grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
            grassland_area.columns = grassland_area.columns.astype(int)
                
            transition = TransitionMatrix(
                baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
            )

            land = LandCover(
                baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
            )


            # Define the expected file name
            expected_file_name = "transition_matrix.csv"
            expected_file_path_csv = os.path.join(tmp_dir, expected_file_name)

            # Call the method under test
            transition_matrix = transition.create_transition_matrix()
            transition_matrix.to_csv(expected_file_path_csv)
            
            # Check if the file was created as expected
            self.assertTrue(os.path.exists(expected_file_path_csv), f"File {expected_file_name} was not created in temporary directory.")

            # Combine future land use area
            # Define the expected file name
            expected_file_name = "combined_future_land_use_area.csv"
            expected_file_path_csv = os.path.join(tmp_dir, expected_file_name)

            land.combined_future_land_use_area().to_csv(expected_file_path_csv)

            # Check if the file was created as expected
            self.assertTrue(os.path.exists(expected_file_path_csv), f"File {expected_file_name} was not created in temporary directory.")


            # Afforestation class instance 
            affor = Afforestation(baseline, target_year, scenario_dataframe, transition_matrix)

            # Define the expected file name
            expected_file_name = "cbm_afforestation.csv"
            expected_file_path_csv = os.path.join(tmp_dir, expected_file_name)

            # Call the method under test
            affor.gen_cbm_afforestation_dataframe(spared_area_breakdown).to_csv(expected_file_path_csv)
            
            # Check if the file was created as expected
            self.assertTrue(os.path.exists(expected_file_path_csv), f"File {expected_file_name} was not created in temporary directory.")

# Running the tests
if __name__ == '__main__':
    unittest.main()
