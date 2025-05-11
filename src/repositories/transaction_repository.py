

from src.core.models.transaction_model import TransactionModel
from src.core.schemas.transaction_schema import CreateTransactionSchema
from src.database.connection import SessionLocal

def get_transaction_repository():
    return TransactionRepository(SessionLocal)


class TransactionRepository:
    def __init__(self, session):
        self.session = session
    
    def create(self, data: CreateTransactionSchema):
        transaction = TransactionModel(
            user_id=data.user_id,
            date=data.date,
            amount=data.amount,
            description=data.description,
            category=data.category,
            type=data.type
        )
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)

    def get_all(self):
        return self.session.query(TransactionModel).all()