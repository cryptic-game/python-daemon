import sys

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from authorization import authorized
from config import API_TOKEN, HOST, PORT, DEBUG
from database import db
from endpoints import ENDPOINT_COLLECTIONS

app = FastAPI()

if not API_TOKEN:
    if DEBUG:
        print("\033[33mWARNING: No API token specified, endpoints can be accessed without authentication!\033[0m")
    else:
        print("\033[31m\033[1mERROR: No API token specified!\033[0m")
        sys.exit(1)

endpoints = [collection.register(app) for collection in ENDPOINT_COLLECTIONS]


@app.get("/daemon/endpoints", dependencies=[Depends(authorized)])
def daemon_endpoints():
    return endpoints


def make_exception(status_code: int, **kwargs) -> JSONResponse:
    detail = HTTPException(status_code).detail
    return JSONResponse({**kwargs, "error": f"{status_code} {detail}"}, status_code)


@app.exception_handler(HTTPException)
def handle_http_exception(_, exception: HTTPException):
    return make_exception(exception.status_code)


@app.exception_handler(RequestValidationError)
def handle_unprocessable_entity(_, exception: RequestValidationError):
    return make_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exception.errors())


@app.exception_handler(Exception)
def handle_internal_server_error(*_):
    # todo: add sentry
    return make_exception(status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/{_:path}")
def handle_not_found():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    db.Base.metadata.create_all(db.engine)  # todo: remove this
    uvicorn.run("daemon:app", host=HOST, port=PORT, reload=DEBUG)
