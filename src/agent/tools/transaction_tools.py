



from src.core.interfaces.tool import Tool


class CreateTransactionTool(Tool):
    def name(self) -> str:
        return "create_transaction"
    
    def description(self) -> str:
        return "Create a new transaction data"
    
    def run(self, args):
        return "Transaction created successfully with data: " + str(args)
    
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