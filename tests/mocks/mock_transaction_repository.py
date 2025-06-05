from typing import List, Union
from src.core.interfaces.transaction_repository_interface import ITransactionRepository
from src.core.models.transaction_model import TransactionModel
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema


class MockTransactionRepository(ITransactionRepository):
    """Mock implementation of transaction repository for testing"""
    
    def __init__(self):
        self.transactions = []
        self.next_id = 1
        
    def create(self, data: Union[CreateTransactionSchema, List[CreateTransactionSchema]]) -> List[TransactionModel]:
        """Mock create transaction"""
        transactions = []
        data_list = data if isinstance(data, list) else [data]
        
        for item in data_list:
            transaction = TransactionModel(
                id=self.next_id,
                user_id=item.user_id,
                date=item.date,
                amount=item.amount,
                description=item.description,
                category=item.category,
                type=item.type
            )
            self.transactions.append(transaction)
            transactions.append(transaction)
            self.next_id += 1
            
        return transactions
    
    def get_all(self) -> List[TransactionModel]:
        """Mock get all transactions"""
        return self.transactions.copy()
    
    def update(self, data: UpdateTransactionSchema) -> TransactionModel:
        """Mock update transaction"""
        for transaction in self.transactions:
            if transaction.id == data.id:
                transaction.user_id = data.user_id
                transaction.date = data.date
                transaction.amount = data.amount
                transaction.description = data.description
                transaction.category = data.category
                transaction.type = data.type
                return transaction
        raise Exception("Transaction not found")
    
    def delete(self, id: int, user_id: str) -> TransactionModel:
        """Mock delete transaction"""
        for i, transaction in enumerate(self.transactions):
            if transaction.id == id and transaction.user_id == user_id:
                return self.transactions.pop(i)
        raise Exception("Transaction not found")
    
    def findRaw(self, query: str) -> List:
        """Mock raw query - returns all transactions for simplicity"""
        return [(t.id, t.user_id, t.date, t.amount, t.description, t.category, t.type) 
                for t in self.transactions]
    
    def clear(self):
        """Helper method to clear all transactions for test isolation"""
        self.transactions.clear()
        self.next_id = 1