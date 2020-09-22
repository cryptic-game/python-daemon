from typing import Optional, get_origin, Union

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.params import Depends
from pydantic.decorator import ValidatedFunction
from pydantic.fields import ModelField

app = FastAPI()


def check_authorization(authorization: Optional[str] = Header(None)):
    if authorization != "ZVLx2iZ4wbL6GEy9TAca39p3AOlDvVw0HJW5JvE8vJH1q7jXUrULFbHC":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization Header")


def create_model_from_function(func):
    model = ValidatedFunction(func).model
    model.__fields__ = {k: v for k, v in model.__fields__.items() if k in func.__code__.co_varnames}
    for k, v in func.__annotations__.items():
        if get_origin(v) is Union and type(None) in v.__args__:
            field: ModelField = model.__fields__[k]
            field.required = False
            field.default = None
    return model


def endpoint(path: str):
    def deco(func):
        async def inner(params: create_model_from_function(func)):
            return {"info": {"error": False}, "data": await func(**params.dict())}

        return app.post(path, dependencies=[Depends(check_authorization)])(inner)

    return deco


@endpoint("/device/info")
async def device_info(user_id: str, foo: str, bar: int, test: Optional[str]):
    return {"user_id": user_id, "foo": foo, "bar": bar + 2, "test": test}


@app.get("/daemon/endpoints", dependencies=[Depends(check_authorization)])
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
