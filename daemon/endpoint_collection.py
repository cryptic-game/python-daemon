import re
from types import FunctionType, MethodType
from typing import get_origin, Union, Dict, Optional

from fastapi import FastAPI, Depends
from pydantic import decorator, BaseModel
from pydantic.fields import ModelField

from authorization import authorized
from database import db
from exceptions import EndpointException

Function = Union[FunctionType, MethodType]


def _create_model_from_function(func: Function) -> BaseModel:
    """
    Create a pydantic model from a function

    :param func: the function
    :return: the pydantic model
    """

    model = decorator.ValidatedFunction(func).model
    model.__fields__ = {k: v for k, v in model.__fields__.items() if k in func.__code__.co_varnames}
    for k, v in func.__annotations__.items():
        if get_origin(v) is Union and type(None) in v.__args__:
            field: ModelField = model.__fields__[k]
            field.required = False
            field.default = None
    model.__fields__["user_id"] = decorator.ValidatedFunction(lambda user_id: None).model.__fields__["user_id"]
    return model


class Endpoint:
    def __init__(self, collection: "EndpointCollection", name: str, func: Function):
        self._collection: EndpointCollection = collection
        self._name: str = name
        self._func: Function = func
        self._model: BaseModel = _create_model_from_function(self._func)

    @property
    def path(self) -> str:
        """path of this endpoint"""

        return f"{self._collection.path}/{self._name}"

    def describe(self) -> dict:
        """
        Describe the endpoint according to the protocol

        :return: dict containing information about this endpoint
        """

        # parse docstring of the function
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

        # endpoint description must not be empty
        endpoint_description = endpoint_description.strip()
        if not endpoint_description:
            raise RuntimeError(f"Description for endpoint '{self.path}' could not be found.")

        # collect parameters from pydantic model and use descriptions from docstring
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
        """
        Register this endpoint in the FastAPI app

        :param app: the FastAPI app
        :return: the endpoint description for the /daemon/endpoints endpoint
        """

        model = self._model

        @app.post(self.path, dependencies=[Depends(authorized)])
        def inner(params: model):
            """
            Wrapper function of all daemon endpoints

            :param params: a pydantic model containing the parameters
            :return: the response of the endpoint
            """

            try:
                kwargs = params.dict()
                if "user_id" not in self._func.__code__.co_varnames:
                    kwargs.pop("user_id")
                return self._func(**kwargs)
            except EndpointException as e:
                return e.make_response()
            finally:
                db.close()

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
        """path of this endpoint collection"""

        return f"/{self._name}"

    def endpoint(self, name: Union[Optional[str], Function] = None):
        """
        Register a new endpoint in this collection

        :param name: name of the endpoint
        """

        def deco(func):
            """
            Decorator for endpoint registration

            :param func: endpoint function
            :return: the same endpoint function
            """

            # use the function name if no other name is provided
            _name = name if name and isinstance(name, str) else func.__name__

            if not re.match(r"^[a-zA-Z0-9\-_]+$", _name):
                raise ValueError("invalid endpoint name")

            if _name in self._endpoints:
                raise ValueError("endpoint already exists")

            self._endpoints[_name] = Endpoint(self, _name, func)
            return func

        return deco(name) if isinstance(name, FunctionType) else deco

    def register(self, app: FastAPI) -> dict:
        """
        Register this endpoint collection in the FastAPI app

        :param app: the FastAPI app
        :return: the endpoint collection description for the /daemon/endpoints endpoint
        """

        return {
            "id": self._name,
            "description": self._description,
            "disabled": False,
            "endpoints": [endpoint.register(app) for endpoint in self._endpoints.values()],
        }
