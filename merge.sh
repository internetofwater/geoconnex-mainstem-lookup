#!/bin/sh
# Copyright 2025 Lincoln Institute of Land Policy
# SPDX-License-Identifier: Apache-2.0


# Merge the catchments and flowlines layers into a single GeoPackage
# and reproject them to EPSG:4326
# this requires that the gpkg files are downloaded from sciencebase and present
# in the examples directory

# Create a new merged GeoPackage with the catchments layer, reprojected to EPSG:4326
ogr2ogr -t_srs EPSG:4326 merged.gpkg examples/reference_catchments.gpkg

# Append the flowlines layer, reprojected to EPSG:4326
ogr2ogr -t_srs EPSG:4326 -update -nln flowlines merged.gpkg examples/reference_flowline.gpkg
