from landcover_assignment.geo_landcover_assignment.geo_afforestation import Afforestation
import os
import pandas as pd


def main():
    path = "./geo_data"

    calibration = 2020
    target = 2050

    transition_data = pd.read_csv(os.path.join(path, "transition_matrix.csv"), index_col=0)
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    sc_data = pd.read_csv(os.path.join(path, "scenario_input_dataframe.csv"), index_col=0)

    affor_class = Afforestation(calibration, target, sc_data, transition_data)

    cbm_df = affor_class.cbm_dataframe_structure()

    print(cbm_df)

    print(affor_class.gen_cbm_afforestation_dataframe(spared_area_breakdown))

    affor_class.gen_cbm_afforestation_dataframe(spared_area_breakdown).to_csv(
        os.path.join(path, "geo_cbm_afforestation.csv")
    )


if __name__ == "__main__":
    main()
