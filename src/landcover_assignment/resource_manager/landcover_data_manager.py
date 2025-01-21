"""
Landcover Data Manager Documentation
====================================

This documentation provides an overview of the ``DataManager`` and ``DistributionManager`` classes, which are for managing and analyzing land cover 
and land use data. These classes facilitate access to national datasets, scenario processing, and distribution calculations for various land use types.

DataManager Class
-----------------

.. class:: DataManager(calibration_year, target_year)

   The DataManager class is responsible for loading and organizing land cover data for a given calibration and target year. 
   It provides structured access to land use information, default Carbon Budget Model (CBM) data, and utilities for scenario-based land use analysis.

   :param calibration_year: The year used as a reference point for calibrating data.
   :param target_year: The future year for projecting land use changes.

   **Attributes**

   - ``data_loader_class`` (:class:`Loader`): An instance of the Loader class to access land cover datasets.
   - ``calibration_year`` (int): The year used as a reference for calibration.
   - ``target_year`` (int): The year to which data projections are made.
   - ``default_calibration_year`` (int): The default year for calibration if none is specified.
   - ``land_use_columns`` (list): A list of strings representing different land use types.
   - ``cbm_default_data`` (dict): Default data structure for initializing CBM data inputs.
   - ``areas_dataframe_cols`` (list): Column names for the areas DataFrame.
   - ``landuse_dict`` (dict): A dictionary mapping land use types to their corresponding data access methods.
   - ``spared_area_dict`` (dict): A dictionary defining how spared areas are categorized by land use type.

   **Methods**

   .. method:: get_default_calibration_year()

      Returns the default calibration year.

      :return: The default calibration year.
      :rtype: int

   .. method:: get_land_use_columns()

      Returns the list of land use columns.

      :return: A list of land use columns.
      :rtype: list

   .. method:: get_cbm_default_data()

      Returns the default CBM data.

      :return: A dictionary containing the default CBM data.
      :rtype: dict

   .. method:: get_areas_dataframe_cols()

      Returns the column names for the areas DataFrame.

      :return: A list of column names for the areas DataFrame.
      :rtype: list

   .. method:: get_landuse_dict()

      Returns the dictionary mapping land use types to their corresponding data access methods.

      :return: A dictionary mapping land use types to data access methods.
      :rtype: dict

   .. method:: get_spared_area_dict()

      Returns the dictionary defining how spared areas are categorized by land use type.

      :return: A dictionary defining spared areas by land use type.
      :rtype: dict

DistributionManager Class
-------------------------

.. class:: DistributionManager()

   Manages the distribution calculations for land use areas, focusing on the composition and characteristics of land based on various environmental factors. 
   It initializes with a default land distribution setup and provides utilities for adjusting and analyzing these distributions.

   **Attributes**

   - ``land_distribution_keys`` (list): A list of keys for area and shares of different soil types and environmental factors.
   - ``geo_land_distribution_keys`` (list): A list of keys for Geo Model land distribution.
   - ``land_shares_keys`` (list): A list of keys for land shares.
   - ``grassland_share_keys`` (list): A list of keys for grassland shares.
   - ``geo_land_share_keys`` (list): A list of keys for Geo Model land shares.

   **Methods**

   .. method:: get_land_distribution_keys()

      Returns the list of keys for area and shares of different soil types and environmental factors.

      :return: A list of keys for land distribution.
      :rtype: list

   .. method:: get_geoland_distribution_keys()

      Returns the list of keys for Geo Model land distribution.

      :return: A list of keys for Geo Model land distribution.
      :rtype: list

   .. method:: get_land_share_keys()

      Returns the list of keys for land shares.

      :return: A list of keys for land shares.
      :rtype: list

   .. method:: get_grassland_share_keys()

      Returns the list of keys for grassland shares.

      :return: A list of keys for grassland shares.
      :rtype: list

   .. method:: get_geoland_share_keys()

      Returns the list of keys for Geo Model land shares.

      :return: A list of keys for Geo Model land shares.
      :rtype: list
"""

from landcover_assignment.resource_manager.data_loader import Loader


