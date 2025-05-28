from sqlalchemy.orm import Session
from src.core.models.message_log_model import MessageLogModel
from src.core.schemas.message_log_schema import CreateMessageLogSchema
from src.database.connection import SessionLocal

def get_message_log_repository():
    return MessageLogRepository(SessionLocal())

class MessageLogRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, message_log_data: CreateMessageLogSchema) -> MessageLogModel:
        message_log = MessageLogModel(
            datetime=message_log_data.datetime,
            message=message_log_data.message,
            model=message_log_data.model,
            status=message_log_data.status
        )
        self.db_session.add(message_log)
        self.db_session.commit()
        self.db_session.refresh(message_log)
        return message_log