from landcover_assignment.national_landcover import NationalLandCover
import os 
import pandas as pd

def main():

    path = "./data/"
    #spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    #spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    landcover = NationalLandCover()

    baseline = 2020

    print("Wetland")
    print(f"area: {landcover.get_landuse_area('wetland',baseline)}")
    print(f"mineral share: {landcover.get_share_mineral('wetland',baseline)}")
    print(f"organic share: {landcover.get_share_organic('wetland',baseline)}")
    print(f"organo mineral: {landcover.get_share_organic_mineral('wetland',baseline)}")
    print(f"share_rewetted_in_mineral: {landcover.get_share_rewetted_in_mineral('wetland',baseline)}")
    print(f"share_rewetted_in_organic: {landcover.get_share_rewetted_in_organic('wetland',baseline)}")
    print(f"share_peat_extraction: {landcover.get_share_peat_extraction('wetland',baseline)}")
    print(f"burned: {landcover.get_share_burnt('wetland',baseline)}")
    print("#"*20)

    print("Cropland")
    print(f"area: {landcover.get_landuse_area('cropland',baseline)}")
    print(f"mineral share: {landcover.get_share_mineral('cropland',baseline)}")
    print(f"organic share: {landcover.get_share_organic('cropland',baseline)}")
    print(f"organo mineral: {landcover.get_share_organic_mineral('cropland',baseline)}")
    print(f"share_rewetted_in_mineral: {landcover.get_share_rewetted_in_mineral('cropland',baseline)}")
    print(f"share_rewetted_in_organic: {landcover.get_share_rewetted_in_organic('cropland',baseline)}")
    print(f"share_peat_extraction: {landcover.get_share_peat_extraction('cropland',baseline)}")
    print(f"burned: {landcover.get_share_burnt('cropland',baseline)}")
    print("#"*20)

    print("Forest")
    print(f"area: {landcover.get_landuse_area('forest',baseline)}")
    print(f"mineral share: {landcover.get_share_mineral('forest',baseline)}")
    print(f"organic share: {landcover.get_share_organic('forest',baseline)}")
    print(f"organo mineral: {landcover.get_share_organic_mineral('forest',baseline)}")
    print(f"share_rewetted_in_mineral: {landcover.get_share_rewetted_in_mineral('forest',baseline)}")
    print(f"share_rewetted_in_organic: {landcover.get_share_rewetted_in_organic('forest',baseline)}")
    print(f"share_peat_extraction: {landcover.get_share_peat_extraction('forest',baseline)}")
    print(f"burned: {landcover.get_share_burnt('forest',baseline)}")
    print("#"*20)
    
    print("Grassland")
    print(f"area: {landcover.get_landuse_area('grassland',baseline, grassland_area)}")
    print(f"mineral share: {landcover.get_share_mineral('grassland',baseline, grassland_area)}")
    print(f"organic share: {landcover.get_share_organic('grassland',baseline, grassland_area)}")
    print(f"organo mineral: {landcover.get_share_organic_mineral('grassland',baseline, grassland_area)}")
    print(f"share_rewetted_in_mineral: {landcover.get_share_rewetted_in_mineral('grassland',baseline, grassland_area)}")
    print(f"share_rewetted_in_organic: {landcover.get_share_rewetted_in_organic('grassland',baseline, grassland_area)}")
    print(f"share_peat_extraction: {landcover.get_share_peat_extraction('grassland',baseline, grassland_area)}")
    print(f"burned: {landcover.get_share_burnt('grassland',baseline, grassland_area)}")
    print("#"*20)

    print("Settlement")
    print(f"area: {landcover.get_landuse_area('settlement',baseline)}")
    print(f"mineral share: {landcover.get_share_mineral('settlement',baseline)}")
    print(f"organic share: {landcover.get_share_organic('settlement',baseline)}")
    print(f"organo mineral: {landcover.get_share_organic_mineral('settlement',baseline)}")
    print(f"share_rewetted_in_mineral: {landcover.get_share_rewetted_in_mineral('settlement',baseline)}")
    print(f"share_rewetted_in_organic: {landcover.get_share_rewetted_in_organic('settlement',baseline)}")
    print(f"share_peat_extraction: {landcover.get_share_peat_extraction('settlement',baseline)}")
    print(f"burned: {landcover.get_share_burnt('settlement',baseline)}")
    print("#"*20)

if __name__ == '__main__':
    main()