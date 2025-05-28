from sqlalchemy import Column, Integer, DateTime, JSON, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MessageLogModel(Base):
    __tablename__ = 'message_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, nullable=False)
    message = Column(JSON, nullable=False)
    model = Column(String(length=255), nullable=False)
    status = Column(Boolean, nullable=True, default=True)