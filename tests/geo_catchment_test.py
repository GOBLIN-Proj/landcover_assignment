from landcover_assignment.geo_landcover_assignment.catchment_landcover import CatchmentLandCover
import os 
import pandas as pd

def main():

    path = "./geo_data/"
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    landcover = CatchmentLandCover()

    df = landcover.get_catchment_grassland_area("blackwater", grassland_area)

    print(df)

    print("Grassland")
    print(landcover.get_landuse_area("grassland","blackwater", grassland_area))
    print(landcover.get_share_mineral("grassland","blackwater", grassland_area))
    print(landcover.get_share_organic("grassland","blackwater", grassland_area))
    print(landcover.get_share_organic_mineral("grassland","blackwater", grassland_area))
    print(landcover.get_share_burnt("grassland","blackwater", grassland_area))
    print("#"*20)

    print("Wetland")
    print(landcover.get_landuse_area("wetland","blackwater"))
    print(landcover.get_share_mineral("wetland","blackwater"))
    print(landcover.get_share_organic("wetland","blackwater"))
    print(landcover.get_share_organic_mineral("wetland","blackwater"))
    print(landcover.get_share_burnt("wetland","blackwater"))
    print("#"*20)

    print("Cropland")
    print(landcover.get_landuse_area("cropland","blackwater"))
    print(landcover.get_share_mineral("cropland","blackwater"))
    print(landcover.get_share_organic("cropland","blackwater"))
    print(landcover.get_share_organic_mineral("cropland","blackwater"))
    print(landcover.get_share_burnt("cropland","blackwater"))
    print("#"*20)

    print("Forest")
    print(landcover.get_landuse_area("forest","blackwater"))
    print(landcover.get_share_mineral("forest","blackwater"))
    print(landcover.get_share_organic("forest","blackwater"))
    print(landcover.get_share_organic_mineral("forest","blackwater"))
    print(landcover.get_share_burnt("forest","blackwater"))
    print("#"*20)

    print("Soil Group")
    print(landcover.get_area_with_organic_potential(spared_area_breakdown, spared_area, 1))

    print("#"*20)
    print("Spared Area")

    print(landcover.get_total_spared_area(spared_area, 0))
    print("#"*20)

    print("Derived Grassland")
    print(landcover.get_derived_catchment_grassland_area(grassland_area))
    
if __name__ == '__main__':
    main()