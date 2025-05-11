from src.core.models.transaction_model import TransactionType

class CreateTransactionSchema:
    user_id: str
    date: str
    amount: float
    description: str
    category: str
    type: TransactionType