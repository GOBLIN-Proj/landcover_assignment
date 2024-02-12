
from landcover_assignment.landcover import LandCover
from landcover_assignment.national_landcover import NationalLandCover
import pandas as pd
import os


def main():

    path = "./data/"
    
    baseline = 2020
    target_year = 2050
    scenario_dataframe = pd.read_csv("./data/scenario_dataframe.csv", index_col=0)
    spared_area = pd.read_csv("./data/spared_area.csv", index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    grassland_area = pd.read_csv("./data/total_grassland_area.csv", index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)
    spared_area_breakdown = pd.read_csv("./data/spared_area_breakdown.csv", index_col=0)



    land = LandCover(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )
    national= NationalLandCover()

    current_area = land.compute_current_area()

    print("Current area")
    print(current_area)
    print("#"*50)
    print("Avaialble organic area")
    print(land._available_organic_area(1))
    print("#"*50)
    print("total spared area")
    print(national.get_total_spared_area(spared_area, 1))
    print("#"*50)
    print("grassland breakdown")
    print(land.grassland_breakdown(1))
    print("#"*50)
    print("spared area breakdown")
    print(land.spared_area_breakdown(1))
    print("#"*50)
    print("combined future land use area")
    print(land.combined_future_land_use_area())
    print("#"*50)
 
    land.combined_future_land_use_area().to_csv(os.path.join(path,"combined_land_uses.csv"))



if __name__ == "__main__":
    main()
