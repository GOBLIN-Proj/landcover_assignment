from landcover_assignment.afforestation import Afforestation
import os
import pandas as pd


def main():
    path = "./data"

    calibration = 2020
    target = 2050

    area = 1000

    sc_data = pd.read_csv(os.path.join(path, "scenario_dataframe.csv"))

    transition_matrix = pd.read_csv(os.path.join(path, "transition.csv"), index_col=0)

    affor_class = Afforestation(calibration, target, sc_data)

    cbm_df = affor_class.cbm_dataframe_structure()

    print(affor_class.compute_cbm_afforestation(0, area, cbm_df))

    print(affor_class.gen_cbm_afforestation_dataframe(transition_matrix))


if __name__ == "__main__":
    main()
