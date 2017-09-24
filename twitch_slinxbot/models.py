from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    last_request = Column(DateTime, default=datetime.utcnow)
    cash = Column(Integer, default=0)


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text, nullable=False)
