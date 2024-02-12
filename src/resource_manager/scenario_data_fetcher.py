"""
Scenario Data Fetcher Documentation
====================================

The ``ScenarioDataFetcher`` class is designed to extract specific pieces of information from a scenario dataset. It enables the retrieval of land use proportions, harvest proportions, afforestation end years, and other scenario-specific data.

.. class:: ScenarioDataFetcher(scenario_data)

   Initializes the ScenarioDataFetcher class with a pandas DataFrame containing scenario data.

   :param scenario_data: A pandas DataFrame containing various scenarios and their respective data points.

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

"""
import pandas as pd

class ScenarioDataFetcher:
    def __init__(self, scenario_data):
        self.scenario_data = scenario_data

    def get_wetland_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Wetland area"].unique().item()


    def get_forest_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Forest area"].unique().item()
    

    def get_cropland_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Crop area"].unique().item()
    
    def get_conifer_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Conifer proportion"].unique().item()
    
    def get_broadleaf_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Broadleaf proportion"].unique().item()
    

    def get_broadleaf_harvest_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Broadleaf harvest"].unique().item()
    
    def get_conifer_harvest_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Conifer harvest"].unique().item()
    
    def get_conifer_thinned_proportion(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Conifer thinned"].unique().item()
    
    def get_afforest_end_year(self, scenario):

        scenario_subset = self.scenario_data.loc[
                (self.scenario_data["Scenarios"] == scenario)
            ]
        
        return scenario_subset["Afforest year"].unique().item()
    
    def get_catchment_name(self):
        
        return self.scenario_data["Catchment"].unique().item()
    
    def get_scenario_list(self):
        return self.scenario_data["Scenarios"].unique().tolist()
