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

    Attributes
    ----------
    loader : Loader
        An instance of Loader to access national datasets.
    methods : dict
        A mapping from land use types to their respective data retrieval methods.
    national_areas : dict
        A dictionary containing methods to retrieve national area data for different land use types.
    """
    def __init__(self):
 
        self.loader = Loader()

        self.national_areas_cache = {}

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

    def _get_cached_data(self, landuse):
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
        if landuse not in self.national_areas_cache:
            # Cache the data if not already present
            self.national_areas_cache[landuse] = self.national_areas[landuse]()()

        return self.national_areas_cache[landuse].copy()
    

    def get_forest_data(self, year):
        """
        Retrieves summary data for forest land use including area, shares of mineral, organic, and organic-mineral soils, 
        peat extraction, and rewetted areas for a given year.

        Parameters
        ----------
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing summary data for forest land use.
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

        Parameters
        ----------
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing summary data for wetland land use.
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

        Parameters
        ----------
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing summary data for cropland use.
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

        Area is derived from total grassland area calculated using the grassland_production module.

        Parameters
        ----------
        year : int
            The year for which data is retrieved.
        total_grassland_area : float
            The total grassland area used for calculations.
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing summary data for grassland use.
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

        Parameters
        ----------
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        pandas.DataFrame
            A DataFrame containing summary data for settlement land use.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The total area for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'area_ha' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share mineral for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_mineral' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share organic for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_organic' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share organic mineral for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_organic_mineral' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share rich organic for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_drained_rich_organic' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share poor organic for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_poor_organic' column is not found in the result.
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
        Retrieves the share of rewetted rich organic soil for grassland for a specified land use type and year. For grassland, the total area must be provided.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share rewetted rich organic for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_rewetted_rich_organic' column is not found in the result.
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
        Retrieves the share of rewetted poor organic soil for grassland for a specified land use type and year. For grassland, the total area must be provided.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share rewetted poor organic for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_rewetted_poor_organic' column is not found in the result.
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
        Retrieves the share of rewetted organic soil for a specified land use type and year. For grassland, the total area must be provided.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share rewetted organic for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_rewetted_in_organic' column is not found in the result.
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
        Retrieves the share of rewetted mineral soil for a specified land use type and year. For grassland, the total area must be provided.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share rewetted mineral for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_rewetted_in_mineral' column is not found in the result.
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
        Retrieves the share of domestic peat extraction for a specified land use type and year.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share domestic peat extraction for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_domestic_peat_extraction' column is not found in the result.
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
        Retrieves the share of industrial peat extraction for a specified land use type and year.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share industrial peat extraction for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_industrial_peat_extraction' column is not found in the result.
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
        Retrieves the share of rewetted domestic peat extraction for a specified land use type and year.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share rewetted domestic peat extraction for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_rewetted_domestic_peat_extraction' column is not found in the result.
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
        Retrieves the share of rewetted industrial peat extraction for a specified land use type and year.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share rewetted industrial peat extraction for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_rewetted_industrial_peat_extraction' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share near natural wetland for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_near_natural_wetland' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share unmanaged wetland for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_unmanaged_wetland' column is not found in the result.
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
        Retrieves the share of burnt areas for a specified land use type and year. For grassland, the total area must be provided.

        Parameters
        ----------
        landuse : str
            The type of land use.
        year : int
            The year for which data is retrieved.
        grassland_area : float, optional
            Relevant only for grassland land use.
        
        Returns
        -------
        float
            The share burnt for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown or if 'share_burnt' column is not found in the result.
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

        Parameters
        ----------
        landuse : str
            The type of land use for which the burnt average is calculated.
        
        Returns
        -------
        float
            The national average of burnt areas for the specified land use type.
        
        Raises
        ------
        ValueError
            If the land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        burn_average = self.national_areas[landuse]()()["burnt_kha"].sum() / self.national_areas[landuse]()()["total_kha"].sum() 

        return burn_average   
    
    def get_national_area(self, landuse, year):
        """
        Retrieves the total area in hectares for a specified land use type and year from national datasets.

        Parameters
        ----------
        landuse : str
            The land use type.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The total area in hectares.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        # Retrieve the cached data
        data = self._get_cached_data(landuse)

        # Check if year exists in the data
        if year not in data.index:
            raise ValueError(f"Year {year} not found for land use type {landuse}")
        
        # Ensure the required column exists
        if "total_kha" not in data.columns:
            raise ValueError(f"'total_kha' column missing for land use type {landuse}")
        
        return data.loc[year, "total_kha"].item()
    

    def get_national_mineral(self, landuse, year):
        """
        Calculates the share of mineral soil for a given land use type and year, based on national datasets.

        Parameters
        ----------
        landuse : str
            The land use type.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of mineral soil.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        if landuse == "forest":
            mineral = (1 - (self.get_national_organic_mineral("forest", year) + self.get_national_organic("forest", year)))
        else:
            data = self._get_cached_data(landuse)
            mineral = data.loc[year,"mineral_kha"].item() / data.loc[year,"total_kha"].item()

        return mineral
    

    def get_national_organic(self, landuse, year):
        """
        Calculates the share of organic soil for a given land use type and year, based on national datasets.

        Parameters
        ----------
        landuse : str
            The land use type.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of organic soil.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown.
        """
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        data = self._get_cached_data(landuse)
        
        if landuse == "forest":
            
            organic = data.loc[year,"organic_emitting_kha"].item() / data.loc[year,"total_kha"].item()
        else:
            organic = data.loc[year,"organic_kha"].item() / data.loc[year,"total_kha"].item()

        return organic

    
    def get_national_organic_mineral(self, landuse, year):
        """
        Calculates the share of organic soil for a given land use type and year, based on national datasets.

        Parameters
        ----------
        landuse : str
            The land use type.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of organic soil.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown.
        """

        if landuse != "forest":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        organic_mineral = data.loc[year,"organo_mineral_emitting_kha"].item()/ data.loc[year,"total_kha"].item()

        return organic_mineral
    

    def get_national_rich_drained_orgainc_grassland(self, landuse, year):
        """
        Calculates the share of rich drained organic soil for grassland in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "grassland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of rich organic soil, returns 0.0 for non-grassland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        data = self._get_cached_data(landuse)

        rich_organic = data.loc[year,"drained_rich_organic_kha"].item() / data.loc[year,"total_kha"].item()

        return rich_organic
    

    def get_national_poor_drained_organic_grassland(self, landuse, year):
        """
        Calculates the share of poor drained organic soil for grassland in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "grassland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of poor organic soil, returns 0.0 for non-grassland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")
        
        data = self._get_cached_data(landuse)

        poor_organic = data.loc[year,"drained_poor_organic_kha"].item() / data.loc[year,"total_kha"].item()

        return poor_organic
    

    def get_national_rich_rewetted_organic_grassland(self, landuse, year):
        """
        Calculates the share of rich rewetted organic soil for grassland in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "grassland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of rich organic soil, returns 0.0 for non-grassland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)

        rich_organic = data.loc[year,"rewetted_rich_organic_kha"].item() / data.loc[year,"total_kha"].item()

        return rich_organic
    

    def get_national_poor_rewetted_organic_grassland(self, landuse, year):
        """
        Calculates the share of poor rewetted organic soil for grassland in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "grassland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of poor organic soil, returns 0.0 for non-grassland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "grassland".
        """
        if landuse != "grassland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        poor_organic = data.loc[year,"rewetted_poor_organic_kha"].item() / data.loc[year,"total_kha"].item()

        return poor_organic
    

    def get_national_domestic_peat_extraction(self, landuse, year):
        """
        Calculates the share of areas under domestic peat extraction for wetlands in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of areas under peat extraction, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)

        peat_extraction = data.loc[year,"domestic_peat_extraction_kha"].item()/ data.loc[year,"total_kha"].item()

        return peat_extraction
    
    
    def get_national_industrial_peat_extraction(self, landuse, year):
        """
        Calculates the share of areas under industrial peat extraction for wetlands in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of areas under peat extraction, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        peat_extraction = data.loc[year,"industrial_peat_extraction_kha"].item()/ data.loc[year,"total_kha"].item()

        return peat_extraction
    

    def get_national_rewetted_domestic_peat(self, landuse, year):
        """
        Calculates the share of rewetted areas under domestic peat extraction for wetlands in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of rewetted areas, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        rewetted = data.loc[year,"rewetted_domestic_peat_kha"].item() / data.loc[year,"total_kha"].item()

        return rewetted
    

    def get_national_rewetted_industrial_peat(self, landuse, year):
        """
        Calculates the share of rewetted areas under industrial peat extraction for wetlands in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of rewetted areas, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        rewetted = data.loc[year,"rewetted_industrial_peat_kha"].item() / data.loc[year,"total_kha"].item()

        return rewetted


    def get_national_rewetted_in_organic(self, landuse, year):
        """
        Calculates the share of rewetted organic areas for wetlands in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of rewetted organic areas, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        rewetted_in_organic = data.loc[year,"rewetted_organic_kha"].item() / data.loc[year,"total_kha"].item()

        return rewetted_in_organic
    
    
    def get_national_rewetted_in_mineral(self, landuse, year):
        """
        Calculates the share of rewetted mineral areas for wetlands in a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of rewetted mineral areas, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """                
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        rewetted_in_mineral = data.loc[year,"rewetted_mineral_kha"].item() / data.loc[year,"total_kha"].item()

        return rewetted_in_mineral
    

    def get_national_unmanaged_wetland(self, landuse, year):
        """
        Calculates the share of unmanaged wetland areas for a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of unmanaged wetland areas, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        unmanaged = data.loc[year,"unmanaged_wetland_kha"].item() / data.loc[year,"total_kha"].item()

        return unmanaged
    

    def get_national_near_natural_wetland(self, landuse, year):
        """
        Calculates the share of near natural wetland areas for a given year, based on national datasets.

        Parameters
        ----------
        landuse : str
            Must be "wetland" for this calculation.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of near natural wetland areas, returns 0.0 for non-wetland land uses.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown or not "wetland".
        """
        if landuse != "wetland":
            return 0.0
        
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)
        near_natural = data.loc[year,"near_natural_wetland_kha"].item() / data.loc[year,"total_kha"].item()

        return near_natural
    
    
    def get_national_burn(self, landuse, year):
        """
        Calculates the share of burnt areas for a given land use type and year, based on national datasets.

        Parameters
        ----------
        landuse : str
            The land use type.
        year : int
            The year for which data is retrieved.
        
        Returns
        -------
        float
            The share of burnt areas.
        
        Raises
        ------
        ValueError
            If the specified land use type is unknown.
        """    
        if landuse not in self.national_areas:
            raise ValueError(f"Unknown land use type: {landuse}")

        data = self._get_cached_data(landuse)

        burn = data.loc[year,"burnt_kha"].item() / data.loc[year,"total_kha"].item()

        return burn

    
    def get_total_spared_area(self, spared_area, sc):
        """
        Retrieves the total spared area for a specific scenario from a spared area dataset.

        Parameters
        ----------
        spared_area : pandas.DataFrame
            A DataFrame containing spared area data.
        sc : str or int
            The scenario.
        
        Returns
        -------
        float
            The total spared area.
        
        Raises
        ------
        ValueError
            If the scenario is not found in the spared area dataset.
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

        Parameters
        ----------
        grassland_area : pandas.DataFrame or pandas.Series
            A DataFrame or Series containing grassland area data.
        sc : str or int, optional
            The scenario, default is 0.
        
        Returns
        -------
        float
            The derived national grassland area.
        
        Raises
        ------
        ValueError
            If the scenario is not found in the grassland area data.
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

        Parameters
        ----------
        spared_breakdown : pandas.DataFrame
            A DataFrame containing spared area breakdown data.
        total_spared_area : pandas.DataFrame or pandas.Series
            A DataFrame or Series containing total spared area data.
        sc : str or int
            The scenario.
        
        Returns
        -------
        float
            The area with organic potential.
        
        Raises
        ------
        ValueError
            If the scenario is not found in the spared breakdown dataset or if all values in the 'area_ha' column are zero.
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


    def get_land_shares(self,key, land_use, year):
            
        """
        Retrieve the share of a specific land type for a given land use and year.
        Parameters:
        key (str): The key representing the specific land share to retrieve.
        land_use (str): The type of land use.
        year (int): The year for which the land share is to be retrieved.
        Returns:
        float: The share of the specified land type.
        Raises:
        KeyError: If the provided key is not found in the shares dictionary.
        Available keys:
        - "share_mineral"
        - "share_organic"
        - "share_drained_rich_organic"
        - "share_drained_poor_organic"
        - "share_rewetted_rich_organic"
        - "share_rewetted_poor_organic"
        - "share_organic_mineral"
        - "share_domestic_peat_extraction"
        - "share_industrial_peat_extraction"
        - "share_rewetted_domestic_peat_extraction"
        - "share_rewetted_industrial_peat_extraction"
        - "share_rewetted_in_mineral"
        - "share_rewetted_in_organic"
        - "share_near_natural_wetland"
        - "share_unmanaged_wetland"
        - "share_burnt"
        """
            
        shares ={
            "share_mineral": self.get_share_mineral(land_use, year),
            "share_organic":self.get_share_organic(land_use, year),
            "share_drained_rich_organic":self.get_share_drained_rich_organic_grassland(land_use, year),
            "share_drained_poor_organic":self.get_share_drained_poor_organic_grassland(land_use, year),
            "share_rewetted_rich_organic":self.get_share_rewetted_rich_in_organic_grassland(land_use, year),
            "share_rewetted_poor_organic":self.get_share_rewetted_poor_in_organic_grassland(land_use, year),
            "share_organic_mineral":self.get_share_organic_mineral(land_use, year),
            "share_domestic_peat_extraction":self.get_share_domestic_peat_extraction(land_use, year),
            "share_industrial_peat_extraction":self.get_share_industrial_peat_extraction(land_use, year),
            "share_rewetted_domestic_peat_extraction":self.get_share_rewetted_domestic_peat_extraction(land_use, year),
            "share_rewetted_industrial_peat_extraction":self.get_share_rewetted_industrial_peat_extraction(land_use, year),
            "share_rewetted_in_mineral":self.get_share_rewetted_in_mineral(land_use, year),
            "share_rewetted_in_organic":self.get_share_rewetted_in_organic(land_use, year),
            "share_near_natural_wetland":self.get_share_near_natural_wetland(land_use, year),
            "share_unmanaged_wetland":self.get_share_unmanaged_wetland(land_use, year),
            "share_burnt":self.get_share_burnt(land_use, year)
        }

        return shares[key]
    

    def get_grassland_shares(self, key, year, grassland_area):
        """
        Retrieve the share of a specific land type for grassland use and year.

        Parameters
        ----------
        key : str
            The key representing the specific land share to retrieve.
        year : int
            The year for which the land share is to be retrieved.
        grassland_area : float
            The total grassland area used for calculations.
        
        Returns
        -------
        float
            The share of the specified land type.
        
        Raises
        ------
        KeyError
            If the provided key is not found in the shares dictionary.
        
        Available keys:
        - "share_mineral"
        - "share_organic"
        - "share_drained_rich_organic"
        - "share_drained_poor_organic"
        - "share_rewetted_rich_in_organic"
        - "share_rewetted_poor_in_organic"
        - "share_organic_mineral"
        - "share_burnt"
        """
        shares ={
                "share_mineral": self.get_share_mineral("grassland", year, grassland_area),
                "share_organic": self.get_share_organic("grassland", year, grassland_area),
                "share_drained_rich_organic": self.get_share_drained_rich_organic_grassland("grassland", year, grassland_area),
                "share_drained_poor_organic": self.get_share_drained_poor_organic_grassland("grassland", year, grassland_area),
                "share_rewetted_rich_in_organic": self.get_share_rewetted_rich_in_organic_grassland("grassland", year, grassland_area),
                "share_rewetted_poor_in_organic": self.get_share_rewetted_poor_in_organic_grassland("grassland", year, grassland_area),
                "share_organic_mineral": self.get_share_organic_mineral("grassland", year, grassland_area),
                "share_burnt": self.get_share_burnt("grassland", year, grassland_area),
            }

        return shares[key]



