import pandas as pd
import os 
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher

def main():
    path = "./geo_data/"

    sc_data = pd.read_csv(os.path.join(path, "scenario_input_dataframe.csv"), index_col=0)

    f_class = ScenarioDataFetcher(sc_data)

    print(f"wetland: {f_class.get_wetland_proportion(0)}")
    print(f"forest: {f_class.get_forest_proportion(0)}")
    print(f"crop: {f_class.get_cropland_proportion(0)}")
    print(f"conifer: {f_class.get_conifer_proportion(0)}")
    print(f"broadleaf: {f_class.get_broadleaf_proportion(0)}")
    print(f"broadleaf harvest: {f_class.get_broadleaf_harvest_proportion(0)}")
    print(f"conifer harvest: {f_class.get_conifer_harvest_proportion(0)}")
    print(f"conifer thinned: {f_class.get_conifer_thinned_proportion(0)}")
    print(f"afforest end: {f_class.get_afforest_end_year(0)}")
    print(f"Catchment: {f_class.get_catchment_name(0)}")

if __name__ == '__main__':
    main()