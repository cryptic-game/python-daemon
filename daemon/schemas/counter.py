from pydantic import BaseModel

from ..utils import example


class ValueResponse(BaseModel):
    value: int

    Config = example(value=42)


class ValueChangedResponse(BaseModel):
    old: int
    new: int

    Config = example(old=42, new=43)
