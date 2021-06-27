from typing import Type, Union

from pydantic import BaseModel
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from exceptions.api_exception import APIException


def responses(default: Type[Union[BaseModel, list]], *args: Type[APIException]) -> dict:
    exceptions: dict[int, list[Type[APIException]]] = {}
    for exc in args:
        exceptions.setdefault(exc.status_code, []).append(exc)

    out: dict[int, dict] = {}
    for code, excs in exceptions.items():
        examples = {}
        for i, exc in enumerate(excs):
            name = exc.__name__ if len(excs) == 1 else f"{exc.__name__} ({i + 1}/{len(excs)})"
            examples[name] = {"description": exc.description, "value": exc().make_dict()}

        out[code] = {
            "description": STATUS_PHRASES[code],
            "content": {"application/json": {"examples": examples}},
        }

    return out | {200: {"model": default}}


def get_example(arg: type) -> dict:
    return getattr(arg, "Config").schema_extra["example"]


def example(*args, **kwargs) -> type:
    ex = dict(e for arg in args for e in get_example(arg).items())
    return type("Config", (), {"schema_extra": {"example": ex | kwargs}})
