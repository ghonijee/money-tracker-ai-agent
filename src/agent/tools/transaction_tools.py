



from src.core.interfaces.tool import Tool
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema
from src.repositories.transaction_repository import get_transaction_repository

class CreateTransactionTool(Tool):
    def __init__(self) -> None:
        self.repository = get_transaction_repository()

    def name(self) -> str:
        return "create_transaction"
    
    def description(self) -> str:
        return "Create a new transaction data"
    
    def run(self, args):
        createData = CreateTransactionSchema(
            user_id=args["user_id"],
            date=args["date"],
            amount=args["amount"],
            description=args["description"],
            category=args["category"],
            type=args["type"]
        )
        transaction = self.repository.create(createData)
        # return string with category, amount, and ref transaction ID
        return f"{transaction.type} record successfully created with ID {transaction.id} for {transaction.amount} amount and {transaction.category} category"
    def get_args_schema(self):
        return [
            {"name": "user_id", "type": "str", "description": "User ID"},
            {"name": "date", "type": "date", "description": "Date of the transaction"},
            {"name": "amount", "type": "int", "description": "Amount of the transaction"},
            {"name": "description", "type": "str", "description": "Description of the transaction"},
            {"name": "category", "type": "str", "description": "Category of the transaction"},
            {"name": "type", "type": "enum(expense, income)", "description": "Type of the transaction"}
        ]
    
    def output_schema(self):
        return "str"
    
class FindTransactionRawSQLTool(Tool):
    def __init__(self) -> None:
        self.repository = get_transaction_repository()

    def name(self) -> str:
        return "find_transaction_using_raw_sql"
    
    def description(self) -> str:
        return (
            "Find transaction using raw SQL query"
            "Example: SELECT * FROM transaction WHERE user_id = '123' AND date = '2023-01-01'"
        )
    
    def run(self, args):
        query = args["query"]
        transactions = self.repository.findRaw(query)
        return f"Transactions found: {transactions}"
       
    def get_args_schema(self):
        return [
            {"name": "query", "type": "string", "description": "Raw SQL query"}
        ]
    
    def output_schema(self):
        return "str"
    
class UpdateTransactionTool(Tool):
    def __init__(self) -> None:
        self.repository = get_transaction_repository()

    def name(self) -> str:
        return "update_transaction"
    
    def description(self) -> str:
        return "Update a transaction data by given ID and new values"
    
    def run(self, args):
        id = args["id"]
        updateData = UpdateTransactionSchema(
            id=id,
            user_id=args["user_id"],
            date=args["date"],
            amount=args["amount"],
            description=args["description"],
            category=args["category"],
            type=args["type"]
        )
        transaction = self.repository.update(updateData)
        return f"{transaction.type} record successfully updated with ID {transaction.id} for {transaction.amount} amount and {transaction.category} category"

    def get_args_schema(self):
        return [
            {"name": "id", "type": "int", "description": "ID of the transaction to update"},
            {"name": "user_id", "type": "str", "description": "User ID"},
            {"name": "date", "type": "date", "description": "Date of the transaction"},
            {"name": "amount", "type": "int", "description": "Amount of the transaction"},
            {"name": "description", "type": "str", "description": "Description of the transaction"},
            {"name": "category", "type": "str", "description": "Category of the transaction"},
            {"name": "type", "type": "enum(expense, income)", "description": "Type of the transaction"}
        ]
    
    def output_schema(self):
        return "str"
    
class DeleteTransactionTool(Tool):
    def __init__(self) -> None:
        self.repository = get_transaction_repository()

    def name(self) -> str:
        return "delete_transaction"
    
    def description(self) -> str:
        return "Delete a transaction data by given ID"
    
    def run(self, args):
        id = args["id"]
        transaction = self.repository.delete(id)
        return f"{transaction.type} record successfully deleted with ID {transaction.id} for {transaction.amount} amount and {transaction.category} category"
    def get_args_schema(self):
        return [
            {"name": "id", "type": "int", "description": "ID of the transaction to delete"}
        ]
    
    def output_schema(self):
        return "str"