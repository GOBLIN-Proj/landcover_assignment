"""
Scenario Data Fetcher Documentation
====================================

The ``ScenarioDataFetcher`` class is designed to extract specific pieces of information from a scenario dataset. It enables the retrieval of land use proportions, harvest proportions, afforestation end years, and other scenario-specific data.

.. class:: ScenarioDataFetcher(scenario_data, validate_on_init=False)

   Initializes the ScenarioDataFetcher class with a pandas DataFrame containing scenario data.

   :param scenario_data: A pandas DataFrame containing various scenarios and their respective data points.
   :param validate_on_init: A boolean indicating whether to validate proportions on initialization.

   **Methods**

   .. method:: get_wetland_proportion(scenario)

      Retrieves the proportion of wetland area for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The wetland proportion as a float.
      :rtype: float

   .. method:: get_forest_proportion(scenario)

      Retrieves the proportion of forest area for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The forest proportion as a float.
      :rtype: float

   .. method:: get_cropland_proportion(scenario)

      Retrieves the proportion of cropland area for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The cropland proportion as a float.
      :rtype: float

   .. method:: get_conifer_proportion(scenario)

      Retrieves the proportion of conifer trees for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The conifer proportion as a float.
      :rtype: float

   .. method:: get_broadleaf_proportion(scenario)

      Retrieves the proportion of broadleaf trees for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The broadleaf proportion as a float.
      :rtype: float

   .. method:: get_broadleaf_harvest_proportion(scenario)

      Retrieves the harvest proportion of broadleaf trees for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The broadleaf harvest proportion as a float.
      :rtype: float

   .. method:: get_conifer_harvest_proportion(scenario)

      Retrieves the harvest proportion of conifer trees for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The conifer harvest proportion as a float.
      :rtype: float

   .. method:: get_conifer_thinned_proportion(scenario)

      Retrieves the thinned proportion of conifer trees for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The conifer thinned proportion as a float.
      :rtype: float

   .. method:: get_afforest_end_year(scenario)

      Retrieves the end year for afforestation activities for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :return: The afforestation end year as an integer.
      :rtype: int

   .. method:: get_catchment_name()

      Retrieves the name of the catchment area defined in the scenario data.

      :return: The catchment name as a string.
      :rtype: str

   .. method:: get_scenario_list()

      Retrieves a list of all scenarios present in the scenario data.

      :return: A list of scenario identifiers.
      :rtype: list

   .. method:: validate_proportions(scenario)

      Validates that the sum of cropland, forestland, and rewetted area proportions equals 1 for a specified scenario.

      :param scenario: The scenario identifier as a string.
      :raises ValueError: If the proportions do not sum to 1.

   .. method:: validate_all_proportions()

      Validates that the proportions for all scenarios in the dataset sum to 1.

      :raises ValueError: If any scenario has invalid proportions.

"""
import pandas as pd

