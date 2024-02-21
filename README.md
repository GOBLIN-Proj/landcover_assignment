# 🏘️🌳🌲🌽🍀 Land cover generator for the GOBLIN model (Ireland only)
[![license](https://img.shields.io/badge/License-MIT-red)](https://github.com/colmduff/landcover_assignment/blob/0.1.0/LICENSE)
[![python](https://img.shields.io/badge/python-3.9-blue?logo=python&logoColor=white)](https://github.com/colmduff/landcover_assignment)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 Based on the [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) land use tool module

 The package takes scenario input data, spared,utilised grassland area, the soil class breakdown for the spared grassland area, as well as the calibration year and target year. It produces a land use dataframe for grassland, cropland, forest, wetland, settlements and farmable conditon. It also produces a transition matrix, in the form of a dataframe, which captures the areas transitioning from one land use category to another. 

 Finally, this package produces an afforestation dataframe that can be used by the [cbm_runner](https://colmduff.github.io/cbm_runner/html/index.html), which is broken down by forest yield classes. The soil groups relate to those found in the [Teagasc national farm survey](https://www.teagasc.ie/rural-economy/rural-economy/national-farm-survey/). The soil groups are mapped to yield classes based on research conducted by [Farrelly, N. and Gallagher, G (2015)](https://journal.societyofirishforesters.ie/index.php/forestry/article/view/10299).

 An example has been provided below. Total grassland, spared area and spared area breakdown area generated by the [grassland_production module](https://colmduff.github.io/grassland_production/html/index.html).


 Final result are pandas dataframes that can be read by numerous GOBLIN packages, including GOBLIN lite and GeoGOBLIN (catchment level).

 The geo_landcover_assignment sub module is intended for use at the catchment level and interfaces with the catchment_data_api to 
 retrieve catchment specific data that has been derived from [Ireland's National Land Cover map](https://www.epa.ie/our-services/monitoring--assessment/assessment/mapping/national-land-cover-map/). 

 ```
    src/
    │
    ├── landcover_assignment
    │   └── ... (other modules and sub-packages)
        │
        ├── geo_landcover_assignment
        |   └── ... (other modules and sub-packages)

 ```

 For national level analysis, the historic land uses and areas of organic and mineral soil are taken from the National Invetory [CRF Tables](https://www.epa.ie/publications/monitoring--assessment/climate-change/air-emissions/irelands-national-inventory-submissions-2022.php).

 The package is currently parameterised for use in the Irish context. 

## Installation

Install from git hub. 

When prompted enter your ```<username>``` and password, which is your ```<access_token>```.

```<access_token>``` is provided by the repo manager.

```<username>``` pass your own github username.


```bash
pip install "landcover_assignment@git+https://github.com/colmduff/landcover_assignment.git@main" 

```

## Usage
The baseline year represents the scenario baseline. The target year is the end year for each one of the scenarios. 

The scenario dataframe is the scenario input parameters. 

Spared area and grassland area represent the calculated spared area and the remaining grassland area, respectively.

```python
import pandas as pd
import os
from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.landcover import LandCover
from landcover_assignment.afforestation import Afforestation

def main():

    path = "./data/"

    baseline = 2020
    target_year = 2050
    scenario_dataframe = pd.read_csv(os.path.join(path, "scenario_dataframe.csv"), index_col=0)
    spared_area = pd.read_csv(os.path.join(path, "spared_area.csv"), index_col=0)
    spared_area_breakdown = pd.read_csv(os.path.join(path, "spared_area_breakdown.csv"), index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    grassland_area = pd.read_csv(os.path.join(path, "total_grassland_area.csv"), index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)


    transition = TransitionMatrix(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    land = LandCover(
        baseline, target_year, scenario_dataframe, grassland_area, spared_area, spared_area_breakdown
    )

    
    #create_combined_future_land_use_area
    print("combined future land use area")
    print(land.combined_future_land_use_area())
    print("#"*50)

    #create_transition_matrix
    transition_matrix = transition.create_transition_matrix()
    print(transition_matrix)
    print("#"*50)

    #create afforestation 
    affor = Afforestation(baseline, target_year, scenario_dataframe, transition_matrix)
    print(affor.gen_cbm_afforestation_dataframe(spared_area_breakdown))

if __name__ == "__main__":
    main()
```
## License
This project is licensed under the terms of the MIT license.
