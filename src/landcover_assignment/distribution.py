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
- ``landcover_assignment.landcover_data_manager.DistributionManager``
- ``landcover_assignment.national_landcover.NatioanlLandCover``
- ``resource_manager.scenario_data_fetcher.ScenarioDataFetcher``
- ``pandas`` for data manipulation and analysis.

Classes:
--------
.. class:: LandDistribution(scenario_data)
   :noindex:

   Handles the distribution of land areas for various land use types under different scenarios, adjusting for changes in
   areas and soil composition.

   .. method:: land_distribution(land_use, new_area)
      Calculates and updates the distribution of land based on land use type and the area change. It supports special 
      handling for grassland, wetland, and forest types, among others, adjusting shares of mineral, organic, and other 
      soil types accordingly.

   .. method:: grassland_distribution(mineral_area, organic_area, grassland_area)
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
    land cover data managers, catchment analysis, and scenario-specific data fetchers to accurately
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
        An instance of NatioanlLandCover for accessing and analyzing Irish national context land cover data.
    sc_fetcher_class : ScenarioDataFetcher
        An instance of ScenarioDataFetcher initialized with scenario data for fetching scenario-specific information.


    Methods
    -------
    land_distribution(land_use, new_area)
        Calculates and updates the distribution of land based on land use type and the area change.
        It supports special handling for grassland, wetland, and forest types, among others, adjusting shares
        of mineral, organic, and other soil types accordingly.

    grassland_distribution(mineral_area, organic_area, grassland_area)
        Specifically handles the distribution and adjustment of grassland areas, considering changes in mineral
        and organic components, and recalculates the total remaining grassland area along with its composition.
    """
    def __init__(self, scenario_data):
        self.data_manager_class = DistributionManager()
        self.national_class = NationalLandCover()
        self.sc_fetcher_class = ScenarioDataFetcher(scenario_data)


    def land_distribution(self, year, land_use, new_area):
        """
        Calculates and updates the land distribution based on land use type and area change.

        :param year: The reference year for national land use data
        :type year: int
        :param land_use: The type of land use to calculate distribution for.
        :type land_use: str
        :param new_area: The area change to be applied to the land use type.
        :type new_area: float
        :return: A dictionary containing updated land distribution details.
        :rtype: dict
        """
        if land_use == "grassland":
            return None
        
        else:
            
            #initialize land dictionary with default values 

            land = {            
                "area_ha": 0,
                "share_mineral": 0,
                "share_organic": 0,
                "share_drained_rich_organic": 0,
                "share_drained_poor_organic": 0,
                "share_rewetted_rich_organic": 0,
                "share_rewetted_poor_organic": 0,
                "share_organic_mineral": 0,
                "share_domestic_peat_extraction": 0,
                "share_industrial_peat_extraction": 0,
                "share_rewetted_domestic_peat_extraction": 0,
                "share_rewetted_industrial_peat_extraction": 0,
                "share_rewetted_in_mineral": 0,
                "share_rewetted_in_organic": 0,
                "share_near_natural_wetland": 0,
                "share_unmanaged_wetland": 0,
                "share_burnt": 0,
            }

            land_share_mineral = self.national_class.get_share_mineral(land_use, year) or 0
            land_share_organic = self.national_class.get_share_organic(land_use, year) or 0
            land_share_drained_rich_organic = self.national_class.get_share_drained_rich_organic_grassland(land_use, year) or 0
            land_share_drained_poor_organic = self.national_class.get_share_drained_poor_organic_grassland(land_use, year) or 0
            land_share_rewetted_rich_organic = self.national_class.get_share_rewetted_rich_in_organic_grassland(land_use, year) or 0
            land_share_rewetted_poor_organic = self.national_class.get_share_rewetted_poor_in_organic_grassland(land_use, year) or 0
            land_share_organic_mineral = self.national_class.get_share_organic_mineral(land_use, year) or 0
            land_share_domestic_peat_extraction = self.national_class.get_share_domestic_peat_extraction(land_use, year) or 0
            land_share_industrial_peat_extraction = self.national_class.get_share_industrial_peat_extraction(land_use, year) or 0
            land_share_rewetted_domestic_peat_extraction = self.national_class.get_share_rewetted_domestic_peat_extraction(land_use, year) or 0
            land_share_rewetted_industrial_peat_extraction = self.national_class.get_share_rewetted_industrial_peat_extraction(land_use, year) or 0
            land_share_rewetted_in_mineral = self.national_class.get_share_rewetted_in_mineral(land_use, year) or 0
            land_share_rewetted_in_organic = self.national_class.get_share_rewetted_in_organic(land_use, year) or 0
            land_share_near_natural_wetland = self.national_class.get_share_near_natural_wetland(land_use, year) or 0
            land_share_unmanaged_wetland = self.national_class.get_share_unmanaged_wetland(land_use, year) or 0
            land_share_burnt = self.national_class.get_share_burnt(land_use, year) or 0
            land_area_current = self.national_class.get_landuse_area(land_use, year) or 0


            #calculate total wetland area 

            if land_use == "wetland":
                land["area_ha"] = land_area_current 
                new_area = 0
            else:
                land["area_ha"] = land_area_current + (new_area or 0)

            #shares to calculate
            shares = {
                "share_mineral": land_share_mineral,
                "share_organic": land_share_organic,
                "share_drained_rich_organic": land_share_drained_rich_organic,
                "share_drained_poor_organic": land_share_drained_poor_organic,
                "share_rewetted_rich_organic": land_share_rewetted_rich_organic,
                "share_rewetted_poor_organic": land_share_rewetted_poor_organic,
                "share_organic_mineral": land_share_organic_mineral,
                "share_domestic_peat_extraction": land_share_domestic_peat_extraction,
                "share_industrial_peat_extraction": land_share_industrial_peat_extraction,
                "share_rewetted_domestic_peat_extraction": land_share_rewetted_domestic_peat_extraction,
                "share_rewetted_industrial_peat_extraction": land_share_rewetted_industrial_peat_extraction,
                "share_rewetted_in_mineral": land_share_rewetted_in_mineral,
                "share_rewetted_in_organic": land_share_rewetted_in_organic,
                "share_near_natural_wetland": land_share_near_natural_wetland,
                "share_unmanaged_wetland": land_share_unmanaged_wetland,
                "share_burnt": land_share_burnt
            }

            # Calculate shares
            if land["area_ha"] != 0:
                for key, share_value in shares.items():
                    if key == "share_mineral" and land_use != "wetland":
                        # Adjust share_mineral specifically to reflect new_area
                        land[key] = ((land_area_current * share_value) + new_area) / land["area_ha"]
                    else:
                        # Calculate other shares proportionally
                        land[key] = (land_area_current * share_value) / land["area_ha"]
            else:
                # If area is zero, retain current shares
                for key, share_value in shares.items():
                    land[key] = share_value


            return land


    def grassland_distriubtion(self, year, mineral_area, organic_area, grassland_area):
        """
        Manages the distribution of grassland areas, taking into account changes in mineral and organic areas.

        :param year: The reference year for national land use data
        :type year: int
        :param mineral_area: The area of grassland to be converted to mineral soil.
        :type mineral_area: float
        :param organic_area: The area of grassland to be converted to rewetted organic soil.
        :type organic_area: float
        :param grassland_area: The total initial grassland area before distribution.
        :type grassland_area: pandas.DataFrame
        :return: A dictionary containing updated grassland distribution details.
        :rtype: dict
        """
        land = self.data_manager_class.land_distribution

        current_grassland_area = self.national_class.get_landuse_area("grassland", year, grassland_area)
        grass_share_mineral = self.national_class.get_share_mineral("grassland", year, grassland_area)
        grass_share_organic = self.national_class.get_share_organic("grassland", year, grassland_area)
        share_drained_rich_organic_grassland = self.national_class.get_share_drained_rich_organic_grassland("grassland", year, grassland_area)
        share_drained_poor_organic_grassland = self.national_class.get_share_drained_poor_organic_grassland("grassland", year, grassland_area)
        share_rewetted_rich_in_organic_grassland = self.national_class.get_share_rewetted_rich_in_organic_grassland("grassland", year, grassland_area)
        share_rewetted_poor_in_organic_grassland = self.national_class.get_share_rewetted_poor_in_organic_grassland("grassland", year, grassland_area)
        grass_share_organic_mineral = self.national_class.get_share_organic_mineral("grassland", year, grassland_area)
        grass_share_burnt = self.national_class.get_share_burnt("grassland", year, grassland_area)

        grass_mineral_area = current_grassland_area * grass_share_mineral
        grass_organic_area = current_grassland_area * grass_share_organic
        grass_organic_mineral_area = current_grassland_area * grass_share_organic_mineral
        grass_drained_rich_organic_area = current_grassland_area * share_drained_rich_organic_grassland
        grass_drained_poor_organic_area = current_grassland_area * share_drained_poor_organic_grassland
        grass_rewetted_rich_organic_area = current_grassland_area * share_rewetted_rich_in_organic_grassland
        grass_rewetted_poor_organic_area = current_grassland_area * share_rewetted_poor_in_organic_grassland

        total_drained_area = grass_drained_rich_organic_area + grass_drained_poor_organic_area

        drained_rich_organic_proportion = grass_drained_rich_organic_area / total_drained_area
        drained_poor_organic_proportion = grass_drained_poor_organic_area / total_drained_area


        grass_remaining_mineral = grass_mineral_area - mineral_area

        grass_remaining_drained_rich_organic = grass_drained_rich_organic_area - (organic_area * drained_rich_organic_proportion)
        grass_remaining_drained_poor_organic = grass_drained_poor_organic_area - (organic_area * drained_poor_organic_proportion)

        grass_rewetted_total_rich_organic = grass_rewetted_rich_organic_area + (organic_area * drained_rich_organic_proportion)
        grass_rewetted_total_poor_organic = grass_rewetted_poor_organic_area + (organic_area * drained_poor_organic_proportion)

        grass_total_remaining = grass_remaining_mineral + grass_organic_area + grass_organic_mineral_area


        land["area_ha"] = grass_total_remaining
        land["share_organic"] = grass_organic_area / grass_total_remaining
        land["share_drained_rich_organic"] = grass_remaining_drained_rich_organic / grass_total_remaining
        land["share_drained_poor_organic"] = grass_remaining_drained_poor_organic / grass_total_remaining
        land["share_rewetted_rich_organic"] = grass_rewetted_total_rich_organic / grass_total_remaining
        land["share_rewetted_poor_organic"] = grass_rewetted_total_poor_organic / grass_total_remaining
        land["share_organic_mineral"] = grass_organic_mineral_area/ grass_total_remaining
        land["share_mineral"] = grass_remaining_mineral / grass_total_remaining
        land["share_rewetted_in_mineral"] = 0
        land["share_rewetted_in_organic"] = 0
        land["share_domestic_peat_extraction"] = 0
        land["share_industrial_peat_extraction"] = 0
        land["share_rewetted_domestic_peat_extraction"] = 0
        land["share_rewetted_industrial_peat_extraction"] = 0
        land["share_near_natural_wetland"] = 0
        land["share_unmanaged_wetland"] = 0
        land["share_burnt"] = grass_share_burnt

        return land
