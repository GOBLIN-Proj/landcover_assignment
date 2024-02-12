import pandas as pd
import os
from landcover_assignment.transition_matrix import TransitionMatrix

def main():

    path = "./data/"

    baseline = 2020
    target_year = 2050
    scenario_dataframe = pd.read_csv(os.path.join(path, "scenario_dataframe.csv"), index_col=0)
    spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)


    transition = TransitionMatrix(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    print(transition.create_transition_matrix())

    print(transition.create_transition_matrix().to_csv(os.path.join(path,"transition_matrix.csv")))

if __name__ == "__main__":
    main()