from typing import Optional

from endpoint_collection import EndpointCollection


device_collection = EndpointCollection("device", "some device endpoints")


@device_collection.endpoint("info")
def device_info(user_id: str, foo: str, bar: int, test: Optional[str]):
    """
    Test endpoint

    :param user_id: id of the user
    :param foo: xy
    :param bar: hello world
    :param test: asdofjaoisdfjoi
    :return: test
    """

    return {"user_id": user_id, "foo": foo, "bar": bar + 2, "test": test}
