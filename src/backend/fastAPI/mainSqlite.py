from fastapi import FastAPI, Request
from pyquadkey2 import quadkey
import sqlite3
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup
    Initialise the Client and add it to request.state
    """
    # Connect to SQLite database
    con = sqlite3.connect("src/data/quadkeyDB.sqlite")
    yield {"con": con}

    """ Run on shutdown
        Close the connection
        Clear variables and release the resources
    """
    con.close()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_process_time_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f'Completed request {request.url} in {process_time} seconds')
    return response

origins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def getData(quadkeys, con, z, y, x):
    if not quadkeys:
        return []
    values_clause = ", ".join(f"('{qk}')" for qk in quadkeys)
    query = f"""
    WITH quadkey_temp(quadkey) AS (
        VALUES {values_clause}
    )
    SELECT t.quadkey, t.raster_1
    FROM data_slice_male_long_lat t
    JOIN quadkey_temp q
    ON t.quadkey = q.quadkey
    """
    # Execute the query
    operation2_start = time.time()
    cur = con.cursor()
    cur.execute(query)
    result = cur.fetchall()
    operation2_end = time.time()
    print(f"DB Query {z, y, x} took {operation2_end - operation2_start} seconds")
    # Map result to dictionary
    columns = [desc[0] for desc in cur.description]
    result_dicts = [dict(zip(columns, row)) for row in result]
    return result_dicts

async def loadTileMale(z, y, x, con):
    qkey = quadkey.from_tile((x, y), z)  # Get quadtree for this tile
    listofQKeys = qkey.children(
        z + 5
    )  # Get all children 3 levels deeper -> 64 data points for this tile
    return await getData(listofQKeys, con, z, y, x)

@app.get("/api/male/{z}/{y}/{x}")
async def get_male_tile(z: int, y: int, x: int, request: Request):
    print("Requesting tile", z, y, x)
    # Call the function and return the result
    operation1_start = time.time()
    result = await loadTileMale(z, y, x, request.state.con)
    operation1_end = time.time()
    print(f"Total time taken for {z, y, x} tile {operation1_end - operation1_start} seconds")
    return result

@app.get("/api/schema")
async def get_schema(request: Request):
    cur = request.state.con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    schema = cur.fetchall()
    return [row[0] for row in schema]
