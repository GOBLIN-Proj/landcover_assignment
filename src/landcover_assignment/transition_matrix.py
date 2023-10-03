import pandas as pd
import numpy as np
from landcover_assignment.landcover import LandCover
from landcover_assignment.landcover_data_manager import DataManager


class TransitionMatrix:
    def __init__(
        self,
        calibration_year,
        target_year,
        scenario_inputs_df,
        total_grassland,
        total_spared_area,
    ):
        self.calibration_year = calibration_year
        self.target_year = target_year
        self.land_cover_class = LandCover(
            calibration_year,
            target_year,
            scenario_inputs_df,
            total_grassland,
            total_spared_area,
        )
        self.data_manager_class = DataManager(
            calibration_year, target_year, scenario_inputs_df
        )

    def create_transition_matrix(self):
        calibration_year = self.calibration_year
        target_year = self.target_year
        land_cover_df = self.land_cover_class.combined_future_land_use_area()

        col_list = [
            land_use.title() + "_to_" + landuse1.title()
            for land_use in self.data_manager_class.land_use_columns
            for landuse1 in self.data_manager_class.land_use_columns
        ]

        index_df = [int(x) for x in land_cover_df.farm_id.unique()]
        data_df = len(index_df)

        transition_matrix = pd.DataFrame(
            np.zeros((data_df, len(col_list))), index=index_df, columns=col_list
        )

        for index in transition_matrix.index:
            if index >= 0:
                for land_use in self.data_manager_class.land_use_columns:
                    if land_use != "grassland":
                        transition_diff = (
                            land_cover_df.loc[
                                (land_cover_df["land_use"] == land_use)
                                & (land_cover_df["year"] == calibration_year),
                                "area_ha",
                            ].item()
                            - land_cover_df.loc[
                                (land_cover_df["farm_id"] == float(index))
                                & (land_cover_df["land_use"] == land_use)
                                & (land_cover_df["year"] == target_year),
                                "area_ha",
                            ].item()
                        )
                        transition_matrix.at[
                            index, "Grassland_to_" + land_use.title()
                        ] = abs(transition_diff)
                    else:
                        transition_diff = (
                            land_cover_df.loc[
                                (land_cover_df["land_use"] == land_use)
                                & (land_cover_df["year"] == calibration_year),
                                "area_ha",
                            ].item()
                            - land_cover_df.loc[
                                (land_cover_df["farm_id"] == float(index))
                                & (land_cover_df["land_use"] == land_use)
                                & (land_cover_df["year"] == target_year),
                                "area_ha",
                            ].item()
                        )
                        transition_matrix.at[
                            index, "Grassland_to_" + land_use.title()
                        ] = -transition_diff
            else:
                for land_use in self.data_manager_class.land_use_columns:
                    transition_matrix.at[index, "Grassland_to_" + land_use.title()] = 0

        return transition_matrix
