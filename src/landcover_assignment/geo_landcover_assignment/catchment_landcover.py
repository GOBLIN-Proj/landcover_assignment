"""
Catchment Land Cover
======================

This module provides a class for managing and analyzing land cover data within catchment areas. It integrates
various APIs and data sources to offer a comprehensive set of functionalities for land cover analysis.

Dependencies
------------
- ``catchment_data_api.catchment_data_api.CatchmentDataAPI``
- ``catchment_data_api.crops.Crops``
- ``resource_manager.data_loader.Loader``
- ``pandas`` as ``pd``

Classes
-------
.. class:: CatchmentLandCover()

   This class is designed to access and analyze land cover data across different land use types within catchment areas.
   It provides methods to calculate areas and shares of different land cover types, including forests, wetlands,
   croplands, and grasslands, based on catchment names.

    Methods:

   .. method:: get_catchment_forest_area(catchment)
      
      Calculates the total forest area within a specified catchment, categorized by cover and soil types.

   .. method:: get_catchment_peat_area(catchment)
      
      Calculates the total peat area within a specified catchment, grouped by cover and soil types.

   .. method:: get_catchment_crop_area(catchment)
      
      Calculates the total crop area within a specified catchment, grouped by cover and soil types.

   .. method:: get_catchment_grassland_area(catchment, total_grassland_area)
      
      Calculates the total grassland area within a specified catchment, grouped by cover and soil types.

   .. method:: get_landuse_area(landuse, catchment, grassland_area=None)
      
      Retrieves the total area for a specified land use within a catchment.

   .. method:: get_share_mineral(landuse, catchment, grassland_area=None)
      
      Calculates the share of mineral soil within a specified land use area in a catchment.

   .. method:: get_share_organic(landuse, catchment, grassland_area=None)
      
      Calculates the share of organic soil within a specified land use area in a catchment.

   .. method:: get_share_organic_mineral(landuse, catchment, grassland_area=None)
      
      Calculates the share of organic-mineral mixed soil within a specified land use area in a catchment.

"""

from catchment_data_api.catchment_data_api import CatchmentDataAPI
from catchment_data_api.crops import Crops
from landcover_assignment.resource_manager.data_loader import Loader
import pandas as pd 

