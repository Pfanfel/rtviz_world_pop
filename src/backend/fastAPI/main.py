from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from quadtree import build_quadtree


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup
    Initialise the Client and add it to request.state
    """
    # Build the tree
    zoom_level_2, zoom_level_13 = build_quadtree()
    yield {"quadtrees": (zoom_level_2, zoom_level_13)}
    """ Run on shutdown
        Close the connection
        Clear variables and release the resources
    """
    # Cleanup the tree?


app = FastAPI(lifespan=lifespan)


@app.get("/api/whole/male")
async def main(request: Request, zoom: int = 2):
    if zoom == 2:
        zoom_level_2 = request.state.quadtrees[0]
        return {"zoom": zoom_level_2}
    elif zoom == 13:
        zoom_level_13 = request.state.quadtrees[1]
        return {"zoom": zoom_level_13}
