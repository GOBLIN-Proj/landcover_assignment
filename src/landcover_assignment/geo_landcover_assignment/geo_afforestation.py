"""
Geo Afforestation
=================
Afforestation input for the Carbon Budget Model (cbm_runner) in the catchment tree.

It is the national :class:`landcover_assignment.afforestation.Afforestation`, except that the scenario table is
validated when the class is created (``ScenarioDataFetcher(..., validate_on_init=True)``). The import path and the
constructor are unchanged: ``Afforestation(calibration_year, target_year, scenario_inputs_df, transition_matrix)``.
"""
from landcover_assignment.afforestation import Afforestation as _NationalAfforestation


class Afforestation(_NationalAfforestation):
    """
    Afforestation input for cbm_runner from a catchment transition matrix and spared-area breakdown. See
    :class:`landcover_assignment.afforestation.Afforestation` for the methods and the output table.

    :param calibration_year: The calibration year.
    :param target_year: The target year.
    :param scenario_inputs_df: The scenario input table (validated on construction).
    :param transition_matrix: The catchment transition matrix (``geo_transition_matrix``).
    """

    validate_scenarios = True
