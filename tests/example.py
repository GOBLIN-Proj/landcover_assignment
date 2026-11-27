import os

import pandas as pd

from landcover_assignment.afforestation import Afforestation
from landcover_assignment.landcover import LandCover
from landcover_assignment.transition_matrix import TransitionMatrix


def main():

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    baseline = 2020  # calibration year
    target_year = 2050
    scenario_dataframe = pd.read_csv(os.path.join(path, "scenario_dataframe.csv"), index_col=0)
    spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)

    land = LandCover(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    # land use areas and shares: calibration year, then the target year of each scenario
    print("combined future land use area")
    print(land.combined_future_land_use_area())
    print("#" * 50)

    # where the spared area went, per scenario
    print("spared area log")
    print(land.get_spared_area_log())
    print("#" * 50)

    # the grassland row's parts: herd grassland, spared organic land, other (national balance)
    print("grassland area breakdown")
    print(land.get_grassland_area_breakdown())
    print("#" * 50)

    # transition matrix (Grassland_to_<land use>, in ha)
    transition = TransitionMatrix(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )
    transition_matrix = transition.create_transition_matrix()
    print("transition matrix")
    print(transition_matrix)
    print("#" * 50)

    # afforestation by species and yield class, for cbm_runner
    affor = Afforestation(baseline, target_year, scenario_dataframe, transition_matrix)
    print("afforestation")
    print(affor.gen_cbm_afforestation_dataframe(spared_area_breakdown))


if __name__ == "__main__":
    main()
