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

   .. method:: get_share_burnt(landuse, catchment, grassland_area=None)
      
      Calculates the share of burnt land within a specified land use area in a catchment.

   .. method:: get_national_burnt_average(landuse)
      
      Retrieves the national average share of burnt land for a specified land use type.

   .. method:: get_catchment_crop_type(catchment)
      
      Retrieves the types of crops grown within a specified catchment.

   .. method:: get_total_spared_area(spared_area, sc)
      
      Retrieves the total spared area for a given scenario.

   .. method:: get_derived_catchment_grassland_area(grassland_area, sc=0)
      
      Retrieves the derived grassland area for a catchment based on a scenario grassland input.

   .. method:: get_area_with_organic_potential(spared_breakdown, total_spared_area, sc)
      
      Calculates the area with organic farming potential based on spared land breakdown and scenario.

   .. method:: get_land_shares(key, landuse, catchment_name)
      
      Retrieves the share of a specific soil type within a specified land use area in a catchment.

   .. method:: get_grassland_shares(key, catchment_name, grassland_area)
      
      Retrieves the share of a specific soil type within the grassland area of a catchment.

"""

from catchment_data_api.catchment_data_api import CatchmentDataAPI
from catchment_data_api.crops import Crops
from landcover_assignment.resource_manager.data_loader import Loader
from functools import lru_cache
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
        cached_national_areas (dict): A dictionary for caching national areas data.
        cached_burnt_averages (dict): A dictionary for caching burnt averages data.
        cached_crops (dict): A dictionary for caching crop data.
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

        self.cached_national_areas = {}

        self.cached_burnt_averages = {}

        self.cached_crops = {}

    def _get_cached_crops(self, catchment):
        """
        Retrieve and cache the data for a specified catchment.

        Parameters
        ----------
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            The cached DataFrame for the specified catchment.
        """
        # Check if the data is already cached
        if catchment not in self.cached_crops:
            # Cache the data if not already present
            self.cached_crops[catchment] = self.get_catchment_crop_type(catchment)

        return self.cached_crops[catchment].copy()


    def _get_cached_burnt_averages(self, landuse):
        """
        Retrieve and cache the data for a specified land use type.

        Parameters
        ----------
        landuse : str
            The land use type to retrieve.

        Returns
        -------
        pandas.DataFrame
            The cached DataFrame for the specified land use type.
        """
        # Validate land use type
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        # Check if the data is already cached
        if landuse not in self.cached_burnt_averages:
            # Cache the data if not already present
            self.cached_burnt_averages[landuse] = self.get_national_burnt_average(landuse)

        return self.cached_burnt_averages[landuse].copy()
    

    def _get_cached_national_areas(self, landuse):
        """
        Retrieve and cache the data for a specified land use type.

        Parameters
        ----------
        landuse : str
            The land use type to retrieve.

        Returns
        -------
        pandas.DataFrame
            The cached DataFrame for the specified land use type.

        Raises
        ------
        ValueError
            If the specified land use type is unknown.
        """
        # Validate land use type
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        # Check if the data is already cached
        if landuse not in self.cached_national_areas:
            # Cache the data if not already present
            self.cached_national_areas[landuse] = self.national_areas[landuse]()()

        return self.cached_national_areas[landuse].copy()


    @lru_cache(maxsize=100)
    def _get_catchment_data(self, landuse, catchment):
        """
        Retrieves catchment data based on the specified land use type.

        Parameters
        ----------
        landuse : str
            The type of land use (e.g., 'forest', 'wetland', 'cropland', 'grassland').
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            The DataFrame containing catchment data for the specified land use type.
        """
        if landuse == 'forest':
            return self.api.get_catchment_forest_data_by_catchment_name(catchment)
        elif landuse == 'wetland':
            return self.api.get_catchment_peat_data_by_catchment_name(catchment)
        elif landuse == 'cropland':
            return self.api.get_catchment_cultivated_data_by_catchment_name(catchment)
        elif landuse == 'grassland':
            return self.api.get_catchment_grass_data_by_catchment_name(catchment)
        else:
            return None

    def get_catchment_data(self, landuse, catchment):
        """
        Wrapper around the cached function to always return a fresh copy of the cached data.

        Parameters
        ----------
        landuse : str
            The type of land use (e.g., 'forest', 'wetland', 'cropland', 'grassland').
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            The DataFrame containing catchment data for the specified land use type.
        """
        cached_data = self._get_catchment_data(landuse, catchment)
        return cached_data.copy() if cached_data is not None else None


    def get_catchment_forest_area(self, catchment):
        """
        Calculates the total forest area within a specified catchment, categorized by cover and soil types.

        Parameters
        ----------
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            A DataFrame summarizing the forest area details.
        """
        forest_df = self.get_catchment_data("forest",catchment)

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
            'share_burnt': self._get_cached_burnt_averages('forest')
        }

        return pd.DataFrame([summary_data])


    def get_catchment_peat_area(self, catchment):
        """
        Calculates the total organic area within a specified catchment, grouped by cover and soil types.

        Parameters
        ----------
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            A DataFrame summarizing the peat area details.
        """
        peat_df = self.get_catchment_data("wetland",catchment)

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
            'share_burnt': self._get_cached_burnt_averages('wetland')
        }

        return pd.DataFrame([summary_data])


    def get_catchment_crop_area(self, catchment):
        """
        Calculates the total crop area within a specified catchment, grouped by cover and soil types.

        Parameters
        ----------
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            A DataFrame summarizing the crop area details.
        """
        cultivated_df = self.get_catchment_data("cropland",catchment)

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
            'share_burnt': self._get_cached_burnt_averages('cropland')
        }

        return pd.DataFrame([summary_data])


    def get_catchment_grassland_area(self, catchment, total_grassland_area):
        """
        Calculates the total grassland area within a specified catchment, using additional grassland area data from the 
        grassland_production package.

        Parameters
        ----------
        catchment : str
            The name of the catchment area.
        total_grassland_area : Various (e.g., int, float, pd.Series)
            The total grassland area data.

        Returns
        -------
        pandas.DataFrame
            A DataFrame summarizing the grassland area details.
        """

        derived_grassland_area = self.get_derived_catchment_grassland_area(total_grassland_area)

        grassland_df = self.get_catchment_data("grassland",catchment)


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
            'share_burnt': self._get_cached_burnt_averages('grassland')
        }

        return pd.DataFrame([summary_data])


    def get_landuse_area(self, landuse, catchment, grassland_area=None):
        """
        Retrieves the total area for a specified land use within a catchment.

        Parameters
        ----------
        landuse : str
            The type of land use (e.g., 'forest', 'wetland', 'cropland', 'grassland').
        catchment : str
            The name of the catchment area.
        grassland_area : Various, optional
            Optional; additional grassland area data, required if landuse is 'grassland'.

        Returns
        -------
        float
            The total area of the specified land use within the catchment.

        Raises
        ------
        ValueError
            If the land use type is unknown or if 'area_ha' column is not found.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        catchment : str
            The name of the catchment area.
        grassland_area : Various, optional
            Optional; additional grassland area data, required if landuse is 'grassland'.

        Returns
        -------
        float
            The share of mineral soil within the specified land use area.

        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_mineral' column is not found.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        catchment : str
            The name of the catchment area.
        grassland_area : Various, optional
            Optional; additional grassland area data, required if landuse is 'grassland'.

        Returns
        -------
        float
            The share of organic soil within the specified land use area.

        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_organic' column is not found.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        catchment : str
            The name of the catchment area.
        grassland_area : Various, optional
            Optional; additional grassland area data, required if landuse is 'grassland'.

        Returns
        -------
        float
            The share of organic-mineral mixed soil within the specified land use area.

        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_organic_mineral' column is not found.
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
        """
        Retrieves the share of burnt land within a specified land use area in a catchment.

        Parameters
        ----------
        landuse : str
            The type of land use.
        catchment : str
            The name of the catchment area.
        grassland_area : Various, optional
            Optional; additional grassland area data, required if landuse is 'grassland'.

        Returns
        -------
        float
            The share of burnt land within the specified land use area.

        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_burnt' column is not found.
        """
        
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        catchment : str
            The name of the catchment area.
        grassland_area : Various, optional
            Optional; additional grassland area data, required if landuse is 'grassland'.

        Returns
        -------
        float
            The share of burnt land within the specified land use area.

        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_burnt' column is not found.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        data = self._get_cached_national_areas(landuse)
        burn_average = data["burnt_kha"].sum() / data["total_kha"].sum() 

        return burn_average   


    def get_catchment_crop_type(self, catchment):
        """
        Retrieves the types of crops grown within a specified catchment.

        Parameters
        ----------
        catchment : str
            The name of the catchment area.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing crop types within the specified catchment.
        """

        crop_df = self._get_cached_crops(catchment)

        return crop_df
    
    def get_total_spared_area(self, spared_area, sc):
        """
        Retrieves the total spared area for a given scenario.

        This method looks up the total spared area based on a specific scenario identifier. It is useful for
        determining the spared area that has been set aside for conservation or other purposes under different
        planning or management scenarios.

        Parameters
        ----------
        spared_area : pd.DataFrame
            A pandas DataFrame containing spared areas for various scenarios.
        sc : str or int
            The scenario identifier for which the total spared area is to be retrieved.

        Returns
        -------
        float
            The total spared area for the given scenario.

        Raises
        ------
        ValueError
            If the scenario is not found in the spared_area DataFrame.
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

        Parameters
        ----------
        grassland_area : pd.DataFrame or pd.Series
            A pandas DataFrame or Series containing grassland areas for various scenarios.
        sc : str or int, optional
            Optional; the scenario identifier for which the derived grassland area is calculated. Defaults to 0.

        Returns
        -------
        float
            The derived grassland area for the specified scenario.

        Raises
        ------
        ValueError
            If the scenario is not found in the grassland_area data.
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

        Parameters
        ----------
        spared_breakdown : pd.DataFrame
            A pandas DataFrame containing detailed breakdown of spared areas, including soil types.
        total_spared_area : pd.DataFrame or pd.Series
            A pandas DataFrame or Series containing total spared areas for various scenarios.
        sc : str or int
            The scenario identifier used for the analysis.

        Returns
        -------
        float
            The area with available organic soils based on the specified scenario.

        Raises
        ------
        ValueError
            If the specific scenario does not exist in the spared_breakdown or total_spared_area data.
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


    def get_land_shares(self, key, landuse, catchment_name):
        """
        Retrieves the share of a specific soil type within a specified land use area in a catchment.

        Parameters
        ----------
        key : str
            The type of share to retrieve (e.g., 'share_mineral', 'share_organic', 'share_organic_mineral', 'share_burnt').
        landuse : str
            The type of land use.
        catchment_name : str
            The name of the catchment area.

        Returns
        -------
        float
            The share of the specified soil type within the land use area.
        """
        
        shares = {
            "share_mineral":self.get_share_mineral(landuse, catchment_name),
            "share_organic":self.get_share_organic(landuse, catchment_name),
            "share_organic_mineral":self.get_share_organic_mineral(landuse, catchment_name),
            "share_burnt":self.get_share_burnt(landuse, catchment_name)
        }

        return shares[key]


    def get_grassland_shares(self, key, catchment_name, grassland_area):
        """
        Retrieves the share of a specific soil type within the grassland area of a catchment.

        Parameters
        ----------
        key : str
            The type of share to retrieve (e.g., 'share_mineral', 'share_organic', 'share_organic_mineral', 'share_burnt').
        catchment_name : str
            The name of the catchment area.
        grassland_area : Various (e.g., int, float, pd.Series)
            The total grassland area data.

        Returns
        -------
        float
            The share of the specified soil type within the grassland area.
        """
        
        shares = {
            "share_mineral":self.get_share_mineral("grassland", catchment_name, grassland_area),
            "share_organic":self.get_share_organic("grassland", catchment_name, grassland_area),
            "share_organic_mineral":self.get_share_organic_mineral("grassland", catchment_name, grassland_area),
            "share_burnt":self.get_share_burnt("grassland", catchment_name, grassland_area)
        }

        return shares[key]


