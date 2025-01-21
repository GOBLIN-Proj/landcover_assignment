from landcover_assignment.geo_landcover_assignment.geo_landcover import LandCover
from landcover_assignment.geo_landcover_assignment.catchment_landcover import CatchmentLandCover
import pandas as pd
import os


def main():

    path = "../geo_data/"

    baseline = 2020
    target_year = 2050
    scenario_dataframe = pd.read_csv(os.path.join(path, "scenario_input_dataframe.csv"), index_col=0)
    spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)

    land = LandCover(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    catchment = CatchmentLandCover()

    current_area = land.compute_current_area()
    initial_spared_area = spared_area.loc[target_year, 0]

    print("Current area")
    print(current_area)
    print("#"*50)
    print("Avaialble organic area")
    print(land._available_organic_area(0))
    print("#"*50)
    print("total spared area")
    print(catchment.get_total_spared_area(spared_area, 0))
    print("#"*50)
    print("grassland breakdown")
    print(land.grassland_breakdown(0))
    print("#"*50)
    print("spared area breakdown")
    print(land.spared_area_breakdown(0))
    print("#"*50)
    print("combined future land use area")
    print(land.combined_future_land_use_area())
    print("#"*50)
 
    land.combined_future_land_use_area().to_csv(os.path.join(path,"land_uses_0.2.0.csv"))



if __name__ == "__main__":
    main()
