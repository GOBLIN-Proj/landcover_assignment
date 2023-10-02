from landcover_assignment.data_loader import Loader

class DataManager():
    def __init__(self, calibration_year, target_year, scenario_inputs_df):

        self.data_loader_class = Loader()
        self.scenario_inputs_df = scenario_inputs_df
        self.calibration_year = calibration_year
        self.target_year = target_year

        self.default_calibration_year = 2015

        self.land_use_columns = ["grassland", "wetland", "cropland", "forest","settlement","farmable_condition"]

        self.cbm_default_data = {"scenario": [-1, -1], 
                         "species":["Sitka", "SGB"], 
                         "total_area":[0,0]}

        self.areas_dataframe_cols = [
                "farm_id",
                "year",
                "land_use",
                "area_ha",
                "share_mineral",
                "share_organic",
                "share_rewetted_in_organic",
                "share_burnt",
            ]
        
        self.landuse_dict = {
            "forest": self.data_loader_class.national_forest_areas,
            "cropland": self.data_loader_class.national_cropland_areas,
            "wetland": self.data_loader_class.national_wetland_areas,
            "settlement": self.data_loader_class.national_settlement_areas,
            "grassland": self.data_loader_class.national_grassland_areas
        }

        self.spared_area_dict = {
            "wetland":"Wetland area",
            "forest": "Forest area",
            "cropland": "Crop area",
            "farmable_condition": None
        }


class DistributionManager():

    def __init__(self):
        
        self.land_distribution = {"area_ha": 0,
        "share_organic": 0,
        "share_mineral": 0,
        "share_rewetted_in_organic": 0,
        "share_burnt": 0,
        "share_rewetted_in_mineral": 0,
        "share_peat_extraction": 0
        }