class ScenarioDataFetcher:
    def __init__(self, scenario_data, validate_on_init=False):
        """
        Initializes the ScenarioDataFetcher class with a pandas DataFrame containing scenario data.

        :param scenario_data: A pandas DataFrame containing various scenarios and their respective data points.
        :param validate_on_init: A boolean indicating whether to validate proportions on initialization.
        """
        self.scenario_data = scenario_data

        if validate_on_init:
            self.validate_all_spared_area_proportions()
            self.validate_all_species_proportions()
            self.validate_all_forest_thinning_and_harvest_proportions()


    def validate_forest_thinning_and_harvest_proportions(self, scenario):
        """
        Validates that the sum of conifer and broadleaf tree proportions equals 1.

        :param scenario: The scenario identifier to validate.
        :type scenario: int or str
        :raises ValueError: If the proportions do not sum to 1.
        """
        
        conifer_harvest = self.get_conifer_harvest_proportion(scenario)
        broadleaf_harvest = self.get_broadleaf_harvest_proportion(scenario)
        conifer_thinned = self.get_conifer_thinned_proportion(scenario)

        #if conifer harvest is less than 0 or greater than 1 return error 
        if conifer_harvest < 0 or conifer_harvest > 1:
            raise ValueError(
                f"Invalid conifer harvest proportion for scenario '{scenario}'. "
                f"Conifer harvest proportion must be between 0 and 1."
            )
        
        #if broadleaf harvest is less than 0 or greater than 1 return error
        if broadleaf_harvest < 0 or broadleaf_harvest > 1:
            raise ValueError(
                f"Invalid broadleaf harvest proportion for scenario '{scenario}'. "
                f"Broadleaf harvest proportion must be between 0 and 1."
            )
        
        #if conifer thinned is less than 0 or greater than 1 return error
        if conifer_thinned < 0 or conifer_thinned > 1:
            raise ValueError(
                f"Invalid conifer thinned proportion for scenario '{scenario}'. "
                f"Conifer thinned proportion must be between 0 and 1."
            )
        

    def validate_all_forest_thinning_and_harvest_proportions(self):
        """
        Validates that the proportions for all scenarios in the dataset sum to 1.

        :raises ValueError: If any scenario has invalid proportions.
        """
        scenarios = self.get_scenario_list()
        for scenario in scenarios:
            self.validate_forest_thinning_and_harvest_proportions(scenario)


    def validate_species_proportions(self, scenario):
        """
        Validates that the sum of conifer and broadleaf tree proportions equals 1.

        :param scenario: The scenario identifier to validate.
        :type scenario: int or str
        :raises ValueError: If the proportions do not sum to 1.
        """
        
        conifer = self.get_conifer_proportion(scenario)
        broadleaf = self.get_broadleaf_proportion(scenario)

        total = conifer + broadleaf

        if total !=1:
            raise ValueError(
                f"Invalid tree species proportions for scenario '{scenario}'. "
                f"The sum of conifer ({conifer}) and broadleaf ({broadleaf}) is {total}, total must be 1."
            )
    
    def validate_all_species_proportions(self):
        """
        Validates that the proportions for all scenarios in the dataset sum to 1.

        :raises ValueError: If any scenario has invalid proportions.
        """
        scenarios = self.get_scenario_list()
        for scenario in scenarios:
            self.validate_species_proportions(scenario)

    def validate_landuse_proportions(self, scenario):
        """
        Validates that the sum of cropland, forestland, and rewetted area proportions equals 1.

        :param scenario: The scenario identifier to validate.
        :type scenario: int or str
        :raises ValueError: If the proportions do not sum to 1.
        """
        
        crop = self.get_cropland_proportion(scenario)
        forest = self.get_forest_proportion(scenario)
        rewetted_area = self.get_rewetted_proportion(scenario)

        total = crop + forest + rewetted_area

        if total > 1:  #Allow less than 1, but not more
            raise ValueError(
                f"Invalid proportions for scenario '{scenario}'. "
                f"The sum of cropland ({crop}), forestland ({forest}), and rewetted area ({rewetted_area}) is {total}, total must be less than 1."
            )

    def validate_all_spared_area_proportions(self):
        """
        Validates that the proportions for all scenarios in the dataset sum to 1.

        :raises ValueError: If any scenario has invalid proportions.
        """
        scenarios = self.get_scenario_list()
        for scenario in scenarios:
            self.validate_landuse_proportions(scenario)


    def get_rewetted_proportion(self, scenario):
        """
        Retrieves the proportion of rewetted area for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The rewetted area proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Wetland area"].unique().item()


    def get_forest_proportion(self, scenario):
        """
        Retrieves the proportion of forest area for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The forest proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Forest area"].unique().item()
    

    def get_cropland_proportion(self, scenario):
        """
        Retrieves the proportion of cropland area for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The cropland proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Crop area"].unique().item()
    
    def get_conifer_proportion(self, scenario):
        """
        Retrieves the proportion of conifer trees for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The conifer proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Conifer proportion"].unique().item()
    
    def get_broadleaf_proportion(self, scenario):
        """
        Retrieves the proportion of broadleaf trees for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The broadleaf proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Broadleaf proportion"].unique().item()
    

    def get_broadleaf_harvest_proportion(self, scenario):
        """
        Retrieves the harvest proportion of broadleaf trees for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The broadleaf harvest proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Broadleaf harvest"].unique().item()
    

    def get_conifer_harvest_proportion(self, scenario):
        """
        Retrieves the harvest proportion of conifer trees for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The conifer harvest proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Conifer harvest"].unique().item()
    

    def get_conifer_thinned_proportion(self, scenario):
        """
        Retrieves the thinned proportion of conifer trees for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The conifer thinned proportion as a float.
        :rtype: float
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Conifer thinned"].unique().item()
    

    def get_afforest_end_year(self, scenario):
        """
        Retrieves the end year for afforestation activities for a specified scenario.

        :param scenario: The scenario identifier as a string.
        :return: The afforestation end year as an integer.
        :rtype: int
        """
        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Afforest year"].unique().item()
    

    def get_catchment_name(self):
        """
        Retrieves the name of the catchment area defined in the scenario data.

        :return: The catchment name as a string.
        :rtype: str
        """
        return self.scenario_data["Catchment"].unique().item()
    

    def get_scenario_list(self):
        """
        Retrieves a list of all scenarios present in the scenario data.

        :return: A list of scenario identifiers.
        :rtype: list
        """
        return self.scenario_data["Scenarios"].unique().tolist()
