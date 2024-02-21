"""
Loader Class Documentation
==========================

The ``Loader`` class serves as an interface to access various national land cover and land use area datasets. It utilizes the ``DataManager`` to retrieve specific datasets related to inventory areas, forest areas, cropland areas, grassland areas, wetland areas, settlement areas, and forest soil yield mappings.

.. _loader-class:

.. class:: Loader()

   Initializes the Loader class with a connection to the data management system for retrieving national land cover datasets.

   **Attributes**

   - ``dataframes`` (:class:`DataManager`): An instance of the DataManager class for accessing land cover data.

   **Methods**

   .. method:: national_inventory_areas()

      Retrieves national inventory areas dataset.

      :return: A DataFrame containing national inventory areas data.
      :rtype: pandas.DataFrame

   .. method:: national_forest_areas()

      Retrieves national forest areas dataset.

      :return: A method object that when called, returns a DataFrame containing national forest areas data.
      :rtype: method

   .. method:: national_cropland_areas()

      Retrieves national cropland areas dataset.

      :return: A method object that when called, returns a DataFrame containing national cropland areas data.
      :rtype: method

   .. method:: national_grassland_areas()

      Retrieves national grassland areas dataset.

      :return: A method object that when called, returns a DataFrame containing national grassland areas data.
      :rtype: method

   .. method:: national_wetland_areas()

      Retrieves national wetland areas dataset.

      :return: A method object that when called, returns a DataFrame containing national wetland areas data.
      :rtype: method

   .. method:: national_settlement_areas()

      Retrieves national settlement areas dataset.

      :return: A method object that when called, returns a DataFrame containing national settlement areas data.
      :rtype: method

   .. method:: forest_soil_yield_mapping()

      Retrieves forest soil yield mapping to soil groups dataset.

      :return: A method object that when called, returns a DataFrame containing forest soil yield mappings.
      :rtype: method

**Usage**

The ``Loader`` class is primarily used within environmental data analysis applications, where accessing standardized datasets on land cover and land use is essential. It abstracts the complexity of data retrieval processes, allowing users to focus on analyzing the data rather than managing data access.

"""

from landcover_assignment.resource_manager.database_manager import DataManager


class Loader:
    def __init__(self):
        self.dataframes = DataManager()

    def national_inventory_areas(self):
        return self.dataframes.get_national_inventory_areas()

    def national_forest_areas(self):
        return self.dataframes.get_national_forest_areas

    def national_cropland_areas(self):
        return self.dataframes.get_national_cropland_areas

    def national_grassland_areas(self):
        return self.dataframes.get_national_grassland_areas

    def national_wetland_areas(self):
        return self.dataframes.get_national_wetland_areas

    def national_settlement_areas(self):
        return self.dataframes.get_national_settlement_areas

    def forest_soil_yield_mapping(self):
        return self.dataframes.get_soil_yield_mapping()