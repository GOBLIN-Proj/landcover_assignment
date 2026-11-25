"""Unit conversions for landcover_assignment, kept in one place (the same pattern as landcover_lca).

The package database stores every value **as published**, in the source's unit (CRT 2026 and NID 2026 areas in kha),
and its ``column_metadata`` table names that unit for every column. The readers in ``database_manager`` convert on
read, column by column, using the table below. So a number in the database can be checked against its source by eye,
and every conversion happens here.

Model units (what the calculations receive):
    areas       ha
    shares      dimensionless (an area divided by an area, so its unit cancels)

To add a column with a new unit, record the unit in ``column_metadata`` (tools/build_database.py) and add it here.
"""

# area
KHA_TO_HA = 1e3
HA_TO_KHA = 1 / KHA_TO_HA     # used by tools/build_database.py: CRF burnt area is published in ha (D6b)

# mass of methane: kg CH4-C to kg CH4 (16/12). Used by tools/build_database.py for the D4 rich/poor split; the NID
# prints the grassland rewet-status CH4 factors in kg CH4-C and the CRT implied factors in kg CH4.
CH4_C_TO_CH4 = 16.0 / 12.0

# published unit -> (multiplier to the model unit, model unit)
UNITS = {
    "kha": (KHA_TO_HA, "ha"),
    "ha": (1.0, "ha"),
    "ha/yr": (1.0, "ha/yr"),     # cbm_runner mean annual fire (D6a)
    "1/yr": (1.0, "1/yr"),       # cbm_runner scenario fire rate (D6a)
}

# column_metadata units that are keys or labels, not quantities: read as they are.
NOT_CONVERTED = {"year", "label", "group"}


def to_model_units(value, unit, name=""):
    """Convert a published value (a number or a pandas object) to the model unit. Raises KeyError for an unlisted
    unit."""
    if unit not in UNITS:
        raise KeyError(f"{name}: unit {unit!r} is not in landcover_assignment.resource_manager.units.UNITS")
    return value * UNITS[unit][0]


def model_unit(unit):
    """The unit a published unit is converted to."""
    return UNITS[unit][1]