class CatchmentLandCover:
    """
    Manages and analyzes land cover data within catchment areas by integrating various APIs and data sources.

    This class provides functionalities for accessing and analyzing land cover data across different land use
    types within catchment areas. It includes methods for calculating areas and shares of different land cover
    types, such as forests, wetlands, croplands, and grasslands, based on catchment names.

    Attributes:
        api (CatchmentDataAPI): An instance of the CatchmentDataAPI for accessing catchment data.
        crops_api (Crops): An instance of the Crops API for accessing crops data.
        loader (Loader): An instance of the Loader for accessing national area data.
        methods (dict): A dictionary mapping land use types to their respective methods.
        national_areas (dict): A dictionary mapping land use types to their national areas data.
    """
    def __init__(self):
        self.api = CatchmentDataAPI()
        self.crops_api = Crops()
        self.loader = Loader()

        self.methods ={
            'forest': self.get_catchment_forest_area,
            'wetland': self.get_catchment_peat_area,
            'cropland': self.get_catchment_crop_area,
            'grassland': self.get_catchment_grassland_area
        }

        self.national_areas = {
            "forest": self.loader.national_forest_areas,
            "cropland": self.loader.national_cropland_areas,
            "wetland": self.loader.national_wetland_areas,
            "settlement": self.loader.national_settlement_areas,
            "grassland": self.loader.national_grassland_areas,
        }


    def get_catchment_forest_area(self, catchment):
        """
        Calculates the total forest area within a specified catchment, categorized by cover and soil types.

        :param catchment: The name of the catchment area.
        :type catchment: str
        :return: A pandas DataFrame summarizing the forest area details.
        :rtype: pd.DataFrame
        """
        forest_df = self.api.get_catchment_forest_data_by_catchment_name(catchment)

        # Check if the DataFrame is empty
        if forest_df.empty:
            summary_data = {
                'area_ha': 0,
                'share_mineral': 0,
                'share_organic': 0,
                'share_organic_mineral': 0,
                'share_burnt': 0  # Assuming a default value; replace with an appropriate call if needed
            }
            return pd.DataFrame([summary_data])

        # Filter for specific types of forests and then group
        forest_types = ['Broadleaved Forest and Woodland', 'Coniferous Forest', 'Mixed Forest', 'Transitional Forest']
        filtered_df = forest_df[forest_df['cover_type'].isin(forest_types)]
        grouped_df = filtered_df.groupby(['cover_type', 'soil_type']).sum()

        # Safely get totals for different soil types, using 0 if the category is missing
        total_area = grouped_df['total_hectares'].sum()
        total_mineral = grouped_df.xs('mineral', level='soil_type')['total_hectares'].sum() if 'mineral' in grouped_df.index.get_level_values('soil_type') else 0
        total_mineral += grouped_df.xs('misc', level='soil_type')['total_hectares'].sum() if 'misc' in grouped_df.index.get_level_values('soil_type') else 0
        total_peat = grouped_df.xs('peat', level='soil_type')['total_hectares'].sum() if 'peat' in grouped_df.index.get_level_values('soil_type') else 0
        total_mineral_peat = grouped_df.xs('peaty_mineral', level='soil_type')['total_hectares'].sum() if 'peaty_mineral' in grouped_df.index.get_level_values('soil_type') else 0

        # Calculating shares, ensuring no division by zero
        summary_data = {
            'area_ha': total_area,
            'share_mineral': total_mineral / total_area if total_area != 0 else 0,
            'share_organic': total_peat / total_area if total_area != 0 else 0,
            'share_organic_mineral': total_mineral_peat / total_area if total_area != 0 else 0,
            'share_burnt': self.get_national_burnt_average('forest')
        }

        return pd.DataFrame([summary_data])

    

    def get_catchment_peat_area(self, catchment):
        """
        Calculates the total organic area within a specified catchment, grouped by cover and soil types.

        :param catchment: The name of the catchment area.
        :type catchment: str
        :return: A pandas DataFrame summarizing the peat area details.
        :rtype: pd.DataFrame
        """
        peat_df = self.api.get_catchment_peat_data_by_catchment_name(catchment)

        # Check if the DataFrame is empty
        if peat_df.empty:
            summary_data = {
                'area_ha': 0,
                'share_mineral': 0,
                'share_organic': 0,
                'share_organic_mineral': 0,
                'share_burnt': 0  # Assuming a default value; replace with an appropriate call if needed
            }
            return pd.DataFrame([summary_data])
        
        # Filter and group by cover and soil types
        grouped_df = peat_df.groupby(['cover_type', 'soil_type']).sum()

        # Safely get totals for different soil types, using 0 if the category is missing
        total_area = grouped_df['total_hectares'].sum()
        total_mineral = grouped_df.xs('mineral', level='soil_type')['total_hectares'].sum() if 'mineral' in grouped_df.index.get_level_values('soil_type') else 0
        total_mineral += grouped_df.xs('misc', level='soil_type')['total_hectares'].sum() if 'misc' in grouped_df.index.get_level_values('soil_type') else 0
        total_peat = grouped_df.xs('peat', level='soil_type')['total_hectares'].sum() if 'peat' in grouped_df.index.get_level_values('soil_type') else 0
        total_mineral_peat = grouped_df.xs('peaty_mineral', level='soil_type')['total_hectares'].sum() if 'peaty_mineral' in grouped_df.index.get_level_values('soil_type') else 0

        # Calculating shares, ensuring no division by zero
        summary_data = {
            'area_ha': total_area,
            'share_mineral': total_mineral / total_area if total_area != 0 else 0,
            'share_organic': total_peat / total_area if total_area != 0 else 0,
            'share_organic_mineral': total_mineral_peat / total_area if total_area != 0 else 0,
            'share_burnt': self.get_national_burnt_average('wetland')
        }

        return pd.DataFrame([summary_data])

    

    def get_catchment_crop_area(self, catchment):
        """
        Calculates the total crop area within a specified catchment, grouped by cover and soil types.

        :param catchment: The name of the catchment area.
        :type catchment: str
        :return: A pandas DataFrame summarizing the crop area details.
        :rtype: pd.DataFrame
        """
        cultivated_df = self.api.get_catchment_cultivated_data_by_catchment_name(catchment)

        # Check if the DataFrame is empty
        if cultivated_df.empty:
            summary_data = {
                'area_ha': 0,
                'share_mineral': 0,
                'share_organic': 0,
                'share_organic_mineral': 0,
                'share_burnt': 0  # Assuming a default value; replace with an appropriate call if needed
            }
            return pd.DataFrame([summary_data])
        
        # Filter and group by cover and soil types
        grouped_df = cultivated_df.groupby(['cover_type', 'soil_type']).sum()

        # Safely get totals for different soil types, using 0 if the category is missing
        total_area = grouped_df['total_hectares'].sum()
        total_mineral = grouped_df.xs('mineral', level='soil_type')['total_hectares'].sum() if 'mineral' in grouped_df.index.get_level_values('soil_type') else 0
        total_mineral += grouped_df.xs('misc', level='soil_type')['total_hectares'].sum() if 'misc' in grouped_df.index.get_level_values('soil_type') else 0
        total_peat = grouped_df.xs('peat', level='soil_type')['total_hectares'].sum() if 'peat' in grouped_df.index.get_level_values('soil_type') else 0
        total_mineral_peat = grouped_df.xs('peaty_mineral', level='soil_type')['total_hectares'].sum() if 'peaty_mineral' in grouped_df.index.get_level_values('soil_type') else 0

        # Calculating shares, ensuring no division by zero
        summary_data = {
            'area_ha': total_area,
            'share_mineral': total_mineral / total_area if total_area != 0 else 0,
            'share_organic': total_peat / total_area if total_area != 0 else 0,
            'share_organic_mineral': total_mineral_peat / total_area if total_area != 0 else 0,
            'share_burnt': self.get_national_burnt_average('cropland')
        }

        return pd.DataFrame([summary_data])

    

    def get_catchment_grassland_area(self, catchment, total_grassland_area):
        """
        Calculates the total grassland area within a specified catchment, using additional grassland area data from the 
        grassland_production package.

        :param catchment: The name of the catchment area.
        :type catchment: str
        :param total_grassland_area: The total grassland area data.
        :type total_grassland_area: Various (e.g., int, float, pd.Series)
        :return: A pandas DataFrame summarizing the grassland area details.
        :rtype: pd.DataFrame
        """

        derived_grassland_area = self.get_derived_catchment_grassland_area(total_grassland_area)

        grassland_df = self.api.get_catchment_grass_data_by_catchment_name(catchment)


        # Select only numeric columns for transposition and summation
        numeric_df = grassland_df.select_dtypes(include=[float, int])
        

        # Transpose the numeric part of the DataFrame
        transposed_numeric_df = numeric_df.T

        # Now, sum across the 'soil_type' level (assuming your DataFrame is structured to allow this)
        summed_df = transposed_numeric_df.groupby(level='soil_type').sum()


        total_area = 0
        total_mineral = 0
        total_peat = 0
        total_mineral_peat = 0

        for soil in summed_df.index:
            total_area += summed_df.loc[soil].sum()

            if soil == 'mineral' or soil == 'misc':
                total_mineral += summed_df.loc[soil].sum()
            elif soil == 'peat':
                total_peat += summed_df.loc[soil].sum()
            elif soil == 'peaty_mineral':
                total_mineral_peat += summed_df.loc[soil].sum()

        # Creating a summary DataFrame
        summary_data = {
            'area_ha': derived_grassland_area,
            'share_mineral': total_mineral / total_area if total_area != 0 else 0,
            'share_organic': total_peat / total_area if total_area != 0 else 0,
            'share_organic_mineral': total_mineral_peat / total_area if total_area != 0 else 0,
            'share_burnt': self.get_national_burnt_average('grassland')
        }

        return pd.DataFrame([summary_data])


    def get_landuse_area(self, landuse, catchment, grassland_area=None):
        """
        Retrieves the total area for a specified land use within a catchment.

        :param landuse: The type of land use (e.g., 'forest', 'wetland', 'cropland', 'grassland').
        :type landuse: str
        :param catchment: The name of the catchment area.
        :type catchment: str
        :param grassland_area: Optional; additional grassland area data, required if landuse is 'grassland'.
        :type grassland_area: Various, optional
        :return: The total area of the specified land use within the catchment.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'area_ha' column is not found.
        """

        if landuse == 'farmable_condition':
            return 0.0
        
        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")

        if landuse == 'grassland':
            result_df = self.methods[landuse](catchment, grassland_area)
        else:
            result_df = self.methods[landuse](catchment)

        if 'area_ha' in result_df.columns:

            return result_df['area_ha'].iloc[0]
        
        else:

            raise ValueError(f"'area_ha' column not found in the result for land use: {landuse}")
        

    def get_share_mineral(self, landuse, catchment, grassland_area=None):
        """
        Retrieves the share of mineral soil within a specified land use area in a catchment.

        :param landuse: The type of land use.
        :type landuse: str
        :param catchment: The name of the catchment area.
        :type catchment: str
        :param grassland_area: Optional; additional grassland area data, required if landuse is 'grassland'.
        :type grassland_area: Various, optional
        :return: The share of mineral soil within the specified land use area.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_mineral' column is not found.
        """

        if landuse == 'farmable_condition':
            return 1.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](catchment, grassland_area)
        else:
            result_df = self.methods[landuse](catchment)

        if 'share_mineral' in result_df.columns:
            return result_df['share_mineral'].iloc[0]
        else:
            raise ValueError(f"'share_mineral' column not found in the result for land use: {landuse}")


    def get_share_organic(self, landuse, catchment, grassland_area=None):
        """
        Retrieves the share of organic soil within a specified land use area in a catchment.

        :param landuse: The type of land use.
        :type landuse: str
        :param catchment: The name of the catchment area.
        :type catchment: str
        :param grassland_area: Optional; additional grassland area data, required if landuse is 'grassland'.
        :type grassland_area: Various, optional
        :return: The share of organic soil within the specified land use area.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_organic' column is not found.
        """

        if landuse == 'farmable_condition':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](catchment, grassland_area)
        else:
            result_df = self.methods[landuse](catchment)

        if 'share_organic' in result_df.columns:
            return result_df['share_organic'].iloc[0]
        else:
            raise ValueError(f"'share_organic' column not found in the result for land use: {landuse}")


    def get_share_organic_mineral(self, landuse, catchment, grassland_area=None):
        """
        Retrieves the share of organic-mineral mixed soil within a specified land use area in a catchment.

        :param landuse: The type of land use.
        :type landuse: str
        :param catchment: The name of the catchment area.
        :type catchment: str
        :param grassland_area: Optional; additional grassland area data, required if landuse is 'grassland'.
        :type grassland_area: Various, optional
        :return: The share of organic-mineral mixed soil within the specified land use area.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_organic_mineral' column is not found.
        """

        if landuse == 'farmable_condition':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](catchment, grassland_area)
        else:
            result_df = self.methods[landuse](catchment)

        if 'share_organic_mineral' in result_df.columns:
            return result_df['share_organic_mineral'].iloc[0]
        else:
            raise ValueError(f"'share_organic_mineral' column not found in the result for land use: {landuse}")
        

    def get_share_burnt(self, landuse, catchment, grassland_area=None):  

        
        if landuse == 'farmable_condition':
            return 0.0
        
        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](catchment, grassland_area)
        else:
            result_df = self.methods[landuse](catchment)

        if 'share_burnt' in result_df.columns:
            return result_df['share_burnt'].iloc[0]
        else:
            raise ValueError(f"'share_burnt' column not found in the result for land use: {landuse}")


    def get_national_burnt_average(self, landuse):
        """
        Retrieves the share of burnt land within a specified land use area in a catchment.

        :param landuse: The type of land use.
        :type landuse: str
        :param catchment: The name of the catchment area.
        :type catchment: str
        :param grassland_area: Optional; additional grassland area data, required if landuse is 'grassland'.
        :type grassland_area: Various, optional
        :return: The share of burnt land within the specified land use area.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_burnt' column is not found.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        burn_average = self.national_areas[landuse]()()["burnt_kha"].sum() / self.national_areas[landuse]()()["total_kha"].sum() 

        return burn_average   


    def get_catchment_crop_type(self, catchment):
        """
        Retrieves the types of crops grown within a specified catchment.

        :param catchment: The name of the catchment area.
        :type catchment: str
        :return: A pandas DataFrame containing crop types within the specified catchment.
        :rtype: pd.DataFrame
        """

        crop_df = self.crops_api.get_catchment_crops(catchment)

        return crop_df
    
    def get_total_spared_area(self, spared_area, sc):
        """
        Retrieves the total spared area for a given scenario.

        This method looks up the total spared area based on a specific scenario identifier. It is useful for
        determining the spared area that has been set aside for conservation or other purposes under different
        planning or management scenarios.

        :param spared_area: A pandas DataFrame containing spared areas for various scenarios.
        :type spared_area: pd.DataFrame
        :param sc: The scenario identifier for which the total spared area is to be retrieved.
        :type sc: str or int
        :return: The total spared area for the given scenario.
        :rtype: float
        :raises ValueError: If the scenario is not found in the spared_area DataFrame.
        """

        try:
            col = str(sc)
            mask = (spared_area[col] !=0)
            return spared_area.loc[mask,col].item()
        except KeyError:
            try:
                col = int(sc)  # Fallback to integer representation
                mask = (spared_area[col] != 0)
                return spared_area.loc[mask, col].item()
            except KeyError:
                # Handle or log the error specifically for this scenario
                # Perhaps log an error or raise a custom exception
                raise ValueError(f"Scenario {sc} not found in spared_area.")
            
    
    def get_derived_catchment_grassland_area(self, grassland_area, sc=0):
        """
        Retrieves the derived grassland area for a catchment based on a scenario grassland input (rather than actual catchment grassland).

        This method is used to look up the calculated grassland area that is derived from available data for a specific
        scenario.

        :param grassland_area: A pandas DataFrame or Series containing grassland areas for various scenarios.
        :type grassland_area: pd.DataFrame or pd.Series
        :param sc: Optional; the scenario identifier for which the derived grassland area is calculated. Defaults to 0.
        :type sc: str or int, optional
        :return: The derived grassland area for the specified scenario.
        :rtype: float
        :raises ValueError: If the scenario is not found in the grassland_area data.
        """
        try:
            col = str(sc)
            return grassland_area[col].iloc[0].item()
        except KeyError:
            try:
                col = int(sc)  # Fallback to integer representation
                return grassland_area[col].iloc[0].item()
            except KeyError:
                # Handle or log the error specifically for this scenario
                # Perhaps log an error or raise a custom exception
                raise ValueError(f"Scenario {sc} not found in grassland_area.")
            
    
    def get_area_with_organic_potential(self,spared_breakdown, total_spared_area, sc):
        """
        Calculates the area with organic farming potential based on spared land breakdown and scenario.

        This method assesses the potential for organic soils in spared areas by analyzing the soil composition
        and other factors. It uses detailed breakdown data of spared areas and soil groups. The input data is calculated
        in the grassland_production module. It is assumed that the area of organic soils cannot be greater than the 
        area of available soil group 3. 

        :param spared_breakdown: A pandas DataFrame containing detailed breakdown of spared areas, including soil types.
        :type spared_breakdown: pd.DataFrame
        :param total_spared_area: A pandas DataFrame or Series containing total spared areas for various scenarios.
        :type total_spared_area: pd.DataFrame or pd.Series
        :param sc: The scenario identifier used for the analysis.
        :type sc: str or int
        :return: The area with available organic soils based on the specified scenario.
        :rtype: float
        :raises ValueError: If the specific scenario does not exist in the spared_breakdown or total_spared_area data.
        """
        # Select only numeric columns 
        numeric_df = spared_breakdown.select_dtypes(include=[float, int])

        grouped_df = numeric_df.groupby(['Scenario','soil_group']).sum()


        try:
            # Using .xs to select all entries for a specific 'Scenario' number
            # and then filter for 'soil_group' == 3
            # Note: .xs returns a DataFrame if there are multiple matches, or a Series if there's only one match
            specific_scenario_df = grouped_df.xs(key=sc, level='Scenario')
         
            # Check if all values in the 'area_ha' column are zero
            if (specific_scenario_df['area_ha'] == 0).all():
                # Handle the case where all values in the 'area_ha' column are zero
                return self.get_total_spared_area(total_spared_area, sc)
            
            if 3 in specific_scenario_df.index:
                area_ha = specific_scenario_df.loc[3, 'area_ha']  # Directly use .loc to access 'soil_group' == 3
            else:
                area_ha = None  # Handle the case where 'soil_group' == 3 is not present
        except ValueError as e:
            # Handle the case where the specific scenario does not exist
            area_ha = None


        return area_ha



