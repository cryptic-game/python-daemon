from pydantic import BaseModel

from utils import example, get_example


class EndpointModel(BaseModel):
    id: str
    description: str
    disabled: bool = False

    Config = example(id="<endpoint id>", description="<endpoint description>", disabled=False)


class EndpointCollectionModel(BaseModel):
    id: str
    description: str
    disabled: bool = False
    endpoints: list[EndpointModel]

    Config = example(
        id="<endpoint collection id>",
        description="<endpoint collection description>",
        disabled=False,
        endpoints=[get_example(EndpointModel)],
    )
