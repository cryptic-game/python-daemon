import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends

from authorization import authorized
from config import API_TOKEN, HOST, PORT, DEBUG
from endpoints import ENDPOINT_COLLECTIONS

app = FastAPI()

if not API_TOKEN:
    if DEBUG:
        print("\033[33mWARNING: No API token specified, endpoints can be accessed without authentication!\033[0m")
    else:
        print("\033[31m\033[1mERROR: No API token specified!\033[0m")
        exit(1)

endpoints = [collection.register(app) for collection in ENDPOINT_COLLECTIONS]


@app.get("/daemon/endpoints", dependencies=[Depends(authorized)])
def daemon_endpoints():
    return endpoints


if __name__ == "__main__":
    uvicorn.run("daemon:app", host=HOST, port=PORT, reload=DEBUG)
