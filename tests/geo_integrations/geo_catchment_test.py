from landcover_assignment.geo_landcover_assignment.catchment_landcover import CatchmentLandCover
import os 
import pandas as pd

def main():

    path = "../geo_data/"
    catchment_names = pd.read_csv(os.path.join(path, "catchment_names.csv"))
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    landcover = CatchmentLandCover()

    for name in catchment_names["Catchment"]:
        print(name)
        print("#"*20)
        df = landcover.get_catchment_grassland_area(name, grassland_area)

        print(df)

        print("Grassland")
        print(landcover.get_landuse_area("grassland",name, grassland_area))
        print(landcover.get_share_mineral("grassland",name, grassland_area))
        print(landcover.get_share_organic("grassland",name, grassland_area))
        print(landcover.get_share_organic_mineral("grassland",name, grassland_area))
        print(landcover.get_share_burnt("grassland",name, grassland_area))
        print("#"*20)

        print("Wetland")
        print(landcover.get_landuse_area("wetland",name))
        print(landcover.get_share_mineral("wetland",name))
        print(landcover.get_share_organic("wetland",name))
        print(landcover.get_share_organic_mineral("wetland",name))
        print(landcover.get_share_burnt("wetland",name))
        print("#"*20)

        print("Cropland")
        print(landcover.get_landuse_area("cropland",name))
        print(landcover.get_share_mineral("cropland",name))
        print(landcover.get_share_organic("cropland",name))
        print(landcover.get_share_organic_mineral("cropland",name))
        print(landcover.get_share_burnt("cropland",name))
        print("#"*20)

        print("Forest")
        print(landcover.get_landuse_area("forest",name))
        print(landcover.get_share_mineral("forest",name))
        print(landcover.get_share_organic("forest",name))
        print(landcover.get_share_organic_mineral("forest",name))
        print(landcover.get_share_burnt("forest",name))
        print("#"*20)

        print("Soil Group")
        print(landcover.get_area_with_organic_potential(spared_area_breakdown, spared_area, 1))

        print("#"*20)
        print("Spared Area")

        print(landcover.get_total_spared_area(spared_area, 0))
        print("#"*20)

        print("Derived Grassland")
        print(landcover.get_derived_catchment_grassland_area(grassland_area))
        print("@"*20)
    
if __name__ == '__main__':
    main()