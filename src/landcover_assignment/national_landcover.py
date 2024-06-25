"""
National Land Cover Data Analysis
=================================

The National Land Cover class is designed to facilitate access and analysis of national land cover data, encompassing various land use types 
such as forests, wetlands, croplands, grasslands, and settlements. This class leverages a data loader to fetch predefined datasets and provides 
a suite of methods to calculate and retrieve detailed information about land cover characteristics, including areas and soil composition shares, 
for different years.

Features:
---------
- Access to national land cover data for multiple land use types.
- Calculation of land use areas and shares of different soil compositions.
- Ability to retrieve data for specific years, enabling temporal analysis.
- Support for scenario-based analysis with functions to handle spared areas and potential for organic soil use.

Dependencies:
-------------
- ``resource_manager.data_loader.Loader``: For loading national land cover datasets.
- ``pandas``: For data manipulation and analysis.
"""
from landcover_assignment.resource_manager.data_loader import Loader
import pandas as pd 

class NationalLandCover:
    """
    Provides detailed national land cover data analysis capabilities, including the extraction of various land use types' data across different years. 
    This class supports the calculation of area shares and specific environmental factors for different land uses at a national level.

    The class leverages a data loader to access pre-defined national area datasets and performs calculations to return comprehensive summaries 
    for each land use type.

    Attributes:
        loader (Loader): An instance of Loader to access national datasets.
        methods (dict): A mapping from land use types to their respective data retrieval methods.
        national_areas (dict): A dictionary containing methods to retrieve national area data for different land use types.
    """
    def __init__(self):
 
        self.loader = Loader()

        self.methods ={
            'forest': self.get_forest_data,
            'wetland': self.get_peat_data,
            'cropland': self.get_crop_data,
            'grassland': self.get_grassland_data,
            'settlement': self.get_settlement_data
        }

        self.national_areas = {
            "forest": self.loader.national_forest_areas,
            "cropland": self.loader.national_cropland_areas,
            "wetland": self.loader.national_wetland_areas,
            "settlement": self.loader.national_settlement_areas,
            "grassland": self.loader.national_grassland_areas,
        }


    def get_forest_data(self, year):
        """
        Retrieves summary data for forest land use including area, shares of mineral, organic, and organic-mineral soils, 
        peat extraction, and rewetted areas for a given year.

        :param year: The year, as int, for which data is retrieved.
        :return: A DataFrame containing summary data for forest land use.
        :rtype: pandas.DataFrame
        """
        # Creating a summary DataFrame
        summary_data = {
            'area_ha': self.get_national_area('forest', year),
            'share_mineral': self.get_national_mineral('forest', year),
            'share_organic': self.get_national_organic('forest', year),
            'share_organic_mineral': self.get_national_organic_mineral('forest', year),
            'share_drained_rich_organic': self.get_national_rich_drained_orgainc_grassland('forest', year),
            'share_drained_poor_organic': self.get_national_poor_drained_organic_grassland('forest', year),
            'share_rewetted_rich_organic':self.get_national_rich_rewetted_organic_grassland('forest', year),
            'share_rewetted_poor_organic': self.get_national_poor_rewetted_organic_grassland('forest', year),
            'share_rewetted_in_organic':self.get_national_rewetted_in_organic('forest', year),
            'share_rewetted_in_mineral': self.get_national_rewetted_in_mineral('forest', year),
            'share_domestic_peat_extraction': self.get_national_domestic_peat_extraction('forest', year),
            'share_industrial_peat_extraction': self.get_national_industrial_peat_extraction('forest', year),
            'share_rewetted_domestic_peat_extraction': self.get_national_rewetted_domestic_peat('forest', year),
            'share_rewetted_industrial_peat_extraction': self.get_national_rewetted_industrial_peat('forest', year),
            'share_near_natural_wetland': self.get_national_near_natural_wetland('forest', year),
            'share_unmanaged_wetland': self.get_national_unmanaged_wetland('forest', year),
            'share_burnt': self.get_national_burn('forest', year)
        }


        return pd.DataFrame([summary_data])
    

    def get_peat_data(self, year):
        """
        Retrieves summary data for wetland (peat) land use including area, shares of mineral, organic, and organic-mineral soils,
        peat extraction, and rewetted areas for a given year.

        :param year: The year, as int, for which data is retrieved.
        :return: A DataFrame containing summary data for wetland land use.
        :rtype: pandas.DataFrame
        """
        # Creating a summary DataFrame
        summary_data = {
            'area_ha': self.get_national_area('wetland', year),
            'share_mineral': self.get_national_mineral('wetland', year),
            'share_organic': self.get_national_organic('wetland', year),
            'share_organic_mineral': self.get_national_organic_mineral('wetland', year),
            'share_drained_rich_organic': self.get_national_rich_drained_orgainc_grassland('wetland', year),
            'share_drained_poor_organic': self.get_national_poor_drained_organic_grassland('wetland', year),
            'share_rewetted_rich_organic':self.get_national_rich_rewetted_organic_grassland('wetland', year),
            'share_rewetted_poor_organic': self.get_national_poor_rewetted_organic_grassland('wetland', year),
            'share_rewetted_in_organic':self.get_national_rewetted_in_organic('wetland', year),
            'share_rewetted_in_mineral': self.get_national_rewetted_in_mineral('wetland', year),
            'share_domestic_peat_extraction': self.get_national_domestic_peat_extraction('wetland', year),
            'share_industrial_peat_extraction': self.get_national_industrial_peat_extraction('wetland', year),
            'share_rewetted_domestic_peat_extraction': self.get_national_rewetted_domestic_peat('wetland', year),
            'share_rewetted_industrial_peat_extraction': self.get_national_rewetted_industrial_peat('wetland', year),
            'share_near_natural_wetland': self.get_national_near_natural_wetland('wetland', year),
            'share_unmanaged_wetland': self.get_national_unmanaged_wetland('wetland', year),
            'share_burnt': self.get_national_burn('wetland', year)
        }
    
        return pd.DataFrame([summary_data])
    

    def get_crop_data(self, year):
        """
        Retrieves summary data for cropland use including area, shares of mineral, organic, and organic-mineral soils,
        peat extraction, and rewetted areas for a given year.

        :param year: The year, as int, for which data is retrieved.
        :return: A DataFrame containing summary data for cropland use.
        :rtype: pandas.DataFrame
        """
        # Creating a summary DataFrame
        summary_data = {
            'area_ha': self.get_national_area('cropland', year),
            'share_mineral': self.get_national_mineral('cropland', year),
            'share_organic': self.get_national_organic('cropland', year),
            'share_organic_mineral': self.get_national_organic_mineral('cropland', year),
            'share_drained_rich_organic': self.get_national_rich_drained_orgainc_grassland('cropland', year),
            'share_drained_poor_organic': self.get_national_poor_drained_organic_grassland('cropland', year),
            'share_rewetted_rich_organic':self.get_national_rich_rewetted_organic_grassland('cropland', year),
            'share_rewetted_poor_organic': self.get_national_poor_rewetted_organic_grassland('cropland', year),
            'share_rewetted_in_organic':self.get_national_rewetted_in_organic('cropland', year),
            'share_rewetted_in_mineral': self.get_national_rewetted_in_mineral('cropland', year),
            'share_domestic_peat_extraction': self.get_national_domestic_peat_extraction('cropland', year),
            'share_industrial_peat_extraction': self.get_national_industrial_peat_extraction('cropland', year),
            'share_rewetted_domestic_peat_extraction': self.get_national_rewetted_domestic_peat('cropland', year),
            'share_rewetted_industrial_peat_extraction': self.get_national_rewetted_industrial_peat('cropland', year),
            'share_near_natural_wetland': self.get_national_near_natural_wetland('cropland', year),
            'share_unmanaged_wetland': self.get_national_unmanaged_wetland('cropland', year),
            'share_burnt': self.get_national_burn('cropland', year)
        }


        return pd.DataFrame([summary_data])
    

    def get_grassland_data(self, year, total_grassland_area):
        """
        Retrieves summary data for grassland use including area, shares of mineral, organic, and organic-mineral soils,
        peat extraction, and rewetted areas, optionally adjusted by total grassland area for a given year.

        Area is derived from total grassland area calculated using the grassland_production module

        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: A DataFrame containing summary data for grassland use.
        :rtype: pandas.DataFrame
        """
        
        derived_grassland_area = self.get_derived_national_grassland_area(total_grassland_area)

     
        # Creating a summary DataFrame
        summary_data = {
            'area_ha': derived_grassland_area,
            'share_mineral': self.get_national_mineral('grassland', year),
            'share_organic': self.get_national_organic('grassland', year),
            'share_organic_mineral': self.get_national_organic_mineral('grassland', year),
            'share_drained_rich_organic': self.get_national_rich_drained_orgainc_grassland('grassland', year),
            'share_drained_poor_organic': self.get_national_poor_drained_organic_grassland('grassland', year),
            'share_rewetted_rich_organic':self.get_national_rich_rewetted_organic_grassland('grassland', year),
            'share_rewetted_poor_organic': self.get_national_poor_rewetted_organic_grassland('grassland', year),
            'share_rewetted_in_organic':self.get_national_rewetted_in_organic('grassland', year),
            'share_rewetted_in_mineral': self.get_national_rewetted_in_mineral('grassland', year),
            'share_domestic_peat_extraction': self.get_national_domestic_peat_extraction('grassland', year),
            'share_industrial_peat_extraction': self.get_national_industrial_peat_extraction('grassland', year),
            'share_rewetted_domestic_peat_extraction': self.get_national_rewetted_domestic_peat('grassland', year),
            'share_rewetted_industrial_peat_extraction': self.get_national_rewetted_industrial_peat('grassland', year),
            'share_near_natural_wetland': self.get_national_near_natural_wetland('grassland', year),
            'share_unmanaged_wetland': self.get_national_unmanaged_wetland('grassland', year),
            'share_burnt': self.get_national_burn('grassland', year)
        }

        return pd.DataFrame([summary_data])
    

    def get_settlement_data(self, year):
        """
        Retrieves summary data for settlement land use including area, shares of mineral, organic, and organic-mineral soils,
        peat extraction, and rewetted areas for a given year.

        :param year: The year, as int, for which data is retrieved.
        :return: A DataFrame containing summary data for settlement land use.
        :rtype: pandas.DataFrame
        """
        # Creating a summary DataFrame
        summary_data = {
            'area_ha': self.get_national_area('settlement', year),
            'share_mineral': self.get_national_mineral('settlement', year),
            'share_organic': self.get_national_organic('settlement', year),
            'share_organic_mineral': self.get_national_organic_mineral('settlement', year),
            'share_drained_rich_organic': self.get_national_rich_drained_orgainc_grassland('settlement', year),
            'share_drained_poor_organic': self.get_national_poor_drained_organic_grassland('settlement', year),
            'share_rewetted_rich_organic':self.get_national_rich_rewetted_organic_grassland('settlement', year),
            'share_rewetted_poor_organic': self.get_national_poor_rewetted_organic_grassland('settlement', year),
            'share_rewetted_in_organic':self.get_national_rewetted_in_organic('settlement', year),
            'share_rewetted_in_mineral': self.get_national_rewetted_in_mineral('settlement', year),
            'share_domestic_peat_extraction': self.get_national_domestic_peat_extraction('settlement', year),
            'share_industrial_peat_extraction': self.get_national_industrial_peat_extraction('settlement', year),
            'share_rewetted_domestic_peat_extraction': self.get_national_rewetted_domestic_peat('settlement', year),
            'share_rewetted_industrial_peat_extraction': self.get_national_rewetted_industrial_peat('settlement', year),
            'share_near_natural_wetland': self.get_national_near_natural_wetland('settlement', year),
            'share_unmanaged_wetland': self.get_national_unmanaged_wetland('settlement', year),
            'share_burnt': self.get_national_burn('settlement', year)
        }


        return pd.DataFrame([summary_data])
    

    def get_landuse_area(self, landuse, year, grassland_area=None):
        """
        Retrieves the total area for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The total area for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'area_ha' column is not found in the result.
        """
        if landuse == 'farmable_condition':
            return 0.0
        
        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")

        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)

        if 'area_ha' in result_df.columns:

            return result_df['area_ha'].iloc[0]
        
        else:

            raise ValueError(f"'area_ha' column not found in the result for land use: {landuse}")
        

    def get_share_mineral(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of mineral soil for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share mineral for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_mineral' column is not found in the result.
        """
        if landuse == 'farmable_condition':
            return 1.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)

        if 'share_mineral' in result_df.columns:
            return result_df['share_mineral'].iloc[0]
        else:
            raise ValueError(f"'share_mineral' column not found in the result for land use: {landuse}")


    def get_share_organic(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of organic soil for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share organic for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_organic' column is not found in the result.
        """
        if landuse == 'farmable_condition':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)

        if 'share_organic' in result_df.columns:
            return result_df['share_organic'].iloc[0]
        else:
            raise ValueError(f"'share_organic' column not found in the result for land use: {landuse}")


    def get_share_organic_mineral(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of organic-mineral mixed soil for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share organic mineral for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_organic_mineral' column is not found in the result.
        """
        if landuse == 'farmable_condition':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)


        if 'share_organic_mineral' in result_df.columns:
            return result_df['share_organic_mineral'].iloc[0]
        else:
            raise ValueError(f"'share_organic_mineral' column not found in the result for land use: {landuse}")
        

    def get_share_drained_rich_organic_grassland(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of rich drained organic soil for grassland for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share rich organic for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_drained_rich_organic' column is not found in the result.
        """
        if landuse != 'grassland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if grassland_area is None:
            raise ValueError(f"Grassland area must be provided for land use: {landuse}")
        else:
            result_df = self.methods[landuse](year, grassland_area)
       
        if 'share_drained_rich_organic' in result_df.columns:
            return result_df['share_drained_rich_organic'].iloc[0]
        else:
            raise ValueError(f"'share_drained_rich_organic' column not found in the result for land use: {landuse}")
        

    def get_share_drained_poor_organic_grassland(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of poor drained organic soil for grassland for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share poor organic for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_poor_organic' column is not found in the result.
        """
        if landuse != 'grassland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if grassland_area is None:
            raise ValueError(f"Grassland area must be provided for land use: {landuse}")
        else:
            result_df = self.methods[landuse](year, grassland_area)
       

        if 'share_drained_poor_organic' in result_df.columns:
            return result_df['share_drained_poor_organic'].iloc[0]
        else:
            raise ValueError(f"'share_drained_poor_organic' column not found in the result for land use: {landuse}")
        
    def get_share_rewetted_rich_in_organic_grassland(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of share rewetted in rich organic for grassland for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share rewetted in organic for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_rewetted_rich_organic' column is not found in the result.
        """
        if landuse != 'grassland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if grassland_area is None:
            raise ValueError(f"Grassland area must be provided for land use: {landuse}")
        else:
            result_df = self.methods[landuse](year, grassland_area)
       

        if 'share_rewetted_rich_organic' in result_df.columns:
            return result_df['share_rewetted_rich_organic'].iloc[0]
        else:
            raise ValueError(f"'share_rewetted_rich_organic' column not found in the result for land use: {landuse}")
        
    def get_share_rewetted_poor_in_organic_grassland(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of share rewetted in poor organic for grassland for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share rewetted in organic for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_rewetted_poor_organic' column is not found in the result.
        """
        if landuse != 'grassland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if grassland_area is None:
            raise ValueError(f"Grassland area must be provided for land use: {landuse}")
        else:
            result_df = self.methods[landuse](year, grassland_area)
       

        if 'share_rewetted_poor_organic' in result_df.columns:
            return result_df['share_rewetted_poor_organic'].iloc[0]
        else:
            raise ValueError(f"'share_rewetted_poor_organic' column not found in the result for land use: {landuse}")
        

    def get_share_rewetted_in_organic(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of share rewetted in organic for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share rewetted in organic for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_rewetted_in_organic' column is not found in the result.
        """

        if landuse == 'farmable_condition':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)

        if 'share_rewetted_in_organic' in result_df.columns:
            return result_df['share_rewetted_in_organic'].iloc[0]
        else:
            raise ValueError(f"'share_rewetted_in_organic' column not found in the result for land use: {landuse}")
        
    
    def get_share_rewetted_in_mineral(self, landuse, year, grassland_area=None):
        """
        Retrieves the share of share rewetted in mineral for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share rewetted in mineral for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_rewetted_in_mineral' column is not found in the result.
        """
        if landuse == 'farmable_condition':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)

        if 'share_rewetted_in_mineral' in result_df.columns:
            return result_df['share_rewetted_in_mineral'].iloc[0]
        else:
            raise ValueError(f"'share_rewetted_in_mineral' column not found in the result for land use: {landuse}")


    def get_share_domestic_peat_extraction(self, landuse, year):
        """
        Retrieves the share of share of peat extraction for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share peat extraction for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_domestic_peat_extraction' column is not found in the result.
        """

        if landuse != 'wetland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
    
        else:
            result_df = self.methods[landuse](year)


        if 'share_domestic_peat_extraction' in result_df.columns:
            return result_df['share_domestic_peat_extraction'].iloc[0]
        else:
            raise ValueError(f"'share_domestic_peat_extraction' column not found in the result for land use: {landuse}")
        

    def get_share_industrial_peat_extraction(self, landuse, year):
        """
        Retrieves the share of share of peat extraction for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share peat extraction for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_industrial_peat_extraction' column is not found in the result.
        """
        if landuse != 'wetland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        else:
            result_df = self.methods[landuse](year)


        if 'share_industrial_peat_extraction' in result_df.columns:
            return result_df['share_industrial_peat_extraction'].iloc[0]
        else:
            raise ValueError(f"'share_industrial_peat_extraction' column not found in the result for land use: {landuse}")
        

    def get_share_rewetted_domestic_peat_extraction(self, landuse, year):
        """
        Retrieves the share of share of peat extraction for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share peat extraction for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_rewetted_domestic_peat_extraction' column is not found in the result.
        """
        if landuse != 'wetland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        else:
            result_df = self.methods[landuse](year)

        if 'share_rewetted_domestic_peat_extraction' in result_df.columns:
            return result_df['share_rewetted_domestic_peat_extraction'].iloc[0]
        else:
            raise ValueError(f"'get_share_rewetted_domestic_peat_extraction' column not found in the result for land use: {landuse}")
        

    def get_share_rewetted_industrial_peat_extraction(self, landuse, year):
        """
        Retrieves the share of share of peat extraction for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share peat extraction for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_rewetted_industrial_peat_extraction' column is not found in the result.
        """
        if landuse != 'wetland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        else:
            result_df = self.methods[landuse](year)


        if 'share_rewetted_industrial_peat_extraction' in result_df.columns:
            return result_df['share_rewetted_industrial_peat_extraction'].iloc[0]
        else:
            raise ValueError(f"'share_rewetted_industrial_peat_extraction' column not found in the result for land use: {landuse}")
        
    def get_share_near_natural_wetland(self, landuse, year):
        """
        Retrieves the share of near natural wetland for a specified land use type and year.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :return: The share near natural wetland for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_near_natural_wetland' column is not found in the result.
        """
        if landuse != 'wetland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        else:
            result_df = self.methods[landuse](year)

        if 'share_near_natural_wetland' in result_df.columns:
            return result_df['share_near_natural_wetland'].iloc[0]
        else:
            raise ValueError(f"'share_near_natural_wetland' column not found in the result for land use: {landuse}")
        
    def get_share_unmanaged_wetland(self, landuse, year):
        """
        Retrieves the share of unmanaged wetland for a specified land use type and year.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :return: The share unmanaged wetland for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_unmanaged_wetland' column is not found in the result.
        """
        if landuse != 'wetland':
            return 0.0

        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        else:
            result_df = self.methods[landuse](year)

        if 'share_unmanaged_wetland' in result_df.columns:
            return result_df['share_unmanaged_wetland'].iloc[0]
        else:
            raise ValueError(f"'share_unmanaged_wetland' column not found in the result for land use: {landuse}")
        
        
    def get_share_burnt(self, landuse, year, grassland_area=None):   
        """
        Retrieves the share of share burnt for a specified land use type and year. For grassland, the total area must be provided.

        :param landuse: The type of land use as string.
        :param year: The year, as int, for which data is retrieved.
        :param grassland_area: An optional parameter (float), relevant only for grassland land use.
        :return: The share burnt for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown or if 'share_burnt' column is not found in the result.
        """
        if landuse == 'farmable_condition':
            return 0.0
        
        if landuse not in self.methods:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == 'grassland':
            result_df = self.methods[landuse](year, grassland_area)
        else:
            result_df = self.methods[landuse](year)

        if 'share_burnt' in result_df.columns:
            return result_df['share_burnt'].iloc[0]
        else:
            raise ValueError(f"'share_burnt' column not found in the result for land use: {landuse}")



    def get_national_burnt_average(self, landuse):
        """
        Calculates the national average of burnt areas for a specified land use type.

        :param landuse: The type of land use for which the burnt average is calculated as string.
        :return: The national average of burnt areas for the specified land use type.
        :rtype: float
        :raises ValueError: If the land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        burn_average = self.national_areas[landuse]()()["burnt_kha"].sum() / self.national_areas[landuse]()()["total_kha"].sum() 

        return burn_average   
    
    
    def get_national_area(self, landuse, year):
        """
        Retrieves the total area in hectares for a specified land use type and year from national datasets.

        :param landuse: The land use type as a string.
        :param year: The year for which data is retrieved as an integer.
        :return: The total area in hectares as a float.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        return self.national_areas[landuse]()().loc[year,"total_kha"].item()
    

    def get_national_mineral(self, landuse, year):
        """
        Calculates the share of mineral soil for a given land use type and year, based on national datasets.

        :param landuse: The land use type as a string.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of mineral soil as a float.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == "forest":
            mineral = (1 - (self.get_national_organic_mineral("forest", year) + self.get_national_organic("forest", year)))
        else:
            mineral = self.national_areas[landuse]()().loc[year,"mineral_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return mineral
    

    def get_national_organic(self, landuse, year):
        """
        Calculates the share of organic soil for a given land use type and year, based on national datasets.

        :param landuse: The land use type as a string.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of organic soil as a float.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == "forest":
            organic = self.national_areas[landuse]()().loc[year,"organic_emitting_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()
        else:
            organic = self.national_areas[landuse]()().loc[year,"organic_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return organic

    
    def get_national_organic_mineral(self, landuse, year):
        """
        Calculates the share of organic soil for a given land use type and year, based on national datasets.

        :param landuse: The land use type as a string.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of organic soil as a float.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown.
        """

        if landuse != "forest":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        organic_mineral = self.national_areas[landuse]()().loc[year,"organo_mineral_emitting_kha"].item()/ self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return organic_mineral
    

    def get_national_rich_drained_orgainc_grassland(self, landuse, year):
        """
        Calculates the share of rich drained organic soil for grassland in a given year, based on national datasets.

        :param landuse: Must be "grassland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of rich organic soil as a float, returns 0.0 for non-grassland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        rich_organic = self.national_areas[landuse]()().loc[year,"drained_rich_organic_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return rich_organic
    
    def get_national_poor_drained_organic_grassland(self, landuse, year):
        """
        Calculates the share of poor drained organic soil for grassland in a given year, based on national datasets.

        :param landuse: Must be "grassland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of poor organic soil as a float, returns 0.0 for non-grassland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        poor_organic = self.national_areas[landuse]()().loc[year,"drained_poor_organic_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return poor_organic
    
    def get_national_rich_rewetted_organic_grassland(self, landuse, year):
        """
        Calculates the share of rich rewetted organic soil for grassland in a given year, based on national datasets.

        :param landuse: Must be "grassland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of rich organic soil as a float, returns 0.0 for non-grassland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        rich_organic = self.national_areas[landuse]()().loc[year,"rewetted_rich_organic_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return rich_organic
    
    def get_national_poor_rewetted_organic_grassland(self, landuse, year):
        """
        Calculates the share of poor rewetted organic soil for grassland in a given year, based on national datasets.

        :param landuse: Must be "grassland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of poor organic soil as a float, returns 0.0 for non-grassland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        poor_organic = self.national_areas[landuse]()().loc[year,"rewetted_poor_organic_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return poor_organic
    

    def get_national_domestic_peat_extraction(self, landuse, year):
        """
        Calculates the share of areas under domestic peat extraction for wetlands in a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of areas under peat extraction as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        peat_extraction = self.national_areas[landuse]()().loc[year,"domestic_peat_extraction_kha"].item()/ self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return peat_extraction
    
    def get_national_industrial_peat_extraction(self, landuse, year):
        """
        Calculates the share of areas under industrial peat extraction for wetlands in a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of areas under peat extraction as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        peat_extraction = self.national_areas[landuse]()().loc[year,"industrial_peat_extraction_kha"].item()/ self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return peat_extraction
    

    def get_national_rewetted_domestic_peat(self, landuse, year):
        """
        Calculates the share of rewetted areas under domestic peat extraction for wetlands in a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of rewetted areas as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        rewetted = self.national_areas[landuse]()().loc[year,"rewetted_domestic_peat_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return rewetted
    

    def get_national_rewetted_industrial_peat(self, landuse, year):
        """
        Calculates the share of rewetted areas under industrial peat extraction for wetlands in a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of rewetted areas as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        rewetted = self.national_areas[landuse]()().loc[year,"rewetted_industrial_peat_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return rewetted


    def get_national_rewetted_in_organic(self, landuse, year):
        """
        Calculates the share of rewetted organic areas for wetlands in a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of rewetted organic areas as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        rewetted_in_organic = self.national_areas[landuse]()().loc[year,"rewetted_organic_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return rewetted_in_organic
    
    
    def get_national_rewetted_in_mineral(self, landuse, year):
        """
        Calculates the share of rewetted mineral areas for wetlands in a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of rewetted mineral areas as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """                
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        rewetted_in_mineral = self.national_areas[landuse]()().loc[year,"rewetted_mineral_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return rewetted_in_mineral
    
    def get_national_unmanaged_wetland(self, landuse, year):
        """
        Calculates the share of unmanaged wetland areas for a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of unmanaged wetland areas as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        unmanaged = self.national_areas[landuse]()().loc[year,"unmanaged_wetland_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return unmanaged
    
    def get_national_near_natural_wetland(self, landuse, year):
        """
        Calculates the share of near natural wetland areas for a given year, based on national datasets.

        :param landuse: Must be "wetland" for this calculation.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of near natural wetland areas as a float, returns 0.0 for non-wetland land uses.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        near_natural = self.national_areas[landuse]()().loc[year,"near_natural_wetland_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return near_natural
    
    
    def get_national_burn(self, landuse, year):
        """
        Calculates the share of burnt areas for a given land use type and year, based on national datasets.

        :param landuse: The land use type as a string.
        :param year: The year for which data is retrieved as an integer.
        :return: The share of burnt areas as a float.
        :rtype: float
        :raises ValueError: If the specified land use type is unknown.
        """    
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
    
        burn = self.national_areas[landuse]()().loc[year,"burnt_kha"].item() / self.national_areas[landuse]()().loc[year,"total_kha"].item()

        return burn

    
    def get_total_spared_area(self, spared_area, sc):
        """
        Retrieves the total spared area for a specific scenario from a spared area dataset.

        :param spared_area: A DataFrame containing spared area data.
        :param sc: The scenario as a string or integer.
        :return: The total spared area as a float.
        :rtype: float
        :raises ValueError: If the scenario is not found in the spared area dataset.
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
            
    
    def get_derived_national_grassland_area(self, grassland_area, sc=0):
        """
        Derives the national grassland area for a given scenario.

        :param grassland_area: A DataFrame or Series containing grassland area data.
        :type grassland_area: 
        :param sc: The scenario as a string or integer, default is 0.
        :return: The derived national grassland area as a float.
        :rtype: float
        :raises ValueError: If the scenario is not found in the grassland area data.
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
        Calculates the area with organic potential based on a spared area breakdown for a specific scenario.

        :param spared_breakdown: A DataFrame containing spared area breakdown data.
        :param total_spared_area: A DataFrame or Series containing total spared area data.
        :param sc: The scenario as a string or integer.
        :return: The area with organic potential as a float.
        :rtype: float
        :raises ValueError: If the scenario is not found in the spared breakdown dataset or if all values in the 'area_ha' column are zero.
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



