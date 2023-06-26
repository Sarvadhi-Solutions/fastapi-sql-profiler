import datetime
import time
import traceback

import sqlalchemy.event
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from .database import session
from .models import QueryInfo, RequestInfo


class SessionHandler(object):
    """Handler for SQLAlchemy session profiling.

    Args:
    ----
        engine (sqlalchemy.engine.Engine, optional): SQLAlchemy Engine object to use for database operations.
            Defaults to `sqlalchemy.engine.Engine`.

    Attributes:
    ----------
        started (bool): Indicates whether the session profiling has been started.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy Engine object used for database operations.
        query_objs (list): List to store query objects during profiling.

    """

    def __init__(self, engine=sqlalchemy.engine.Engine):
        """Initialize a SessionHandler object.

        Args:
        ----
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine to be used for the session.
            Defaults to `sqlalchemy.engine.Engine`.

        """
        self.started = False
        self.engine = engine
        self.query_objs = []

    def _before_exec(self, conn, clause, multiparams, params):  # noqa: ARG002
        """SQLAlchemy event hook for handling before query execution.

        This method is called as an event hook by SQLAlchemy before a query is executed.
        It sets the start time of the query execution on the connection object.
        """
        conn._sqltap_query_start_time = time.time()

    def _after_exec(self, conn, clause, multiparams, params, results):  # noqa: ARG002
        """SQLAlchemy event hook called after query execution.

        This method is an event hook that is called after the execution of a database query.
        It captures the end time of the query execution, retrieves the start time from the connection object,
        compiles the query text, captures the stack trace, and appends the query information
        to the list of query objects.

        Args:
        ----
        conn (sqlalchemy.engine.Connection): The SQLAlchemy connection object.
        clause (sqlalchemy.sql.ClauseElement or str): The SQLAlchemy statement or clause that was executed.
        multiparams (tuple or dict): The multiparams passed to the executed statement.
        params (dict): The params passed to the executed statement.
        results: The results of the query execution.
        """
        end_time = time.time()
        start_time = getattr(conn, '_sqltap_query_start_time', end_time)

        try:
            text = clause.compile(dialect=conn.engine.dialect)
        except AttributeError:
            text = clause
        stack = traceback.extract_stack()
        stack_string = ''.join(traceback.format_list(stack))
        d = {
            "start_time": start_time,
            "end_time": end_time,
            "text": text,
            "stack": stack_string,
        }
        self.query_objs.append(d)

    def start(self):
        """Start profiling.

        :raises AssertionError: If calling this function when the session
            is already started.
        """
        if self.started is True:
            msg = "Profiling session is already started!"
            raise AssertionError(msg)
        self.started = True
        sqlalchemy.event.listen(self.engine, "before_execute",
                                self._before_exec)
        sqlalchemy.event.listen(self.engine, "after_execute", self._after_exec)

    def stop(self):
        """Stop profiling.

        :raises AssertionError: If calling this function when the session
            is already stopped.
        """
        if self.started is False:
            msg = "Profiling session is already stopped"
            raise AssertionError(msg)

        self.started = False
        sqlalchemy.event.remove(self.engine, "before_execute",
                                self._before_exec)
        sqlalchemy.event.remove(self.engine, "after_execute", self._after_exec)


