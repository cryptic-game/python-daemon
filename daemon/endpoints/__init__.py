from fastapi import FastAPI

from .counter import counter_collection
from .device import device_collection

ENDPOINT_COLLECTIONS = [
    device_collection,
    counter_collection,
]


def register_collections(app: FastAPI) -> list[dict]:
    """
    Register endpoint collections and prepare response for /daemon/endpoints endpoint

    :param app: the fastapi app
    :return: a list of dicts containing information about all endpoints and endpoint collections
    """

    return [description for collection in ENDPOINT_COLLECTIONS if (description := collection.register(app))]
