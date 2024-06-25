"""
Landcover
================
This module facilitates the management and analysis of land cover changes within the Irish National context, focusing on the dynamics of land use 
transitions under various scenarios. It leverages data from land cover assignments, national analyses, and scenario-driven land distribution calculations 
to provide tools for detailed land cover change analysis.

Features:
---------
- **Land Cover Analysis**: Provides functionalities to analyze and compute land cover distributions and transitions based on calibration and target years, 
scenario inputs, and specific land area considerations.
- **Scenario-driven Land Distribution**: Manages the distribution and transition of land areas across different land use types, adjusting for 
scenario-specific changes.

Dependencies:
-------------
- ``pandas``: Used for data manipulation and analysis.
- ``landcover_assignment.distribution.LandDistribution``: Manages land distribution scenarios.
- ``landcover_assignment.national_landcover.NationalLandCover``: Analyzes land cover within national areas.
- ``landcover_assignment.landcover_data_manager.DataManager``: Manages land cover data.
- ``resource_manager.data_loader.Loader``: Loads required data resources.
- ``resource_manager.scenario_data_fetcher.ScenarioDataFetcher``: Fetches scenario-specific data.

Classes:
--------
.. class:: LandCover(calibration_year, target_year, scenario_inputs_df, total_grassland, total_spared_area, spared_area_breakdown)
   :noindex:

   Manages the computation and analysis of land cover changes, focusing on the adjustments of land areas under different scenarios 
   and their implications on land use distribution.

   The class initializes with the required data and parameters for analysis, including calibration and target years, scenario inputs, and areas related 
   to grassland and spared lands. It provides methods to fill current area data, compute current and future land use areas, 
   and analyze spared area breakdowns and grassland distributions based on scenario inputs.

   Methods include:
   - `_fill_current_area_row`: Fills data for the current area based on land use type.
   - `_fill_future_area_row`: Fills data for the future area based on land use type.
   - `compute_current_area`: Computes the current area distribution for all land uses.
   - `combined_future_land_use_area`: Combines current and future land use areas under different scenarios.
   - `spared_area_breakdown`: Analyzes the breakdown of spared areas based on scenarios.
   - `grassland_breakdown`: Specifically analyzes the breakdown of grassland areas under scenarios.
   - `_available_organic_area`: Computes the available organic area for scenarios.

"""

import pandas as pd
import numpy as np

from landcover_assignment.distribution import LandDistribution
from landcover_assignment.national_landcover import NationalLandCover
from landcover_assignment.landcover_data_manager import DataManager
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from landcover_assignment.resource_manager.data_loader import Loader



