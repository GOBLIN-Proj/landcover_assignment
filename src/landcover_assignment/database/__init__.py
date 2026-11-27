import os

# The package database, built by tools/build_database.py from data_sources/ (see docs/data_sources.md).
# The version in the name is the package version that built it.
DATABASE_FILE = "land_use_database_0.5.0.db"


def get_local_dir():
    """Gets the directory containing this script

    Returns:
        str: full path to the the script's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def get_database_path():
    """Full path to the package database (``DATABASE_FILE``)."""
    return os.path.join(get_local_dir(), DATABASE_FILE)
