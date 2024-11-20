from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from quadtree import (
    load_male_dataset,
    df_to_json,
    filter_by_ancestor,
    filter_by_descendent,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup
    Initialise the Client and add it to request.state
    """
    # Build the tree
    data_slice_male_quadkey = load_male_dataset()
    yield {"data_slice_male_quadkey": data_slice_male_quadkey}
    """ Run on shutdown
        Close the connection
        Clear variables and release the resources
    """
    # Cleanup the tree?


app = FastAPI(lifespan=lifespan)


@app.get("/api/male/whole")
async def main(request: Request):
    data_slice_male_quadkey = request.state.data_slice_male_quadkey
    return df_to_json(data_slice_male_quadkey)


@app.get("/api/male/ancestor/{quadkey}")
async def get_ancestors(quadkey: int, request: Request):
    data_slice_male_quadkey = request.state.data_slice_male_quadkey
    filtered_data = filter_by_ancestor(data_slice_male_quadkey, str(quadkey))
    return df_to_json(filtered_data)


@app.get("/api/male/descendant/{quadkey}")
async def get_descendants(quadkey: int, request: Request):
    data_slice_male_quadkey = request.state.data_slice_male_quadkey
    filtered_data = filter_by_descendent(data_slice_male_quadkey, str(quadkey))
    return df_to_json(filtered_data)
