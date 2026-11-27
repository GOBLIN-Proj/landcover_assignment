"""
Landcover
================
This module facilitates the management and analysis of land cover changes within the Irish National context, focusing on the dynamics of land use 
transitions under various scenarios. It leverages data from land cover assignments, national analyses, and scenario-driven land distribution calculations 
to provide tools for detailed land cover change analysis.

Features:
---------
- **Land Cover Analysis**: Provides functionalities to analyze and compute land cover distributions and transitions based on calibration and target years, 
  scenario inputs, and specific land area considerations.
- **Scenario-driven Land Distribution**: Manages the distribution and transition of land areas across different land use types, adjusting for 
  scenario-specific changes.

Dependencies:
-------------
- ``pandas``: Used for data manipulation and analysis.
- ``landcover_assignment.distribution.LandDistribution``: Manages land distribution scenarios.
- ``landcover_assignment.national_landcover.NationalLandCover``: Analyzes land cover within national areas.
- ``landcover_assignment.resource_manager.landcover_data_manager.DataManager``: Manages land cover data.
- ``landcover_assignment.resource_manager.scenario_data_fetcher.ScenarioDataFetcher``: Fetches scenario-specific data.
- ``landcover_assignment.optimisation.landcover_optimisation.LandCoverOptimisation``: Optimizes land cover distribution.

Classes:
--------
``LandCover(calibration_year, target_year, scenario_inputs_df, total_grassland, total_spared_area, spared_area_breakdown)``

   Manages the computation and analysis of land cover changes, focusing on the adjustments of land areas under different scenarios 
   and their implications on land use distribution.

   The class initializes with the required data and parameters for analysis, including calibration and target years, scenario inputs, and areas related 
   to grassland and spared lands. It provides methods to fill current area data, compute current and future land use areas, 
   and analyze spared area breakdowns and grassland distributions based on scenario inputs.

   Methods include:

   - `_log_spared_area`: Logs the spared area details for a specific scenario and land use.
   - `get_spared_area_log`: Returns the log of spared area details.
   - `_fill_current_area_row`: Fills data for the current area based on land use type.
   - `_fill_future_area_row`: Fills data for the future area based on land use type.
   - `compute_current_area`: Computes the current area distribution for all land uses.
   - `combined_future_land_use_area`: Combines current and future land use areas under different scenarios.
   - `spared_area_breakdown`: Analyzes the breakdown of spared areas based on scenarios.
   - `grassland_breakdown`: Specifically analyzes the breakdown of grassland areas under scenarios.
   - `_available_organic_area`: Computes the available organic area for scenarios.

"""
import pandas as pd
from landcover_assignment._deprecation import renamed_keyword
import numpy as np

from landcover_assignment.distribution import LandDistribution
from landcover_assignment.national_landcover import NationalLandCover
from landcover_assignment.resource_manager.landcover_data_manager import DataManager
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher
from landcover_assignment.optimisation.landcover_optimisation import LandCoverOptimisation

