"""
Geo Landcover
================
This module facilitates the management and analysis of land cover changes within specified geographic areas, focusing on the dynamics of land use 
transitions under various scenarios. It leverages data from land cover assignments, catchment analyses, and scenario-driven land distribution calculations 
to provide tools for detailed land cover change analysis.

Features:
---------
- **Land Cover Analysis**: Provides functionalities to analyze and compute land cover distributions and transitions based on calibration and target years, 
scenario inputs, and specific land area considerations.
- **Scenario-driven Land Distribution**: Manages the distribution and transition of land areas across different land use types, adjusting for 
scenario-specific changes.

Dependencies:
-------------
- `pandas`: Used for data manipulation and analysis.
- `geo_landcover_assignment.geo_distribution.LandDistribution`: Manages land distribution scenarios.
- `geo_landcover_assignment.catchment_landcover.CatchmentLandCover`: Analyzes land cover within catchment areas.
- `landcover_assignment.landcover_data_manager.DataManager`: Manages land cover data.
- `resource_manager.data_loader.Loader`: Loads required data resources.
- `resource_manager.scenario_data_fetcher.ScenarioDataFetcher`: Fetches scenario-specific data.
- `landcover_assignment.optimisation.landcover_optimisation.LandCoverOptimisation`: Optimizes land cover distribution.

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
   - _fill_current_area_row: Fills data for the current area based on land use type.
   - compute_current_area: Computes the current area distribution for all land uses.
   - combined_future_land_use_area: Combines current and future land use areas under different scenarios.
   - spared_area_breakdown: Analyzes the breakdown of spared areas based on scenarios.
   - grassland_breakdown: Specifically analyzes the breakdown of grassland areas under scenarios.
   - _available_organic_area: Computes the available organic area for scenarios.
   - _log_spared_area: Logs the spared area details for a specific scenario and land use.
   - get_spared_area_log: Returns the log of spared area details.
   - _calculate_rewetted_areas: Calculates the areas to be rewetted based on the scenario and target rewetted area.
"""
import pandas as pd
from landcover_assignment.geo_landcover_assignment.geo_distribution import LandDistribution
from landcover_assignment.geo_landcover_assignment.catchment_landcover import CatchmentLandCover
from landcover_assignment.resource_manager.landcover_data_manager import DataManager
from landcover_assignment.resource_manager.data_loader import Loader
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from landcover_assignment.optimisation.landcover_optimisation import LandCoverOptimisation