class SQLProfilerMiddleware(BaseHTTPMiddleware):
    """Middleware for database profiling.

    Args:
    ----
        app (ASGIApp): The ASGI application to wrap the middleware around.
        Base: The SQLAlchemy Base class for table creation.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy Engine object for database operations.

    Attributes:
    ----------
        app (ASGIApp): The ASGI application to wrap the middleware around.
        Base: The SQLAlchemy Base class for table creation.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy Engine object for database operations.
        Session (sqlalchemy.orm.session.sessionmaker): The SQLAlchemy sessionmaker for creating database sessions.
        RequestInfo (class): The SQLAlchemy model class representing the 'middleware_requests' table.
        QueryInfo (class): The SQLAlchemy model class representing the 'middleware_query' table.
        queries (list): List to store query information during profiling.

    """

    def __init__(self, app, engine) -> None:
        """Initialize a SQLProfilerMiddleware object.

        Args:
        ----
        app: The Starlette application instance.
        base: The SQLAlchemy Base class.
        engine: The SQLAlchemy engine to be used for the database connection.

        """
        self.app = app
        self.engine = engine
        self.dispatch_func = self.dispatch
        self.queries = []

    def add_request(self, request, raw_body, body):
        """Add a new request to the 'middleware_requests' table.

        Args:
        ----
        request (Request): The incoming Starlette Request object.
        raw_body (str): The raw body of the request.
        body (str): The processed body of the request.

        Returns:
        -------
        RequestInfo: The newly added request object.

        """
        method = request.method
        path = request.url.path
        query_params = str(request.query_params)
        headers_json = dict(request.headers)
        request_info = RequestInfo(path=path, query_params=query_params, raw_body=raw_body,
                                   body=body, method=method, start_time=datetime.datetime.utcnow(), headers=headers_json)
        session.add(request_info)
        session.commit()
        session.refresh(request_info)
        return request_info

    def store(self, session_handler, request_id):
        """Store the profiling information into the database.

        Args:
        ----
        session_handler (SessionHandler): The SessionHandler object containing the query information.
        request_id (int): The ID of the request being profiled.

        """
        for query_obj in session_handler.query_objs:
            time_taken = query_obj['end_time'] - query_obj['start_time']
            mstimetaken = round(time_taken*1000, 3)
            query_data = QueryInfo(query=str(
                query_obj['text']), request_id=request_id, time_taken=mstimetaken, traceback=query_obj['stack'])
            session.add(query_data)
            session.commit()
            session.close()
        end_time = datetime.datetime.utcnow()
        request_obj = session.get(RequestInfo, request_id)
        time_taken = end_time - request_obj.start_time
        time_taken_second = time_taken.total_seconds()
        time_taken_ms = round(time_taken_second*1000, 3)
        request_obj.end_time = end_time
        request_obj.time_taken = time_taken_ms
        request_obj.total_queries = len(session_handler.query_objs)
        session.add(request_obj)
        session.commit()
        session.refresh(request_obj)
        session.close()

    async def set_body(self, request: Request, body: bytes):
        """Set the body of the request.

        This method is used to set the body of the request to the provided bytes.
        It updates the `request._receive` attribute with an asynchronous function
        that returns a dictionary containing the request type and body.

        Args:
        ----
        request: The Starlette Request object.
        body: The bytes representing the body of the request.

        """
        async def receive():
            """Asynchronous function to return the request type and body.

            Returns
            -------
            A dictionary with keys 'type' and 'body' containing the request type and body, respectively.

            """
            return {"type": "http.request", "body": body}
        request._receive = receive

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """Process the incoming request and generate a response while profiling the database queries.

        Args:
        ----
        request (Request): The incoming Starlette Request object.
        call_next (RequestResponseEndpoint): The endpoint to call to get the response.

        Returns:
        -------
        Response: The generated response.

        """
        # print("Before Request")
        await self.set_body(request, await request.body())
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" in content_type:
            raw_body = await request.form()
            body = str(dict(raw_body))
            raw_body = str(raw_body)
        elif "application/json" in content_type:
            raw_body = await request.body()
            body = raw_body.decode()
        else:
            raw_body = ''
            body = ''
        request_path = request.url.path
        if request_path == '/all_request' or request_path.startswith(('/request_detail', '/request_query','/favicon')):
            response = await call_next(request)
        else:
            requset_data = self.add_request(request, raw_body, body)
            request_id = requset_data.id
            session_handler = SessionHandler(self.engine)
            session_handler.start()
            response = await call_next(request)
            session_handler.stop()
            # print("After Request")
            self.store(session_handler, request_id)
        return response
