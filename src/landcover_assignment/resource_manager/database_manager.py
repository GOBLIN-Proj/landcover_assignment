"""
DataManager for Land Use Databases
==================================

The ``DataManager`` class serves as an interface to interact with a land use database, facilitating the retrieval of various datasets 
related to national land cover areas such as forests, wetlands, croplands, grasslands, and settlements, as well as soil yield mappings for forests. 
This class is designed to support environmental data analysis and modeling tasks by providing structured access to key land use datasets.

Attributes:
    database_dir (str): Directory where the database file is located.
    engine (sqlalchemy.engine.Engine): SQLAlchemy engine object for database connection.

Methods:
    data_engine_creator(): Creates a SQLAlchemy engine connected to the SQLite database containing land use data.
    get_national_inventory_areas(): Retrieves national inventory area data from the database and converts its areas from kha to ha.
    get_national_forest_areas(): Retrieves national forest area data from the database and converts its areas from kha to ha.
    get_national_settlement_areas(): Retrieves national settlement area data from the database and converts its areas from kha to ha.
    get_national_grassland_areas(): Retrieves national grassland area data from the database and converts its areas from kha to ha.
    get_national_cropland_areas(): Retrieves national cropland area data from the database and converts its areas from kha to ha.
    get_national_wetland_areas(): Retrieves national wetland area data from the database and converts its areas from kha to ha.
    get_soil_yield_mapping(): Retrieves forest soil yield mapping data from the database without scaling.
"""

import sqlalchemy as sqa
import pandas as pd
from landcover_assignment.database import get_database_path, get_local_dir
from landcover_assignment.resource_manager import units
import os
from landcover_assignment._deprecation import renamed_method


class DataManager:
    def __init__(self):
        """
        Initializes the DataManager class, setting up a connection to a SQLite database containing land use data.
        """
        self.database_dir = get_local_dir()
        self.engine = self.data_engine_creator()

    def data_engine_creator(self):
        """
        Creates a SQLAlchemy engine connected to the SQLite database containing land use data.

        Returns:
            sqlalchemy.engine.Engine: A SQLAlchemy engine instance connected to the land use database.
        """
        database_path = os.path.abspath(get_database_path())
        engine_url = f"sqlite:///{database_path}"

        return sqa.create_engine(engine_url)

    data_engine_creater = renamed_method("data_engine_creator", "data_engine_creater")  # DEPRECATED_NAME

    def _to_model_units(self, table, dataframe):
        """
        Converts each column of ``dataframe`` from the unit recorded for it in the database's ``column_metadata``
        table to the model unit (areas: kha to ha), using :mod:`landcover_assignment.resource_manager.units`.
        Keys and labels (units ``year``, ``label``, ``group``) are left as they are.
        """
        if not hasattr(self, "_column_units"):
            meta = pd.read_sql("SELECT table_name, column_name, unit FROM column_metadata", self.engine)
            self._column_units = {(t, c): u for t, c, u in meta.itertuples(index=False, name=None)}
        for column in dataframe.columns:
            unit = self._column_units[(table, column)]
            if unit not in units.NOT_CONVERTED:
                dataframe[column] = units.to_model_units(dataframe[column], unit, f"{table}.{column}")
        return dataframe

    def get_national_inventory_areas(self):
        """
        Retrieves the national land area by land category (CRT 2026 Table4.1 final area, 1990-2024) and
        converts its areas from kha to ha.

        Useful as a quick national check: the categories add up to the national land area (7,111,785 ha) in
        every year. Labels are the inventory's (e.g. "Grassland (managed)(2)"); the ``Area_kha`` column name is
        kept from 0.4.0 but holds ha after conversion.

        Returns:
            pandas.DataFrame: indexed by ``Year``, with ``Land_cover`` and ``Area_kha`` (in ha).
        """
        table = "NIR"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        dataframe = self._to_model_units(table, dataframe)

        return dataframe

    def get_national_forest_areas(self):
        """
        Retrieves national forest area data from the database and converts its areas from kha to ha.

        Returns:
            pandas.DataFrame: A DataFrame containing national forest area data with the area values scaled.
        """
        table = "forest_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe = self._to_model_units(table, dataframe)

        return dataframe

    def get_managed_forest_areas(self):
        """
        Retrieves cbm_runner 0.6.1's managed forest (FM + AF) area and forest fire by year, 1990-2070 (decision D6a;
        derived from cbm_runner's disturbance events, aligned with the NID and forest expert judgement).

        Returns:
            pandas.DataFrame: managed_forest_data in ha, indexed by year.
        """
        table = "managed_forest_data"
        dataframe = pd.read_sql("SELECT * FROM '%s'" % (table), self.engine, index_col=["year"])
        return self._to_model_units(table, dataframe)

    def get_forest_fire_rate(self):
        """
        Retrieves cbm_runner 0.6.1's scenario forest fire rate (per year) and the values it is calculated from
        (decision D6a).

        Returns:
            pandas.Series: the one row of forest_fire_rate.
        """
        table = "forest_fire_rate"
        dataframe = pd.read_sql("SELECT * FROM '%s'" % (table), self.engine)
        return self._to_model_units(table, dataframe).iloc[0]

    def get_national_settlement_areas(self):
        """
        Retrieves national settlement area data from the database and converts its areas from kha to ha.

        Returns:
            pandas.DataFrame: A DataFrame containing national settlement area data with the area values scaled.
        """
        table = "settlement_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe = self._to_model_units(table, dataframe)

        return dataframe

    def get_national_grassland_areas(self):
        """
        Retrieves national grassland area data from the database and converts its areas from kha to ha.

        Returns:
            pandas.DataFrame: A DataFrame containing national grassland area data with the area values scaled.
        """
        table = "grassland_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe = self._to_model_units(table, dataframe)

        return dataframe

    def get_national_cropland_areas(self):
        """
        Retrieves national cropland area data from the database and converts its areas from kha to ha.

        Returns:
            pandas.DataFrame: A DataFrame containing national cropland area data with the area values scaled.
        """
        table = "cropland_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe = self._to_model_units(table, dataframe)

        return dataframe

    def get_national_wetland_areas(self):
        """
        Retrieves national wetland area data from the database and converts its areas from kha to ha.

        Returns:
            pandas.DataFrame: A DataFrame containing national wetland area data with the area values scaled.
        """
        table = "wetland_data"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["year"],
        )

        dataframe = self._to_model_units(table, dataframe)

        return dataframe

    def get_soil_yield_mapping(self):
        """
        Retrieves forest soil yield mapping data from the database without scaling.

        Returns:
            pandas.DataFrame: A DataFrame containing forest soil yield mapping data.
        """
        table = "forest_soil_yield_mapping"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
        )

        return dataframe