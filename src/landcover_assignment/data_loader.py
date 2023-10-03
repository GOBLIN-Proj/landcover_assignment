from landcover_assignment.database_manager import DataManager


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
