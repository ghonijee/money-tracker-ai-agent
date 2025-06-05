from src.core.interfaces.tool import Tool
from src.core.interfaces.transaction_repository_interface import ITransactionRepository
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema
from src.repositories.transaction_repository import get_transaction_repository
from src.services.llm_service import get_llm_service
from typing import Optional

class CreateTransactionTool(Tool):
    def __init__(self, repository: Optional[ITransactionRepository] = None) -> None:
        self.repository = repository or get_transaction_repository()

    def name(self) -> str:
        return "create_transaction"

    def description(self) -> str:
        return "Create a new transaction data"

    def validate_args(self, args):
        required_keys = ["user_id", "date", "amount", "description", "category", "type"]
        for key in required_keys:
            if key not in args:
                raise ValueError(f"Missing required argument: {key}")
            if key == "user_id" and not isinstance(args[key], str):
                raise ValueError("User ID must be a string")
            if key == "date" and not isinstance(args[key], str):
                raise ValueError("Date must be a string")
            if key == "amount" and not isinstance(args[key], (int, float)):
                raise ValueError("Amount must be a number")
            if key == "type" and args[key] not in ["expense", "income"]:
                raise ValueError("Type must be either 'expense' or 'income'")
            if key == "category" and not isinstance(args[key], str):
                raise ValueError("Category must be a string")
            if key == "description" and not isinstance(args[key], str):
                raise ValueError("Description must be a string")

    def run(self, args: list):
        createData = []
        # check if args is list
        if not isinstance(args, list):
            return "Args should be a list"

        if len(args) == 0:
            return "Args list cannot be empty"

        for arg in args:
            # Validate each argument in the list
            if not isinstance(arg, dict):
                return "Each argument in the list should be a dictionary"
            self.validate_args(arg)
            # Create a transaction schema for each argument
            createData.append(CreateTransactionSchema(user_id=arg["user_id"], date=arg["date"], amount=arg["amount"], description=arg["description"], category=arg["category"], type=arg["type"]))

        self.repository.create(createData)
        return {
            "message": f"{len(createData)} record(s) successfully created",
            "transactions": [item.to_dict() for item in createData],
        }

    def get_args_schema(self):
        return """
        Args should be a list of dictionaries with the following keys
        [
            {
                "user_id":"User ID",
                "date":"Date of the transaction",
                "amount":"Amount of the transaction",
                "description":"Description of the transaction",
                "category":"Category of the transaction",
                "type":"Type of the transaction (expense, income)"
            }
        ]
        """

    def output_schema(self):
        return "str"


class FindTransactionRawSQLTool(Tool):
    def __init__(self, repository: Optional[ITransactionRepository] = None) -> None:
        self.repository = repository or get_transaction_repository()

    def name(self) -> str:
        return "find_transaction_using_raw_sql"

    def description(self) -> str:
        return "Find transaction using raw SQL queryExample: SELECT * FROM transaction WHERE user_id = '123' AND date = '2023-01-01'"

    def run(self, args):
        query = args["query"]
        transactions = self.repository.findRaw(query)
        return f"Transactions found: {transactions}"

    def get_args_schema(self):
        return [{"name": "query", "type": "string", "description": "Raw SQL query"}]

    def output_schema(self):
        return "str"


