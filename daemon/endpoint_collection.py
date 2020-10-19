import re
from types import FunctionType, MethodType
from typing import get_origin, Union, Dict

from fastapi import FastAPI, Depends
from pydantic import decorator, BaseModel
from pydantic.fields import ModelField

from authorization import authorized


def _create_model_from_function(func: Union[FunctionType, MethodType]) -> BaseModel:
    model = decorator.ValidatedFunction(func).model
    model.__fields__ = {k: v for k, v in model.__fields__.items() if k in func.__code__.co_varnames}
    for k, v in func.__annotations__.items():
        if get_origin(v) is Union and type(None) in v.__args__:
            field: ModelField = model.__fields__[k]
            field.required = False
            field.default = None
    return model


class Endpoint:
    def __init__(self, collection: "EndpointCollection", name: str, func: FunctionType):
        self._collection: EndpointCollection = collection
        self._name: str = name
        self._func: FunctionType = func
        self._model: BaseModel = _create_model_from_function(self._func)

    @property
    def path(self) -> str:
        return f"{self._collection.path}/{self._name}"

    def describe(self) -> dict:
        parameter_descriptions: Dict[str, str] = {}
        endpoint_description: str = ""
        reached_metadata = False
        for line in map(str.strip, self._func.__doc__.splitlines()):
            if not line:
                continue

            if match := re.match(r"^:param ([a-zA-Z0-9_]+): (.+)$", line):
                parameter_descriptions[match.group(1)] = match.group(2)
            elif not (reached_metadata := reached_metadata or line.startswith(":")):
                endpoint_description += line + "\n"

        endpoint_description = endpoint_description.strip()
        if not endpoint_description:
            raise RuntimeError(f"Description for endpoint '{self.path}' could not be found.")

        parameters = []
        for name, field in self._model.__fields__.items():
            if name == "user_id":
                continue
            if name not in parameter_descriptions:
                raise RuntimeError(f"Description for paramter '{name}' of endpoint '{self.path}' could not be found.")
            parameters.append({"id": name, "description": parameter_descriptions[name], "required": field.required})

        return {
            "id": self._name,
            "description": endpoint_description,
            "disabled": False,
            "parameters": parameters,
        }

    def register(self, app: FastAPI) -> dict:
        model = self._model

        @app.post(self.path, dependencies=[Depends(authorized)])
        def inner(params: model):
            return self._func(**params.dict())

        return self.describe()


class EndpointCollection:
    def __init__(self, name: str, description: str):
        if not re.match(r"^[a-zA-Z0-9\-_]+(/[a-zA-Z0-9\-_]+)*$", name):
            raise ValueError("empty endpoint collection name")

        self._name: str = name
        self._description: str = description
        self._endpoints: Dict[str, Endpoint] = {}

    @property
    def path(self) -> str:
        return f"/{self._name}"

    def endpoint(self, name: str):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", name):
            raise ValueError("invalid endpoint name")

        def deco(func):
            if name in self._endpoints:
                raise ValueError("endpoint already exists")

            self._endpoints[name] = Endpoint(self, name, func)
            return func

        return deco

    def register(self, app: FastAPI) -> dict:
        return {
            "id": self._name,
            "description": self._description,
            "disabled": False,
            "endpoints": [endpoint.register(app) for endpoint in self._endpoints.values()],
        }
