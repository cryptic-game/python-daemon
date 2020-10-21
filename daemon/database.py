from typing import TypeVar

from sqlalchemy import create_engine

# noinspection PyProtectedMember
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session, Query

from config import (
    SQL_SERVER_LOCATION,
    SQL_SERVER_DATABASE,
    SQL_SERVER_USERNAME,
    SQL_SERVER_PASSWORD,
    SQL_SHOW_STATEMENTS,
)

T = TypeVar("T")


class DB:
    def __init__(self, location: str, database: str, username: str, password: str, echo: bool):
        protocol, location = location.split("://")
        self.engine: Engine = create_engine(
            f"{protocol}://{username}:{password}@{location}/{database}",
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=echo,
        )

        self._SessionFactory: sessionmaker = sessionmaker(bind=self.engine)
        self._Session = scoped_session(self._SessionFactory)
        self.Base: DeclarativeMeta = declarative_base()

    def add(self, obj: T) -> T:
        self.session.add(obj)
        return obj

    def delete(self, obj: T) -> T:
        self.session.delete(obj)
        return obj

    def query(self, *entities, **kwargs) -> Query:
        return self.session.query(*entities, **kwargs)

    def commit(self):
        self.session.commit()

    def close(self):
        self._Session.remove()

    @property
    def session(self) -> Session:
        return self._Session()


db = DB(
    location=SQL_SERVER_LOCATION,
    database=SQL_SERVER_DATABASE,
    username=SQL_SERVER_USERNAME,
    password=SQL_SERVER_PASSWORD,
    echo=SQL_SHOW_STATEMENTS,
)
