"""
Transition Data Fetcher Documentation
======================================

The ``TransitionDataFetcher`` class is designed to process and analyze transition data from grasslands to various land uses based on specific scenarios. 
This class simplifies the process of extracting transition area data and supports detailed environmental and land use planning analyses.

``TransitionDataFetcher(transition_data)``

   Initializes the TransitionDataFetcher with a pandas DataFrame containing transition data between different land use types.

   :param transition_data: A pandas DataFrame containing transition matrices for various scenarios.

   **Methods**

   ``get_grassland_to_forest_areas()``

      Retrieves the areas transitioning from grasslands to forests across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to forests.
      :rtype: pandas.DataFrame

   ``get_grassland_to_grassland_areas()``

      Retrieves the areas remaining as grasslands across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas remaining as grasslands.
      :rtype: pandas.DataFrame

   ``get_grassland_to_wetland_areas()``

      Retrieves the areas transitioning from grasslands to wetlands across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to wetlands.
      :rtype: pandas.DataFrame

   ``get_grassland_to_cropland_areas()``

      Retrieves the areas transitioning from grasslands to croplands across all scenarios.

      :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas transitioning from grasslands to croplands.
      :rtype: pandas.DataFrame

   ``get_grassland_to_forest_soil_group_areas(spared_area_breakdown)``

      Retrieves the areas transitioning from grasslands to forests, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Forest``.
      :rtype: pandas.DataFrame

   ``get_grassland_to_wetland_soil_group_areas(spared_area_breakdown)``

      Retrieves the areas transitioning from grasslands to wetlands, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Wetland``.
      :rtype: pandas.DataFrame

   ``get_grassland_to_cropland_soil_group_areas(spared_area_breakdown)``

      Retrieves the areas transitioning from grasslands to croplands, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Cropland``.
      :rtype: pandas.DataFrame

   ``get_grassland_to_farmable_condition_soil_group_areas(spared_area_breakdown)``

      Retrieves the areas transitioning from grasslands to farmable conditions, categorized by soil groups, based on spared area breakdown.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_to_Farmable_Condition``.
      :rtype: pandas.DataFrame

   ``get_grassland_spared_organic_soil_group_areas(spared_area_breakdown)``

      Retrieves the spared organic grassland by soil group: spared organic land that stays in the grassland row,
      whether rewetted (drained -> rewet status) or spared in its current condition. It is placed in soil group 3.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_Spared_Organic``.
      :rtype: pandas.DataFrame

   ``get_grassland_to_landuse_soil_group_area(spared_area_breakdown)``

      Internal method to derive areas transitioning from grasslands to various land uses, categorized by soil groups, based on spared area breakdown. This method is used as a helper function for other public methods.
      Each soil group is filled with cropland, then forest, then farmable condition (mineral soil), each capped by what
      is left; the spared area the transition matrix does not account for is the spared organic land, which stays
      grassland and is placed in soil group 3. See docs/rewetting.md.

      :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
      :return: A pandas DataFrame with transition areas categorized by soil group.
      :rtype: pandas.DataFrame

   ``_derive_soil_group_area(soil_group, soil_group_pool, transition_area_dict)``

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
        """
        Initializes the TransitionDataFetcher with a pandas DataFrame containing transition data between different land use types.

        :param transition_data: A pandas DataFrame containing transition matrices for various scenarios.
        """
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
        Retrieves the areas remaining as grasslands across all scenarios.

        :return: A pandas DataFrame with columns ``scenario`` and ``area_ha`` indicating the areas remaining as grasslands.
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
    

    def get_grassland_spared_organic_soil_group_areas(self, spared_area_breakdown):
        """
        Retrieves the spared organic grassland by soil group: spared organic land that stays in the grassland row.
        That is the rewetted area (drained -> rewet-status shares, up to the scenario's rewetting target) plus any
        organic land spared beyond the target, which stays in its current condition (drained, or rewet status); the
        spared-area log separates the three (``rewet_grassland``, ``spared_drained_organic_grassland``,
        ``spared_rewetted_organic_grassland``). ``Grassland_to_Wetland`` is 0 by design (docs/rewetting.md).
        It is not a transition between land uses, so the transition matrix has no column for it: it is the spared
        area that forest, cropland and farmable condition (mineral soil only) do not take. It is placed in soil
        group 3, the group rewetting draws on.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with columns ``scenario``, ``soil_group``, and ``Grassland_Spared_Organic``.
        :rtype: pandas.DataFrame
        """
        transition_areas_by_soil_group = self.get_grassland_to_landuse_soil_group_area(spared_area_breakdown)

        columns = ["scenario", "soil_group", "Grassland_Spared_Organic"]

        return transition_areas_by_soil_group[columns]


    #: Transitions split by soil group, in the order each soil group is filled.
    SOIL_GROUP_TRANSITIONS = ("Grassland_to_Cropland", "Grassland_to_Forest", "Grassland_to_Farmable_Condition")

    def get_grassland_to_landuse_soil_group_area(self, spared_area_breakdown):
        """
        Internal method to derive areas transitioning from grasslands to various land uses, categorized by soil groups,
        based on spared area breakdown. This method is used as a helper function for other public methods.

        Each scenario's spared area by soil group (the breakdown) is filled with the transition matrix's areas, soil
        group 1 first, then 2, then 3: in each group cropland, then forest, then farmable condition, each capped by
        what is left in the group and by what is still to place. The spared area the matrix does not account for is
        the spared organic land (it stays grassland); it is placed in soil group 3 (``Grassland_Spared_Organic``). With the
        breakdown and the matrix consistent, each soil group's columns add up to its spared area.
        ``Grassland_to_Wetland`` is kept as a column and is always 0 by design. A soil group with no rows counts as
        0 ha.

        :param spared_area_breakdown: A pandas DataFrame detailing the breakdown of spared areas by soil group.
        :return: A pandas DataFrame with transition areas categorized by soil group.
        :rtype: pandas.DataFrame
        """
        # Select only numeric columns
        numeric_df = spared_area_breakdown.select_dtypes(include=[float, int])

        grouped_df = numeric_df.groupby(['Scenario','soil_group']).sum()
        soil_groups = list(grouped_df.index.levels[1])

        data = []
        for sc in grouped_df.index.levels[0]:
            # Soil groups (a soil group with no rows for this scenario counts as 0 ha)
            soil_pool_dict = {
                f"sg_{soil_group}": float(grouped_df['area_ha'].get((sc, soil_group), 0.0))
                for soil_group in soil_groups
            }

            # Transition values (a column the matrix does not have counts as 0)
            transition_dict = {
                column: float(self.transition_matrix.at[sc, column]) if column in self.transition_matrix.columns else 0.0
                for column in ("Grassland_to_Forest", "Grassland_to_Wetland", "Grassland_to_Cropland",
                               "Grassland_to_Farmable_Condition")
            }

            # Spared area not accounted for by the matrix: spared organic land, which stays grassland
            transition_dict["Grassland_Spared_Organic"] = max(
                0.0, sum(soil_pool_dict.values()) - sum(transition_dict.values()))

            if sum(soil_pool_dict.values()) == 0:
                print(f"Sum of soil group areas for scenario {sc} is equal to 0. Assuming sparead area is Soil Group 3")

                for soil_group in soil_groups:
                    row = {"scenario": sc, "soil_group": soil_group}
                    for column in self._COLUMNS:
                        row[column] = transition_dict[column] if soil_group == 3 else 0
                    data.append(row)

            else:
                for soil_group in soil_groups:

                    soil_group_area_dict = self._derive_soil_group_area(soil_group, soil_pool_dict, transition_dict)

                    row = {"scenario": sc, "soil_group": soil_group}
                    row.update({column: soil_group_area_dict[column] for column in self._COLUMNS})

                    data.append(row)


        return pd.DataFrame(data, columns=["scenario", "soil_group", *self._COLUMNS])

    _COLUMNS = ("Grassland_to_Forest", "Grassland_to_Wetland", "Grassland_to_Cropland",
                "Grassland_to_Farmable_Condition", "Grassland_Spared_Organic")


    def _derive_soil_group_area(self, soil_group, soil_group_pool, transition_area_dict):
        """
        Internal helper method to calculate the allocation of transition areas by soil group.

        Cropland, then forest, then farmable condition each take ``min(left in the group, still to place)``. In soil
        group 3 the spared organic land (stays grassland) then takes what is left, up to the scenario's amount.
        ``soil_group_pool`` and ``transition_area_dict`` are reduced by what is placed.

        :param soil_group: The soil group identifier.
        :param soil_group_pool: A dictionary containing available areas for each soil group.
        :param transition_area_dict: A dictionary containing the areas allocated for transition to different land uses.
        :return: A dictionary with updated transition area allocations by soil group.
        :rtype: dict
        """
        transition_area_allocations = {column: 0 for column in self._COLUMNS}

        sg_key = f"sg_{soil_group}"

        transitions = list(self.SOIL_GROUP_TRANSITIONS)
        if soil_group == 3:
            transitions.append("Grassland_Spared_Organic")

        for transition in transitions:
            if transition_area_dict[transition] > 0:
                available_area = min(soil_group_pool[sg_key], transition_area_dict[transition])
                transition_area_allocations[transition] = available_area
                soil_group_pool[sg_key] -= available_area
                transition_area_dict[transition] -= available_area

        return transition_area_allocations
