"""
Distribution
================
This module is designed to manage and process land distribution scenarios for the Irish national context, particularly focusing on adjustments 
in land use areas based on various scenario inputs. It integrates with land cover data management,
scenario-specific data fetching, and national area analysis to provide a comprehensive tool for land distribution analysis.

Features:
---------
- **Land Distribution Analysis**: Manages the calculation and distribution of land areas across different land use types 
  based on scenario-driven changes.
- **Grassland Distribution Management**: Specifically handles the redistribution of grassland areas, taking into account
  changes in mineral and organic components.

Dependencies:
-------------
- ``landcover_assignment.resource_manager.landcover_data_manager.DistributionManager``
- ``landcover_assignment.national_landcover.NationalLandCover``
- ``landcover_assignment.resource_manager.scenario_data_fetcher.ScenarioDataFetcher``
- ``pandas`` for data manipulation and analysis.

Classes:
--------
.. class:: LandDistribution(scenario_data)
   :noindex:

   Handles the distribution of land areas for various land use types under different scenarios, adjusting for changes in
   areas and soil composition.

   .. method:: land_distribution(year, land_use, new_area)
      Calculates and updates the distribution of land based on land use type and the area change. It supports special 
      handling for grassland, wetland, and forest types, among others, adjusting shares of mineral, organic, and other 
      soil types accordingly.

   .. method:: grassland_distribution(year, mineral_area, organic_area, grassland_area)
      Specifically handles the distribution and adjustment of grassland areas, considering changes in mineral and organic
      components, and recalculates the total remaining grassland area along with its composition.

"""

from landcover_assignment.resource_manager.landcover_data_manager import DistributionManager
from landcover_assignment.national_landcover import NationalLandCover
from landcover_assignment.resource_manager.scenario_data_fetcher import ScenarioDataFetcher

