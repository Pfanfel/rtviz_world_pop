
# FastAPI Backend

## Overview

This project provides a lightweight backend service using FastAPI, which serves geospatial data stored in a SQLite database. Key features include:
- Retrieval of tile data using quadkeys.
- Detail-level control for granular queries.
- Database schema inspection.

### Technology Stack
- **Backend:** FastAPI
- **Database:** SQLite

## API Endpoints

### `/api/male/{z}/{y}/{x}/{raster_index}/{detailLevel}/{heightLevel}/{maxValue}`
Fetch tile data for a specific area.

**Parameters:**

  - `z` (int): Zoom level
  - `y` (int): Tile Y-coordinate
  - `x` (int): Tile X-coordinate
  - `raster_index` (int): Raster index for database query
  - `detailLevel` (int): Depth of children quadkeys

**Response:**
  JSON object with quadkey and corresponding data values.

### `/api/schema`
Retrieve the database schema.

**Response:**
  List of table names in the SQLite database.

## Key Components

### Middleware
A middleware logs the time taken for each request to help monitor performance.

### Database Interaction
The `lifespan` manager initializes a connection to the SQLite database and safely closes it when the app shuts down.

### Quadkey Usage
The application uses `pyquadkey2` to generate quadkeys and fetch detailed tile data.