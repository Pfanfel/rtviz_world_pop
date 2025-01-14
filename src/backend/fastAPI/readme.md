# Running the Backend Server

## Prerequisites

- Ensure the SQLite database exists at `src/data/quadkeyDB.sqlite`
- Database should be created using `loadDataSQLite.ipynb`

## Start the Server

Run the following command from the project root:

```bash
fastapi dev src/backend/fastAPI/mainSqlite.py
```
