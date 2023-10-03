from landcover_assignment.landcover_data_manager import DataManager
import pandas as pd


class Afforestation:
    def __init__(self, calibration_year, target_year, scenario_inputs_df):
        self.data_manager_class = DataManager(
            calibration_year, target_year, scenario_inputs_df
        )

    def gen_cbm_afforestation_dataframe(self, transition_matrix):
        cbm_data = self.cbm_dataframe_structure()

        afforestation_dataframe = self.get_afforest_areas(transition_matrix)

        for i in afforestation_dataframe.index:
            scenario = afforestation_dataframe.at[i, "scenario"]
            future_forest_area = afforestation_dataframe.at[i, "area_ha"]

            if scenario >= 0:
                cbm_data = self.compute_cbm_afforestation(
                    scenario, future_forest_area, cbm_data
                )

        return cbm_data

    def compute_cbm_afforestation(self, sc, future_forest_area, cbm_dataframe):
        cbm_df = self.cbm_dataframe_structure()

        scenario_data = self.data_manager_class.scenario_inputs_df

        grouped_data = scenario_data.drop_duplicates(
            subset=["Scenarios", "Conifer proportion"]
        ).reset_index(drop=True)

        mask = grouped_data["Scenarios"] == sc

        # check future_forest_area
        if future_forest_area < 0:
            raise ValueError(
                f"Invalid Forest amount for scenario {sc}, check scenario grassland area is not greater than baseline year"
            )

        dict_values = {
            "Sitka": grouped_data.loc[mask, "Conifer proportion"].item(),
            "SGB": (1 - grouped_data.loc[mask, "Conifer proportion"].item()),
        }

        for value, key in enumerate(dict_values.keys()):
            cbm_df.loc[value, "scenario"] = sc
            cbm_df.loc[value, "species"] = key
            cbm_df.loc[value, "total_area"] = future_forest_area * dict_values[key]

        frames = [cbm_dataframe, cbm_df]

        output_frame = pd.concat(frames)

        return output_frame

    def get_afforest_areas(self, transition_matrix):
        cols = ["scenario", "area_ha"]

        afforest_df = pd.DataFrame(columns=cols)

        index = 0
        for i in transition_matrix.index:
            afforest_df.at[index, "scenario"] = i if i >= 0 else -1
            afforest_df.at[index, "area_ha"] = transition_matrix.at[
                i, "Grassland_to_Forest"
            ]

            index += 1

        return afforest_df

    def cbm_dataframe_structure(self):
        cbm_default_data = self.data_manager_class.cbm_default_data

        cbm_df = pd.DataFrame(cbm_default_data)

        return cbm_df
