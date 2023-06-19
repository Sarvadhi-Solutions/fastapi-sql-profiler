## Database Query Profiling Middleware

This project is a middleware implementation for profiling and logging database queries in a Python web application. It utilizes the Starlette framework and SQLAlchemy for interacting with the database.

## Features

    * Profiles and logs database queries made within the web application.
    * Captures query execution times, query texts, and stack traces.
    * Stores query information in a database table along with request details.
    * Provides insights into query performance for debugging and optimization.

## Installation

pip install fastapi-sql-profiler

## Usage:

```python
from fastapi_sql_profiler.middleware import SQLProfilerMiddleware
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
base = declarative_base()
engine = create_engine("your-database-connection-string")
app.add_middleware(SQLProfilerMiddleware, base=Base, engine=engine)
```

## Contributing

Contributions are welcome! If you find a bug or have suggestions for improvements, please open an issue or submit a pull request.
