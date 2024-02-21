"""
DataManager for Land Use Databases
==================================

The ``DataManager`` class serves as an interface to interact with a land use database, facilitating the retrieval of various datasets 
related to national land cover areas such as forests, wetlands, croplands, grasslands, and settlements, as well as soil yield mappings for forests. 
This class is designed to support environmental data analysis and modeling tasks by providing structured access to key land use datasets.

.. class:: DataManager()

   Initializes the DataManager class, setting up a connection to a SQLite database containing land use data.

   **Attributes**

   - ``database_dir`` (str): Directory where the database file is located.
   - ``engine`` (:class:`sqlalchemy.engine.Engine`): SQLAlchemy engine object for database connection.

   **Methods**

   .. method:: data_engine_creater()

      Creates a SQLAlchemy engine connected to the SQLite database containing land use data.

      :return: A SQLAlchemy engine instance connected to the land use database.
      :rtype: :class:`sqlalchemy.engine.Engine`

   .. method:: get_national_inventory_areas()

      Retrieves national inventory area data from the database and scales the values by 1000.

      :return: A pandas DataFrame containing national inventory area data with the area values scaled.
      :rtype: pandas.DataFrame

   .. method:: get_national_forest_areas()

      Retrieves national forest area data from the database and scales the values by 1000.

      :return: A pandas DataFrame containing national forest area data with the area values scaled.
      :rtype: pandas.DataFrame

   .. method:: get_national_settlement_areas()

      Retrieves national settlement area data from the database and scales the values by 1000.

      :return: A pandas DataFrame containing national settlement area data with the area values scaled.
      :rtype: pandas.DataFrame

   .. method:: get_national_grassland_areas()

      Retrieves national grassland area data from the database and scales the values by 1000.

      :return: A pandas DataFrame containing national grassland area data with the area values scaled.
      :rtype: pandas.DataFrame

   .. method:: get_national_cropland_areas()

      Retrieves national cropland area data from the database and scales the values by 1000.

      :return: A pandas DataFrame containing national cropland area data with the area values scaled.
      :rtype: pandas.DataFrame

   .. method:: get_national_wetland_areas()

      Retrieves national wetland area data from the database and scales the values by 1000.

      :return: A pandas DataFrame containing national wetland area data with the area values scaled.
      :rtype: pandas.DataFrame

   .. method:: get_soil_yield_mapping()

      Retrieves forest soil yield mapping data from the database without scaling.

      :return: A pandas DataFrame containing forest soil yield mapping data.
      :rtype: pandas.DataFrame

"""
import sqlalchemy as sqa
import pandas as pd
from landcover_assignment.database import get_local_dir
import os


class DataManager:
    def __init__(self):
        self.database_dir = get_local_dir()
        self.engine = self.data_engine_creater()

    def data_engine_creater(self):
        database_path = os.path.abspath(
            os.path.join(self.database_dir, "land_use_database.db")
        )
        engine_url = f"sqlite:///{database_path}"

        return sqa.create_engine(engine_url)

    def get_national_inventory_areas(self):
        table = "NIR"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        # Scale the values by 1000
        dataframe["Area_kha"] *= 1000

        return dataframe

    def get_national_forest_areas(self):
        table = "forest_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe

    def get_national_settlement_areas(self):
        table = "settlement_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe

    def get_national_grassland_areas(self):
        table = "grassland_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe

    def get_national_cropland_areas(self):
        table = "cropland_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe

    def get_national_wetland_areas(self):
        table = "wetland_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        # Scale the values by 1000
        dataframe *= 1000

        return dataframe


    def get_soil_yield_mapping(self):
        table = "forest_soil_yield_mapping"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
        )

        return dataframe