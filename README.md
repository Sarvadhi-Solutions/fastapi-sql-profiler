## Database Query Profiling Middleware

This project is a middleware implementation for profiling and logging database queries in a Python web application. It utilizes the Starlette framework and SQLAlchemy for interacting with the database.

## Features

    * Logs database queries made within the web application.
    * Captures query execution times, query texts, and stack traces.
    * Stores query information in a database table along with request details.
    * Provides insights into query performance for debugging and optimization.

## Installation

pip install fastapi-sql-profiler

## Usage:
Update the database connection URL in the .env file.
```python
SQLALCHEMY_DATABASE_URL=<database_connection_url>
```
```python
from fastapi_sql_profiler.middleware import SQLProfilerMiddleware
from fastapi_sql_profiler.add_request import router
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
base = declarative_base()
engine = create_engine("your-database-connection-string")
app.include_router(router)
app.add_middleware(SQLProfilerMiddleware, engine=engine)
```

## Endpoints
Please paste the following endpoints in the browser to see the results.

    * `/all_request`: Displays all captured requests with pagination support.
    * `/request_detail/{id}`: Displays details of a specific request identified by its ID.
    * `/request_query/{id}`: Displays the queries associated with a specific request identified its ID.
    * `/request_query_details/{id}`: Displays details of a specific query identified by its ID.

![](https://github.com/Sarvadhi-Solutions/fastapi-sql-profiler/blob/main/doc/images/request.png)
## Contributing

Contributions are welcome! If you find a bug or have suggestions for improvements, please open an issue or submit a pull request.
