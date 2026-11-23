"""Shared helpers for the characterisation tests: paths, input loaders and pipeline runners.

The paths are absolute, so the tests run from any folder. No test writes into a data folder.

The optimiser uses the open-source HiGHS solver by default (Pyomo "highs"); no solver switch is needed.
"""
import io
from pathlib import Path

import pandas as pd

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parent
GOLDEN = TESTS / "golden"
CAL, TARGET = 2020, 2050


def load_national():
    path = TESTS / "data"
    sc = pd.read_csv(path / "scenario_dataframe.csv", index_col=0)
    spared = pd.read_csv(path / "spared_area.csv", index_col=0)
    spared.columns = spared.columns.astype(int)
    breakdown = pd.read_csv(path / "spared_area_breakdown.csv", index_col=0)
    grass = pd.read_csv(path / "total_grassland_area.csv", index_col=0)
    grass.columns = grass.columns.astype(int)
    return sc, grass, spared, breakdown


def load_geo():
    path = TESTS / "geo_data"
    sc = pd.read_csv(path / "scenario_input_dataframe.csv", index_col=0)
    spared = pd.read_csv(path / "spared_area.csv", index_col=0)
    spared.columns = spared.columns.astype(int)
    breakdown = pd.read_csv(path / "spared_area_breakdown.csv", index_col=0)
    grass = pd.read_csv(path / "grassland_area.csv", index_col=0)
    grass.columns = grass.columns.astype(int)
    return sc, grass, spared, breakdown


def load_goblin_lite():
    """goblin_lite's integration inputs, read as goblin_lite's test reads them (no index_col, string columns)."""
    path = TESTS / "data" / "goblin_lite_input"
    return tuple(pd.read_csv(path / f) for f in (
        "scenario_input_dataframe.csv", "total_grassland_area.csv", "total_spared_area.csv",
        "total_spared_area_by_soil_group.csv"))


CASES = {"national": ("national", load_national), "geo": ("geo", load_geo),
         "goblin_lite": ("national", load_goblin_lite)}


def classes(tree):
    if tree == "national":
        from landcover_assignment.afforestation import Afforestation
        from landcover_assignment.landcover import LandCover
        from landcover_assignment.transition_matrix import TransitionMatrix
    else:
        from landcover_assignment.geo_landcover_assignment.geo_afforestation import Afforestation
        from landcover_assignment.geo_landcover_assignment.geo_landcover import LandCover
        from landcover_assignment.geo_landcover_assignment.geo_transition_matrix import TransitionMatrix
    return LandCover, TransitionMatrix, Afforestation


_CACHE = {}


def run_case(name):
    """Run the full pipeline for one case, the way goblin_lite and geo_goblin_py call it. The result is cached."""
    if name not in _CACHE:
        tree, loader = CASES[name]
        LandCover, TransitionMatrix, Afforestation = classes(tree)
        sc, grass, spared, breakdown = loader()
        land = LandCover(CAL, TARGET, sc, grass, spared, breakdown)
        landuse = land.combined_future_land_use_area()
        log = land.get_spared_area_log()
        tm = TransitionMatrix(CAL, TARGET, sc, grass, spared, breakdown).create_transition_matrix()
        affor = Afforestation(CAL, TARGET, sc, tm).gen_cbm_afforestation_dataframe(breakdown)
        _CACHE[name] = {"landuse": landuse, "transition_matrix": tm, "afforestation": affor, "spared_area_log": log}
    return _CACHE[name]


def roundtrip(df):
    """Write to CSV and read back, as the golden files were stored, so the two compare like for like."""
    buf = io.StringIO()
    df.to_csv(buf)
    buf.seek(0)
    return pd.read_csv(buf, index_col=0)