class FindTransactionTool(Tool):
    def __init__(self, repository: Optional[ITransactionRepository] = None) -> None:
        self.repository = repository or get_transaction_repository()

    def name(self) -> str:
        return "find_transaction"

    def description(self) -> str:
        return "Find or Get data from the database by natural-language query from user input and user_id."

    def run(self, args):
        if "query" not in args or "user_id" not in args:
            return "Args should contain 'query' and 'user_id' keys"
        if not isinstance(args["query"], str) or not isinstance(args["user_id"], str):
            return "Args 'query' and 'user_id' should be strings"
        query = f"Natural Query: {args['query']} User ID: {args['user_id']}"

        system_prompt = """
            You are a precise transaction finder. 
            You must return only string the RAW SQL query to solve the natural-language query from user input.
            
            You have knowledge about DDL the database: 

            TABLE `transaction` (
                `id` int NOT NULL AUTO_INCREMENT,
                `user_id` varchar(255) NOT NULL,
                `date` datetime NOT NULL,
                `amount` float NOT NULL,
                `description` varchar(255) DEFAULT NULL,
                `category` varchar(100) DEFAULT NULL,
                `type` enum('expense','income') DEFAULT NULL,
                PRIMARY KEY (`id`)
            )
            Rules:
            1. Generate a PostgreSQL compatible SQL query to find transactions based on the user's natural language query.
            2. Always include a filter for user_id in the query to ensure data is scoped to the specific user.
            3. Return only string the RAW SQL query without any other text or formatting or wrapping.
            """

        # 2) Call the LLM
        llm_service = get_llm_service()
        resp = llm_service.query_execute(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="meta-llama/llama-4-scout:free"
        )
        if not resp:
            return "No response from LLM, please try again"

        raw_query = self.validate_query_raw_sql(resp)
        try:
            print(f"Raw SQL Query: {raw_query}")
            transactions = self.repository.findRaw(raw_query)
            return f"{transactions}"
        except Exception as e:
            return f"Error executing query: {e}"

    def get_args_schema(self):
        return [{"name": "query", "type": "string", "description": "Natural-language query"}, {"name": "user_id", "type": "str", "description": "User ID"}]

    def output_schema(self):
        return "str"

    def validate_query_raw_sql(self, query: str) -> str:
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]
        elif query.startswith("'") and query.endswith("'"):
            query = query[1:-1]
        # This method can be used to validate the raw SQL query if needed
        if not query.strip().lower().startswith("select"):
            return "Query must start with SELECT"
        if "user_id" not in query:
            return "Query must contain user_id filter"


        return query


class UpdateTransactionTool(Tool):
    def __init__(self, repository: Optional[ITransactionRepository] = None) -> None:
        self.repository = repository or get_transaction_repository()

    def name(self) -> str:
        return "update_transaction"

    def description(self) -> str:
        return "Update a transaction data by given ID and new values"

    def validate_args(self, args):
        required_keys = ["id", "user_id", "date", "amount", "description", "category", "type"]
        for key in required_keys:
            if key not in args:
                raise ValueError(f"Missing required argument: {key}")
            if key == "id" and not isinstance(args[key], int):
                raise ValueError("ID must be an integer")
            if key == "amount" and not isinstance(args[key], (int, float)):
                raise ValueError("Amount must be a number")
            if key == "type" and args[key] not in ["expense", "income"]:
                raise ValueError("Type must be either 'expense' or 'income'")

    def run(self, args):
        # Validate the arguments
        self.validate_args(args)

        id = args["id"]
        updateData = UpdateTransactionSchema(id=id, user_id=args["user_id"], date=args["date"], amount=args["amount"], description=args["description"], category=args["category"], type=args["type"])
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
            {"name": "type", "type": "enum(expense, income)", "description": "Type of the transaction"},
        ]

    def output_schema(self):
        return "str"


class DeleteTransactionTool(Tool):
    def __init__(self, repository: Optional[ITransactionRepository] = None) -> None:
        self.repository = repository or get_transaction_repository()

    def name(self) -> str:
        return "delete_transaction"

    def description(self) -> str:
        return "Delete a transaction data by given ID and user_id"

    def run(self, args):
        id = args["id"]
        user_id = args["user_id"]
        if not isinstance(id, int) or not isinstance(user_id, str):
            return "ID must be an integer and user_id must be a string"
        transaction = self.repository.delete(id, user_id)
        return f"{transaction.type} record successfully deleted with ID {transaction.id} for {transaction.amount} amount and {transaction.category} category"

    def get_args_schema(self):
        return [{"name": "id", "type": "int", "description": "ID of the transaction to delete"}, {"name": "user_id", "type": "str", "description": "User ID"}]

    def output_schema(self):
        return "str"
