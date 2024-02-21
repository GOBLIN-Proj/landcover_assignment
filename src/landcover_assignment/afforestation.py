"""
Afforestation
======================

This module provides functionalities for processing afforestation Irish national context scenarios, particularly for preparing inputs
for the Carbon Budget Model (CBM). It enables the generation of afforestation dataframes based on spared area
breakdowns, scenario-based afforestation calculations, and structuring data to meet CBM requirements.

Features:
---------

- **Afforestation Class**: Manages afforestation scenario data processing for CBM input preparation, integrating
  various data management and fetching utilities to prepare datasets for environmental modeling and analysis.

Dependencies:
-------------

- **pandas**: Utilized for data manipulation and analysis.
- **DataManager**: Manages land cover and calibration data.
- **ScenarioDataFetcher**: Fetches scenario-specific input data.
- **TransitionDataFetcher**: Handles land cover transition matrices.
- **Loader**: Loads various data resources, including yield mappings.

Usage:
------

This module is intended for use in environmental data processing pipelines, specifically for preparing input data
for the Carbon Budget Model (CBM) in the context of afforestation scenario analysis.

"""

from landcover_assignment.landcover_data_manager import DataManager
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from landcover_assignment.resource_manager.data_loader import Loader
from landcover_assignment.resource_manager.transition_data_fetcher import TransitionDataFetcher
import pandas as pd


class Afforestation:
    """
    Manages afforestation outputs for scenarios and data processing for Carbon Budget Model (CBM) inputs.

    This class is designed to output afforestation data, including generating afforestation scenarios,
    managing transition matrices, and preparing data for CBM simulations based on different scenarios
    and soil group transitions from grassland to forest.

    Parameters:
        calibration_year (int): The base year for calibration data.
        target_year (int): The target year for scenario projections.
        scenario_inputs_df (pd.DataFrame): A DataFrame containing scenario inputs.
        transition_matrix (pd.DataFrame): A DataFrame representing the transition matrix for land cover changes.

    Attributes:
        data_manager_class (DataManager): An instance of DataManager for managing land cover data.
        scenario_data_fetcher (ScenarioDataFetcher): An instance for fetching scenario-specific data.
        transition_data_fetcher (TransitionDataFetcher): An instance for fetching transition data.
        data_loader (Loader): An instance for loading necessary data resources.
        yield_mapping (pd.DataFrame): A DataFrame containing yield mapping for different forest soil groups.
    """
    def __init__(self, calibration_year, target_year, scenario_inputs_df, transition_matrix):
        self.data_manager_class = DataManager(
            calibration_year, target_year
        )
        self.scenario_data_fetcher = ScenarioDataFetcher(scenario_inputs_df)
        self.transition_data_fetcher = TransitionDataFetcher(transition_matrix)
        self.data_loader = Loader()
        self.yield_mapping = self.data_loader.forest_soil_yield_mapping()


    def gen_cbm_afforestation_dataframe(self, spared_area_breakdown):
        """
        Generates a DataFrame structured for CBM inputs, detailing afforestation areas by scenario.

        Processes spared area breakdown to determine afforestation areas transitioning from grassland
        to forest under different scenarios. This method structures the data to be compatible with CBM
        simulation requirements.

        :param spared_area_breakdown: A DataFrame containing the breakdown of spared areas by scenario.
        :type spared_area_breakdown: pd.DataFrame
        :return: A DataFrame structured for CBM afforestation inputs.
        :rtype: pd.DataFrame
        """
        cbm_data = self.cbm_dataframe_structure()

        afforestation_dataframe = self.transition_data_fetcher.get_grassland_to_forest_soil_group_areas(spared_area_breakdown)

        for i in afforestation_dataframe.index:
            scenario = afforestation_dataframe.at[i, "scenario"]
            future_forest_area = afforestation_dataframe.at[i, "Grassland_to_Forest"]
            soil_group = afforestation_dataframe.at[i, "soil_group"]

            if scenario >= 0:
                cbm_data = self.compute_cbm_afforestation(
                    scenario, soil_group, future_forest_area, cbm_data
                )

        # Reset the index of cbm_data before returning it
        cbm_data_reset = cbm_data.reset_index(drop=True)

        return cbm_data_reset


    def compute_cbm_afforestation(self, sc, soil_group, future_forest_area, cbm_dataframe):
        """
        Computes afforestation outputs for a specific scenario and updates the CBM DataFrame.

        This method calculates the distribution of future forest areas between different species
        and yield classes based on the soil group. It updates and returns the CBM DataFrame with
        the new data.

        :param sc: The scenario identifier.
        :type sc: int
        :param soil_group: The soil group identifier.
        :type soil_group: int
        :param future_forest_area: The future forest area for the scenario and soil group.
        :type future_forest_area: float
        :param cbm_dataframe: The existing CBM DataFrame to be updated.
        :type cbm_dataframe: pd.DataFrame
        :return: The updated CBM DataFrame with the new afforestation data.
        :rtype: pd.DataFrame
        :raises ValueError: If the future forest area is less than 0.
        """
        # check future_forest_area
        if future_forest_area < 0:
            raise ValueError(
                f"Invalid Forest amount for scenario {sc}, check scenario grassland area is not greater than baseline year"
            )

        dict_values = {
            "Sitka": self.scenario_data_fetcher.get_conifer_proportion(sc),
            "SGB": (1 - self.scenario_data_fetcher.get_conifer_proportion(sc)),
        }

        sitka_yield_mask = (self.yield_mapping["species"] == "Sitka") & (self.yield_mapping["soil_group"]==soil_group)
        sgb_yield_mask = (self.yield_mapping["species"] == "SGB") & (self.yield_mapping["soil_group"]==soil_group)

        yield_dict_values = {
            "Sitka": self.yield_mapping.loc[sitka_yield_mask, "yield_class"].item(),
            "SGB": self.yield_mapping.loc[sgb_yield_mask, "yield_class"].item(),
        }

        data = []

        for value, key in enumerate(dict_values.keys()):
            row ={
                "scenario": sc,
                "species":key,
                "yield_class": yield_dict_values[key],
                "total_area": future_forest_area * dict_values[key]
            }

            data.append(row)
        

        frames = [cbm_dataframe, pd.DataFrame(data)]

        output_frame = pd.concat(frames)

        return output_frame
    

    def cbm_dataframe_structure(self):
        """
        Initializes the structure of the CBM DataFrame based on default data.

        This method creates a new DataFrame structured for CBM inputs using default data
        from the data manager class. It serves as the initial template for accumulating
        afforestation scenario data.

        :return: A DataFrame structured for CBM afforestation inputs.
        :rtype: pd.DataFrame
        """
        cbm_default_data = self.data_manager_class.cbm_default_data

        cbm_df = pd.DataFrame(cbm_default_data)

        return cbm_df
