# 🏘️🌳🌲🌽🍀 Land cover generator for the GOBLIN model (Ireland only)

 Based on the [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) land use tool module

 The package takes scenario input data, spared and utilised grassland area, as well as the calibration year and target year. It produces a land use dataframe for grassland, cropland, forest, wetland, settlements and farmable conditon. It also produces a transition matrix, in the form of a dataframe, which captures the areas transitioning from one land use category to another. 

 Currently parameterised for Ireland, the historic land uses and areas of organic and mineral soil are taken from the National Invetory [CRF Tables](https://www.epa.ie/publications/monitoring--assessment/climate-change/air-emissions/irelands-national-inventory-submissions-2022.php)

 Final result are pandas dataframes that can be read by numerous GOBLIN packages.

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
from landcover_assignment.transition_matrix import TransitionMatrix
from landcover_assignment.landcover import LandCover
import pandas as pd


def main():
    
    baseline = 2020
    target_year = 2050
    scenario_dataframe = pd.read_csv("./data/scenario_dataframe.csv", index_col=0)
    spared_area = pd.read_csv("./data/spared_area.csv", index_col=0)
    spared_area.columns = spared_area.columns.astype(int)
    grassland_area = pd.read_csv("./data/total_grassland_area.csv", index_col=0)
    grassland_area.columns = grassland_area.columns.astype(int)
    
    transition = TransitionMatrix(baseline, target_year, scenario_dataframe, grassland_area, spared_area)

    transition.create_transition_matrix().to_csv("./data/transition.csv")

    land = LandCover(baseline, target_year, scenario_dataframe, grassland_area, spared_area)

    land.combined_future_land_use_area().to_csv("./data/land_uses.csv")


if __name__ == "__main__":
    main()
    
```
## License
This project is licensed under the terms of the MIT license.
