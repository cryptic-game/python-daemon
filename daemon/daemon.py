import sys

import sentry_sdk
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from authorization import HTTPAuthorization
from config import API_TOKEN, HOST, PORT, DEBUG, SQL_CREATE_TABLES, SENTRY_DSN
from database import db
from endpoints import ENDPOINT_COLLECTIONS

if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, attach_stacktrace=True, shutdown_timeout=5)


app = FastAPI()

if not API_TOKEN:
    if DEBUG:
        print("\033[33mWARNING: No API token specified, endpoints can be accessed without authentication!\033[0m")
    else:
        print("\033[31m\033[1mERROR: No API token specified!\033[0m")
        sys.exit(1)

# register endpoint collections and prepare response for /daemon/endpoints endpoint
endpoints = [collection.register(app) for collection in ENDPOINT_COLLECTIONS]


@app.get("/daemon/endpoints", dependencies=[Depends(HTTPAuthorization())])
def daemon_endpoints():
    """
    Daemon info endpoint for the server

    :return: a dict containing information about all endpoints and endpoint collections
    """

    return endpoints


def _make_exception(status_code: int, **kwargs) -> JSONResponse:
    """
    Create a JSONResponse object containing an error message
    as specified in the protocol

    :param status_code: the http status code
    :param kwargs: any additional parameters
    :return: the JSONResponse object
    """

    detail = HTTPException(status_code).detail
    return JSONResponse({**kwargs, "error": f"{status_code} {detail}"}, status_code)


@app.exception_handler(HTTPException)
def handle_http_exception(_, exception: HTTPException):
    """Handle http exceptions"""

    return _make_exception(exception.status_code)


@app.exception_handler(RequestValidationError)
def handle_unprocessable_entity(_, exception: RequestValidationError):
    """Handle invalid request parameters"""

    return _make_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exception.errors())


@app.exception_handler(Exception)
def handle_internal_server_error(*_):
    """Handle any uncaught exception and return an Internal Server Error"""

    return _make_exception(status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/{_:path}")
def handle_not_found():
    """Handle Not Found exceptions"""

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    if SQL_CREATE_TABLES:
        db.Base.metadata.create_all(db.engine)
    uvicorn.run("daemon:app", host=HOST, port=PORT, reload=DEBUG)
