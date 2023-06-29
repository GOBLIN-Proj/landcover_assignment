from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.landcover import LandCover
import pandas as pd


def main():
    
    baseline = 2020
    target_year = 2050
    scenario_dataframe = pd.read_csv("./data/scenario_dataframe.csv", index_col=0)
    spared_area = pd.read_csv("./data/spared_area.csv", index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    grassland_area = pd.read_csv("./data/total_grassland_area.csv", index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)
    
    transition = TransitionMatrix(baseline, target_year, scenario_dataframe, grassland_area, spared_area)

    transition.create_transition_matrix().to_csv("./data/transition.csv")

    land = LandCover(baseline, target_year, scenario_dataframe, grassland_area, spared_area)

    land.combined_future_land_use_area().to_csv("./data/land_uses.csv")


if __name__ == "__main__":
    main()

