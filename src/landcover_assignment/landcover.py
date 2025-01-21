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
- ``landcover_assignment.resource_manager.landcover_data_manager.DataManager``: Manages land cover data.
- ``landcover_assignment.resource_manager.data_loader.Loader``: Loads required data resources.
- ``landcover_assignment.resource_manager.scenario_data_fetcher.ScenarioDataFetcher``: Fetches scenario-specific data.
- ``landcover_assignment.optimisation.landcover_optimisation.LandCoverOptimisation``: Optimizes land cover distribution.

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
   - `_log_spared_area`: Logs the spared area details for a specific scenario and land use.
   - `get_spared_area_log`: Returns the log of spared area details.
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
from landcover_assignment.resource_manager.landcover_data_manager import DataManager
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from landcover_assignment.resource_manager.data_loader import Loader
from landcover_assignment.optimisation.landcover_optimisation import LandCoverOptimisation

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
    _log_spared_area(scenario, land_use, area, rewetted_area, mineral_area)
        Logs the spared area details for a specific scenario and land use.
    get_spared_area_log() -> pandas.DataFrame
        Returns the log of spared area details.
    _fill_current_area_row(farm_id, year, land_use) -> dict
        Fills a row of data representing the current state of a specific land use area.
    _fill_future_area_row(farm_id, refyear, target_year, land_use) -> dict
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
        self.sc_fetch_class = ScenarioDataFetcher(scenario_inputs_df, validate_on_init=True)
        self.land_dist_class = LandDistribution(scenario_inputs_df)
        self.total_grassland = total_grassland
        self.total_spared_area = total_spared_area
        self.total_spared_area_breakdown = spared_area_breakdown
        self.scenario_list = self.sc_fetch_class.get_scenario_list()
        self._spared_area_log = pd.DataFrame()


    def _log_spared_area(self, scenario, land_use, mineral_area, organic_area):
        """
        Logs the spared area details for a specific scenario and land use.

        Parameters
        ----------
        scenario : int
            The scenario identifier.
        land_use : str
            The type of land use.
        mineral_area : float
            The amount of area spared on mineral soil.
        organic_area : float
            The amount of area spared on organic soil.
        """
        new_entry = {
            "scenario": scenario,
            "land_use": land_use,
            "mineral_area": mineral_area,
            "organic_area": organic_area,
        }
        
        # Handle the case where the log is empty
        if self._spared_area_log.empty:
            self._spared_area_log = pd.concat(
                [self._spared_area_log, pd.DataFrame([new_entry])], ignore_index=True
            )

        # Append new entries if the combination of scenario and land use does not already exist
        elif not ((self._spared_area_log["scenario"] == scenario) &
                (self._spared_area_log["land_use"] == land_use)).any():
            self._spared_area_log = pd.concat(
                [self._spared_area_log, pd.DataFrame([new_entry])], ignore_index=True
            )


    def get_spared_area_log(self):
        """
        Returns the log of spared area details.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the log of spared area details.
        """
        return self._spared_area_log
    

    def _fill_current_area_row(self, farm_id, year, land_use):
        """
        Fills a row of data representing the current state of a specific land use area.
        
        Parameters
        ----------
        farm_id : int
            Identifier, a legacy term that represents the scenario identifier.
        year : int
            The year for which the data row is relevant.
        land_use : str
            The type of land use being considered.
        
        Returns
        -------
        dict
            A dictionary containing filled data for the current area row.
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
        
        Parameters
        ----------
        farm_id : int
            Identifier, a legacy term that represents the scenario identifier.
        refyear : int
            The year for which the data row is relevant.
        target_year : int
            The future year for which the data row is relevant.
        land_use : str
            The type of land use being considered.
        
        Returns
        -------
        dict
            A dictionary containing filled data for the future area row.
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
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the computed current land use areas.
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
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing both current and projected future land use areas.
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
        Analyzes the breakdown of spared areas under a specific scenario.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the spared area breakdown is calculated.
        
        Returns
        -------
        dict
            A dictionary containing the breakdown of spared areas for the given scenario.
        """
        result_dict = {}

        year = self.data_manager_class.calibration_year
        spared_land_use_dict = self.data_manager_class.get_spared_area_dict()

        max_organic_available = self._available_organic_area(scenario)["available_organic"]
        initial_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)

        # Step 1: Handle wetlands (special case)
        rewet_proportion = self.sc_fetch_class.get_rewetted_proportion(scenario)  # Target proportion for wetlands
        target_rewetted = initial_spared_area * rewet_proportion  # Area to be rewetted (from grassland)
        rewetted_area = min(max_organic_available, target_rewetted)  # Limit rewetted area to organic availability

        self._log_spared_area(scenario, "rewet_grassland", 0, rewetted_area)

        # Update spared area by subtracting the rewetted area
        mineral_spared_area = initial_spared_area - rewetted_area

        # Generate wetland data and add to results
        wetland_data = self.land_dist_class.land_distribution(year, "wetland", None)  # Wetlands don't increase
        result_dict["wetland"] = wetland_data

        # Step 2: Define target shares
        target_areas = {
            land_use: (initial_spared_area * getattr(self.sc_fetch_class, f"get_{land_use}_proportion")(scenario))
            for land_use in spared_land_use_dict.keys()
            if land_use not in ["farmable_condition", "rewetted"]# Exclude "farmable condition" (fallback) & rewetted
        }

        # Step 3: Optimize spared area distribution
        optimizer = LandCoverOptimisation()
        optimised_allocations = optimizer.optimise_mineral_spared_area_distribution(
            mineral_area_available=mineral_spared_area,
            target_areas=target_areas,
        )

        # Step 4: Distribute spared area based on optimised allocations
        for land_use, allocated_area in optimised_allocations.items():
            generated_land_use_data = self.land_dist_class.land_distribution(
                year, land_use, allocated_area
            )

            self._log_spared_area(scenario, land_use, allocated_area, 0)
            result_dict[land_use] = generated_land_use_data

        return result_dict


    def grassland_breakdown(self, scenario):
        """
        Specifically analyzes the distribution and adjustment of grassland areas under a given scenario.

        This method computes how changes in land use, particularly the conversion of grassland to other types or
        its retention, affect the overall grassland area. It considers organic and mineral soil proportions and
        adjusts them based on scenario inputs.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the grassland distribution is calculated.
        
        Returns
        -------
        dict
            A dictionary containing updated grassland distribution details, including areas and proportions
            of soil types.
        """
        result_dict = {}

        calibration_year = self.data_manager_class.calibration_year

        initial_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)


        max_organic_available = self._available_organic_area(scenario)["available_organic"]

        sc_rewetted_proportion = self.sc_fetch_class.get_rewetted_proportion(scenario)
        target_rewet= initial_spared_area * sc_rewetted_proportion

        new_rewetted_area_achieved = min(max_organic_available,target_rewet)


        spared_mineral_achieved = initial_spared_area - new_rewetted_area_achieved

        generated_land_use_data = self.land_dist_class.grassland_distribution(
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

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the available organic area is calculated.
        
        Returns
        -------
        dict
            A dictionary containing the available organic area and available mineral-organic area.
        """
        year = self.data_manager_class.calibration_year

        organic_potential = self.national_class.get_area_with_organic_potential(self.total_spared_area_breakdown, self.total_spared_area, scenario)
        
        drained_rich_current_organic_area = self.national_class.get_landuse_area("grassland", year, self.total_grassland) * self.national_class.get_share_drained_rich_organic_grassland("grassland", year, self.total_grassland)
        drained_poor_current_organic_area = self.national_class.get_landuse_area("grassland", year, self.total_grassland) * self.national_class.get_share_drained_poor_organic_grassland("grassland", year, self.total_grassland)
        
        total_drained = drained_rich_current_organic_area + drained_poor_current_organic_area

        max_organic_spared = min(organic_potential, total_drained)

        return {"available_organic":max_organic_spared}
