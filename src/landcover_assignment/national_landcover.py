"""
National Land Cover
===================
National areas and soil, peat and burnt shares for each land use, read from the package database (via ``Loader``).

Each land use's calibration-year row is its area plus 17 share columns. Every share is one database column divided by
the land use's total area (``total_kha``), applied to the land uses in ``SHARE_SOURCES`` and 0 for the rest.

Forest is different (decision D6a): it mirrors cbm_runner 0.6.1, whose historic forest is aligned with the NID and
forest expert judgement (package database ``managed_forest_data`` and ``forest_fire_rate``, derived from cbm_runner's
disturbance events):

- area = cbm_runner managed forest, FM (present before 1990) + AF (planted since 1990), in that year;
- ``share_organic`` / ``share_organic_mineral`` = the NID 2026 drained N-poor / N-rich hectares of the calibration year
  (Tables 6.7 + 6.15, decision D3) / area. The open area and roads that CBM doesn't model are not emitting (as in the
  NID), and AF planting after the calibration year is on mineral soil, so the drained hectares stay fixed and
  ``share_mineral`` is the rest;
- ``share_burnt`` = cbm_runner FM + AF fire in that year / area.

Target-year forest rows (:meth:`NationalLandCover.get_forest_target_row`) add the scenario's afforestation to the
area, and cbm_runner's scenario fire on it (rate x afforestation) to the burnt area.

Burnt area of the other land uses (decision D6b): calibration-year rows take that year's inventory burnt area / area
(CRF 2024; 2023-2024 derived, see docs/data_sources.md). Target-year rows take the 3-year rate over
``BURNT_RATE_YEARS`` (:meth:`NationalLandCover.get_burnt_rate`: sum of burnt area / sum of area), on the whole row,
so land a scenario adds to wetland or cropland burns at the same rate. Settlement and farmable_condition: 0.

Peat extraction (decision D10, a modelling assumption): industrial and domestic extraction phase out linearly from
the calibration year to 0 in ``PEAT_PHASE_OUT_YEAR`` (2040). In target-year wetland rows the stopped share moves to
the matching rewetted share (``PEAT_PHASE_OUT``); the wetland area and every other share are unchanged
(:meth:`NationalLandCover.get_peat_extraction_remaining`, docs/peat_extraction.md). Calibration-year rows stay the
inventory.

The grassland area is not a database area: it is grassland_production's herd-derived area plus the national balance
(see :meth:`NationalLandCover.get_grassland_balance_area` and docs/grassland_area.md).
"""
import logging

import pandas as pd

from landcover_assignment._deprecation import renamed_method
from landcover_assignment.resource_manager.data_loader import Loader

logger = logging.getLogger(__name__)

LAND_USES = ("forest", "wetland", "cropland", "grassland", "settlement")
ALL = LAND_USES

