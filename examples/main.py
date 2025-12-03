# Copyright 2025 Lincoln Institute of Land Policy
# SPDX-License-Identifier: Apache-2.0

"""
This file is an example showing how to do a geoconnex
mainstem lookup with geopandas. It is useful if you want
a way that does not require a server and you just want to
download the script / gpkg directly
"""

# %%
from pathlib import Path
import geopandas as gpd
import shapely

# %%
# Read in the geopackage files; these can be downloaded from
# https://www.sciencebase.gov/catalog/item/61295190d34e40dd9c06bcd7
catchments = gpd.read_file(Path(__file__).parent / "reference_catchments.gpkg")
flowlines = gpd.read_file(Path(__file__).parent / "reference_flowline.gpkg")

# %%
# Project catchments to the same coordinate system
catchments = catchments.to_crs("epsg:4326")
assert catchments.crs == "epsg:4326", catchments.crs
flowlines = flowlines.to_crs("epsg:4326")
assert flowlines.crs == "epsg:4326", flowlines.crs

# %%
# First we get the featureid for the catchment. This is a catchment id aka COMID
pointOnColoradoRiver = shapely.geometry.Point(-108.50231860661755, 39.05108882481538)
associatedCatchment = catchments[catchments.intersects(pointOnColoradoRiver)]
featureID = associatedCatchment["featureid"].iloc[0]  # type: ignore
assert featureID == 3185828

# %%
# Next we get the associated flowline(s) for the catchment
relevantFlowline = flowlines[flowlines["COMID"] == featureID]
assert relevantFlowline.shape[0] == 1
assert relevantFlowline["gnis_name"].iloc[0] == "Colorado River"  # type: ignore
assert relevantFlowline["gnis_id"].iloc[0] == 45730  # type: ignore

# The terminal path is the last segment of the flowline (aka the mainstem)
TERMINAL_PATH = "TerminalPa"
terminalPathID = relevantFlowline[TERMINAL_PATH].iloc[0]  # type: ignore
assert terminalPathID == 308280

# %%
# Finally we use the id of the terminal path to find the associated geoconnex mainstem
mainstem_lookup = gpd.read_file(
    "https://github.com/internetofwater/ref_rivers/releases/download/v2.1/mainstem_lookup.csv"
)
# The mainstem lookup CSV uses strings instead of integers so we cast
mainstem_lookup["lp_mainstem"] = mainstem_lookup["lp_mainstem"].astype(int)
mainstem_lookup["ref_mainstem_id"] = mainstem_lookup["ref_mainstem_id"].astype(int)

geoconnex_mainstem_id = mainstem_lookup.loc[
    mainstem_lookup["lp_mainstem"] == terminalPathID
]["ref_mainstem_id"].iloc[0]  # type: ignore

assert geoconnex_mainstem_id == 29559

# The point POINT (-108.50231860661755 39.05108882481538) is associated with the mainstem https://reference.geoconnex.us/collections/mainstems/items/29559
print(
    f"The point {pointOnColoradoRiver} is associated with the mainstem https://reference.geoconnex.us/collections/mainstems/items/{geoconnex_mainstem_id}"
)
