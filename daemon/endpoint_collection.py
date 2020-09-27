import re
from typing import get_origin, Union

from fastapi import FastAPI, Depends
from pydantic import decorator
from pydantic.fields import ModelField

from authorization import authorized


def _create_model_from_function(func):
    model = decorator.ValidatedFunction(func).model
    model.__fields__ = {k: v for k, v in model.__fields__.items() if k in func.__code__.co_varnames}
    for k, v in func.__annotations__.items():
        if get_origin(v) is Union and type(None) in v.__args__:
            field: ModelField = model.__fields__[k]
            field.required = False
            field.default = None
    return model


class EndpointCollection:
    def __init__(self, name: str, description: str):
        if not re.match(r"^[a-zA-Z0-9\-_]+(/[a-zA-Z0-9\-_]+)*$", name):
            raise ValueError("empty endpoint collection name")

        self._name: str = name
        self._description: str = description
        self._endpoints = {}

    def endpoint(self, name: str):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", name):
            raise ValueError("invalid endpoint name")

        def deco(func):
            if name in self._endpoints:
                raise ValueError("endpoint already exists")

            self._endpoints[name] = func
            return func

        return deco

    def register(self, app: FastAPI):
        for name, func in self._endpoints.items():
            @app.post(f"/{self._name}/{name}", dependencies=[Depends(authorized)])
            def inner(params: _create_model_from_function(func)):
                return {"info": {"error": False}, "data": func(**params.dict())}
