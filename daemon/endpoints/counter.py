from typing import Optional

from fastapi import status

from database import db
from endpoint_collection import EndpointCollection
from exceptions import EndpointException
from models.counter import Counter

counter_collection = EndpointCollection("counter", "test endpoints")


@counter_collection.endpoint
async def exception():
    """
    Raises an exception

    :return: nothing
    """

    return 1 / 0


@counter_collection.endpoint
async def get(user_id: str) -> int:
    """
    Fetch the current counter value

    :param user_id: id of the user
    :return: the current counter value
    """

    counter: Optional[Counter] = await db.get(Counter, user_id=user_id)
    if counter is None:
        raise EndpointException(status.HTTP_404_NOT_FOUND, "counter_not_found")

    return counter.value


@counter_collection.endpoint()
async def increment(user_id: str) -> dict:
    """
    Increment the counter value

    :param user_id:  id of the user
    :return: the old and the new counter value
    """

    if counter := await db.get(Counter, user_id=user_id):
        old = counter.value
        counter.value += 1
    else:
        old = None
        counter = await db.add(Counter(user_id=user_id, value=1))

    return {"old": old, "new": counter.value}


@counter_collection.endpoint("reset")
async def magic(user_id: str):
    """
    Reset the counter using magic

    :param user_id: id of the user
    :return: True
    """

    counter: Optional[Counter] = await db.get(Counter, user_id=user_id)
    if counter is None:
        raise EndpointException(status.HTTP_404_NOT_FOUND, "counter_not_found")

    await db.delete(counter)

    return True


@counter_collection.endpoint("set")
async def set_value(user_id: str, password: str, value: int):
    """
    Set the counter to a specific value

    :param user_id: id of the user
    :param password: secret password
    :param value: new counter value
    :return: True
    """

    if password != "S3cr3t":
        raise EndpointException(status.HTTP_401_UNAUTHORIZED, "wrong_password")

    if counter := await db.get(Counter, user_id=user_id):
        old = counter.value
        counter.value = value
    else:
        old = None
        counter = await db.add(Counter(user_id=user_id, value=value))

    return {"old": old, "new": counter.value}
