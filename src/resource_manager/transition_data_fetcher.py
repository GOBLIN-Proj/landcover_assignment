"""
Transition Data Fetcher Documentation
======================================

The ``TransitionDataFetcher`` class is designed to process and analyze transition data from grasslands to various land uses based on specific scenarios. 
This class simplifies the process of extracting transition area data and supports detailed environmental and land use planning analyses.

.. class:: TransitionDataFetcher(transition_data)

   Initializes the TransitionDataFetcher with a pandas DataFrame containing transition data between different land use types.

   :param transition_data: A pandas DataFrame containing transition matrices for various scenarios.

   **Methods**

   .. method:: get_grassland_to_forest_areas()

      Retrieves the areas transitioning from grasslands to forests across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to forests.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_grassland_areas()

      Retrieves the areas remaining as grasslands across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas remaining as grasslands.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_wetland_areas()

      Retrieves the areas transitioning from grasslands to wetlands across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to wetlands.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_cropland_areas()

      Retrieves the areas transitioning from grasslands to croplands across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to croplands.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_forest_soil_group_areas(spared_area_breakdown)

      Retrieves the areas transitioning from grasslands to forests, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Forest``.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_wetland_soil_group_areas(spared_area_breakdown)

      Retrieves the areas transitioning from grasslands to wetlands, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Wetland``.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_cropland_soil_group_areas(spared_area_breakdown)

      Retrieves the areas transitioning from grasslands to croplands, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Cropland``.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_farmable_condition_soil_group_areas(spared_area_breakdown)

      Retrieves the areas transitioning from grasslands to farmable conditions, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Farmable_Condition``.
      :rtype: pandas.DataFrame

   .. method:: get_grassland_to_landuse_soil_group_area(spared_area_breakdown)

      Internal method to derive areas transitioning from grasslands to various land uses, categorized by soil groups, based on spared area breakdown. This method is used as a helper function for other public methods.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with transition areas categorized by soil group.
      :rtype: pandas.DataFrame

   .. method:: _derive_soil_group_area(soil_group, soil_group_pool, transition_area_dict)

      Internal helper method to calculate the allocation of transition areas by soil group.

      :param soil_group: The soil group identifier.
      :param soil_group_pool: A dictionary containing available areas for each soil group.
      :param transition_area_dict: A dictionary containing the areas allocated for transition to different land uses.
      :return: A dictionary with updated transition area allocations by soil group.
      :rtype: dict
"""

import pandas as pd

