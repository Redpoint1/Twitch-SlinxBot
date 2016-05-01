from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    text = Column(Text)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nick = Column(String)
    cash = Column(Integer)
