from contextlib import asynccontextmanager
from functools import wraps

from database.database import get_database


@asynccontextmanager
async def db_context():
    """Async context manager for database sessions."""

    db.create_session()
    try:
        yield
    finally:
        await db.commit()
        await db.close()


def db_wrapper(f):
    """Decorator which wraps an async function in a database context."""

    @wraps(f)
    async def inner(*args, **kwargs):
        async with db_context():
            return await f(*args, **kwargs)

    return inner


# global database connection object
db = get_database()
