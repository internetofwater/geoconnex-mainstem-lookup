#!/bin/sh
# Copyright 2025 Lincoln Institute of Land Policy
# SPDX-License-Identifier: Apache-2.0


# Duckdb can also read in geoparquet; this script converts the geopackages to parquet

ogr2ogr -f "Parquet" reference_flowline.parquet examples/reference_flowline.gpkg -t_srs EPSG:4326

ogr2ogr -f "Parquet" reference_catchments.parquet examples/reference_catchments.gpkg -t_srs EPSG:4326