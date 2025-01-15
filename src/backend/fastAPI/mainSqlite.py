from fastapi import FastAPI, Request
from pyquadkey2 import quadkey
import sqlite3
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager.
    Connect to the SQLite database on startup
    and clean up resources on shutdown.
    """
    con = sqlite3.connect("../../data/quadkeyDB.sqlite")  # Database connection
    yield {"con": con}  # Provide connection to app state
    con.close()  # Close the database connection


app = FastAPI(lifespan=lifespan)  # Create FastAPI instance


@app.middleware("http")
async def add_process_time_logging(request: Request, call_next):
    """
    Middleware to log request processing time.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    return response


# Enable CORS for all origins
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def getData(quadkeys, con, z, y, x, raster_index):
    """
    Query the database for data matching the given quadkeys.
    """
    if not quadkeys:
        return []
    values_clause = ", ".join(f"('{qk}')" for qk in quadkeys)
    query = f"""
    WITH quadkey_temp(quadkey) AS (
        VALUES {values_clause}
    )
    SELECT t.quadkey, t.raster_{raster_index} as value
    FROM data_slice_male_long_lat t
    JOIN quadkey_temp q
    ON t.quadkey = q.quadkey
    """
    cur = con.cursor()
    cur.execute(query)  # Execute the query
    result = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result_dicts = [dict(zip(columns, row)) for row in result]
    return result_dicts


async def loadTileMale(z, y, x, con, raster_index, detailLevel):
    """
    Load detailed data for a specific tile based on zoom level.
    """
    qkey = quadkey.from_tile((x, y), z)  # Get the quadkey for the tile
    listofQKeys = qkey.children(z + detailLevel)  # Get children at the specified detail level
    return await getData(listofQKeys, con, z, y, x, raster_index)


@app.get("/api/male/{z}/{y}/{x}/{raster_index}/{detailLevel}/{heightLevel}/{maxValue}")
async def get_male_tile(
    z: int, y: int, x: int, raster_index: int, detailLevel: int, request: Request
):
    """
    API endpoint to fetch tile data.
    Parameters:
        z, y, x: Tile coordinates
        raster_index: Raster column index
        detailLevel: Detail level for children quadkeys
    """
    result = await loadTileMale(z, y, x, request.state.con, raster_index, detailLevel)
    return result


@app.get("/api/schema")
async def get_schema(request: Request):
    """
    API endpoint to fetch the database schema.
    """
    cur = request.state.con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    schema = cur.fetchall()
    return [row[0] for row in schema]
