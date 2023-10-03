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
