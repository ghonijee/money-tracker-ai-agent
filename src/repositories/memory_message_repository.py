from sqlalchemy import desc
from src.core.models.memory_message_model import MemoryMessageModel
from src.core.schemas.memory_message_schema import CreateMemoryMessageSchema
from src.database.connection import SessionLocal


def get_memory_message_repository():
	return MemoryMessageRepository(SessionLocal())


class MemoryMessageRepository:
	def __init__(self, session):
		self.session = session

	def create(self, data: CreateMemoryMessageSchema) -> MemoryMessageModel:
		if not isinstance(data, CreateMemoryMessageSchema):
			raise TypeError("data should be an instance of CreateMemoryMessageSchema")
		
		memory_message = MemoryMessageModel(
			user_id=data.user_id,
			role=data.role,
			message=data.message
		)
		
		self.session.add(memory_message)
		self.session.commit()
		self.session.refresh(memory_message)
		return memory_message

	def get_list(self, user_id: str, limit: int = 50) -> list[MemoryMessageModel]:
		return (
			self.session.query(MemoryMessageModel)
			.filter_by(user_id=user_id)
			.order_by(desc(MemoryMessageModel.created_at))
			.limit(limit)
			.all()
		)