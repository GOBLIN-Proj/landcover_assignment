Installation
============

This section provides instructions on how to install the software.

Requirements
------------
The software requires the following:

- Python 3.9 or higher
- pyomo 6.9.4 or higher (below 7)
- highspy 1.7.2 or higher (the HiGHS solver; open source, no commercial solver needed)
- typing_extensions 4.0 or higher (Python 3.9 and 3.10 only; highspy needs it)
- pandas 2.1.4 or higher (below 4)
- numpy 1.25 or higher (below 3)
- sqlalchemy 1.4 or higher (below 3)
- catchment_data_api 0.1.0 or higher (below 0.2; catchment tree)

pip installs all of them with the package.


Install with pip
----------------
You can install the package using pip:

```bash

    pip install landcover_assignment
```

Install from Source
-------------------
To install from source using pip and git:

```bash
    pip install git+https://github.com/GOBLIN-Proj/landcover_assignment.git@main
```