class LandCover:
    """
    Manages the computation and analysis of land cover changes, focusing on adjustments in land areas under different scenarios.

    This class is designed to analyze land cover transitions and distributions within Irish national areas, 
    taking into account various scenarios. It leverages data from land cover assignments, national analyses, scenario-driven 
    land distribution calculations to model land cover changes effectively.

    The `LandCover` class provides functionalities to compute current land use distributions based on calibration year data, 
    project future land use areas under different scenarios, and analyze the breakdown of spared areas and grassland distributions
    based on specific scenario inputs.

    Parameters
    ----------
    calibration_year : int
        The year used as a baseline for land cover data and analysis.
    target_year : int
        The future year for which land cover changes are projected.
    scenario_inputs_df : pandas.DataFrame
        A DataFrame containing inputs for various scenarios, used to drive the scenario-based inputs for land distribution adjustments.
    total_grassland : float
        The total area of grassland, used in calculations involving grassland distributions.
    total_spared_area : float
        The total area of land spared from agricultural use, key to scenario-based land distribution analysis.
    spared_area_breakdown : pandas.DataFrame
        A breakdown of how spared areas are allocated across different land use types.

    Attributes
    ----------
    data_manager_class : DataManager
        Manages land cover data and provides access to calibration and target year data.
    data_loader_class : Loader
        Loads required data resources, including environmental and land use data.
    national_class : NationalLandCover
        Provides functionalities for accessing and analyzing national land cover data.
    sc_fetch_class : ScenarioDataFetcher
        Fetches scenario-specific information from the input data.
    land_dist_class : LandDistribution
        Manages the distribution and transition of land areas across different land use types.
    scenario_list : list
        A list of scenarios derived from the scenario inputs, driving the land cover analysis.

    Methods
    -------
    _fill_current_area_row(farm_id, year, land_use) -> dict
        Fills a row of data representing the current state of a specific land use area.
    _fill_future_area_row(farm_id, year, land_use) -> dict
        Fills a row of data representing the future state of a specific land use area.
    compute_current_area() -> pandas.DataFrame
        Computes the current distribution of land use areas based on calibration year data.
    combined_future_land_use_area() -> pandas.DataFrame
        Combines current and future land use areas under different scenarios into a single DataFrame.
    spared_area_breakdown(scenario) -> dict
        Analyzes the breakdown of spared areas under a specific scenario.
    grassland_breakdown(scenario) -> dict
        Specifically analyzes the distribution and adjustment of grassland areas under a given scenario.
    _available_organic_area(scenario) -> dict
        Computes the available area for organic soil-based land uses under a given scenario.
    """
    def __init__(
        self,
        calibration_year,
        target_year,
        scenario_inputs_df,
        total_grassland,
        total_spared_area,
        spared_area_breakdown,
    ):
        self.data_manager_class = DataManager(
            calibration_year, target_year
        )
        self.data_loader_class = Loader()
        self.national_class = NationalLandCover()
        self.sc_fetch_class = ScenarioDataFetcher(scenario_inputs_df)
        self.land_dist_class = LandDistribution(scenario_inputs_df)
        self.total_grassland = total_grassland
        self.total_spared_area = total_spared_area
        self.total_spared_area_breakdown = spared_area_breakdown
        self.scenario_list = self.sc_fetch_class.get_scenario_list()


    def _fill_current_area_row(self, farm_id, year, land_use):
        """
        Fills a row of data representing the current state of a specific land use area.
        
        :param farm_id: Identifier for the farm or land area.
        :type farm_id: int
        :param year: The year for which the data row is relevant.
        :type year: int
        :param land_use: The type of land use being considered.
        :type land_use: str
        :return: A dictionary containing filled data for the current area row.
        :rtype: dict
        """
        if land_use == "grassland":
            
            return {
                "farm_id": farm_id,
                "year": year,
                "land_use": land_use,
                "area_ha": self.national_class.get_landuse_area(land_use, year, self.total_grassland),
                "share_mineral": self.national_class.get_share_mineral(land_use, year, self.total_grassland),
                "share_organic": self.national_class.get_share_organic(land_use, year, self.total_grassland),
                "share_drained_rich_organic": self.national_class.get_share_drained_rich_organic_grassland(land_use, year, self.total_grassland),
                "share_drained_poor_organic": self.national_class.get_share_drained_poor_organic_grassland(land_use, year, self.total_grassland),
                "share_rewetted_rich_organic": self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, year, self.total_grassland),
                "share_rewetted_poor_organic": self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, year, self.total_grassland),
                "share_organic_mineral": self.national_class.get_share_organic_mineral(land_use, year, self.total_grassland),
                "share_rewetted_in_organic": self.national_class.get_share_rewetted_in_organic(land_use, year, self.total_grassland),
                "share_rewetted_in_mineral": self.national_class.get_share_rewetted_in_mineral(land_use, year, self.total_grassland),
                "share_domestic_peat_extraction": self.national_class.get_share_domestic_peat_extraction(land_use, year),
                "share_industrial_peat_extraction": self.national_class.get_share_industrial_peat_extraction(land_use, year),
                "share_rewetted_industrial_peat_extraction": self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, year),
                "share_rewetted_domestic_peat_extraction": self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, year),
                "share_near_natural_wetland": self.national_class.get_share_near_natural_wetland(land_use, year),
                "share_unmanaged_wetland": self.national_class.get_share_unmanaged_wetland(land_use, year),
                "share_burnt": self.national_class.get_share_burnt(land_use, year, self.total_grassland),
            }
        
        else:

            return {
                "farm_id": farm_id,
                "year": year,
                "land_use": land_use,
                "area_ha": self.national_class.get_landuse_area(land_use, year),
                "share_mineral": self.national_class.get_share_mineral(land_use, year),
                "share_organic": self.national_class.get_share_organic(land_use, year),
                "share_drained_rich_organic": self.national_class.get_share_drained_rich_organic_grassland(land_use, year),
                "share_drained_poor_organic": self.national_class.get_share_drained_poor_organic_grassland(land_use, year),
                "share_rewetted_rich_organic": self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, year),
                "share_rewetted_poor_organic": self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, year),
                "share_organic_mineral": self.national_class.get_share_organic_mineral(land_use, year),
                "share_rewetted_in_organic": self.national_class.get_share_rewetted_in_organic(land_use, year),
                "share_rewetted_in_mineral": self.national_class.get_share_rewetted_in_mineral(land_use, year),
                "share_domestic_peat_extraction": self.national_class.get_share_domestic_peat_extraction(land_use, year),
                "share_industrial_peat_extraction": self.national_class.get_share_industrial_peat_extraction(land_use, year),
                "share_rewetted_industrial_peat_extraction": self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, year),
                "share_rewetted_domestic_peat_extraction": self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, year),
                "share_near_natural_wetland": self.national_class.get_share_near_natural_wetland(land_use, year),
                "share_unmanaged_wetland": self.national_class.get_share_unmanaged_wetland(land_use, year),
                "share_burnt": self.national_class.get_share_burnt(land_use, year),
            } 
        
    def _fill_future_area_row(self, farm_id, refyear, target_year, land_use):
        """
        Fills a row of data representing the future state of a specific land use area.
        
        :param farm_id: Identifier for the farm or land area.
        :type farm_id: int
        :param refyear: The year for which the data row is relevant.
        :type ref_year: int
        :param target_year: The future year for which the data row is relevant.
        :type target_year: int
        :param land_use: The type of land use being considered.
        :type land_use: str
        :return: A dictionary containing filled data for the future area row.
        :rtype: dict
        """
        return {
            "farm_id": farm_id,
            "year": target_year,
            "land_use": land_use,
            "area_ha": self.national_class.get_landuse_area(land_use, refyear),
            "share_mineral": self.national_class.get_share_mineral(land_use, refyear),
            "share_organic": self.national_class.get_share_organic(land_use, refyear),
            "share_drained_rich_organic": self.national_class.get_share_drained_rich_organic_grassland(land_use, refyear),
            "share_drained_poor_organic": self.national_class.get_share_drained_poor_organic_grassland(land_use, refyear),
            "share_rewetted_rich_organic": self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, refyear),
            "share_rewetted_poor_organic": self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, refyear),
            "share_organic_mineral": self.national_class.get_share_organic_mineral(land_use, refyear),
            "share_rewetted_in_organic": self.national_class.get_share_rewetted_in_organic(land_use, refyear),
            "share_rewetted_in_mineral": self.national_class.get_share_rewetted_in_mineral(land_use, refyear),
            "share_domestic_peat_extraction": self.national_class.get_share_domestic_peat_extraction(land_use, refyear),
            "share_industrial_peat_extraction": self.national_class.get_share_industrial_peat_extraction(land_use, refyear),
            "share_rewetted_industrial_peat_extraction": self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, refyear),
            "share_rewetted_domestic_peat_extraction": self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, refyear),
            "share_near_natural_wetland": self.national_class.get_share_near_natural_wetland(land_use, refyear),
            "share_unmanaged_wetland": self.national_class.get_share_unmanaged_wetland(land_use, refyear),
            "share_burnt": self.national_class.get_share_burnt(land_use, refyear),
        }  
        

    def compute_current_area(self):
        """
        Computes the distribution of current land use areas based on the calibration year and available data.
        
        :return A DataFrame containing the computed current land use areas.
        :rtype: pandas.DataFrame
        """
        calibration_year = self.data_manager_class.calibration_year
        landuses = self.data_manager_class.land_use_columns

        data = []
        for landuse in landuses:
        
            row = self._fill_current_area_row(-calibration_year, calibration_year, landuse)
            data.append(row)

        return pd.DataFrame(data)
    

    def combined_future_land_use_area(self):
        """
        Combines the calculated current land use areas with projected future areas under different scenarios.
        
        :return: A DataFrame containing both current and projected future land use areas.
        :rtype: pandas.DataFrame
        """
        target_year = self.data_manager_class.target_year
        calibration_year = self.data_manager_class.calibration_year

        scenarios = self.scenario_list

        land_use_columns = self.data_manager_class.land_use_columns

        current_area_pd = self.compute_current_area()

        future_area_pd = pd.DataFrame(columns=current_area_pd.columns)

        data = []
        for sc in scenarios:
            land_use_data_future = self.spared_area_breakdown(sc)
            grassland_data_future = self.grassland_breakdown(sc)
            for landuse in land_use_columns:
                
                if landuse == "grassland":
               
                    row ={
                            "farm_id": sc,
                            "year": target_year,
                            "land_use": landuse,
                            "area_ha": grassland_data_future[landuse]["area_ha"],
                            "share_mineral": grassland_data_future[landuse][
                                "share_mineral"
                            ],
                            "share_organic": grassland_data_future[landuse][
                                "share_organic"
                            ],
                            "share_drained_rich_organic": grassland_data_future[landuse]["share_drained_rich_organic"],

                            "share_drained_poor_organic": grassland_data_future[landuse]["share_drained_poor_organic"],

                            "share_rewetted_rich_organic": grassland_data_future[landuse]["share_rewetted_rich_organic"],

                            "share_rewetted_poor_organic": grassland_data_future[landuse]["share_rewetted_poor_organic"],

                            "share_organic_mineral": grassland_data_future[landuse][
                                "share_organic_mineral"
                            ],
                            "share_rewetted_in_organic": grassland_data_future[landuse][
                                "share_rewetted_in_organic"
                            ],
                            "share_rewetted_in_mineral": grassland_data_future[landuse][
                                "share_rewetted_in_mineral"
                            ],
                            "share_domestic_peat_extraction": grassland_data_future[landuse][
                                "share_domestic_peat_extraction"
                            ],
                            "share_industrial_peat_extraction": grassland_data_future[landuse][
                                "share_industrial_peat_extraction"
                            ],
                            "share_rewetted_industrial_peat_extraction": grassland_data_future[landuse][
                                "share_rewetted_industrial_peat_extraction"
                            ],
                            "share_rewetted_domestic_peat_extraction": grassland_data_future[landuse][
                                "share_rewetted_domestic_peat_extraction"
                            ],
                            "share_near_natural_wetland": grassland_data_future[landuse]["share_near_natural_wetland"],
                            "share_unmanaged_wetland": grassland_data_future[landuse]["share_unmanaged_wetland"],
                            "share_burnt": grassland_data_future[landuse]["share_burnt"],
                        }
                    data.append(row)

                elif landuse == "settlement":
                    row =self._fill_future_area_row(sc, calibration_year, target_year, landuse)

                    data.append(row)
                

                else:

                    row ={
                            "farm_id": sc,
                            "year": target_year,
                            "land_use": landuse,
                            "area_ha": land_use_data_future[landuse]["area_ha"],
                            "share_mineral": land_use_data_future[landuse][
                                "share_mineral"
                            ],
                            "share_organic": land_use_data_future[landuse][
                                "share_organic"
                            ],
                            "share_drained_rich_organic": land_use_data_future[landuse]["share_drained_rich_organic"],

                            "share_drained_poor_organic": land_use_data_future[landuse]["share_drained_poor_organic"],

                            "share_rewetted_rich_organic": land_use_data_future[landuse]["share_rewetted_rich_organic"],

                            "share_rewetted_poor_organic": land_use_data_future[landuse]["share_rewetted_poor_organic"],

                            "share_organic_mineral": land_use_data_future[landuse][
                                "share_organic_mineral"
                            ],
                            "share_rewetted_in_organic": land_use_data_future[landuse][
                                "share_rewetted_in_organic"
                            ],
                            "share_rewetted_in_mineral": land_use_data_future[landuse][
                                "share_rewetted_in_mineral"
                            ],
                            "share_domestic_peat_extraction": land_use_data_future[landuse][
                                "share_domestic_peat_extraction"
                            ],
                            "share_industrial_peat_extraction": land_use_data_future[landuse][
                                "share_industrial_peat_extraction"
                            ],
                            "share_rewetted_industrial_peat_extraction": land_use_data_future[landuse][
                                "share_rewetted_industrial_peat_extraction"
                            ],
                            "share_rewetted_domestic_peat_extraction": land_use_data_future[landuse][
                                "share_rewetted_domestic_peat_extraction"
                            ],
                            "share_near_natural_wetland": land_use_data_future[landuse]["share_near_natural_wetland"],
                            "share_unmanaged_wetland": land_use_data_future[landuse]["share_unmanaged_wetland"],
                            "share_burnt": land_use_data_future[landuse]["share_burnt"],
                        }
                    
                    

                    data.append(row)
        
        future_area_pd = pd.DataFrame(data)

        combined_df = pd.concat([current_area_pd, future_area_pd], ignore_index=True)
        
        return combined_df


    def spared_area_breakdown(self, scenario):
        """
        Analyzes the breakdown of spared areas under a specific scenario, adjusting land use distributions accordingly.

        This method calculates how spared areas should be distributed among various land use types based on scenario-specific
        proportions and environmental considerations, such as the availability of organic soil.

        :param scenario (int): The scenario identifier for which the spared area breakdown is calculated.
        :type scenario: int
        :return: A dictionary containing the breakdown of spared areas by land use type, with detailed proportions
                and areas for each type.
        :rtype: dict
        """
        result_dict = {}

        year = self.data_manager_class.calibration_year

        spared_land_use_dict = self.data_manager_class.spared_area_dict

        max_organic_available = self._available_organic_area(scenario)["available_organic"]
        initial_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)
        adjusted_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)

        for land_use in spared_land_use_dict.keys():

            result_dict[land_use] = {}
            method_name = f"get_{land_use}_proportion"
            method = getattr(self.sc_fetch_class, method_name, None)

            if land_use == "wetland":
                # wetland area does not increase, transfer is between categories in grassland
                # however, spared area must still be accounted for

                land_use_proportion = method(scenario)
                target_wetland = initial_spared_area * land_use_proportion

                spared_area_reduction = min(max_organic_available,target_wetland)

                generated_land_use_data = self.land_dist_class.land_distribution(
                    year, land_use, None
                )

                result_dict[land_use] = generated_land_use_data

                adjusted_spared_area = initial_spared_area - spared_area_reduction

            elif land_use != "farmable_condition":

                land_use_proportion = method(scenario)

                target_area = initial_spared_area * land_use_proportion

                
                new_land_use_area = min(adjusted_spared_area,target_area)

                if new_land_use_area < 0:
                    new_land_use_area = 0

                generated_land_use_data = self.land_dist_class.land_distribution(year, land_use, new_land_use_area)


                result_dict[land_use] = generated_land_use_data

                adjusted_spared_area -= new_land_use_area

            else:
                generated_land_use_data = self.land_dist_class.land_distribution(
                    year, land_use, adjusted_spared_area
                )

                result_dict[land_use] = generated_land_use_data

        return result_dict    


    def grassland_breakdown(self, scenario):
        """
        Specifically analyzes the distribution and adjustment of grassland areas under a given scenario.

        This method computes how changes in land use, particularly the conversion of grassland to other types or
        its retention, affect the overall grassland area. It considers organic and mineral soil proportions and
        adjusts them based on scenario inputs.

        :param scenario: The scenario identifier for which the grassland distribution is calculated.
        :type scenario: int
        :return: A dictionary containing updated grassland distribution details, including areas and proportions
                of soil types.
        :rtype: dict
        """
        result_dict = {}

        calibration_year = self.data_manager_class.calibration_year

        initial_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)


        max_organic_available = self._available_organic_area(scenario)["available_organic"]

        sc_wetland_proportion = self.sc_fetch_class.get_wetland_proportion(scenario)
        target_rewet= initial_spared_area * sc_wetland_proportion

        new_rewetted_area_achieved = min(max_organic_available,target_rewet)


        spared_mineral_achieved = initial_spared_area - new_rewetted_area_achieved

        generated_land_use_data = self.land_dist_class.grassland_distriubtion(
            calibration_year, spared_mineral_achieved, new_rewetted_area_achieved, self.total_grassland
        )

        result_dict["grassland"] = generated_land_use_data


        return result_dict
    


    def _available_organic_area(self, scenario):
        """
        Computes the available area for organic soil under a given scenario.

        This internal method calculates the maximum possible area that can be transitioned to organic soil-based
        land uses, such as wetlands, based on the current organic and organic-mineral soil areas and scenario-specific
        spared area allocations.

        :param scenario (int): The scenario identifier for which the available organic area is calculated.
        :type scenario: int
        :return: A dictionary containing the available organic area and available mineral-organic area.
        :rtype: dict
        """
        year = self.data_manager_class.calibration_year

        #initial_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)
        organic_potential = self.national_class.get_area_with_organic_potential(self.total_spared_area_breakdown, self.total_spared_area, scenario)
        drained_rich_current_organic_area = self.national_class.get_landuse_area("grassland", year, self.total_grassland) * self.national_class.get_share_drained_rich_organic_grassland("grassland", year, self.total_grassland)
        drained_poor_current_organic_area = self.national_class.get_landuse_area("grassland", year, self.total_grassland) * self.national_class.get_share_drained_poor_organic_grassland("grassland", year, self.total_grassland)
        total_drained = drained_rich_current_organic_area + drained_poor_current_organic_area

        current_mineral_organic_area = self.national_class.get_landuse_area("grassland", year, self.total_grassland) * self.national_class.get_share_organic_mineral("grassland", year, self.total_grassland)

        max_organic_spared = min(organic_potential, total_drained)

        #max_mineral_organic_spared = min(initial_spared_area,current_mineral_organic_area)

        return {"available_organic":max_organic_spared}
