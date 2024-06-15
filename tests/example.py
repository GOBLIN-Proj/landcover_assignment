import pandas as pd
import os
from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.landcover import LandCover
from landcover_assignment.afforestation import Afforestation

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

    land = LandCover(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    
    #create_combined_future_land_use_area
    print("combined future land use area")
    print(land.combined_future_land_use_area())
    land.combined_future_land_use_area().to_csv(os.path.join(path,"combined_future_land_use_area_results.csv"))
    print("#"*50)

    #create_transition_matrix
    transition_matrix = transition.create_transition_matrix()
    print(transition_matrix)
    print("#"*50)
    transition_matrix.to_csv(os.path.join(path,"transition_matrix_results.csv"))

    #create afforestation 
    affor = Afforestation(baseline, target_year, scenario_dataframe, transition_matrix)
    print(affor.gen_cbm_afforestation_dataframe(spared_area_breakdown))

if __name__ == "__main__":
    main()