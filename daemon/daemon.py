from fastapi import FastAPI, status, Request
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from authorization import HTTPAuthorization
from database import db
from endpoint_collection import format_docs
from endpoints import register_collections
from environment import SQL_CREATE_TABLES
from exceptions.api_exception import APIException
from schemas.daemon import EndpointCollectionModel
from utils import responses

# create fastapi app and register endpoint collections
app = FastAPI(title="Python Daemon")
endpoints: list[dict] = register_collections(app)


@app.middleware("http")
async def db_session(request: Request, call_next):
    db.create_session()
    try:
        return await call_next(request)
    finally:
        await db.commit()
        await db.close()


@app.on_event("startup")
async def on_startup():
    if SQL_CREATE_TABLES:
        await db.create_tables()


@app.get(
    "/daemon/endpoints",
    name="List Daemon Endpoints",
    tags=["daemon"],
    dependencies=[Depends(HTTPAuthorization())],
    responses=responses(list[EndpointCollectionModel]),
)
@format_docs
async def daemon_endpoints():
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


@app.exception_handler(APIException)
async def handle_api_exception(_, exception: APIException):
    """Handle api exceptions"""

    return exception.make_response()


@app.exception_handler(HTTPException)
async def handle_http_exception(_, exception: HTTPException):
    """Handle http exceptions"""

    return _make_exception(exception.status_code)


@app.exception_handler(RequestValidationError)
async def handle_unprocessable_entity(_, exception: RequestValidationError):
    """Handle invalid request parameters"""

    return _make_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exception.errors())


@app.exception_handler(Exception)
async def handle_internal_server_error(*_):
    """Handle any uncaught exception and return an Internal Server Error"""

    return _make_exception(status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/{_:path}", include_in_schema=False)
async def handle_not_found():
    """Handle Not Found exceptions"""

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