# share column: (land uses it applies to (0 for the others), database column divided by total_kha)
SHARE_SOURCES = {
    "share_mineral": (ALL, "mineral_kha"),
    "share_organic": (ALL, "organic_kha"),                       # forest: organic_emitting_kha (drained N-poor)
    "share_organic_mineral": (("forest",), "organo_mineral_emitting_kha"),
    "share_drained_rich_organic": (("grassland",), "drained_rich_organic_kha"),
    "share_drained_poor_organic": (("grassland",), "drained_poor_organic_kha"),
    "share_rewetted_rich_organic": (("grassland",), "rewetted_rich_organic_kha"),
    "share_rewetted_poor_organic": (("grassland",), "rewetted_poor_organic_kha"),
    "share_rewetted_in_organic": (("wetland",), "rewetted_organic_kha"),
    "share_rewetted_in_mineral": (("wetland",), "rewetted_mineral_kha"),
    "share_domestic_peat_extraction": (("wetland",), "domestic_peat_extraction_kha"),
    "share_industrial_peat_extraction": (("wetland",), "industrial_peat_extraction_kha"),
    "share_rewetted_domestic_peat_extraction": (("wetland",), "rewetted_domestic_peat_kha"),
    "share_rewetted_industrial_peat_extraction": (("wetland",), "rewetted_industrial_peat_kha"),
    "share_near_natural_wetland": (("wetland",), "near_natural_wetland_kha"),
    "share_unmanaged_wetland": (("wetland",), "unmanaged_wetland_kha"),
    "share_burnt": (ALL, "burnt_kha"),
}
# Decision D6b: target-year rows of the non-forest land uses burn at the rate over these years (first, last).
BURNT_RATE_YEARS = (2022, 2024)
# Decision D10 (modelling assumption, owner 2026-11-27): peat extraction ends in this year. Each extraction share in a
# target-year wetland row phases out linearly from the calibration year and moves to its rewetted share.
PEAT_PHASE_OUT_YEAR = 2040
PEAT_PHASE_OUT = {
    "share_industrial_peat_extraction": "share_rewetted_industrial_peat_extraction",
    "share_domestic_peat_extraction": "share_rewetted_domestic_peat_extraction",
}
# Order of the columns in a land use's row.
ROW_COLUMNS = ["area_ha", "share_mineral", "share_organic", "share_organic_mineral", "share_drained_rich_organic",
               "share_drained_poor_organic", "share_rewetted_rich_organic", "share_rewetted_poor_organic",
               "share_rewetted_in_organic", "share_rewetted_in_mineral", "share_domestic_peat_extraction",
               "share_industrial_peat_extraction", "share_rewetted_domestic_peat_extraction",
               "share_rewetted_industrial_peat_extraction", "share_near_natural_wetland", "share_unmanaged_wetland",
               "share_burnt"]
# Shares that the public get_share_* getters return for the fallback land use, farmable_condition.
FARMABLE_SHARES = {"share_mineral": 1.0}
# Shares whose public getter returns 0 for any land use outside SHARE_SOURCES (no validation): the grassland- and
# wetland-only shares. The others raise ValueError for an unknown land use.
SPECIFIC_SHARES = {k for k, (uses, _) in SHARE_SOURCES.items() if uses in (("grassland",), ("wetland",))}


