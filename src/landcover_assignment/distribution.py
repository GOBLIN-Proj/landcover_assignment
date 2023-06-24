from landcover_assignment.landcover_data_manager import DistributionManager

class LandDistribution:

    @classmethod
    def land_distribution(cls,land_use, current_area, new_area):

        data_manager_class = DistributionManager()

        land = data_manager_class.land_distribution

        
        land_df = current_area.loc[(current_area["land_use"]==land_use)]


        land["area_ha"] = land_df["area_ha"].item() + new_area

        if land_use == "grassland":
            return None

        elif land_use == "wetland":
            land["share_organic"] = ((land_df["area_ha"].item() * land_df["share_organic"].item()) + new_area) / land["area_ha"]
            land["share_mineral"] = (land_df["area_ha"].item() * land_df["share_mineral"].item())/land["area_ha"]
            land["share_rewetted_in_mineral"] = (land_df["area_ha"].item() * land_df["share_rewetted_in_mineral"].item())/land["area_ha"]
            land["share_rewetted_in_organic"] = ((land_df["area_ha"].item() * land_df["share_rewetted_in_organic"].item()) + new_area)/land["area_ha"]
            land["share_peat_extraction"] = (land_df["area_ha"].item() * land_df["share_peat_extraction"].item())/land["area_ha"]
            land["share_burnt"] = land_df["share_burnt"].item()

        elif land_use != "farmable_condition": 
            land["share_organic"] = (land_df["area_ha"].item() * land_df["share_organic"].item())/land["area_ha"]
            land["share_mineral"] = ((land_df["area_ha"].item() * land_df["share_mineral"].item()) + new_area) / land["area_ha"]
            land["share_rewetted_in_mineral"] = land_df["share_rewetted_in_mineral"].item()
            land["share_rewetted_in_organic"] = land_df["share_rewetted_in_organic"].item()
            land["share_peat_extraction"] = land_df["share_peat_extraction"].item()
            land["share_burnt"] = land_df["share_burnt"].item()
    
        else: 

            if land["area_ha"] != 0: 
                land["share_mineral"] = ((land_df["area_ha"].item() * land_df["share_mineral"].item()) + new_area) / land["area_ha"]
            else:
                land["share_mineral"] = land_df["share_mineral"].item()

        return land
        
    @classmethod
    def grassland_distriubtion(cls, current_area, mineral_area, organic_area):

        data_manager_class = DistributionManager()

        land = data_manager_class.land_distribution

        land_df = current_area.loc[(current_area["land_use"]=="grassland")]

        current_mineral = land_df["area_ha"].item() * land_df["share_mineral"].item()
        current_organic = land_df["area_ha"].item() * land_df["share_organic"].item()

        remaining_mineral = current_mineral - mineral_area
        remaining_organic = current_organic - organic_area
        total_remaining = remaining_mineral + remaining_organic

        land["area_ha"] = total_remaining
        land["share_organic"] = remaining_organic/total_remaining
        land["share_mineral"] = remaining_mineral/total_remaining
        land["share_rewetted_in_mineral"] = land_df["share_rewetted_in_mineral"].item()
        land["share_rewetted_in_organic"] = land_df["share_rewetted_in_organic"].item()
        land["share_peat_extraction"] = land_df["share_peat_extraction"].item()
        land["share_burnt"] = land_df["share_burnt"].item()
    
        return land


