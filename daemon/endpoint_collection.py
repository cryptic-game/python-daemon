import re
from collections import namedtuple
from types import FunctionType
from typing import Optional

from fastapi import FastAPI, Depends, APIRouter, Body
from pydantic import UUID4

from .authorization import HTTPAuthorization
from .environment import DEBUG

Endpoint = namedtuple("Endpoint", ["name", "description"])


def format_docs(func):
    doc = "\n".join(line.strip() for line in func.__doc__.splitlines()).replace(
        "\n\n:param",
        "\n\n**Parameters:**\n:param",
    )
    doc = re.sub(r":param ([a-zA-Z\d_]+):", r"- **\1:**", doc)
    doc = re.sub(r":returns?:", r"\n**Returns:**", doc)
    func.__doc__ = doc
    return func


def default_parameter(default):
    def deco(func):
        prev = func.__defaults__ or ()
        func.__defaults__ = (default,) * (func.__code__.co_argcount - len(prev)) + prev
        return func

    return deco


def dependency(f):
    return Depends(default_parameter(Body(...))(f))


@dependency
async def get_user(user_id: UUID4) -> str:
    return str(user_id)


class EndpointCollection(APIRouter):
    """Collection of daemon endpoints"""

    def __init__(self, name: str, description: str, *, disabled: bool = False, test: bool = False):
        tag = name
        if test:
            tag = f"[TEST] {tag}"

        super().__init__(prefix=f"/{name}", tags=[tag], dependencies=[Depends(HTTPAuthorization())])

        self._name: str = name
        self._description: str = description
        self._test: bool = test
        self._disabled: bool = disabled or test and not DEBUG
        self._endpoints: list[Endpoint] = []

    def endpoint(self, name: Optional[str] = None, *args, disabled: bool = False, test: bool = False, **kwargs):
        """
        Register a new endpoint in this collection.

        :param name: name of the endpoint
        :param disabled: whether this endpoint is disabled or not
        :param test: whether this endpoint is only for testing
        """

        test = test or self._test

        def deco(func):
            """Decorator for endpoint registration"""

            if disabled or test and not DEBUG:
                return func

            # use the function name if no other name is provided
            _name = name if isinstance(name, str) else func.__name__

            doc = "\n".join(line.strip() for line in func.__doc__.splitlines())
            self._endpoints.append(Endpoint(_name, doc))

            func = format_docs(func)
            func = default_parameter(Body(...))(func)
            return self.post(f"/{_name}", name="[TEST] " * test + func.__name__, *args, **kwargs)(func)

        return deco(name) if isinstance(name, FunctionType) else deco

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def register(self, app: FastAPI) -> Optional[dict]:
        """
        Register this endpoint collection in the FastAPI app

        :param app: the FastAPI app
        :return: the endpoint collection description for the `/daemon/endpoints` endpoint
        """

        if self._disabled:
            return None

        app.include_router(self)

        return {
            "id": self.name,
            "description": self.description,
            "disabled": False,
            "endpoints": [
                {
                    "id": endpoint.name,
                    "description": endpoint.description.strip().rpartition("\n\n")[0],
                    "disabled": False,
                }
                for endpoint in self._endpoints
            ],
        }
