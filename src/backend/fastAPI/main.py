from fastapi import FastAPI, Request
import math
from pyquadkey2 import quadkey
import duckdb
from contextlib import asynccontextmanager
import json
from fastapi.middleware.cors import CORSMiddleware
import time



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup
    Initialise the Client and add it to request.state
    """
    # Build the tree
    con = duckdb.connect("src/data/qudkeydb.duckdb", read_only=True)  # Note: duckdb.sql connects to the default in-memory database connection
    con.install_extension("spatial")
    con.load_extension("spatial")
    yield {"con": con}

    """ Run on shutdown
        Close the connection
        Clear variables and release the resources
    """
    # Cleanup the tree?


app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_process_time_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f'Completed request in {process_time} seconds')
    return response

origins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def num2deg(xtile, ytile, zoom):
    n = 1 << zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def getData(quadkeys, con):
    operation1_start = time.time()
    if not quadkeys:
        return []
    values_clause = ", ".join(f"('{quadkey}')" for quadkey in quadkeys)
    # Query with list binding
    query = f"""
    WITH quadkey_temp(quadkey) AS (
        VALUES {values_clause}
    )
    SELECT t.*
    FROM data_slice_male_long_lat t
    JOIN quadkey_temp q
    ON t.quadkey = q.quadkey
    """
    # Execute the query
    operation1_end = time.time()
    print(f"Creating Query took {operation1_end - operation1_start} seconds")
    operation2_start = time.time()
    result = con.execute(query).df()
    operation2_end = time.time()
    print(f"DB Query took {operation2_end - operation2_start} seconds")
    operation3_start = time.time()
    result = result.fillna(0)
    resultsDic = result.to_dict(orient="records")
    operation3_end = time.time()
    print(f"Res reshape took {operation3_end - operation3_start} seconds")
    return resultsDic


def loadTileMale(z, y, x, con):
    qkey = quadkey.from_tile((x, y), z)  # get quadtree for this tile
    listofQKeys = qkey.children(
        z + 4
    )  # get all children 3 levels deeper -> 64 data points for this til
    return getData(listofQKeys, con)


@app.get("/api/male/{z}/{y}/{x}")
async def get_male_tile(z: int, y: int, x: int, request: Request):
    # Call the function and return the result
    operation1_start = time.time()
    result = loadTileMale(z, y, x, request.state.con)
    operation1_end = time.time()
    print(f"Total time taken for tile {operation1_end - operation1_start} seconds")
    return result


# @app.get("/api/male/whole")
# async def main(request: Request):
#     data_slice_male_quadkey = request.state.data_slice_male_quadkey
#     return df_to_json(data_slice_male_quadkey)


# @app.get("/api/male/ancestor/{quadkey}")
# async def get_ancestors(quadkey: int, request: Request):
#     data_slice_male_quadkey = request.state.data_slice_male_quadkey
#     filtered_data = filter_by_ancestor(data_slice_male_quadkey, str(quadkey))
#     return df_to_json(filtered_data)


@app.get("/api/male/descendant/{quadkey}")
async def get_descendants(quadkey: int, request: Request):
    data_slice_male_quadkey = request.state.data_slice_male_quadkey
    filtered_data = filter_by_descendent(data_slice_male_quadkey, str(quadkey))
    return df_to_json(filtered_data)

@app.get("/api/schema")
async def get_schema(request: Request):
    schema = request.state.con.sql("""PRAGMA show_tables;""").df()
    return schema

@app.get("/api/create_table")
async def create_table(request: Request):
    create_table_query = """
    CREATE TABLE if not exists data_slice_male_long_lat (
        quadkey VARCHAR,
        raster_1 FLOAT,
        raster_2 FLOAT,
        raster_3 FLOAT,
        raster_4 FLOAT,
        raster_5 FLOAT,
        raster_6 FLOAT,
        raster_7 FLOAT,
        raster_8 FLOAT,
        raster_9 FLOAT,
        raster_10 FLOAT,
        raster_11 FLOAT,
        raster_12 FLOAT,
        raster_13 FLOAT,
        raster_14 FLOAT,
        raster_15 FLOAT,
        raster_16 FLOAT,
        raster_17 FLOAT,
        raster_18 FLOAT,
        raster_19 FLOAT,
        raster_20 FLOAT,
        raster_21 FLOAT,
        raster_22 FLOAT,
        raster_23 FLOAT,
        raster_24 FLOAT,
        raster_25 FLOAT,
        raster_26 FLOAT,
        raster_27 FLOAT,
        raster_28 FLOAT,
        raster_29 FLOAT,
        raster_30 FLOAT
    );
"""
    # Execute the query to create the table
    request.state.con.execute(create_table_query)