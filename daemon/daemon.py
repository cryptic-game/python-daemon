import uvicorn
from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from authorization import HTTPAuthorization
from config import HOST, PORT, DEBUG
from endpoints import register_collections

# create fastapi app and register endpoint collections
app = FastAPI()
endpoints: list[dict] = register_collections(app)


@app.get("/daemon/endpoints", dependencies=[Depends(HTTPAuthorization())])
def daemon_endpoints():
    """
    Daemon info endpoint for the server

    :return: a list of dicts containing information about all endpoints and endpoint collections
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


def run_daemon():
    """Run the uvicorn http server"""

    uvicorn.run("daemon:app", host=HOST, port=PORT, reload=DEBUG)
