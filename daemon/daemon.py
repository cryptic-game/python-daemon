import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends

from authorization import authorized
from config import API_TOKEN, HOST, PORT, DEBUG
from endpoints import ENDPOINT_COLLECTIONS

app = FastAPI()

if not API_TOKEN:
    print("\033[33mWARNING: Authorization is disabled!\033[0m")

for collection in ENDPOINT_COLLECTIONS:
    collection.register(app)


@app.get("/daemon/endpoints", dependencies=[Depends(authorized)])
def daemon_endpoints():
    return {
        "info": {"error": False},
        "data": [
            {
                "name": "device",
                "description": "Device endpoints",
                "endpoints": [
                    {
                        "name": "device/info",
                        "description": "hello world",
                        "parameters": [
                            {"name": "foo", "description": "foo", "optional": False, "type": "string"},
                            {"name": "bar", "description": "bar", "optional": False, "type": "int"},
                            {"name": "test", "description": "optional test parameter", "optional": True, "type": "str"},
                        ],
                    }
                ],
            }
        ],
    }


if __name__ == "__main__":
    uvicorn.run("daemon:app", host=HOST, port=PORT, reload=DEBUG)