class LandCover:
    """
    Manages the computation and analysis of land cover changes, focusing on adjustments in land areas under different scenarios.

    This class is designed to analyze land cover transitions and distributions within Irish national areas, 
    taking into account various scenarios. It leverages data from land cover assignments, national analyses, scenario-driven 
    land distribution calculations to model land cover changes effectively.

    The `LandCover` class provides functionalities to compute current land use distributions based on calibration year data, 
    project future land use areas under different scenarios, and analyze the breakdown of spared areas and grassland distributions
    based on specific scenario inputs.

    Parameters
    ----------
    calibration_year : int
        The year used as a baseline for land cover data and analysis.
    target_year : int
        The future year for which land cover changes are projected.
    scenario_inputs_df : pandas.DataFrame
        A DataFrame containing inputs for various scenarios, used to drive the scenario-based inputs for land distribution adjustments.
    total_grassland : float
        The total area of grassland, used in calculations involving grassland distributions.
    total_spared_area : float
        The total area of land spared from agricultural use, key to scenario-based land distribution analysis.
    spared_area_breakdown : pandas.DataFrame
        A breakdown of how spared areas are allocated across different land use types.

    Attributes
    ----------
    data_manager_class : landcover_assignment.resource_manager.landcover_data_manager.DataManager
        Manages land cover data and provides access to calibration and target year data.
    national_class : NationalLandCover
        Provides functionalities for accessing and analyzing national land cover data.
    sc_fetch_class : ScenarioDataFetcher
        Fetches scenario-specific information from the input data.
    land_dist_class : landcover_assignment.distribution.LandDistribution
        Manages the distribution and transition of land areas across different land use types.
    scenario_list : list
        A list of scenarios derived from the scenario inputs, driving the land cover analysis.

    Methods
    -------
    _log_spared_area(scenario, land_use, area, rewetted_area, mineral_area)
        Logs the spared area details for a specific scenario and land use.
    get_spared_area_log() -> pandas.DataFrame
        Returns the log of spared area details.
    _fill_current_area_row(farm_id, year, land_use) -> dict
        Fills a row of data representing the current state of a specific land use area.
    _fill_future_area_row(farm_id, refyear, target_year, land_use) -> dict
        Fills a row of data representing the future state of a specific land use area.
    compute_current_area() -> pandas.DataFrame
        Computes the current distribution of land use areas based on calibration year data.
    combined_future_land_use_area() -> pandas.DataFrame
        Combines current and future land use areas under different scenarios into a single DataFrame.
    spared_area_breakdown(scenario) -> dict
        Analyzes the breakdown of spared areas under a specific scenario.
    grassland_breakdown(scenario) -> dict
        Specifically analyzes the distribution and adjustment of grassland areas under a given scenario.
    _available_organic_area(scenario) -> dict
        Computes the available area for organic soil-based land uses under a given scenario.
    """
    def __init__(
        self,
        calibration_year,
        target_year,
        scenario_inputs_df,
        total_grassland,
        total_spared_area,
        spared_area_breakdown,
    ):
        self.data_manager_class = DataManager(
            calibration_year, target_year
        )
        self.national_class = NationalLandCover()
        self.sc_fetch_class = ScenarioDataFetcher(scenario_inputs_df, validate_on_init=True)
        self.land_dist_class = LandDistribution(scenario_inputs_df)
        self.total_grassland = total_grassland
        self.total_spared_area = total_spared_area
        self.total_spared_area_breakdown = spared_area_breakdown
        self.scenario_list = self.sc_fetch_class.get_scenario_list()
        self._spared_area_log = pd.DataFrame()
        self._combined_land_use = None


    def _log_spared_area(self, scenario, land_use, mineral_area, organic_area):
        """
        Logs the spared area details for a specific scenario and land use.

        Parameters
        ----------
        scenario : int
            The scenario identifier.
        land_use : str
            The type of land use.
        mineral_area : float
            The amount of area spared on mineral soil.
        organic_area : float
            The amount of area spared on organic soil.
        """
        new_entry = {
            "scenario": scenario,
            "land_use": land_use,
            "mineral_area": mineral_area,
            "organic_area": organic_area,
        }
        
        # Handle the case where the log is empty
        if self._spared_area_log.empty:
            self._spared_area_log = pd.concat(
                [self._spared_area_log, pd.DataFrame([new_entry])], ignore_index=True
            )

        # Append new entries if the combination of scenario and land use does not already exist
        elif not ((self._spared_area_log["scenario"] == scenario) &
                (self._spared_area_log["land_use"] == land_use)).any():
            self._spared_area_log = pd.concat(
                [self._spared_area_log, pd.DataFrame([new_entry])], ignore_index=True
            )


    def _herd_grassland_area(self):
        """Herd-derived grassland area in the calibration year (grassland_production's total_grassland input). This,
        not the grassland row (which also holds the national balance), is the area that can be spared."""
        return self.national_class.get_derived_national_grassland_area(self.total_grassland)

    def get_grassland_area_breakdown(self):
        """
        Reports what the grassland row is made of, for the baseline and each scenario. Reporting only: it doesn't
        change any output.

        - ``herd_grassland_ha``: grassland the herd needs (grassland_production's total_grassland input): the
          calibration-year area for the baseline; for a scenario, the calibration-year area minus its spared area.
        - Spared organic grassland, which stays in the grassland row (docs/rewetting.md); 0 in the baseline. Taken from
          the spared-area log:

          - ``rewetted_spared_ha``: drained land that is rewetted (drained -> rewet-status shares); never more than
            the scenario's rewetting target (log entry ``rewet_grassland``);
          - ``spared_drained_organic_ha``: drained land spared beyond the rewetting target; it stays drained, only
            the animals go (``spared_drained_organic_grassland``);
          - ``spared_rewetted_organic_ha``: spared land that already had rewet status (CRT "Other organic soils");
            it stays so (``spared_rewetted_organic_grassland``).
        - ``other_grassland_ha``: national grassland the herd doesn't need, in the calibration year (national area
          from the package database, grassland_data.total_kha, minus the herd area). The same in every row and never
          spared (docs/grassland_area.md).
        - ``total_grassland_ha``: the grassland row's ``area_ha`` in :meth:`combined_future_land_use_area`; the
          other columns add up to it.

        Returns
        -------
        pandas.DataFrame
            Columns ``farm_id, year, herd_grassland_ha, rewetted_spared_ha, spared_drained_organic_ha,
            spared_rewetted_organic_ha, other_grassland_ha, total_grassland_ha``; baseline row
            ``farm_id = -calibration_year``, then one row per scenario.
        """
        calibration_year = self.data_manager_class.calibration_year
        target_year = self.data_manager_class.target_year
        land_use = self.combined_future_land_use_area()
        grassland = land_use[land_use["land_use"] == "grassland"].set_index("farm_id")["area_ha"]
        log = self.get_spared_area_log()
        organic_entries = {"rewetted_spared_ha": "rewet_grassland",
                           "spared_drained_organic_ha": "spared_drained_organic_grassland",
                           "spared_rewetted_organic_ha": "spared_rewetted_organic_grassland"}

        herd_baseline = self._herd_grassland_area()
        other = self.national_class.get_grassland_balance_area(calibration_year, self.total_grassland)

        rows = [{"farm_id": -calibration_year, "year": calibration_year, "herd_grassland_ha": herd_baseline,
                 **{column: 0.0 for column in organic_entries}, "other_grassland_ha": other,
                 "total_grassland_ha": grassland[-calibration_year]}]
        for scenario in self.scenario_list:
            herd = herd_baseline - self.national_class.get_total_spared_area(self.total_spared_area, scenario)
            scenario_log = log[log["scenario"] == scenario].set_index("land_use")["organic_area"]
            rows.append({"farm_id": scenario, "year": target_year, "herd_grassland_ha": herd,
                         **{column: float(scenario_log.get(entry, 0.0)) for column, entry in organic_entries.items()},
                         "other_grassland_ha": other, "total_grassland_ha": grassland[scenario]})
        return pd.DataFrame(rows)

    def get_spared_area_log(self):
        """
        Returns the log of spared area details.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the log of spared area details.
        """
        return self._spared_area_log
    

    def _fill_current_area_row(self, farm_id, year, land_use):
        """
        Fills a row of data representing the current state of a specific land use area.
        
        Parameters
        ----------
        farm_id : int
            Identifier, a legacy term that represents the scenario identifier.
        year : int
            The year for which the data row is relevant.
        land_use : str
            The type of land use being considered.
        
        Returns
        -------
        dict
            A dictionary containing filled data for the current area row.
        """
        if land_use == "grassland":
            
            return {
                "farm_id": farm_id,
                "year": year,
                "land_use": land_use,
                "area_ha": self.national_class.get_landuse_area(land_use, year, self.total_grassland),
                "share_mineral": self.national_class.get_share_mineral(land_use, year, self.total_grassland),
                "share_organic": self.national_class.get_share_organic(land_use, year, self.total_grassland),
                "share_drained_rich_organic": self.national_class.get_share_drained_rich_organic_grassland(land_use, year, self.total_grassland),
                "share_drained_poor_organic": self.national_class.get_share_drained_poor_organic_grassland(land_use, year, self.total_grassland),
                "share_rewetted_rich_organic": self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, year, self.total_grassland),
                "share_rewetted_poor_organic": self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, year, self.total_grassland),
                "share_organic_mineral": self.national_class.get_share_organic_mineral(land_use, year, self.total_grassland),
                "share_rewetted_in_organic": self.national_class.get_share_rewetted_in_organic(land_use, year, self.total_grassland),
                "share_rewetted_in_mineral": self.national_class.get_share_rewetted_in_mineral(land_use, year, self.total_grassland),
                "share_domestic_peat_extraction": self.national_class.get_share_domestic_peat_extraction(land_use, year),
                "share_industrial_peat_extraction": self.national_class.get_share_industrial_peat_extraction(land_use, year),
                "share_rewetted_industrial_peat_extraction": self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, year),
                "share_rewetted_domestic_peat_extraction": self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, year),
                "share_near_natural_wetland": self.national_class.get_share_near_natural_wetland(land_use, year),
                "share_unmanaged_wetland": self.national_class.get_share_unmanaged_wetland(land_use, year),
                "share_burnt": self.national_class.get_share_burnt(land_use, year, self.total_grassland),
            }
        
        else:

            return {
                "farm_id": farm_id,
                "year": year,
                "land_use": land_use,
                "area_ha": self.national_class.get_landuse_area(land_use, year),
                "share_mineral": self.national_class.get_share_mineral(land_use, year),
                "share_organic": self.national_class.get_share_organic(land_use, year),
                "share_drained_rich_organic": self.national_class.get_share_drained_rich_organic_grassland(land_use, year),
                "share_drained_poor_organic": self.national_class.get_share_drained_poor_organic_grassland(land_use, year),
                "share_rewetted_rich_organic": self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, year),
                "share_rewetted_poor_organic": self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, year),
                "share_organic_mineral": self.national_class.get_share_organic_mineral(land_use, year),
                "share_rewetted_in_organic": self.national_class.get_share_rewetted_in_organic(land_use, year),
                "share_rewetted_in_mineral": self.national_class.get_share_rewetted_in_mineral(land_use, year),
                "share_domestic_peat_extraction": self.national_class.get_share_domestic_peat_extraction(land_use, year),
                "share_industrial_peat_extraction": self.national_class.get_share_industrial_peat_extraction(land_use, year),
                "share_rewetted_industrial_peat_extraction": self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, year),
                "share_rewetted_domestic_peat_extraction": self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, year),
                "share_near_natural_wetland": self.national_class.get_share_near_natural_wetland(land_use, year),
                "share_unmanaged_wetland": self.national_class.get_share_unmanaged_wetland(land_use, year),
                "share_burnt": self.national_class.get_share_burnt(land_use, year),
            } 
        
    def _fill_future_area_row(self, farm_id, refyear, target_year, land_use):
        """
        Fills a row of data representing the future state of a specific land use area.
        
        Parameters
        ----------
        farm_id : int
            Identifier, a legacy term that represents the scenario identifier.
        refyear : int
            The year for which the data row is relevant.
        target_year : int
            The future year for which the data row is relevant.
        land_use : str
            The type of land use being considered.
        
        Returns
        -------
        dict
            A dictionary containing filled data for the future area row.
        """
        return {
            "farm_id": farm_id,
            "year": target_year,
            "land_use": land_use,
            "area_ha": self.national_class.get_landuse_area(land_use, refyear),
            "share_mineral": self.national_class.get_share_mineral(land_use, refyear),
            "share_organic": self.national_class.get_share_organic(land_use, refyear),
            "share_drained_rich_organic": self.national_class.get_share_drained_rich_organic_grassland(land_use, refyear),
            "share_drained_poor_organic": self.national_class.get_share_drained_poor_organic_grassland(land_use, refyear),
            "share_rewetted_rich_organic": self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, refyear),
            "share_rewetted_poor_organic": self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, refyear),
            "share_organic_mineral": self.national_class.get_share_organic_mineral(land_use, refyear),
            "share_rewetted_in_organic": self.national_class.get_share_rewetted_in_organic(land_use, refyear),
            "share_rewetted_in_mineral": self.national_class.get_share_rewetted_in_mineral(land_use, refyear),
            "share_domestic_peat_extraction": self.national_class.get_share_domestic_peat_extraction(land_use, refyear),
            "share_industrial_peat_extraction": self.national_class.get_share_industrial_peat_extraction(land_use, refyear),
            "share_rewetted_industrial_peat_extraction": self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, refyear),
            "share_rewetted_domestic_peat_extraction": self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, refyear),
            "share_near_natural_wetland": self.national_class.get_share_near_natural_wetland(land_use, refyear),
            "share_unmanaged_wetland": self.national_class.get_share_unmanaged_wetland(land_use, refyear),
            # Decision D6b: target-year rows burn at the 3-year rate (NationalLandCover.get_burnt_rate).
            "share_burnt": self.national_class.get_burnt_rate(land_use),
        }  
        

    def compute_current_area(self):
        """
        Computes the distribution of current land use areas based on the calibration year and available data.
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the computed current land use areas.
        """
        calibration_year = self.data_manager_class.calibration_year
        landuses = self.data_manager_class.land_use_columns

        data = []
        for landuse in landuses:
        
            row = self._fill_current_area_row(-calibration_year, calibration_year, landuse)
            data.append(row)

        return pd.DataFrame(data)
    

    def combined_future_land_use_area(self):
        """
        Combines the calculated current land use areas with projected future areas under different scenarios.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing both current and projected future land use areas.
        """
        # Computed once per instance (the allocation is the expensive part); callers get a copy.
        if self._combined_land_use is None:
            self._combined_land_use = self._build_combined_future_land_use_area()
        return self._combined_land_use.copy()

    def _build_combined_future_land_use_area(self):
        """Builds the table returned by :meth:`combined_future_land_use_area`."""
        target_year = self.data_manager_class.target_year
        calibration_year = self.data_manager_class.calibration_year

        # Step 1: Compute current areas
        current_area_pd = self.compute_current_area()

        # Step 2: Initialize list to collect future data
        data = []

        # Step 3: Iterate through scenarios, calculate spared/grassland breakdown once
        for sc in self.scenario_list:
            
            # Calculate spared area breakdown and grassland breakdown
            spared_area_breakdown, grassland_breakdown = self.calculate_spared_area_allocation(sc)

            # Step 4: Process land uses from spared and grassland breakdowns
            for land_use, land_use_data in {**spared_area_breakdown, **grassland_breakdown}.items():
                
                row = {
                    "farm_id": sc,
                    "year": target_year,
                    "land_use": land_use,
                    "area_ha": land_use_data.get("area_ha", 0),
                    "share_mineral": land_use_data.get("share_mineral", 0),
                    "share_organic": land_use_data.get("share_organic", 0),
                    "share_drained_rich_organic": land_use_data.get("share_drained_rich_organic", 0),
                    "share_drained_poor_organic": land_use_data.get("share_drained_poor_organic", 0),
                    "share_rewetted_rich_organic": land_use_data.get("share_rewetted_rich_organic", 0),
                    "share_rewetted_poor_organic": land_use_data.get("share_rewetted_poor_organic", 0),
                    "share_organic_mineral": land_use_data.get("share_organic_mineral", 0),
                    "share_rewetted_in_organic": land_use_data.get("share_rewetted_in_organic", 0),
                    "share_rewetted_in_mineral": land_use_data.get("share_rewetted_in_mineral", 0),
                    "share_domestic_peat_extraction": land_use_data.get("share_domestic_peat_extraction", 0),
                    "share_industrial_peat_extraction": land_use_data.get("share_industrial_peat_extraction", 0),
                    "share_rewetted_industrial_peat_extraction": land_use_data.get("share_rewetted_industrial_peat_extraction", 0),
                    "share_rewetted_domestic_peat_extraction": land_use_data.get("share_rewetted_domestic_peat_extraction", 0),
                    "share_near_natural_wetland": land_use_data.get("share_near_natural_wetland", 0),
                    "share_unmanaged_wetland": land_use_data.get("share_unmanaged_wetland", 0),
                    "share_burnt": land_use_data.get("share_burnt", 0),
                }
                data.append(row)

            # Step 5: Add settlement data
            settlement_data = self.handle_settlement(sc, calibration_year, target_year)
            data.append(settlement_data)

        # Step 6: Combine current and future areas into a single DataFrame
        future_area_pd = pd.DataFrame(data)
        combined_df = pd.concat([current_area_pd, future_area_pd], ignore_index=True)

        return combined_df


    def calculate_spared_area_allocation(self, scenario):
        """
        Wrapper function to handle spared area allocation across mineral and organic soils
        before passing clean parameters to breakdown methods.

        The spared area is split in three:

        - **Rewetted organic soil**: rewetted proportion x spared area (the rewetting target), capped by the drained
          organic grassland available. It stays in the grassland row, moving from the drained to the rewet-status
          shares, and never enters the wetland row (NID 2026 s.6.5.2; CRT 4.C.1 organic = drained + "Other organic
          soils"). Rewetting never goes beyond the target (finding 8, owner 2026-11-27).
        - **Mineral soil**: the rest, capped by the mineral grassland available. The optimiser divides it between
          forest and cropland targets, and any remainder goes to farmable_condition (mineral soil only).
        - **Spared organic soil in its current condition**: when the spared area is larger than the mineral land plus
          the rewetted area (e.g. a scenario that spares all herd grassland), the rest is herd organic grassland that
          only loses its animals. It stays in the grassland row unchanged: drained land stays drained, land with rewet
          status stays so. It is logged as ``spared_drained_organic_grassland`` (up to the herd's drained land not
          rewetted, in proportion to the two pools) and ``spared_rewetted_organic_grassland`` (the rest).

        See docs/rewetting.md.

        Parameters
        ----------
        scenario : int
            Scenario identifier.

        Returns
        -------
        spared_area_breakdown, grassland_breakdown : tuple
            Two dictionaries representing the spared area and grassland area breakdowns.
        """
        # Step 1: Fetch total spared area and max available areas
        initial_spared_area = self.national_class.get_total_spared_area(self.total_spared_area, scenario)
        max_organic_available = self._available_organic_area(scenario)["available_organic"]
        max_mineral_available = self._available_mineral_area()["available_mineral"]

        # Step 2: Rewetting: the target, capped by the drained organic land available; never more
        rewet_proportion = self.sc_fetch_class.get_rewetted_proportion(scenario)
        target_rewetted = initial_spared_area * rewet_proportion
        actual_rewetted_area = min(max_organic_available, target_rewetted)

        # Step 3: Mineral land: the rest, capped by the mineral land available
        required_mineral_area = initial_spared_area - actual_rewetted_area
        actual_mineral_area = min(max_mineral_available, required_mineral_area)

        # Step 4: Spared area beyond mineral land + rewetting: herd organic land that stays in its current condition
        spared_drained_organic_area, spared_rewetted_organic_area = self._spared_organic_in_condition(
            required_mineral_area - actual_mineral_area, actual_rewetted_area)

        # Step 5: Generate spared area breakdown (and the spared-area log)
        spared_area_breakdown = self.spared_area_breakdown(
            scenario,
            initial_spared_area=initial_spared_area,
            actual_rewetted_area=actual_rewetted_area,
            actual_mineral_area=actual_mineral_area,
            spared_drained_organic_area=spared_drained_organic_area,
            spared_rewetted_organic_area=spared_rewetted_organic_area,
        )

        # Step 6: Generate grassland breakdown: only the rewetted area changes status (drained -> rewet status)
        grassland_breakdown = self.grassland_breakdown(
            area_previously_drained=actual_rewetted_area,
            actual_mineral_area=actual_mineral_area,
        )

        # Step 7: Return results
        return spared_area_breakdown, grassland_breakdown


    def _spared_organic_in_condition(self, area, actual_rewetted_area):
        """
        Splits spared organic land that is not rewetted (it only loses its animals) into its drained and rewet-status
        parts. The herd's organic land not rewetted is drained (herd drained land - rewetted area) or already has
        rewet status (herd area x the rewet-status shares). ``area`` is split in proportion to those two pools; the
        drained part is capped by the drained pool and the rest is rewet status. The rest also takes the small
        organic area that the inventory shares put in neither pool (national 2020: about 57 ha).

        Parameters
        ----------
        area : float
            Spared area beyond the mineral land and the rewetted area (ha); 0 in most scenarios.
        actual_rewetted_area : float
            Rewetted spared area (ha).

        Returns
        -------
        tuple of float
            (drained, rewet status) areas in ha.
        """
        if area <= 0:
            return 0.0, 0.0
        year = self.data_manager_class.calibration_year
        herd_area = self._herd_grassland_area()
        drained_pool = max(0.0, self._herd_drained_organic_area() - actual_rewetted_area)
        rewet_pool = herd_area * (
            self.national_class.get_grassland_shares("share_rewetted_rich_in_organic", year, self.total_grassland)
            + self.national_class.get_grassland_shares("share_rewetted_poor_in_organic", year, self.total_grassland))
        pools = drained_pool + rewet_pool
        drained = min(drained_pool, area * drained_pool / pools) if pools > 0 else 0.0
        return drained, area - drained


    @renamed_keyword("intial_spared_area", "initial_spared_area")  # DEPRECATED_NAME
    def spared_area_breakdown(self, scenario, initial_spared_area, actual_rewetted_area, actual_mineral_area,
                              spared_drained_organic_area=0.0, spared_rewetted_organic_area=0.0):
        """
        Analyzes the breakdown of spared areas under a specific scenario.

        Every scenario gets the same log entries, in this order: ``rewet_grassland``,
        ``spared_drained_organic_grassland``, ``spared_rewetted_organic_grassland`` (organic areas), then ``forest``,
        ``cropland``, ``farmable_condition`` (mineral areas). They add up to the spared area.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the spared area breakdown is calculated.
        initial_spared_area : float
            The scenario's spared area (ha).
        actual_rewetted_area : float
            Spared drained organic land that is rewetted (ha; never more than the rewetting target).
        actual_mineral_area : float
            Spared mineral land (ha), divided by the optimiser.
        spared_drained_organic_area : float, optional
            Spared drained organic land that is not rewetted: it stays drained grassland (ha).
        spared_rewetted_organic_area : float, optional
            Spared organic land that already had rewet status: it stays so (ha).
        
        Returns
        -------
        dict
            A dictionary containing the breakdown of spared areas for the given scenario.
        """
        result_dict = {}

        year = self.data_manager_class.calibration_year
        spared_land_use_dict = self.data_manager_class.get_spared_area_dict()

        # Step 1: Rewetted area. Rewetted spared grassland stays in the grassland row (its drained share moves to
        # rewet status in grassland_breakdown). It is recorded here in the log only; it does not become wetland.
        self._log_spared_area(scenario, "rewet_grassland", 0, actual_rewetted_area)

        # Spared organic land beyond the rewetting target and the mineral land: it only loses its animals and stays in
        # the grassland row in its current condition (drained, or rewet status). Logged only.
        self._log_spared_area(scenario, "spared_drained_organic_grassland", 0, spared_drained_organic_area)
        self._log_spared_area(scenario, "spared_rewetted_organic_grassland", 0, spared_rewetted_organic_area)


        # The wetland row keeps its calibration-year area: no spared grassland is converted to wetland.
        wetland_data = self.land_dist_class.land_distribution(
            year, "wetland", None, target_year=self.data_manager_class.target_year)
        result_dict["wetland"] = wetland_data

        # Step 2: Define target shares
        target_areas = {
            land_use: (initial_spared_area * getattr(self.sc_fetch_class, f"get_{land_use}_proportion")(scenario))
            for land_use in spared_land_use_dict.keys()
            if land_use not in ["farmable_condition", "rewetted"]# Exclude "farmable condition" (fallback) & rewetted
        }

        # Step 3: Optimize spared area distribution
        optimizer = LandCoverOptimisation()
        optimised_allocations = optimizer.optimise_mineral_spared_area_distribution(
            mineral_area_available=actual_mineral_area,
            target_areas=target_areas,
        )

        # Step 4: Distribute spared area based on optimised allocations
        for land_use, allocated_area in optimised_allocations.items():
            generated_land_use_data = self.land_dist_class.land_distribution(
                year, land_use, allocated_area, target_year=self.data_manager_class.target_year
            )

            self._log_spared_area(scenario, land_use, allocated_area, 0)
            result_dict[land_use] = generated_land_use_data

        return result_dict


    def grassland_breakdown(self, area_previously_drained, actual_mineral_area):
        """
        Specifically analyzes the distribution and adjustment of grassland areas under a given scenario.

        Spared mineral grassland leaves the grassland row. Rewetted spared organic grassland stays in it: its area
        moves from the drained to the rewet-status shares. The scenario's grassland row is therefore productive
        grassland plus the rewetted spared area. See docs/rewetting.md.

        Parameters
        ----------
        area_previously_drained : float
            Spared organic area that is rewetted (ha). It moves from drained to rewet status within grassland.
        actual_mineral_area : float
            Spared mineral area that leaves grassland (ha).
        
        Returns
        -------
        dict
            A dictionary containing updated grassland distribution details, including areas and proportions
            of soil types.
        """
        result_dict = {}

        calibration_year = self.data_manager_class.calibration_year

        generated_land_use_data = self.land_dist_class.grassland_distribution(
            calibration_year, actual_mineral_area, area_previously_drained, self.total_grassland
        )

        result_dict["grassland"] = generated_land_use_data


        return result_dict
    


    def _available_organic_area(self, scenario):
        """
        Computes the available area for organic soil under a given scenario.

        This internal method calculates the maximum possible area that can be transitioned to organic soil-based
        land uses, such as wetlands, based on the current organic and organic-mineral soil areas and scenario-specific
        spared area allocations.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the available organic area is calculated.
        
        Returns
        -------
        dict
            A dictionary containing the available organic area and available mineral-organic area.
        """
        year = self.data_manager_class.calibration_year

        organic_potential = self.national_class.get_area_with_organic_potential(self.total_spared_area_breakdown, self.total_spared_area, scenario)
        
        total_drained = self._herd_drained_organic_area()

        max_organic_spared = min(organic_potential, total_drained)

        return {"available_organic":max_organic_spared}
    

    def _herd_drained_organic_area(self):
        """Drained organic grassland of the herd (ha): herd area x the calibration-year drained rich and poor shares.
        Herd grassland only: the national balance (docs/grassland_area.md) is never available to be spared."""
        year = self.data_manager_class.calibration_year
        herd_area = self._herd_grassland_area()
        return herd_area * (
            self.national_class.get_share_drained_rich_organic_grassland("grassland", year, self.total_grassland)
            + self.national_class.get_share_drained_poor_organic_grassland("grassland", year, self.total_grassland))


    def _available_mineral_area(self):
        """
        Computes the available area for mineral soil under a given scenario.

        This internal method calculates the maximum possible area that can be transitioned to mineral soil-based
        land uses, such as wetlands, based on the current mineral and soil areas and scenario-specific
        spared area allocations.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the available mineral area is calculated.
        
        Returns
        -------
        dict
            A dictionary containing the available mineral area.
        """
        year = self.data_manager_class.calibration_year

        # Herd grassland only: the national balance (docs/grassland_area.md) is never available to be spared.
        mineral_area = self._herd_grassland_area() * self.national_class.get_share_mineral("grassland", year, self.total_grassland)
    
        return {"available_mineral":mineral_area}


    def handle_settlement(self, scenario, calibration_year, target_year):
        """
        Handles settlement data, which remains relatively constant and requires specific logic.

        Parameters
        ----------
        scenario : int
            The scenario identifier for which the settlement data is being processed.
        calibration_year : int
            The baseline year for settlement data.
        target_year : int
            The target year for settlement projections.

        Returns
        -------
        dict
            A dictionary representing settlement data for the specified scenario and target year.
        """
        settlement_data = self._fill_future_area_row(scenario, calibration_year, target_year, "settlement")
        return settlement_data