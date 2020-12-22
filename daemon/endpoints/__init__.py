from fastapi import FastAPI

from endpoints.counter import counter_collection
from endpoints.device import device_collection

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

    return [collection.register(app) for collection in ENDPOINT_COLLECTIONS]
