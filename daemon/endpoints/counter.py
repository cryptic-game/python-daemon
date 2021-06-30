from typing import Optional

from database import db
from endpoint_collection import EndpointCollection, get_user
from exceptions.counter import CounterNotFoundException, WrongPasswordException
from models.counter import Counter
from schemas.counter import ValueResponse, ValueChangedResponse
from schemas.ok import OKResponse
from utils import responses

counter_collection = EndpointCollection("counter", "test endpoints", test=True)


@counter_collection.endpoint
async def exception():
    """
    Raises an exception

    :return: nothing
    """

    return 1 / 0


@counter_collection.endpoint(responses=responses(ValueResponse, CounterNotFoundException))
async def get(user_id: str = get_user) -> int:
    """
    Fetch the current counter value

    :param user_id: id of the user
    :return: the current counter value
    """

    counter: Optional[Counter] = await db.get(Counter, user_id=user_id)
    if counter is None:
        raise CounterNotFoundException

    return counter.value


@counter_collection.endpoint(responses=responses(ValueChangedResponse))
async def increment(user_id: str = get_user) -> dict:
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


@counter_collection.endpoint("reset", responses=responses(OKResponse, CounterNotFoundException))
async def magic(user_id: str = get_user):
    """
    Reset the counter using magic

    :param user_id: id of the user
    :return: True
    """

    counter: Optional[Counter] = await db.get(Counter, user_id=user_id)
    if counter is None:
        raise CounterNotFoundException

    await db.delete(counter)

    return True


@counter_collection.endpoint("set", responses=responses(ValueChangedResponse, WrongPasswordException))
async def set_value(password: str, value: int, user_id: str = get_user):
    """
    Set the counter to a specific value

    :param user_id: id of the user
    :param password: secret password
    :param value: new counter value
    :return: True
    """

    if password != "S3cr3t":  # noqa: S105
        raise WrongPasswordException

    if counter := await db.get(Counter, user_id=user_id):
        old = counter.value
        counter.value = value
    else:
        old = None
        counter = await db.add(Counter(user_id=user_id, value=value))

    return {"old": old, "new": counter.value}
