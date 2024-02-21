"""
Geo Transition Matrix
=====================
This module is dedicated to generating transition matrices that represent land use changes between different land uses over time, 
based on scenario-driven projections. It leverages land cover analysis and data management functionalities to calculate transitions, 
particularly focusing on the dynamics between grassland and other land uses under various scenarios.

Features:
---------
- **Transition Matrix Generation**: Creates matrices that detail the transitions of land use areas from one type to another, 
facilitating scenario analysis and environmental planning.
- **Land Cover Integration**: Utilizes the `LandCover` class for comprehensive future land use area calculations, 
forming the basis of transition matrix computations.

Dependencies:
-------------
- `pandas` for data manipulation and analysis.
- `numpy` for numerical calculations.
- `geo_landcover_assignment.geo_landcover.LandCover` for accessing combined future land use areas.
- `landcover_assignment.landcover_data_manager.DataManager` for accessing land use columns and other data management tasks.

Class Documentation:
--------------------
.. class:: TransitionMatrix(calibration_year, target_year, scenario_inputs_df, total_grassland, total_spared_area, spared_area_breakdown)
   :noindex:

   Manages the creation of transition matrices for land use changes, supporting environmental and land management scenario analysis.

   Parameters:
   - calibration_year (int): The base year from which land use changes are measured.
   - target_year (int): The future year to which land use changes are projected.
   - scenario_inputs_df (pandas.DataFrame): Inputs defining various scenarios for projection.
   - total_grassland (float): The total area of grassland, important for certain transition calculations.
   - total_spared_area (float): The total area of land spared from development or conversion, influencing land use transitions.
   - spared_area_breakdown (pandas.DataFrame): Detailed breakdown of how spared areas are allocated across land uses.

   Methods:
   - create_transition_matrix() -> pandas.DataFrame:
     Generates a transition matrix detailing the changes in land use areas from the calibration year to the target year.
   - _transition_difference(landuse, index, calibration_year, target_year, land_cover_df) -> float:
     Calculates the difference in area for a specific land use between the calibration and target years.
   - _create_transition_frame(land_cover_df) -> pandas.DataFrame:
     Initializes the structure of the transition matrix based on land use columns and scenario data.
"""
import pandas as pd
import numpy as np
from landcover_assignment.geo_landcover_assignment.geo_landcover import LandCover
from landcover_assignment.landcover_data_manager import DataManager


class TransitionMatrix:
    """
    Constructs transition matrices to analyze land use changes between a calibration year and a target year under various scenarios.

    Parameters:
    - calibration_year (int): Base year for calibrating land use changes.
    - target_year (int): Future year for projecting land use changes.
    - scenario_inputs_df (pandas.DataFrame): Contains scenario-specific data inputs.
    - total_grassland (float): Total area of grassland, crucial for certain transition calculations.
    - total_spared_area (float): Total area of land spared from development or conversion.
    - spared_area_breakdown (pandas.DataFrame): Details the allocation of spared areas across different land uses.

    Attributes:
    - land_cover_class (LandCover): Instance of LandCover for accessing combined future land use areas.
    - data_manager_class (DataManager): Instance of DataManager for land use data management.
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
        self.calibration_year = calibration_year
        self.target_year = target_year
        self.land_cover_class = LandCover(
            calibration_year,
            target_year,
            scenario_inputs_df,
            total_grassland,
            total_spared_area,
            spared_area_breakdown
        )
        self.data_manager_class = DataManager(
            calibration_year, target_year
        )

    def create_transition_matrix(self):
        """
        Generates a transition matrix detailing the changes in land use areas from the calibration year to the target year.

        :return: A DataFrame representing the transition matrix with changes in land use areas.
        :rtype: pandas.DataFrame
        """
        calibration_year = self.calibration_year
        target_year = self.target_year
        land_cover_df = self.land_cover_class.combined_future_land_use_area()

        transition_matrix = self._create_transition_frame(land_cover_df)

        for index in transition_matrix.index:
            if index >= 0:
                for land_use in self.data_manager_class.land_use_columns:

                    if land_use == "settlement":
                        continue

                    elif land_use != "grassland":
      
                        transition_diff = self._transition_difference(land_use, index, calibration_year, target_year, land_cover_df)
                        transition_matrix.at[
                            index, "Grassland_to_" + land_use.title()
                        ] = abs(transition_diff)
                    else:
                        transition_diff = self._transition_difference(land_use, index, calibration_year, target_year, land_cover_df)
                        transition_matrix.at[
                            index, "Grassland_to_" + land_use.title()
                        ] = -transition_diff
            else:
                for land_use in self.data_manager_class.land_use_columns:
                    if land_use == "settlement":
                        continue

                    transition_matrix.at[index, "Grassland_to_" + land_use.title()] = 0
                   

        return transition_matrix


    def _transition_difference(self, landuse, index, calibration_year,target_year, land_cover_df):
        """
        Calculates the difference in area for a specific land use between the calibration and target years.

        :param landuse: Specific land use type.
        :type landuse: str
        :param index: Scenario identifier.
        :type index: int
        :param calibration_year: Initial year for transition.
        :type calibration_year: int
        :param target_year: Target year for transition.
        :type targe_year: int
        :param land_cover_df: DataFrame containing land cover data.
        :type land_cover_df: pandas.DataFrame
        :return: The difference in area for the specified land use between years.
        :rtype: float
        """
        transition_diff = (
            land_cover_df.loc[
                (land_cover_df["land_use"] == landuse)
                & (land_cover_df["year"] == calibration_year),
                "area_ha",
            ].item()
            - land_cover_df.loc[
                (land_cover_df["farm_id"] == float(index))
                & (land_cover_df["land_use"] == landuse)
                & (land_cover_df["year"] == target_year),
                "area_ha",
            ].item()
        )
        return transition_diff
    

    def _create_transition_frame(self, land_cover_df):
        """
        Initializes the structure of the transition matrix based on land use columns and scenario data.

        
        :param land_cover_df: DataFrame containing combined future land use areas.
        :type land_cover_df: pandas.DataFrame
        :return: An empty DataFrame structured to represent the transition matrix.
        :rtype: pandas.DataFrame
        """
        col_list = [
            land_use.title() + "_to_" + landuse1.title()
            for land_use in self.data_manager_class.land_use_columns
            for landuse1 in self.data_manager_class.land_use_columns
            if land_use != "settlement" and landuse1 != "settlement"
        ]
        index_df = [int(x) for x in land_cover_df.farm_id.unique()]
        data_df = len(index_df)

        transition_matrix = pd.DataFrame(
            np.zeros((data_df, len(col_list))), index=index_df, columns=col_list
        )
        return transition_matrix