class TransitionDataFetcher:
    def __init__(self, transition_data):
        self.transition_matrix = transition_data


    def get_grassland_to_forest_areas(self):
        """
        Retrieves the areas transitioning from grasslands to forests across all scenarios.

        :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to forests.
        :rtype: pandas.DataFrame

        """
        data =[]
        for i in self.transition_matrix.index:

            row = {
                "scenario": i if i >= 0 else -1,
                "area_ha": self.transition_matrix.at[i, "Grassland_to_Forest"]
            }

            data.append(row)

        return pd.DataFrame(data)
    

    def get_grassland_to_grassland_areas(self):
        """
        Retrieves the areas transitioning from grasslands to wetlands across all scenarios.

        :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to wetlands.
        :rtype: pandas.DataFrame
        """
        data =[]
        for i in self.transition_matrix.index:

            row = {
                "scenario": i if i >= 0 else -1,
                "area_ha": self.transition_matrix.at[i, "Grassland_to_Grassland"]
            }

            data.append(row)

        return pd.DataFrame(data)
    
    
    def get_grassland_to_wetland_areas(self):
        """
        Retrieves the areas transitioning from grasslands to wetlands across all scenarios.

        :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to wetlands.
        :rtype: pandas.DataFrame
        """

        data =[]
        for i in self.transition_matrix.index:

            row = {
                "scenario": i if i >= 0 else -1,
                "area_ha": self.transition_matrix.at[i, "Grassland_to_Wetland"]
            }

            data.append(row)

        return pd.DataFrame(data)
    

    def get_grassland_to_cropland_areas(self):
        """
         Retrieves the areas transitioning from grasslands to croplands across all scenarios.

        :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to croplands.
        :rtype: pandas.DataFrame
        """
        data =[]
        for i in self.transition_matrix.index:

            row = {
                "scenario": i if i >= 0 else -1,
                "area_ha": self.transition_matrix.at[i, "Grassland_to_Cropland"]
            }

            data.append(row)

        return pd.DataFrame(data)
    

    def get_grassland_to_forest_soil_group_areas(self, spared_area_breakdown):
        """
        Retrieves the areas transitioning from grasslands to forests, categorized by soil groups, based on spared area breakdown.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Forest``.
        :rtype: pandas.DataFrame
        """

        transition_areas_by_soil_group = self.get_grassland_to_landuse_soil_group_area(spared_area_breakdown)

        columns = ["scenario", "soil_group", "Grassland_to_Forest"]

        return transition_areas_by_soil_group[columns]
    

    def get_grassland_to_wetland_soil_group_areas(self, spared_area_breakdown):
        """
         Retrieves the areas transitioning from grasslands to wetlands, categorized by soil groups, based on spared area breakdown.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Wetland``.
        :rtype: pandas.DataFrame
        """
        
        transition_areas_by_soil_group = self.get_grassland_to_landuse_soil_group_area(spared_area_breakdown)

        columns = ["scenario", "soil_group", "Grassland_to_Wetland"]

        return transition_areas_by_soil_group[columns]
    

    def get_grassland_to_cropland_soil_group_areas(self, spared_area_breakdown):
        """
        Retrieves the areas transitioning from grasslands to croplands, categorized by soil groups, based on spared area breakdown.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Cropland``.
        :rtype: pandas.DataFrame
        """
        transition_areas_by_soil_group = self.get_grassland_to_landuse_soil_group_area(spared_area_breakdown)

        columns = ["scenario", "soil_group", "Grassland_to_Cropland"]

        return transition_areas_by_soil_group[columns]
    

    def get_grassland_to_farmable_condition_soil_group_areas(self, spared_area_breakdown):
        """
         Retrieves the areas transitioning from grasslands to farmable conditions, categorized by soil groups, based on spared area breakdown.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Farmable_Condition``.
        :rtype: pandas.DataFrame
        """
        transition_areas_by_soil_group = self.get_grassland_to_landuse_soil_group_area(spared_area_breakdown)

        columns = ["scenario", "soil_group", "Grassland_to_Farmable_Condition"]

        return transition_areas_by_soil_group[columns]
    

    def get_grassland_to_landuse_soil_group_area(self, spared_area_breakdown):
        """
         Internal method to derive areas transitioning from grasslands to various land uses, categorized by soil groups, based on spared area breakdown. This method is used as a helper function for other public methods.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with transition areas categorized by soil group.
        :rtype: pandas.DataFrame
        """
        # Select only numeric columns 
        numeric_df = spared_area_breakdown.select_dtypes(include=[float, int])

        grouped_df = numeric_df.groupby(['Scenario','soil_group']).sum()

        data = []
        for sc in grouped_df.index.levels[0]:
            #Soil groups 
            soil_pool_dict = {
                "sg_1":grouped_df.at[(sc, 1), 'area_ha'],
                "sg_2":grouped_df.at[(sc, 2), 'area_ha'],
                "sg_3":grouped_df.at[(sc, 3), 'area_ha']
            }

            #transition values 
            transition_dict = {
                "Grassland_to_Forest": self.transition_matrix.at[sc, "Grassland_to_Forest"],
                "Grassland_to_Wetland": self.transition_matrix.at[sc, "Grassland_to_Wetland"],
                "Grassland_to_Cropland": self.transition_matrix.at[sc, "Grassland_to_Cropland"],
                "Grassland_to_Farmable_Condition": self.transition_matrix.at[sc, "Grassland_to_Farmable_Condition"]
            }
            
            if sum(soil_pool_dict.values()) == 0:
                print(f"Sum of soil group areas for scenario {sc} is equal to 0. Assuming sparead area is Soil Group 3")

                for soil_group in grouped_df.index.levels[1]:
                    if soil_group == 3:
                        row = {
                            "scenario": sc,
                            "soil_group": 3,
                            "Grassland_to_Forest": transition_dict["Grassland_to_Forest"],
                            "Grassland_to_Wetland": transition_dict["Grassland_to_Wetland"],
                            "Grassland_to_Cropland": transition_dict["Grassland_to_Cropland"],
                            "Grassland_to_Farmable_Condition": transition_dict["Grassland_to_Farmable_Condition"],
                        }
                    else: 
                        row = {
                            "scenario": sc,
                            "soil_group": soil_group,
                            "Grassland_to_Forest": 0,
                            "Grassland_to_Wetland": 0,
                            "Grassland_to_Cropland": 0,
                            "Grassland_to_Farmable_Condition": 0,
                        }
                    data.append(row)

            else:
                for soil_group in grouped_df.index.levels[1]:

                    soil_group_area_dict = self._derive_soil_group_area(soil_group, soil_pool_dict, transition_dict)


                    row = {
                        "scenario": sc,
                        "soil_group": soil_group,
                        "Grassland_to_Forest": soil_group_area_dict["Grassland_to_Forest"],
                        "Grassland_to_Wetland": soil_group_area_dict["Grassland_to_Wetland"],
                        "Grassland_to_Cropland": soil_group_area_dict["Grassland_to_Cropland"],
                        "Grassland_to_Farmable_Condition": soil_group_area_dict["Grassland_to_Farmable_Condition"],
                    }

                    data.append(row)


        return pd.DataFrame(data)
    

    def _derive_soil_group_area(self, soil_group, soil_group_pool, transition_area_dict):
        """
        _derive_soil_group_area(soil_group, soil_group_pool, transition_area_dict)

        Internal helper method to calculate the allocation of transition areas by soil group.

        :param soil_group: The soil group identifier.
        :param soil_group_pool: A dictionary containing available areas for each soil group.
        :param transition_area_dict: A dictionary containing the areas allocated for transition to different land uses.
        :return: A dictionary with updated transition area allocations by soil group.
      :rtype: dict
        """
        transition_area_allocations = {
            "Grassland_to_Forest": 0,
            "Grassland_to_Wetland": 0,
            "Grassland_to_Cropland": 0,
            "Grassland_to_Farmable_Condition": 0
        }

        sg_key = f"sg_{soil_group}"

        # Handle transitions for soil group 3 with priority for Wetland
        if soil_group == 3:
            # Wetland has priority for soil group 3
            if transition_area_dict["Grassland_to_Wetland"] > 0:
                available_area = min(soil_group_pool[sg_key], transition_area_dict["Grassland_to_Wetland"])
                transition_area_allocations["Grassland_to_Wetland"] = available_area
                soil_group_pool[sg_key] -= available_area
                transition_area_dict["Grassland_to_Wetland"] -= available_area

            # Process Cropland and Forest transitions after Wetland
            for transition in ["Grassland_to_Cropland", "Grassland_to_Forest"]:
                available_area = min(soil_group_pool[sg_key], transition_area_dict[transition])
                transition_area_allocations[transition] = available_area
                soil_group_pool[sg_key] -= available_area
                transition_area_dict[transition] -= available_area

        # Handle transitions for soil groups 1 and 2 without Wetland
        else:
            for transition in ["Grassland_to_Cropland", "Grassland_to_Forest"]:
                if transition_area_dict[transition] > 0:
                    available_area = min(soil_group_pool[sg_key], transition_area_dict[transition])
                    transition_area_allocations[transition] = available_area
                    soil_group_pool[sg_key] -= available_area
                    transition_area_dict[transition] -= available_area

        # Farmable Condition is considered if there is an explicit transition area for it and after other transitions
        if transition_area_dict["Grassland_to_Farmable_Condition"] > 0:
            available_area = soil_group_pool[sg_key]  # Remaining area goes to Farmable Condition
            transition_area_allocations["Grassland_to_Farmable_Condition"] = available_area
            soil_group_pool[sg_key] -= available_area 

        return transition_area_allocations



        

            
            


            


        