class LandDistribution:
    """
    Handles the distribution of land areas for various land use types under different scenarios,
    adjusting for changes in areas and soil composition.

    This class provides methods to calculate and update land distribution based on changes in land use
    types, including special considerations for grassland, wetland, and forest. It utilizes data from
    land cover data managers, national land cover analysis, and scenario-specific data fetchers to accurately
    model land distribution adjustments under various scenarios.

    Parameters
    ----------
    scenario_data : pd.DataFrame
        A DataFrame containing scenario-specific data inputs. This data is used to fetch catchment
        names and drive the scenario-based calculations for land distribution adjustments.

    Attributes
    ----------
    data_manager_class : DistributionManager
        An instance of DistributionManager for managing land distribution data.
    national_class : NationalLandCover
        An instance of NationalLandCover for accessing and analyzing Irish national context land cover data.
    sc_fetcher_class : ScenarioDataFetcher
        An instance of ScenarioDataFetcher initialized with scenario data for fetching scenario-specific information.

    Methods
    -------
    land_distribution(year, land_use, new_area)
        Calculates and updates the distribution of land based on land use type and the area change.
        It supports special handling for grassland, wetland, and forest types, among others, adjusting shares
        of mineral, organic, and other soil types accordingly.

    grassland_distribution(year, mineral_area, organic_area, grassland_area)
        Specifically handles the distribution and adjustment of grassland areas, considering changes in mineral
        and organic components, and recalculates the total remaining grassland area along with its composition.
    """
    def __init__(self, scenario_data):
        self.data_manager_class = DistributionManager()
        self.national_class = NationalLandCover()
        self.sc_fetcher_class = ScenarioDataFetcher(scenario_data, validate_on_init=True)


    def land_distribution(self, year, land_use, new_area):
        """
        Calculates and updates the land distribution based on land use type and area change.

        Parameters
        ----------
        year : int
            The reference year for national land use data.
        land_use : str
            The type of land use to calculate distribution for.
        new_area : float
            The area change to be applied to the land use type.

        Returns
        -------
        dict
            A dictionary containing updated land distribution details.
        """
        if land_use == "grassland":
            return None

        land = {key: 0 for key in self.data_manager_class.get_land_distribution_keys()}

        current_area = self.national_class.get_landuse_area(land_use, year) or 0

        shares = {
            key: self.national_class.get_land_shares(key, land_use, year) or 0
            for key in self.data_manager_class.get_land_share_keys()
        }

        # Calculate total area
        land["area_ha"] = current_area + (new_area or 0)

        # Calculate updated shares
        if land["area_ha"] != 0:
            for key, share_value in shares.items():
                # Adjust `share_mineral` differently if it's not "wetland"
                if key == "share_mineral" and land_use != "wetland":
                    land[key] = ((current_area * share_value) + (new_area or 0)) / land["area_ha"]
                else:
                    # Proportionally adjust other shares
                    land[key] = (current_area * share_value) / land["area_ha"]
        else:
            # Retain original shares if total area is zero
            for key, share_value in shares.items():
                land[key] = share_value

        return land


    def grassland_distribution(self, year, mineral_area, organic_area_to_wet, grassland_area):
        """
        Optimized version to manage the distribution of grassland areas, considering mineral and organic changes.

        Parameters
        ----------
        year : int
            The reference year for national land use data.
        mineral_area : float
            The area of mineral soil to be adjusted.
        organic_area : float
            The area of organic soil to be adjusted.
        grassland_area : float
            The total grassland area to be considered.

        Returns
        -------
        dict
            A dictionary containing updated grassland distribution details.
        """
        # Initialize land dictionary with default values
        land = {key: 0 for key in self.data_manager_class.get_land_distribution_keys()}

        current_grassland_area = self.national_class.get_landuse_area("grassland", year, grassland_area) or 0

        # Fetch all relevant shares dynamically
        shares = {
            key: self.national_class.get_grassland_shares(key, year, grassland_area) or 0
            for key in self.data_manager_class.get_grassland_share_keys()
        }

        # Calculate areas
        grass_mineral_area = current_grassland_area * shares["share_mineral"]
        grass_organic_area = current_grassland_area * shares["share_organic"]
        grass_organic_mineral_area = current_grassland_area * shares["share_organic_mineral"]
        grass_drained_rich_organic_area = current_grassland_area * shares["share_drained_rich_organic"]
        grass_drained_poor_organic_area = current_grassland_area * shares["share_drained_poor_organic"]
        grass_rewetted_rich_organic_area = current_grassland_area * shares["share_rewetted_rich_in_organic"]
        grass_rewetted_poor_organic_area = current_grassland_area * shares["share_rewetted_poor_in_organic"]

        # Calculate rewetted areas and proportions
        total_drained_area = grass_drained_rich_organic_area + grass_drained_poor_organic_area

        if total_drained_area > 0:
            drained_rich_organic_proportion = grass_drained_rich_organic_area / total_drained_area
            drained_poor_organic_proportion = grass_drained_poor_organic_area / total_drained_area
        else:
            drained_rich_organic_proportion = drained_poor_organic_proportion = 0

        grass_remaining_mineral = grass_mineral_area - mineral_area
        grass_remaining_drained_rich_organic = grass_drained_rich_organic_area - (organic_area_to_wet * drained_rich_organic_proportion)
        grass_remaining_drained_poor_organic = grass_drained_poor_organic_area - (organic_area_to_wet * drained_poor_organic_proportion)

        grass_rewetted_total_rich_organic = grass_rewetted_rich_organic_area + (organic_area_to_wet * drained_rich_organic_proportion)
        grass_rewetted_total_poor_organic = grass_rewetted_poor_organic_area + (organic_area_to_wet * drained_poor_organic_proportion)

        grass_total_remaining = grass_remaining_mineral + grass_organic_area + grass_organic_mineral_area

        if grass_total_remaining > 0:
            # Update land shares proportionally
            land["area_ha"] = grass_total_remaining
            land["share_organic"] = grass_organic_area / grass_total_remaining
            land["share_drained_rich_organic"] = grass_remaining_drained_rich_organic / grass_total_remaining
            land["share_drained_poor_organic"] = grass_remaining_drained_poor_organic / grass_total_remaining
            land["share_rewetted_rich_organic"] = grass_rewetted_total_rich_organic / grass_total_remaining
            land["share_rewetted_poor_organic"] = grass_rewetted_total_poor_organic / grass_total_remaining
            land["share_organic_mineral"] = grass_organic_mineral_area / grass_total_remaining
            land["share_mineral"] = grass_remaining_mineral / grass_total_remaining
            land["share_burnt"] = shares["share_burnt"]
        else:
            # Set everything to zero to reflect no remaining grassland
            land = {key: 0 for key in land.keys()}

        # Set fixed shares
        land.update({
            "share_rewetted_in_mineral": 0,
            "share_rewetted_in_organic": 0,
            "share_domestic_peat_extraction": 0,
            "share_industrial_peat_extraction": 0,
            "share_rewetted_domestic_peat_extraction": 0,
            "share_rewetted_industrial_peat_extraction": 0,
            "share_near_natural_wetland": 0,
            "share_unmanaged_wetland": 0,
        })

        return land