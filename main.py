# Copyright 2025 Lincoln Institute of Land Policy
# SPDX-License-Identifier: Apache-2.0

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request
from pathlib import Path
import duckdb
import pandas as pd
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

BASE_PATH = Path(__file__).parent
MERGED_GPKG = BASE_PATH / "merged.gpkg"

# Create a DuckDB in-memory connection and enable spatial extension
LOGGER.info("Creating DuckDB connection")
con = duckdb.connect(database=":memory:")
con.execute("INSTALL spatial;")
con.execute("LOAD spatial;")

LOGGER.info("Loading data into DuckDB")
# Load catchments and flowlines into DuckDB
con.execute("""
CREATE TABLE catchments AS 
SELECT * FROM st_read('merged.gpkg', layer='reference_catchments')
""")

con.execute("""
CREATE INDEX catchments_geom_idx ON catchments USING rtree(geom);
""")

con.execute("""
CREATE TABLE flowlines AS 
SELECT * FROM st_read('merged.gpkg', layer='flowlines')
""")


# Load mainstem lookup as a DuckDB table
mainstem_lookup = pd.read_csv(
    "https://github.com/internetofwater/ref_rivers/releases/download/v2.1/mainstem_lookup.csv"
)
mainstem_lookup["lp_mainstem"] = mainstem_lookup["lp_mainstem"].astype(int)
mainstem_lookup["ref_mainstem_id"] = mainstem_lookup["ref_mainstem_id"].astype(int)
con.register("mainstem_lookup", mainstem_lookup)


async def get_mainstem(request: Request):
    """Given a point, return the Geoconnex mainstem associated with it"""
    try:
        lon = float(request.query_params["lon"])
        lat = float(request.query_params["lat"])
    except (KeyError, ValueError):
        return JSONResponse(
            {"error": "Invalid or missing 'lon'/'lat' query parameters"},
            status_code=400,
        )

    # Query for the catchment containing the point
    catchment_query = f"""
    SELECT featureid 
    FROM catchments
    WHERE ST_Intersects(geom, ST_Point({lon}, {lat}))
    LIMIT 1
    """
    catchment_result = con.execute(catchment_query).fetchone()
    if not catchment_result:
        return JSONResponse(
            {"error": "No catchment found for this point"}, status_code=404
        )

    feature_id = catchment_result[0]

    # Query flowline for that catchment
    flowline_query = f"""
    SELECT "TerminalPa" AS terminal_path
    FROM flowlines
    WHERE COMID = {feature_id}
    LIMIT 1
    """
    flowline_result = con.execute(flowline_query).fetchone()
    if not flowline_result:
        return JSONResponse(
            {"error": "No flowline found for this catchment"}, status_code=404
        )

    terminal_path_id = int(flowline_result[0])

    # Lookup mainstem
    mainstem_query = f"""
    SELECT ref_mainstem_id FROM mainstem_lookup
    WHERE lp_mainstem = {terminal_path_id}
    LIMIT 1
    """
    mainstem_result = con.execute(mainstem_query).fetchone()
    if not mainstem_result:
        return JSONResponse(
            {"error": "No Geoconnex mainstem found for this flowline"}, status_code=404
        )

    mainstem_id = int(mainstem_result[0])
    mainstem_url = (
        f"https://reference.geoconnex.us/collections/mainstems/items/{mainstem_id}"
    )

    return JSONResponse(
        {
            "lon": lon,
            "lat": lat,
            "mainstem_id": mainstem_id,
            "mainstem_url": mainstem_url,
        }
    )


routes = [Route("/", get_mainstem)]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
