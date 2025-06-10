from abc import ABC, abstractmethod
from typing import List, Union
from src.core.models.transaction_model import TransactionModel
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema


class ITransactionRepository(ABC):
    """Abstract interface for transaction repository operations"""
    
    @abstractmethod
    def create(self, data: Union[CreateTransactionSchema, List[CreateTransactionSchema]]) -> List[TransactionModel]:
        """Create one or more transactions"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[TransactionModel]:
        """Get all transactions"""
        pass
    
    @abstractmethod
    def update(self, data: UpdateTransactionSchema) -> TransactionModel:
        """Update a transaction"""
        pass
    
    @abstractmethod
    def delete(self, id: int, user_id: str) -> TransactionModel:
        """Delete a transaction"""
        pass
    
    @abstractmethod
    def findRaw(self, query: str) -> List:
        """Execute raw SQL query"""
        pass