class NationalLandCover:
    """
    National land use areas and shares for a year, from the package database.

    The rows are built from ``SHARE_SOURCES`` (see the module docstring). The ``get_share_*`` and ``get_national_*``
    methods are thin wrappers over :meth:`get_share` and :meth:`get_national_share`.
    """

    def __init__(self):
        self.loader = Loader()
        self.national_areas_cache = {}
        self._managed_forest = None
        self._forest_fire_rate = None
        self.methods = {
            "forest": self.get_forest_data,
            "wetland": self.get_peat_data,
            "cropland": self.get_crop_data,
            "grassland": self.get_grassland_data,
            "settlement": self.get_settlement_data,
        }
        self.national_areas = {
            "forest": self.loader.national_forest_areas,
            "cropland": self.loader.national_cropland_areas,
            "wetland": self.loader.national_wetland_areas,
            "settlement": self.loader.national_settlement_areas,
            "grassland": self.loader.national_grassland_areas,
        }

    def _get_cached_data(self, landuse):
        """The database table for a land use (cached), indexed by year. Raises ValueError for an unknown land use."""
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        if landuse not in self.national_areas_cache:
            self.national_areas_cache[landuse] = self.national_areas[landuse]()
        return self.national_areas_cache[landuse].copy()

    # ----------------------------------------------------------------------------------------------- national shares
    def get_national_share(self, share, landuse, year):
        """
        A share of a land use's national area in a year, from ``SHARE_SOURCES``.

        :param share: A share column, e.g. ``"share_drained_rich_organic"``.
        :param landuse: forest, wetland, cropland, grassland or settlement.
        :param year: The year.
        :return: The share (0.0 if the share doesn't apply to this land use).
        :raises ValueError: for an unknown land use (unless the share applies to one land use only).
        """
        uses, column = SHARE_SOURCES[share]
        if len(uses) == 1 and landuse not in uses:
            return 0.0
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        if landuse not in uses:
            return 0.0
        if landuse == "forest":
            return self._forest_share(share, year, year)
        data = self._get_cached_data(landuse)
        return data.loc[year, column].item() / data.loc[year, "total_kha"].item()

    def get_national_area(self, landuse, year):
        """
        A land use's national area (ha) in a year, from the package database.

        :raises ValueError: for an unknown land use, or a year that isn't in the database.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        if landuse == "forest":
            return self.get_managed_forest_area(year)
        data = self._get_cached_data(landuse)
        if year not in data.index:
            raise ValueError(f"Year {year} not found for land use type {landuse}")
        if "total_kha" not in data.columns:
            raise ValueError(f"'total_kha' column missing for land use type {landuse}")
        return data.loc[year, "total_kha"].item()

    # --------------------------------------------------------------------------- forest: cbm_runner mirror (D6a)
    def _managed(self, year, column):
        if self._managed_forest is None:
            self._managed_forest = self.loader.managed_forest_areas()
        if year not in self._managed_forest.index or pd.isna(self._managed_forest.loc[year, column]):
            raise ValueError(f"No cbm_runner managed forest {column} for {year} (FM area from 2016, FM fire from 2017)")
        return self._managed_forest.loc[year, column].item()

    def get_managed_forest_area(self, year):
        """cbm_runner managed forest area (ha), FM + AF, in a year (2016-2070). Decision D6a."""
        return self._managed(year, "total_ha")

    def get_managed_forest_burnt_area(self, year):
        """cbm_runner FM + AF forest fire (ha) in a year (2017-2070). Decision D6a."""
        return self._managed(year, "burnt_ha")

    def get_managed_forest_change(self, calibration_year, target_year):
        """Change in cbm_runner managed forest (ha) between two years: AF baseline planting less FM deforestation. It is
        in every scenario's forest row, and it is not a transition from grassland."""
        return self.get_managed_forest_area(target_year) - self.get_managed_forest_area(calibration_year)

    def get_forest_fire_rate(self):
        """cbm_runner's scenario forest fire rate (burnt ha per ha of scenario afforestation per year):
        (mean annual FM fire + mean annual AF fire) / (FM + AF inventory area). Decision D6a."""
        if self._forest_fire_rate is None:
            self._forest_fire_rate = self.loader.forest_fire_rate()["rate_per_year"].item()
        return self._forest_fire_rate

    def _forest_drained_ha(self, calibration_year):
        """NID 2026 drained N-poor and N-rich forest hectares in the calibration year (decision D3)."""
        data = self._get_cached_data("forest")
        return (data.loc[calibration_year, "organic_emitting_kha"].item(),
                data.loc[calibration_year, "organo_mineral_emitting_kha"].item())

    def _forest_share(self, share, calibration_year, year, scenario_afforestation=0.0):
        """A forest share for ``year`` (the calibration year, or a target year with the scenario's afforestation)."""
        return self.get_forest_target_row(calibration_year, year, scenario_afforestation)[share]

    def get_forest_target_row(self, calibration_year, target_year, scenario_afforestation):
        """
        The national forest row in ``target_year`` for a scenario that afforests ``scenario_afforestation`` ha
        (decision D6a, mirroring cbm_runner 0.6.1). With ``target_year == calibration_year`` and no afforestation it
        is the calibration-year row.

        - area_ha = managed forest (FM + AF) in the target year + scenario afforestation;
        - drained N-poor / N-rich hectares = the NID calibration-year hectares (fixed; all new forest is mineral);
        - burnt ha = FM + AF fire in the target year + scenario fire rate x scenario afforestation (cbm_runner plants
          the scenario's afforestation by its afforestation end year and burns rate x the area planted so far).

        :return: dict with ``area_ha`` and every share in ``ROW_COLUMNS`` (0 for shares that don't apply to forest).
        """
        area = self.get_managed_forest_area(target_year) + scenario_afforestation
        poor, rich = self._forest_drained_ha(calibration_year)
        burnt = self.get_managed_forest_burnt_area(target_year) + self.get_forest_fire_rate() * scenario_afforestation
        row = {column: 0.0 for column in ROW_COLUMNS}
        row.update(area_ha=area, share_organic=poor / area, share_organic_mineral=rich / area,
                   share_mineral=1.0 - (poor + rich) / area, share_burnt=burnt / area)
        return row

    def get_national_burnt_average(self, landuse):
        """Burnt area as a share of the land use's area, over all years in the database that have a burnt area."""
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        data = self.national_areas[landuse]()
        data = data[data["burnt_kha"].notna()]
        return data["burnt_kha"].sum() / data["total_kha"].sum()

    def get_burnt_rate(self, landuse):
        """
        Burnt area per ha in a target year, for the non-forest land uses (decision D6b): the sum of the burnt area
        over ``BURNT_RATE_YEARS`` / the sum of the land use's area over the same years. 0 for farmable_condition.

        :raises ValueError: for forest (its target-year burnt area is cbm_runner's, see
            :meth:`get_forest_target_row`) and for an unknown land use.
        """
        if landuse == "farmable_condition":
            return 0.0
        if landuse == "forest":
            raise ValueError("Forest burnt area in a target year is cbm_runner's fire: use get_forest_target_row")
        data = self._get_cached_data(landuse).loc[BURNT_RATE_YEARS[0]:BURNT_RATE_YEARS[1]]
        if len(data) != BURNT_RATE_YEARS[1] - BURNT_RATE_YEARS[0] + 1 or data["burnt_kha"].isna().any():
            raise ValueError(f"No burnt area for {landuse} in every year {BURNT_RATE_YEARS[0]}-{BURNT_RATE_YEARS[1]}")
        return data["burnt_kha"].sum() / data["total_kha"].sum()

    @staticmethod
    def get_peat_extraction_remaining(calibration_year, target_year):
        """
        Share of the calibration year's peat extraction still going on in the target year (decision D10): a straight
        line from 1 in the calibration year to 0 in ``PEAT_PHASE_OUT_YEAR``, and 0 after it (also 0 when the
        calibration year is after ``PEAT_PHASE_OUT_YEAR``).

        :param calibration_year: The calibration year.
        :param target_year: The target year.
        :return: A fraction between 0 and 1.
        :rtype: float
        """
        if calibration_year >= PEAT_PHASE_OUT_YEAR:
            return 0.0
        remaining = (PEAT_PHASE_OUT_YEAR - target_year) / (PEAT_PHASE_OUT_YEAR - calibration_year)
        return min(1.0, max(0.0, remaining))

    def get_national_mineral(self, landuse, year):
        return self.get_national_share("share_mineral", landuse, year)

    def get_national_organic(self, landuse, year):
        return self.get_national_share("share_organic", landuse, year)

    def get_national_organic_mineral(self, landuse, year):
        return self.get_national_share("share_organic_mineral", landuse, year)

    def get_national_rich_drained_organic_grassland(self, landuse, year):
        return self.get_national_share("share_drained_rich_organic", landuse, year)

    get_national_rich_drained_orgainc_grassland = renamed_method(  # DEPRECATED_NAME
        "get_national_rich_drained_organic_grassland", "get_national_rich_drained_orgainc_grassland")  # DEPRECATED_NAME

    def get_national_poor_drained_organic_grassland(self, landuse, year):
        return self.get_national_share("share_drained_poor_organic", landuse, year)

    def get_national_rich_rewetted_organic_grassland(self, landuse, year):
        return self.get_national_share("share_rewetted_rich_organic", landuse, year)

    def get_national_poor_rewetted_organic_grassland(self, landuse, year):
        return self.get_national_share("share_rewetted_poor_organic", landuse, year)

    def get_national_domestic_peat_extraction(self, landuse, year):
        return self.get_national_share("share_domestic_peat_extraction", landuse, year)

    def get_national_industrial_peat_extraction(self, landuse, year):
        return self.get_national_share("share_industrial_peat_extraction", landuse, year)

    def get_national_rewetted_domestic_peat(self, landuse, year):
        return self.get_national_share("share_rewetted_domestic_peat_extraction", landuse, year)

    def get_national_rewetted_industrial_peat(self, landuse, year):
        return self.get_national_share("share_rewetted_industrial_peat_extraction", landuse, year)

    def get_national_rewetted_in_organic(self, landuse, year):
        return self.get_national_share("share_rewetted_in_organic", landuse, year)

    def get_national_rewetted_in_mineral(self, landuse, year):
        return self.get_national_share("share_rewetted_in_mineral", landuse, year)

    def get_national_unmanaged_wetland(self, landuse, year):
        return self.get_national_share("share_unmanaged_wetland", landuse, year)

    def get_national_near_natural_wetland(self, landuse, year):
        return self.get_national_share("share_near_natural_wetland", landuse, year)

    def get_national_burn(self, landuse, year):
        return self.get_national_share("share_burnt", landuse, year)

    # ------------------------------------------------------------------------------------------------ land use rows
    def get_landuse_data(self, landuse, year, total_grassland_area=None):
        """
        A land use's row: its area (ha) and the 17 shares, as a one-row DataFrame (columns ``ROW_COLUMNS``).

        :param landuse: forest, wetland, cropland, grassland or settlement.
        :param year: The year (the calibration year).
        :param total_grassland_area: grassland_production's total_grassland input (grassland only).
        """
        if landuse == "grassland":
            # Herd-derived grassland (grassland_production) plus the national balance, which the herd doesn't need.
            # The balance is never available to be spared (spareable areas use get_derived_national_grassland_area
            # only). See docs/grassland_area.md.
            area = (self.get_derived_national_grassland_area(total_grassland_area)
                    + self.get_grassland_balance_area(year, total_grassland_area))
        else:
            area = self.get_national_area(landuse, year)
        row = {"area_ha": area}
        row.update({share: self.get_national_share(share, landuse, year) for share in ROW_COLUMNS[1:]})
        return pd.DataFrame([row])

    def get_forest_data(self, year):
        return self.get_landuse_data("forest", year)

    def get_peat_data(self, year):
        return self.get_landuse_data("wetland", year)

    def get_crop_data(self, year):
        return self.get_landuse_data("cropland", year)

    def get_grassland_data(self, year, total_grassland_area):
        return self.get_landuse_data("grassland", year, total_grassland_area)

    def get_settlement_data(self, year):
        return self.get_landuse_data("settlement", year)

    # ---------------------------------------------------------------------------- shares for the land-use table
    def get_landuse_area(self, landuse, year, grassland_area=None):
        """A land use's area (ha) in the land-use table; 0 for farmable_condition."""
        if landuse == "farmable_condition":
            return 0.0
        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        return self.get_landuse_data(landuse, year, grassland_area)["area_ha"].iloc[0]

    def get_share(self, share, landuse, year, grassland_area=None):
        """
        A share for the land-use table: as :meth:`get_national_share`, plus the fallback land use
        ``farmable_condition`` (all mineral, nothing else).

        :param grassland_area: grassland_production's total_grassland input. Required for grassland, as before.
        :raises ValueError: for an unknown land use, or grassland without ``grassland_area``.
        """
        if share in SPECIFIC_SHARES and landuse not in SHARE_SOURCES[share][0]:
            return 0.0
        if landuse == "farmable_condition":
            return FARMABLE_SHARES.get(share, 0.0)
        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        if landuse == "grassland" and grassland_area is None:
            raise ValueError(f"Grassland area must be provided for land use: {landuse}")
        return self.get_national_share(share, landuse, year)

    def get_share_mineral(self, landuse, year, grassland_area=None):
        return self.get_share("share_mineral", landuse, year, grassland_area)

    def get_share_organic(self, landuse, year, grassland_area=None):
        return self.get_share("share_organic", landuse, year, grassland_area)

    def get_share_organic_mineral(self, landuse, year, grassland_area=None):
        return self.get_share("share_organic_mineral", landuse, year, grassland_area)

    def get_share_drained_rich_organic_grassland(self, landuse, year, grassland_area=None):
        return self.get_share("share_drained_rich_organic", landuse, year, grassland_area)

    def get_share_drained_poor_organic_grassland(self, landuse, year, grassland_area=None):
        return self.get_share("share_drained_poor_organic", landuse, year, grassland_area)

    def get_share_rewetted_rich_in_organic_grassland(self, landuse, year, grassland_area=None):
        return self.get_share("share_rewetted_rich_organic", landuse, year, grassland_area)

    def get_share_rewetted_poor_in_organic_grassland(self, landuse, year, grassland_area=None):
        return self.get_share("share_rewetted_poor_organic", landuse, year, grassland_area)

    def get_share_rewetted_in_organic(self, landuse, year, grassland_area=None):
        return self.get_share("share_rewetted_in_organic", landuse, year, grassland_area)

    def get_share_rewetted_in_mineral(self, landuse, year, grassland_area=None):
        return self.get_share("share_rewetted_in_mineral", landuse, year, grassland_area)

    def get_share_domestic_peat_extraction(self, landuse, year):
        return self.get_share("share_domestic_peat_extraction", landuse, year)

    def get_share_industrial_peat_extraction(self, landuse, year):
        return self.get_share("share_industrial_peat_extraction", landuse, year)

    def get_share_rewetted_domestic_peat_extraction(self, landuse, year):
        return self.get_share("share_rewetted_domestic_peat_extraction", landuse, year)

    def get_share_rewetted_industrial_peat_extraction(self, landuse, year):
        return self.get_share("share_rewetted_industrial_peat_extraction", landuse, year)

    def get_share_near_natural_wetland(self, landuse, year):
        return self.get_share("share_near_natural_wetland", landuse, year)

    def get_share_unmanaged_wetland(self, landuse, year):
        return self.get_share("share_unmanaged_wetland", landuse, year)

    def get_share_burnt(self, landuse, year, grassland_area=None):
        return self.get_share("share_burnt", landuse, year, grassland_area)

    def get_land_shares(self, key, land_use, year):
        """A share (``key``, a ``ROW_COLUMNS`` share) of a non-grassland land use; see :meth:`get_share`."""
        if key not in SHARE_SOURCES:
            raise KeyError(key)
        return self.get_share(key, land_use, year)

    def get_grassland_shares(self, key, year, grassland_area):
        """
        A grassland share. ``key`` is a share column; the rewet-status shares are also accepted as
        ``share_rewetted_rich_in_organic`` / ``share_rewetted_poor_in_organic``.
        """
        aliases = {"share_rewetted_rich_in_organic": "share_rewetted_rich_organic",
                   "share_rewetted_poor_in_organic": "share_rewetted_poor_organic"}
        allowed = {"share_mineral", "share_organic", "share_drained_rich_organic", "share_drained_poor_organic",
                   "share_organic_mineral", "share_burnt", *aliases}
        if key not in allowed:
            raise KeyError(key)
        return self.get_share(aliases.get(key, key), "grassland", year, grassland_area)

    # ------------------------------------------------------------------------ grassland and spared area (inputs)
    def get_total_spared_area(self, spared_area, sc):
        """
        Retrieves the total spared area for a specific scenario from a spared area dataset.

        Parameters
        ----------
        spared_area : pandas.DataFrame
            A DataFrame containing spared area data.
        sc : str or int
            The scenario.
        
        Returns
        -------
        float
            The total spared area.
        
        Raises
        ------
        ValueError
            If the scenario is not found in the spared area dataset, or if its column holds more than one non-zero
            value.

        Notes
        -----
        The scenario column holds the target year's spared area and zeros elsewhere. It is read as "the one non-zero
        value" rather than by year, because goblin_lite passes the table with the years in a column (``index``),
        not as the index. A column with no non-zero value is a scenario with no spared area: 0.0 (finding 4).
        """
        for col in (str(sc), int(sc)):
            if col in spared_area.columns:
                values = spared_area.loc[spared_area[col] != 0, col]
                if len(values) == 0:
                    return 0.0
                if len(values) > 1:
                    raise ValueError(f"Scenario {sc}: spared_area has more than one non-zero value "
                                     f"({len(values)}); expected only the target year's spared area.")
                return float(values.item())
        raise ValueError(f"Scenario {sc} not found in spared_area.")


    def get_grassland_balance_area(self, year, total_grassland_area):
        """
        National grassland that the herd doesn't need: the national grassland area minus the herd-derived grassland
        area, in ``year`` (the calibration year). It is added to the grassland row so that its emissions are counted,
        it stays the same in every scenario, and it is never available to be spared. National tree only.

        Sources:

        - national grassland area: package database, ``grassland_data.total_kha`` (EPA CRT 2026 Table4.C, total
          grassland, 1990-2024), via :meth:`get_national_area`;
        - herd-derived grassland area: grassland_production's ``total_grassland`` input, calibration-year row, via
          :meth:`get_derived_national_grassland_area`.

        Parameters
        ----------
        year : int
            The calibration year.
        total_grassland_area : pandas.DataFrame
            The total_grassland input (grassland_production).

        Returns
        -------
        float
            The balance (ha). If the herd area exceeds the national area, 0, with a warning.

        Raises
        ------
        ValueError
            If ``year`` is not in the database.
        """
        national_area = self.get_national_area("grassland", year)
        herd_area = self.get_derived_national_grassland_area(total_grassland_area)
        balance = national_area - herd_area
        if balance < 0:
            logger.warning(
                "Herd-derived grassland (%.0f ha) exceeds the national grassland area in %s (%.0f ha); "
                "grassland balance set to 0.", herd_area, year, national_area)
            return 0.0
        return balance

    def get_derived_national_grassland_area(self, grassland_area, sc=0):
        """
        Derives the national grassland area for a given scenario.

        Parameters
        ----------
        grassland_area : pandas.DataFrame or pandas.Series
            A DataFrame or Series containing grassland area data.
        sc : str or int, optional
            The scenario, default is 0.
        
        Returns
        -------
        float
            The derived national grassland area.
        
        Raises
        ------
        ValueError
            If the scenario is not found in the grassland area data.
        """
        try:
            col = str(sc)
            return grassland_area[col].iloc[0].item()
        except KeyError:
            try:
                col = int(sc)  # Fallback to integer representation
                return grassland_area[col].iloc[0].item()
            except KeyError:
                # Handle or log the error specifically for this scenario
                # Perhaps log an error or raise a custom exception
                raise ValueError(f"Scenario {sc} not found in grassland_area.")
            
    
    def get_area_with_organic_potential(self,spared_breakdown, total_spared_area, sc):
        """
        Calculates the area with organic potential based on a spared area breakdown for a specific scenario.

        Parameters
        ----------
        spared_breakdown : pandas.DataFrame
            A DataFrame containing spared area breakdown data.
        total_spared_area : pandas.DataFrame or pandas.Series
            A DataFrame or Series containing total spared area data.
        sc : str or int
            The scenario.
        
        Returns
        -------
        float
            The area with organic potential: the scenario's spared area on soil group 3 (0.0 if it has no soil group 3
            rows). If the scenario's breakdown is all zero, the total spared area (no cap).

        Raises
        ------
        ValueError
            If the scenario is not found in the spared breakdown dataset (finding 5a).
        """
        # Select only numeric columns 
        numeric_df = spared_breakdown.select_dtypes(include=[float, int])

        grouped_df = numeric_df.groupby(['Scenario','soil_group']).sum()


        if sc not in grouped_df.index.get_level_values('Scenario'):
            raise ValueError(f"Scenario {sc} not found in the spared area breakdown.")
        specific_scenario_df = grouped_df.xs(key=sc, level='Scenario')

        # An all-zero breakdown gives no soil information: no cap (the total spared area).
        if (specific_scenario_df['area_ha'] == 0).all():
            return self.get_total_spared_area(total_spared_area, sc)

        # No soil group 3 rows: no spared land with organic potential (finding 5b).
        if 3 not in specific_scenario_df.index:
            return 0.0
        return float(specific_scenario_df.loc[3, 'area_ha'])
