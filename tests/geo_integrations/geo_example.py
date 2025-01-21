import pandas as pd
import os
from landcover_assignment.geo_landcover_assignment.geo_transition_matrix import TransitionMatrix
from landcover_assignment.geo_landcover_assignment.geo_landcover import LandCover
from landcover_assignment.geo_landcover_assignment.geo_afforestation import Afforestation
from grassland_production.geo_grassland_production.geo_grassland_output import GrasslandOutput


def main():

    input_path = "../geo_data/"

    ef_country = "ireland"
    baseline = 2020 #the calibration year
    target_year = 2050 #the target year

    scenario_dataframe = pd.read_csv(os.path.join(input_path, "scenario_input_dataframe.csv"), index_col=0) #scenario inputs 
    scenario_animal_dataframe = pd.read_csv(os.path.join(input_path,"future_animals.csv"))
    baseline_animal_dataframe = pd.read_csv(os.path.join(input_path,"past_animals.csv"))

    #class instance
    grassland = GrasslandOutput(
        ef_country,
        baseline,
        target_year,
        scenario_dataframe,
        scenario_animal_dataframe,
        baseline_animal_dataframe,
    )


    grassland_area = grassland.total_grassland_area()
    spared_area = grassland.total_spared_area()
    spared_area_breakdown = grassland.total_spared_area_breakdown()

    #save to csv
    grassland_area.to_csv(os.path.join(input_path, "grassland_area.csv"))
    spared_area.to_csv(os.path.join(input_path, "spared_area.csv"))
    spared_area_breakdown.to_csv(os.path.join(input_path, "spared_area_breakdown.csv"))



    transition = TransitionMatrix(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    transition_matrix = transition.create_transition_matrix()

    land = LandCover(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    

    affor = Afforestation(baseline, target_year, scenario_dataframe,transition_matrix)

    future_land_use = land.combined_future_land_use_area()

    

    affor_area = affor.gen_cbm_afforestation_dataframe(spared_area_breakdown)

    #save to csv

    affor_area.to_csv(os.path.join(input_path, "afforestation_area.csv"))
    future_land_use.to_csv(os.path.join(input_path, "geo_landuse_generation.csv"))
    transition_matrix.to_csv(os.path.join(input_path, "transition_matrix.csv"))
    land.get_spared_area_log().to_csv(os.path.join(input_path, "spared_area_log.csv"))

    print("COMPLETED")

if __name__ == "__main__":
    main()