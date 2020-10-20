from typing import Union

from sqlalchemy import Column, String, Integer

from database import db


class Counter(db.Base):
    __tablename__ = "counter"

    user_id: Union[Column, str] = Column(String, primary_key=True, unique=True)
    value: Union[Column, int] = Column(Integer)