class DataManager:
    def __init__(self, calibration_year, target_year):
        self.data_loader_class = Loader()
        self.calibration_year = calibration_year
        self.target_year = target_year

        self.default_calibration_year = 2015

        self.land_use_columns = [
            "grassland",
            "wetland",
            "cropland",
            "forest",
            "settlement",
            "farmable_condition",
        ]

        self.cbm_default_data = {
            "scenario": [-1, -1, -1, -1, -1, -1],
            "species": ["Sitka", "Sitka","Sitka","SGB","SGB","SGB"],
            "yield_class": ["YC17_20", "YC20_24", "YC24_30", "YC6", "YC6", "YC6"],
            "total_area": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        }

        self.areas_dataframe_cols = [
            "farm_id",
            "year",
            "land_use",
            "area_ha",
            "share_mineral",
            "share_organic",
            "share_drained_rich_organic",
            "share_drained_poor_organic",
            "share_rewetted_in_organic",
            "share_rewetted_rich_organic",
            "share_rewetted_poor_organic",
            "share_rewetted_in_mineral",
            "share_organic_mineral",
            "share_domestic_peat_extraction",
            "share_industrial_peat_extraction",
            "share_rewetted_domestic_peat_extraction",
            "share_rewetted_industrial_peat_extraction",
            "share_near_natural_wetland",
            "share_unmanaged_wetland",
            "share_burnt",
        ]

        self.landuse_dict = {
            "forest": self.data_loader_class.national_forest_areas,
            "cropland": self.data_loader_class.national_cropland_areas,
            "wetland": self.data_loader_class.national_wetland_areas,
            "settlement": self.data_loader_class.national_settlement_areas,
            "grassland": self.data_loader_class.national_grassland_areas,
        }

        self.spared_area_dict = {
            "rewetted": "Wetland area",
            "forest": "Forest area",
            "cropland": "Crop area",
            "farmable_condition": None
        }

    def get_default_calibration_year(self):
        """
        Returns the default calibration year.

        Returns:
            int: The default calibration year.
        """
        return self.default_calibration_year
    
    def get_land_use_columns(self):
        """
        Returns the list of land use columns.

        Returns:
            list: A list of land use columns.
        """
        return self.land_use_columns
    
    def get_cbm_default_data(self):
        """
        Returns the default CBM data.

        Returns:
            dict: A dictionary containing the default CBM data.
        """
        return self.cbm_default_data
    
    def get_areas_dataframe_cols(self):
        """
        Returns the column names for the areas DataFrame.

        Returns:
            list: A list of column names for the areas DataFrame.
        """
        return self.areas_dataframe_cols
    
    def get_landuse_dict(self):
        """
        Returns the dictionary mapping land use types to their corresponding data access methods.

        Returns:
            dict: A dictionary mapping land use types to data access methods.
        """
        return self.landuse_dict
    
    def get_spared_area_dict(self):
        """
        Returns the dictionary defining how spared areas are categorized by land use type.

        Returns:
            dict: A dictionary defining spared areas by land use type.
        """
        return self.spared_area_dict


class DistributionManager:
    def __init__(self):
        self.land_distribution_keys = [
            "area_ha", 
            "share_mineral", 
            "share_organic", 
            "share_drained_rich_organic",
            "share_drained_poor_organic", 
            "share_rewetted_rich_organic",
            "share_rewetted_poor_organic", 
            "share_organic_mineral",
            "share_domestic_peat_extraction", 
            "share_industrial_peat_extraction",
            "share_rewetted_domestic_peat_extraction", 
            "share_rewetted_industrial_peat_extraction",
            "share_rewetted_in_mineral", 
            "share_rewetted_in_organic",
            "share_near_natural_wetland", 
            "share_unmanaged_wetland", 
            "share_burnt"
        ]
        
        self.geo_land_distribution_keys = [
            "area_ha",
            "share_mineral",
            "share_organic",
            "share_organic_mineral",
            "share_peat_extraction",
            "share_rewetted_in_mineral",
            "share_rewetted_in_organic",
            "share_rewetted_in_organic_mineral",
            "share_burnt"
        ]

        self.land_shares_keys = [
            "share_mineral", 
            "share_organic", 
            "share_drained_rich_organic",
            "share_drained_poor_organic", 
            "share_rewetted_rich_organic",
            "share_rewetted_poor_organic", 
            "share_organic_mineral",
            "share_domestic_peat_extraction", 
            "share_industrial_peat_extraction",
            "share_rewetted_domestic_peat_extraction", 
            "share_rewetted_industrial_peat_extraction",
            "share_rewetted_in_mineral", 
            "share_rewetted_in_organic",
            "share_near_natural_wetland", 
            "share_unmanaged_wetland", 
            "share_burnt"
        ]

        self.grassland_share_keys = [
            "share_mineral", "share_organic", "share_drained_rich_organic", "share_drained_poor_organic",
            "share_rewetted_rich_in_organic", "share_rewetted_poor_in_organic", "share_organic_mineral", "share_burnt"
        ]

        self.geo_land_share_keys = [
            "share_mineral", "share_organic", "share_organic_mineral", "share_burnt"
        ]

    def get_land_distribution_keys(self):
        """
        Returns the list of keys for area and shares of different soil types and environmental factors.

        Returns:
            list: A list of keys for land distribution.
        """
        return self.land_distribution_keys
    
    def get_geoland_distribution_keys(self):
        """
        Returns the list of keys for Geo Model land distribution.

        Returns:
            list: A list of keys for Geo Model land distribution.
        """
        return self.geo_land_distribution_keys
    
    def get_land_share_keys(self):
        """
        Returns the list of keys for land shares.

        Returns:
            list: A list of keys for land shares.
        """
        return self.land_shares_keys
    
    def get_grassland_share_keys(self):
        """
        Returns the list of keys for grassland shares.

        Returns:
            list: A list of keys for grassland shares.
        """
        return self.grassland_share_keys
    
    def get_geoland_share_keys(self):
        """
        Returns the list of keys for Geo Model land shares.

        Returns:
            list: A list of keys for Geo Model land shares.
        """
        return self.geo_land_share_keys



