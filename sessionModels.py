from sqlalchemy import DateTime, BigInteger, Column, JSON, Integer, Boolean, String, Sequence, Float, LargeBinary, Date, Table, \
    ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BlockedUser(Base):
    __tablename__ = 'blocked'
    id = Column(Integer, primary_key=True)
    client_number = Column(Integer, unique=True)
    time = Column(Float)


class SessionInfo(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True)
    client_number = Column(Integer)
    is_login = Column(Boolean, default=False)
    time = Column(Float)
    set = Column(Integer)
    attempts = Column(Integer)
    transfer_data = Column(JSON)
    error = Column(String)