class LandCover:
    """
    Manages the computation and analysis of land cover changes, focusing on adjustments in land areas under different scenarios.

    This class is designed to analyze land cover transitions and distributions within specified geographic areas, 
    taking into account various scenarios. It leverages data from land cover assignments, catchment analyses, scenario-driven 
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
    catchment_class : CatchmentLandCover
        Provides functionalities for accessing and analyzing catchment land cover data.
    sc_fetch_class : ScenarioDataFetcher
        Fetches scenario-specific information from the input data.
    land_dist_class : LandDistribution
        Manages the distribution and transition of land areas across different land use types.
    catchment_name : str
        The name of the catchment area, derived from scenario data, used in land cover calculations.
    scenario_list : list
        A list of scenarios derived from the scenario inputs, driving the land cover analysis.

    Methods
    -------
    _fill_current_area_row(farm_id, year, land_use) -> dict
        Fills a row of data representing the current state of a specific land use area.
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
    _log_spared_area(scenario, land_use, mineral_area, organic_area, mineral_organic_area)
        Logs the spared area details for a specific scenario and land use.
    get_spared_area_log() -> pandas.DataFrame
        Returns the log of spared area details.
    _calculate_rewetted_areas(scenario, target_rewetted) -> tuple
        Calculates the areas to be rewetted based on the scenario and target rewetted area.
    """
    def __init__(
        self,
        calibration_year,
        target_year,
        scenario_inputs_df,
        total_grassland,
        total_spared_area,
        spared_area_breakdown
    ):
        self.data_manager_class = DataManager(
            calibration_year, target_year
        )
        self.data_loader_class = Loader()
        self.catchemnt_class = CatchmentLandCover()
        self.sc_fetch_class = ScenarioDataFetcher(scenario_inputs_df, validate_on_init=True)
        self.land_dist_class = LandDistribution(scenario_inputs_df)
        self.total_grassland = total_grassland
        self.total_spared_area = total_spared_area
        self.total_spared_area_breakdown = spared_area_breakdown
        self.catchment_name = self.sc_fetch_class.get_catchment_name()
        self.scenario_list = self.sc_fetch_class.get_scenario_list()
        self._spared_area_log = pd.DataFrame()


    def _log_spared_area(self, scenario, land_use, mineral_area, organic_area, mineral_organic_area):
        """
        Logs the spared area details for a specific scenario and land use.

        Parameters
        ----------
        scenario : int
            The scenario identifier.
        catchment_name : str
            The name of the catchment area.
        land_use : str
            The type of land use.
        mineral_area : float
            The amount of area spared on mineral soil.
        organic_area : float
            The amount of area spared on organic soil.
        mineral_organic_area : float
            The amount of area spared on mineral-organic soil.
        """
        new_entry = {
            "scenario": scenario,
            "catchment_name": self.catchment_name,
            "land_use": land_use,
            "mineral_area": mineral_area,
            "organic_area": organic_area,
            "mineral_organic_area": mineral_organic_area,
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
                "area_ha": self.catchemnt_class.get_landuse_area(land_use, self.catchment_name, self.total_grassland),
                "share_mineral": self.catchemnt_class.get_share_mineral(land_use, self.catchment_name, self.total_grassland),
                "share_organic": self.catchemnt_class.get_share_organic(land_use, self.catchment_name, self.total_grassland),
                "share_organic_mineral": self.catchemnt_class.get_share_organic_mineral(land_use, self.catchment_name, self.total_grassland),
                "share_rewetted_in_organic": 0.0,
                "share_rewetted_in_mineral": 0.0,
                "share_rewetted_in_organic_mineral":0.0,
                "share_peat_extraction": 0.0,
                "share_burnt": self.catchemnt_class.get_share_burnt(land_use, self.catchment_name, self.total_grassland),
            }
        
        else:

            return {
                "farm_id": farm_id,
                "year": year,
                "land_use": land_use,
                "area_ha": self.catchemnt_class.get_landuse_area(land_use, self.catchment_name),
                "share_mineral": self.catchemnt_class.get_share_mineral(land_use, self.catchment_name),
                "share_organic": self.catchemnt_class.get_share_organic(land_use, self.catchment_name),
                "share_organic_mineral": self.catchemnt_class.get_share_organic_mineral(land_use, self.catchment_name),
                "share_rewetted_in_organic": 0.0,
                "share_rewetted_in_mineral": 0.0,
                "share_rewetted_in_organic_mineral":0.0,
                "share_peat_extraction": 0.0,
                "share_burnt": self.catchemnt_class.get_share_burnt(land_use, self.catchment_name),
            }
        

    def compute_current_area(self):
        """
        Computes the distribution of current land use areas based on the calibration year and available data.
        
        :return pd.DataFrame: A DataFrame containing the computed current land use areas.
        """
        calibration_year = self.data_manager_class.calibration_year
        landuses = self.data_manager_class.get_land_use_columns()

        data = []
        for landuse in landuses:
            if landuse != "settlement":
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

        # Step 1: Compute current areas
        current_area_pd = self.compute_current_area()

        # Step 2: Initialize list to collect future data
        data = []

        # Step 3: Iterate through scenarios and calculate spared/grassland breakdowns
        for sc in self.scenario_list:

            # Calculate spared area breakdown and grassland breakdown
            spared_area_breakdown, grassland_breakdown = self.calculate_spared_area_allocation(sc)

            # Combine spared and grassland breakdowns into a single loop
            for land_use, land_use_data in {**spared_area_breakdown, **grassland_breakdown}.items():


                row = {
                    "farm_id": sc,
                    "year": target_year,
                    "land_use": land_use,
                    "area_ha": land_use_data.get("area_ha", 0),
                    "share_mineral": land_use_data.get("share_mineral", 0),
                    "share_organic": land_use_data.get("share_organic", 0),
                    "share_organic_mineral": land_use_data.get("share_organic_mineral", 0),
                    "share_rewetted_in_organic": land_use_data.get("share_rewetted_in_organic", 0),
                    "share_rewetted_in_mineral": land_use_data.get("share_rewetted_in_mineral", 0),
                    "share_rewetted_in_organic_mineral": land_use_data.get("share_rewetted_in_organic_mineral", 0),
                    "share_peat_extraction": land_use_data.get("share_peat_extraction", 0),
                    "share_burnt": land_use_data.get("share_burnt", 0),
                }
                data.append(row)

        # Step 4: Combine current and future areas into a single DataFrame
        future_area_pd = pd.DataFrame(data)
        combined_df = pd.concat([current_area_pd, future_area_pd], ignore_index=True)

        return combined_df


    def combined_future_land_use_area_old(self):
        """
        Combines the calculated current land use areas with projected future areas under different scenarios.
        
        :return pd.DataFrame: A DataFrame containing both current and projected future land use areas.
        """
        target_year = self.data_manager_class.target_year

        scenarios = self.scenario_list

        land_use_columns = self.data_manager_class.get_land_use_columns()

        current_area_pd = self.compute_current_area()

        future_area_pd = pd.DataFrame(columns=current_area_pd.columns)

        data = []
        for sc in scenarios:
            land_use_data_future, grassland_data_future = self.calculate_spared_area_allocation(sc)
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
                            "share_organic_mineral": grassland_data_future[landuse][
                                "share_organic_mineral"
                            ],
                            "share_rewetted_in_organic": grassland_data_future[landuse][
                                "share_rewetted_in_organic"
                            ],
                            "share_rewetted_in_mineral": grassland_data_future[landuse][
                                "share_rewetted_in_mineral"
                            ],
                            "share_rewetted_in_organic_mineral": grassland_data_future[landuse][
                                "share_rewetted_in_organic_mineral"
                            ],
                            "share_peat_extraction": grassland_data_future[landuse][
                                "share_peat_extraction"
                            ],
                            "share_burnt": grassland_data_future[landuse]["share_burnt"],
                        }
                    data.append(row)


                elif landuse != "settlement":

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
                            "share_organic_mineral": land_use_data_future[landuse][
                                "share_organic_mineral"
                            ],
                            "share_rewetted_in_organic": land_use_data_future[landuse][
                                "share_rewetted_in_organic"
                            ],
                            "share_rewetted_in_mineral": land_use_data_future[landuse][
                                "share_rewetted_in_mineral"
                            ],
                            "share_rewetted_in_organic_mineral": land_use_data_future[landuse][
                                "share_rewetted_in_organic_mineral"
                            ],
                            "share_peat_extraction": land_use_data_future[landuse][
                                "share_peat_extraction"
                            ],
                            "share_burnt": land_use_data_future[landuse]["share_burnt"],
                        }

                    data.append(row)
        
        future_area_pd = pd.DataFrame(data)

        combined_df = pd.concat([current_area_pd, future_area_pd], ignore_index=True)

        return combined_df
    

    def calculate_spared_area_allocation(self, scenario):
        """
        Wrapper function to handle spared area allocation across mineral and organic soils
        before passing clean parameters to breakdown methods.

        Parameters
        ----------
        scenario : int
            Scenario identifier.

        Returns
        -------
        spared_area_breakdown, grassland_breakdown : tuple
            Two dictionaries representing the spared area and grassland area breakdowns.
        """
        # Step 1: Fetch total spared area and max available areas
        initial_spared_area = self.catchemnt_class.get_total_spared_area(self.total_spared_area, scenario)
        max_mineral_available = self._available_mineral_area()["available_mineral"]


        # Step 2: Calculate rewetting (organic allocation)
        rewet_proportion = self.sc_fetch_class.get_rewetted_proportion(scenario)
        target_rewetted = initial_spared_area * rewet_proportion
        actual_rewetted_area, rewetted_organic_area, rewetted_mineral_organic_area = self._calculate_rewetted_areas(scenario, target_rewetted)

        # Step 3: Calculate remaining mineral area after rewetting
        required_mineral_area = initial_spared_area - actual_rewetted_area
        actual_mineral_area = min(max_mineral_available, required_mineral_area)

        # Step 4: Handle spillover (excess spared area beyond mineral availability)
        spillover_area = 0
        if required_mineral_area > max_mineral_available:
            spillover_area = required_mineral_area - max_mineral_available
            actual_rewetted_area += spillover_area
            actual_rewetted_area, rewetted_organic_area, rewetted_mineral_organic_area = self._calculate_rewetted_areas(scenario, actual_rewetted_area)

        # Step 5: Generate spared area breakdown
        spared_area_breakdown = self.spared_area_breakdown(
            scenario,
            intial_spared_area=initial_spared_area,
            actual_rewetted_area_organic=rewetted_organic_area,
            actual_rewetted_area_mineral_organic=rewetted_mineral_organic_area,
            actual_mineral_area=actual_mineral_area,
        )

        # Step 6: Generate grassland breakdown, including spillover adjustments
        grassland_breakdown = self.grassland_breakdown(
            actual_rewetted_area_organic=rewetted_organic_area,
            actual_rewetted_area_mineral_organic=rewetted_mineral_organic_area,
            actual_mineral_area=actual_mineral_area,
            )

        # Step 8: Return results
        return spared_area_breakdown, grassland_breakdown


    def spared_area_breakdown(self, scenario, 
                              intial_spared_area, 
                              actual_rewetted_area_organic, 
                              actual_rewetted_area_mineral_organic,
                              actual_mineral_area):
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

        spared_land_use_dict = self.data_manager_class.get_spared_area_dict()

        # Step 1: Handle wetlands (special case)
        self._log_spared_area(scenario, 
                              "rewet_grassland", 
                              0, 
                              actual_rewetted_area_organic,
                              actual_rewetted_area_mineral_organic)


        # Generate wetland data and add to results
        wetland_data = self.land_dist_class.land_distribution("wetland", None)  # Wetlands don't increase
        result_dict["wetland"] = wetland_data

        # Step 2: Define target shares
        target_areas = {
            land_use: (intial_spared_area * getattr(self.sc_fetch_class, f"get_{land_use}_proportion")(scenario))
            for land_use in spared_land_use_dict.keys()
            if land_use not in ["farmable_condition", "rewetted"]# Exclude "farmable condition" (fallback) & rewetted
        }

        # Step 3: Optimize spared area distribution
        optimizer = LandCoverOptimisation()
        optimised_allocations = optimizer.optimise_mineral_spared_area_distribution(
            mineral_area_available=actual_mineral_area,
            target_areas=target_areas,
        )

        # Step 4: Distribute spared area based on optimised allocations
        for land_use, allocated_area in optimised_allocations.items():
            generated_land_use_data = self.land_dist_class.land_distribution(
                land_use, allocated_area
            )

            self._log_spared_area(scenario, land_use, allocated_area, 0, 0)
            result_dict[land_use] = generated_land_use_data

        return result_dict


    def grassland_breakdown(self, actual_rewetted_area_organic, 
                              actual_rewetted_area_mineral_organic,
                              actual_mineral_area):
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


        generated_land_use_data = self.land_dist_class.grassland_distribution(
            actual_mineral_area, actual_rewetted_area_organic,actual_rewetted_area_mineral_organic, self.total_grassland
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
        #initial_spared_area = self.catchemnt_class.get_total_spared_area(self.total_spared_area, scenario)
        organic_potential = self.catchemnt_class.get_area_with_organic_potential(self.total_spared_area_breakdown, self.total_spared_area, scenario)
        current_organic_area = self.catchemnt_class.get_landuse_area("grassland", self.catchment_name, self.total_grassland) * self.catchemnt_class.get_share_organic("grassland", self.catchment_name, self.total_grassland)
        current_mineral_organic_area = self.catchemnt_class.get_landuse_area("grassland", self.catchment_name, self.total_grassland) * self.catchemnt_class.get_share_organic_mineral("grassland", self.catchment_name, self.total_grassland)

        total_organic_area = current_organic_area + current_mineral_organic_area

        max_organic_spared_total = min(organic_potential, total_organic_area)

        proportion_organic = current_organic_area / total_organic_area
        proportion_mineral_organic = current_mineral_organic_area / total_organic_area

        max_mineral_organic_spared = max_organic_spared_total * proportion_mineral_organic
        max_organic_spared = max_organic_spared_total * proportion_organic

        return {"available_organic":max_organic_spared, "available_mineral_organic": max_mineral_organic_spared}


    def _available_mineral_area(self):
        """
        Computes the available area for mineral soil under a given scenario.

        This internal method calculates the maximum possible area that can be transitioned to mineral soil-based
        land uses, such as wetlands, based on the current mineral and soil areas and scenario-specific
        spared area allocations.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the available mineral area is calculated.
        
        Returns
        -------
        dict
            A dictionary containing the available mineral area.
        """
        mineral_area = self.catchemnt_class.get_landuse_area("grassland", self.catchment_name, self.total_grassland) * self.catchemnt_class.get_share_mineral("grassland", self.catchment_name, self.total_grassland)

        return {"available_mineral":mineral_area}
    

    def _calculate_rewetted_areas(self, scenario, target_rewetted):
        """
        Calculates the areas to be rewetted based on the scenario and target rewetted area.

        This method computes the areas to be rewetted, considering the available organic and mineral-organic areas

        :param scenario: The scenario identifier for which the rewetted areas are calculated.
        :type scenario: int
        :param target_rewetted: The target area to be rewetted.
        :type target_rewetted: float
        :return: A tuple containing the rewetted area, rewetted organic area, and rewetted mineral-organic area.
        :rtype: tuple

        
        """
        organic_areas = self._available_organic_area(scenario)

        max_organic = organic_areas["available_organic"]
        max_mineral_organic = organic_areas["available_mineral_organic"]


        combined_max_organic = max_organic + max_mineral_organic
        rewetted_area = min(combined_max_organic, target_rewetted)

        # Calculate proportions
        proportion_organic = max_organic / combined_max_organic
        proportion_mineral_organic = max_mineral_organic / combined_max_organic

        # Calculate areas
        rewetted_organic_area = rewetted_area * proportion_organic
        rewetted_mineral_organic_area = rewetted_area * proportion_mineral_organic

        return rewetted_area, rewetted_organic_area, rewetted_mineral_organic_area