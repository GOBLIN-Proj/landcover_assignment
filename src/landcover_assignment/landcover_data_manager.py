"""
Landcover Data Manager Documentation
==========================

This documentation provides an overview of the ``DataManager`` and ``DistributionManager`` classes, which is for managing and analyzing land cover 
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

DistributionManager Class
-------------------------

.. class:: DistributionManager()

   Manages the distribution calculations columns for land use areas, focusing on the composition and characteristics of land based on various environmental factors. 
   It initializes with a default land distribution setup and provides utilities for adjusting and analyzing these distributions.

   **Attributes**

   - ``land_distribution`` (dict): A dictionary with keys for area and shares of different soil types and environmental factors, initialized with default values.
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
            "wetland": "Wetland area",
            "forest": "Forest area",
            "cropland": "Crop area",
            "farmable_condition": None
        }


class DistributionManager:
    def __init__(self):
        self.land_distribution = {
            "area_ha":0,
            "share_mineral":0,
            "share_organic":0,
            "share_drained_rich_organic":0,
            "share_drained_poor_organic":0,
            "share_rewetted_in_organic":0,
            "share_rewetted_rich_organic":0,
            "share_rewetted_poor_organic":0,
            "share_rewetted_in_mineral":0,
            "share_organic_mineral":0,
            "share_domestic_peat_extraction":0,
            "share_industrial_peat_extraction":0,
            "share_rewetted_domestic_peat_extraction":0,
            "share_rewetted_industrial_peat_extraction":0,
            "share_near_natural_wetland":0,
            "share_unmanaged_wetland":0,
            "share_burnt":0,
        }
