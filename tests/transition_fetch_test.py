import pandas as pd
import os 
from landcover_assignment.resource_manager.transition_data_fetcher import TransitionDataFetcher

def main():
    path = "./geo_data/"

    transition_data = pd.read_csv(os.path.join(path, "transition_matrix.csv"), index_col=0)
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)

    t_class = TransitionDataFetcher(transition_data)

    print(f"Grassland to Forest: {t_class.get_grassland_to_forest_areas()}")
    print("#"*50)
    print(f"Grassland to Grassland: {t_class.get_grassland_to_grassland_areas()}")
    print("#"*50)
    print(f"Grassland to Wetland: {t_class.get_grassland_to_wetland_areas()}")
    print("#"*50)
    print(f"Grassland to Cropland: {t_class.get_grassland_to_cropland_areas()}")
    print("#"*50)
    print(f"Grassland to Landuse Spared Area Breakdown")
    print(t_class.get_grassland_to_landuse_soil_group_area(spared_area_breakdown))

    print("#"*50)
    print(f"Grassland to Forest Soil Group Areas")
    print(t_class.get_grassland_to_forest_soil_group_areas(spared_area_breakdown))

    print("#"*50)
    print(f"Grassland to Wetland Soil Group Areas")
    print(t_class.get_grassland_to_wetland_soil_group_areas(spared_area_breakdown))

    print("#"*50)
    print(f"Grassland to Cropland Soil Group Areas")
    print(t_class.get_grassland_to_cropland_soil_group_areas(spared_area_breakdown))

    print("#"*50)
    print(f"Grassland to farmable condition Soil Group Areas")
    print(t_class.get_grassland_to_farmable_condition_soil_group_areas(spared_area_breakdown))


if __name__ == '__main__':
    main()