from landcover_assignment.resource_manager.data_loader import Loader

def main():
    loader = Loader()
    print(loader.national_inventory_areas())
    print(loader.national_forest_areas()())
    print(loader.national_cropland_areas()())
    print(loader.national_grassland_areas()())
    print(loader.national_wetland_areas()())
    print(loader.national_settlement_areas()())
    print(loader.forest_soil_yield_mapping())

if __name__ == '__main__':
    main()