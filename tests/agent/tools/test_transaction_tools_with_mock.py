import pytest
from datetime import datetime
from src.agent.tools.transaction_tools import CreateTransactionTool, UpdateTransactionTool, DeleteTransactionTool
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema
from tests.mocks.mock_transaction_repository import MockTransactionRepository


class TestCreateTransactionToolWithMock:
    """Test CreateTransactionTool using mock repository for better isolation"""
    
    def setup_method(self):
        """Setup fresh mock repository for each test"""
        self.mock_repo = MockTransactionRepository()
        self.tool = CreateTransactionTool(repository=self.mock_repo)
    
    def test_create_single_transaction_success(self):
        """Test successful creation of single transaction"""
        transaction_data = [{
            "user_id": "test_user_123",
            "date": "2024-01-15",
            "amount": 50.75,
            "description": "Lunch at restaurant",
            "category": "Food",
            "type": "expense"
        }]
        
        result = self.tool.run(transaction_data)
        
        assert "1 record(s) successfully created" in result["message"]
        assert len(result["transactions"]) == 1
        assert len(self.mock_repo.get_all()) == 1
        
        created_transaction = self.mock_repo.get_all()[0]
        assert created_transaction.user_id == "test_user_123"
        assert created_transaction.amount == 50.75
        assert created_transaction.category == "Food"
    
    def test_create_multiple_transactions_success(self):
        """Test successful creation of multiple transactions"""
        transaction_data = [
            {
                "user_id": "test_user_123",
                "date": "2024-01-15",
                "amount": 50.75,
                "description": "Lunch",
                "category": "Food",
                "type": "expense"
            },
            {
                "user_id": "test_user_123", 
                "date": "2024-01-16",
                "amount": 1000.0,
                "description": "Salary",
                "category": "Work",
                "type": "income"
            }
        ]
        
        result = self.tool.run(transaction_data)
        
        assert "2 record(s) successfully created" in result["message"]
        assert len(result["transactions"]) == 2
        assert len(self.mock_repo.get_all()) == 2
    
    def test_create_transaction_validation_error(self):
        """Test validation error handling"""
        invalid_data = [{
            "user_id": "test_user_123",
            "date": "2024-01-15",
            "amount": "invalid_amount",  # Should be number
            "description": "Test",
            "category": "Test",
            "type": "expense"
        }]
        
        result = self.tool.run(invalid_data)
        
        assert "Amount must be a number" in result
        assert len(self.mock_repo.get_all()) == 0  # No transaction created
    
    def test_create_transaction_empty_args(self):
        """Test empty args handling"""
        result = self.tool.run([])
        
        assert "Args list cannot be empty" in result
        assert len(self.mock_repo.get_all()) == 0


class TestUpdateTransactionToolWithMock:
    """Test UpdateTransactionTool using mock repository"""
    
    def setup_method(self):
        """Setup fresh mock repository with test data"""
        self.mock_repo = MockTransactionRepository()
        self.tool = UpdateTransactionTool(repository=self.mock_repo)
        
        # Create initial transaction
        create_data = CreateTransactionSchema(
            user_id="test_user_123",
            date="2024-01-15",
            amount=50.0,
            description="Original transaction",
            category="Food",
            type="expense"
        )
        self.mock_repo.create(create_data)
    
    def test_update_transaction_success(self):
        """Test successful transaction update"""
        update_data = {
            "id": 1,
            "user_id": "test_user_123",
            "date": "2024-01-16",
            "amount": 75.0,
            "description": "Updated transaction",
            "category": "Entertainment",
            "type": "expense"
        }
        
        result = self.tool.run(update_data)
        
        assert "expense record successfully updated with ID 1" in result
        
        updated_transaction = self.mock_repo.get_all()[0]
        assert updated_transaction.amount == 75.0
        assert updated_transaction.description == "Updated transaction"
        assert updated_transaction.category == "Entertainment"
    
    def test_update_nonexistent_transaction(self):
        """Test updating non-existent transaction"""
        update_data = {
            "id": 999,  # Non-existent ID
            "user_id": "test_user_123",
            "date": "2024-01-16",
            "amount": 75.0,
            "description": "Updated transaction",
            "category": "Entertainment",
            "type": "expense"
        }
        
        with pytest.raises(Exception, match="Transaction not found"):
            self.tool.run(update_data)


class TestDeleteTransactionToolWithMock:
    """Test DeleteTransactionTool using mock repository"""
    
    def setup_method(self):
        """Setup fresh mock repository with test data"""
        self.mock_repo = MockTransactionRepository()
        self.tool = DeleteTransactionTool(repository=self.mock_repo)
        
        # Create initial transaction
        create_data = CreateTransactionSchema(
            user_id="test_user_123",
            date="2024-01-15",
            amount=50.0,
            description="Transaction to delete",
            category="Food", 
            type="expense"
        )
        self.mock_repo.create(create_data)
    
    def test_delete_transaction_success(self):
        """Test successful transaction deletion"""
        result = self.tool.run({"id": 1, "user_id": "test_user_123"})
        
        assert "expense record successfully deleted with ID 1" in result
        assert len(self.mock_repo.get_all()) == 0  # Transaction removed
    
    def test_delete_nonexistent_transaction(self):
        """Test deleting non-existent transaction"""
        with pytest.raises(Exception, match="Transaction not found"):
            self.tool.run({"id": 999, "user_id": "test_user_123"})
    
    def test_delete_transaction_wrong_user(self):
        """Test deleting transaction with wrong user_id"""
        with pytest.raises(Exception, match="Transaction not found"):
            self.tool.run({"id": 1, "user_id": "wrong_user"})


class TestRepositoryIsolation:
    """Test that mock repository provides proper test isolation"""
    
    def test_multiple_tests_are_isolated(self):
        """Test that each test gets fresh repository state"""
        mock_repo1 = MockTransactionRepository()
        mock_repo2 = MockTransactionRepository()
        
        # Add data to first repo
        create_data = CreateTransactionSchema(
            user_id="user1",
            date="2024-01-15", 
            amount=100.0,
            description="Test",
            category="Test",
            type="expense"
        )
        mock_repo1.create(create_data)
        
        # Second repo should be empty
        assert len(mock_repo1.get_all()) == 1
        assert len(mock_repo2.get_all()) == 0
        
        # Clear first repo
        mock_repo1.clear()
        assert len(mock_repo1.get_all()) == 0