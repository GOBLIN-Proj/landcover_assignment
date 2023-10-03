import pandas as pd
import numpy as np

from landcover_assignment.distribution import LandDistribution

from landcover_assignment.landcover_data_manager import DataManager
from landcover_assignment.data_loader import Loader


class LandCover:
    def __init__(self, calibration_year, target_year, scenario_inputs_df, total_grassland, total_spared_area):
       
        self.data_manager_class = DataManager(calibration_year, target_year, scenario_inputs_df)
        self.data_loader_class = Loader()
        self.total_grassland = total_grassland
        self.total_spared_area = total_spared_area




    
    def compute_current_area(self):

        """
        Utilised the processed data from corine and the soil GIS output to calculate the total area of each of the land uses. The land uses are converted from
        corine land uses to GOBLIN land uses with the help of the create_land_use_dict method. Despite having the total areas for land uses in relation to organic, mineral and mineral/organic,
        they are calculated as shares of the total land use area in order to increase compatibility with the GOBLIN modelling framework.
        """
        
        calibration_year = self.data_manager_class.calibration_year


        land_use_dict = self.data_manager_class.landuse_dict

        calculated_current_areas_pd = pd.DataFrame(columns=self.data_manager_class.areas_dataframe_cols)

        calculated_current_areas_pd["land_use"] = self.data_manager_class.land_use_columns
        calculated_current_areas_pd[
            "farm_id"
        ] = -calibration_year

        calculated_current_areas_pd["year"] = calibration_year

        calculated_current_areas_pd[
            [
                "area_ha",
                "share_mineral",
                "share_organic",
                "share_rewetted_in_organic",
                "share_rewetted_in_mineral",
                "share_peat_extraction",
                "share_burnt",
            ]
        ] = 0
        

        for index in calculated_current_areas_pd.index:

            land_use = calculated_current_areas_pd.loc[index, 'land_use']

            if land_use == "farmable_condition":
                area_value = 0
                calculated_current_areas_pd.loc[index, "share_mineral"] = 1
                calculated_current_areas_pd.loc[index, "share_organic"] = 0
                calculated_current_areas_pd.loc[index, "share_burnt"] = 0

            elif land_use == "grassland":
                method = land_use_dict.get(land_use)
                if method:
                    df = method()()  # Call the method and get the DataFrame
                    estimated_area = self.total_grassland.loc[calibration_year, 0].item()
                    area_value = df.loc[calibration_year, "total_kha"].item()
                    share_mineral = df.loc[calibration_year, "mineral_kha"].item()/area_value
                    share_organic = 1 - share_mineral
                    share_burnt = df.loc[calibration_year, "burnt_kha"].item()/area_value
                    calculated_current_areas_pd.loc[index, "area_ha"] = estimated_area
                    calculated_current_areas_pd.loc[index, "share_mineral"] = share_mineral
                    calculated_current_areas_pd.loc[index, "share_organic"] = share_organic
                    calculated_current_areas_pd.loc[index, "share_burnt"] = share_burnt

            else:
                method = land_use_dict.get(land_use)
                if method:
                    
                    df = method()()  # Call the method and get the DataFrame
                    area_value = df.loc[calibration_year, "total_kha"].item() 
                    share_mineral = df.loc[calibration_year, "mineral_kha"].item()/area_value
                    share_organic = df.loc[calibration_year, "organic_kha"].item()/area_value
                    share_burnt = df.loc[calibration_year, "burnt_kha"].item()/area_value
                    calculated_current_areas_pd.loc[index, "area_ha"] = area_value
                    calculated_current_areas_pd.loc[index, "share_mineral"] = share_mineral

                    if land_use == "forest":
                        forest_share_organic = (df.loc[calibration_year, "organic_emitting_kha"].item() + df.loc[calibration_year, "organo_mineral_emitting_kha"].item())/area_value
                        calculated_current_areas_pd.loc[index, "share_organic"] = forest_share_organic
                    else:
                        calculated_current_areas_pd.loc[index, "share_organic"] = share_organic
                    
                    calculated_current_areas_pd.loc[index, "share_burnt"] = share_burnt

                if land_use == "wetland":
                    share_rewetted_in_organic = df.loc[calibration_year, "rewetted_organic_kha"].item()/area_value
                    share_rewetted_in_mineral = df.loc[calibration_year, "rewetted_mineral_kha"].item()/area_value
                    share_peat_extraction = (df.loc[calibration_year, "peat_extraction_kha"].item() + df.loc[calibration_year, "drained_extraction_kha"].item())/area_value


                    calculated_current_areas_pd.loc[index, "share_rewetted_in_organic"] = share_rewetted_in_organic
                    calculated_current_areas_pd.loc[index, "share_rewetted_in_mineral"] = share_rewetted_in_mineral
                    calculated_current_areas_pd.loc[index, "share_peat_extraction"] = share_peat_extraction
                
        return calculated_current_areas_pd
    

    def combined_future_land_use_area(self):
        
        target_year = self.data_manager_class.target_year
        scenarios = list(self.data_manager_class.scenario_inputs_df["Scenarios"].unique())
        land_use_columns = self.data_manager_class.land_use_columns

        current_area_pd = self.compute_current_area()

        future_area_pd = pd.DataFrame(columns=current_area_pd.columns)

        for sc in scenarios:
            for landuse in land_use_columns:
                if landuse == "grassland":
                    land_use_data_future = self.grassland_breakdown(sc)

                    temp = pd.DataFrame({"farm_id": sc, "year": target_year, "land_use":landuse, "area_ha": land_use_data_future[landuse]["area_ha"], 
                    "share_mineral":land_use_data_future[landuse]["share_mineral"],
                    "share_organic": land_use_data_future[landuse]["share_organic"],
                    "share_rewetted_in_organic": land_use_data_future[landuse]["share_rewetted_in_organic"],
                    "share_rewetted_in_mineral": land_use_data_future[landuse]["share_rewetted_in_mineral"],
                    "share_peat_extraction": land_use_data_future[landuse]["share_peat_extraction"],
                    "share_burnt": land_use_data_future[landuse]["share_burnt"]},
                    index=[0])

                    future_area_pd = pd.concat([future_area_pd, temp], ignore_index=True)

                elif landuse == "settlement":

                    settlement_pd = current_area_pd.loc[(current_area_pd["land_use"]== landuse)]

                    temp = pd.DataFrame({"farm_id": sc, "year": target_year, "land_use":landuse, "area_ha": settlement_pd["area_ha"].item(),
                    "share_mineral":settlement_pd["share_mineral"].item(),
                    "share_organic": settlement_pd["share_organic"].item(),
                    "share_rewetted_in_organic": settlement_pd["share_rewetted_in_organic"].item(),
                    "share_rewetted_in_mineral": settlement_pd["share_rewetted_in_mineral"].item(),
                    "share_peat_extraction": settlement_pd["share_peat_extraction"].item(),
                    "share_burnt": settlement_pd["share_burnt"].item()},
                    index=[0])

                    future_area_pd = pd.concat([future_area_pd, temp], ignore_index=True)

                else:

                    land_use_data_future = self.spared_area_breakdown(sc)

                    temp = pd.DataFrame({"farm_id": sc, "year": target_year, "land_use":landuse, "area_ha": land_use_data_future[landuse]["area_ha"], 
                    "share_mineral":land_use_data_future[landuse]["share_mineral"],
                    "share_organic": land_use_data_future[landuse]["share_organic"],
                    "share_rewetted_in_organic": land_use_data_future[landuse]["share_rewetted_in_organic"],
                    "share_rewetted_in_mineral": land_use_data_future[landuse]["share_rewetted_in_mineral"],
                    "share_peat_extraction": land_use_data_future[landuse]["share_peat_extraction"],
                    "share_burnt": land_use_data_future[landuse]["share_burnt"]},
                    index=[0])

                    future_area_pd = pd.concat([future_area_pd, temp], ignore_index=True)

        
        combined_df = pd.concat([current_area_pd, future_area_pd], ignore_index=True)

        return combined_df


    def spared_area_breakdown(self, scenario):
        
        result_dict = {} 

        current_areas = self.compute_current_area()

        spared_land_use_dict = self.data_manager_class.spared_area_dict

        scenario_dataframe = self.data_manager_class.scenario_inputs_df

        scenario_subset = scenario_dataframe.loc[(scenario_dataframe["Scenarios"] == scenario)]

        calibration_year = self.data_manager_class.calibration_year
        target_year = self.data_manager_class.target_year

        initial_spared_area = self.total_spared_area.loc[target_year, scenario]
        

        current_grassland_mask =  ((current_areas['year'] == calibration_year) & (current_areas['land_use'] == 'grassland'))


        max_organic_available = min(initial_spared_area,(current_areas.loc[current_grassland_mask, "area_ha"].item() * current_areas.loc[current_grassland_mask, "share_organic"].item()))

        adjusted_spared_area = self.total_spared_area.loc[target_year, scenario]

        for land_use in spared_land_use_dict.keys():

            if land_use == "wetland":
                result_dict[land_use] ={}

                new_wetland_area = min(max_organic_available,(initial_spared_area*scenario_subset[spared_land_use_dict[land_use]].values[0]))

                generated_land_use_data = LandDistribution.land_distribution(land_use,current_areas, new_wetland_area)

                result_dict[land_use] = generated_land_use_data

                adjusted_spared_area = initial_spared_area - new_wetland_area

            elif land_use != "farmable_condition":

                result_dict[land_use] ={}

                new_land_use_area = min(adjusted_spared_area, (initial_spared_area*scenario_subset[spared_land_use_dict[land_use]].values[0]))


                if new_land_use_area < 0:
                    new_land_use_area = 0 

                generated_land_use_data = LandDistribution.land_distribution(land_use,current_areas, new_land_use_area)


                result_dict[land_use]=generated_land_use_data

                adjusted_spared_area -= new_land_use_area

            else:
                generated_land_use_data = LandDistribution.land_distribution(land_use,current_areas, adjusted_spared_area)
                result_dict[land_use] = generated_land_use_data

        return result_dict


    def grassland_breakdown(self, scenario):
        result_dict = {} 

        current_areas = self.compute_current_area()

        spared_land_use_dict = self.data_manager_class.spared_area_dict

        scenario_dataframe = self.data_manager_class.scenario_inputs_df

        scenario_subset = scenario_dataframe.loc[(scenario_dataframe["Scenarios"] == scenario)]

        calibration_year = self.data_manager_class.calibration_year
        target_year = self.data_manager_class.target_year

        initial_spared_area = self.total_spared_area.loc[target_year, scenario]
    

        current_grassland_mask =  ((current_areas['year'] == calibration_year) & (current_areas['land_use'] == 'grassland'))


        max_organic_available = min(initial_spared_area,(current_areas.loc[current_grassland_mask, "area_ha"].item() * current_areas.loc[current_grassland_mask, "share_organic"].item()))

        new_wetland_area = min(max_organic_available,(initial_spared_area*scenario_subset[spared_land_use_dict["wetland"]].values[0]))

        spared_mineral = initial_spared_area - new_wetland_area

        spared_organic = new_wetland_area

        generated_land_use_data = LandDistribution.grassland_distriubtion(current_areas, spared_mineral, spared_organic)
        result_dict["grassland"] = generated_land_use_data

        return result_dict
