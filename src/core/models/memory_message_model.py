from sqlalchemy import Column, DateTime, Integer, String, Text, func

from src.database.base import Base


class MemoryMessageModel(Base):
	__tablename__ = "memory_message"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(String(255), nullable=False)
	role = Column(String(50), nullable=False)
	message = Column(Text, nullable=False)
	created_at = Column(DateTime, nullable=False, server_default=func.now())
	updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())