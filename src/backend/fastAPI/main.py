from fastapi import FastAPI, Request
from pyquadkey2 import quadkey
import duckdb

app = FastAPI(debug=True)





def getData(quadkeys):
    if not quadkeys:
        return []
    values_clause = ', '.join(f"('{quadkey}')" for quadkey in quadkeys)
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
    print(query)
    # Execute the query
    return con.execute(query).fetchall()

def loadTileMale(z, y, x):
    qkey = quadkey.from_tile((x,y), z) # get quadtree for this tile
    listofQKeys = qkey.children(z+3) # get all children 3 levels deeper -> 64 data points for this til
    return getData(listofQKeys)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Run at startup
#     Initialise the Client and add it to request.state
#     """
#     # Build the tree
#     data_slice_male_quadkey = load_male_dataset()
#     yield {"data_slice_male_quadkey": data_slice_male_quadkey}
#     """ Run on shutdown
#         Close the connection
#         Clear variables and release the resources
#     """
#     # Cleanup the tree?

# app = FastAPI(lifespan=lifespan)

con = duckdb.connect("../../data/qudkeyDB.duckdb") # Note: duckdb.sql connects to the default in-memory database connection
con.install_extension("spatial")
con.load_extension("spatial")

@app.get("/api/male/{z}/{y}/{x}")
async def get_male_tile(z: int, y: int, x: int):
    # Call the function and return the result
    result = loadTileMale(z, y, x)
    return result

@app.get("/api/schema")
async def showTables():
    # Call the function and return the result
    tables = con.execute("SHOW TABLES").fetchdf()
    return tables

# @app.get("/api/male/whole")
# async def main(request: Request):
#     data_slice_male_quadkey = request.state.data_slice_male_quadkey
#     return df_to_json(data_slice_male_quadkey)


# @app.get("/api/male/ancestor/{quadkey}")
# async def get_ancestors(quadkey: int, request: Request):
#     data_slice_male_quadkey = request.state.data_slice_male_quadkey
#     filtered_data = filter_by_ancestor(data_slice_male_quadkey, str(quadkey))
#     return df_to_json(filtered_data)


# @app.get("/api/male/descendant/{quadkey}")
# async def get_descendants(quadkey: int, request: Request):
#     data_slice_male_quadkey = request.state.data_slice_male_quadkey
#     filtered_data = filter_by_descendent(data_slice_male_quadkey, str(quadkey))
#     return df_to_json(filtered_data)
