from fastapi import FastAPI, Request
import math
from pyquadkey2 import quadkey
import duckdb
from contextlib import asynccontextmanager
import json
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup
    Initialise the Client and add it to request.state
    """
    # Build the tree
    con = duckdb.connect(
        "../../data/qudkeyDB.duckdb"
    )  # Note: duckdb.sql connects to the default in-memory database connection
    con.install_extension("spatial")
    con.load_extension("spatial")
    yield {"con": con}

    """ Run on shutdown
        Close the connection
        Clear variables and release the resources
    """
    # Cleanup the tree?


app = FastAPI(lifespan=lifespan)

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
    result = con.execute(query).df()
    result = result.fillna(0)
    return result.to_dict(orient="records")


def loadTileMale(z, y, x, con):
    qkey = quadkey.from_tile((x, y), z)  # get quadtree for this tile
    listofQKeys = qkey.children(
        z + 1
    )  # get all children 3 levels deeper -> 64 data points for this til
    return getData(listofQKeys, con)


@app.get("/api/male/{z}/{y}/{x}")
async def get_male_tile(z: int, y: int, x: int, request: Request):
    # Call the function and return the result
    result = loadTileMale(z, y, x, request.state.con)
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
