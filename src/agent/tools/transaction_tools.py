from src.core.interfaces.tool import Tool
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema
from src.repositories.transaction_repository import get_transaction_repository
from src.services.llm_service import get_llm_service


class CreateTransactionTool(Tool):
	def __init__(self) -> None:
		self.repository = get_transaction_repository()

	def name(self) -> str:
		return "create_transaction"

	def description(self) -> str:
		return "Create a new transaction data"

	def run(self, args: list):
		createData = []
		# check if args is list
		if not isinstance(args, list):
			return "Args should be a list"

		if len(args) == 0:
			return "Args list cannot be empty"

		for arg in args:
			createData.append(CreateTransactionSchema(user_id=arg["user_id"], date=arg["date"], amount=arg["amount"], description=arg["description"], category=arg["category"], type=arg["type"]))

		transactions = self.repository.create(createData)
		return {
			"message": f"{len(transactions)} record(s) successfully created",
			"transactions": createData,
		}

	def get_args_schema(self):
		return """
		Args: Accepts list of objects to create one or multiple transactions.
		List of objects example:
		[
			{
				"user_id": "string",
				"date": "YYYY-MM-DD",
				"amount": 1000,
				"description": "Description of the transaction",
				"category": "Category of the transaction",
				"type": "expense"
			},
			{
				"user_id": "string",
				"date": "YYYY-MM-DD",
				"amount": 500,
				"description": "Another transaction",
				"category": "Another category",
				"type": "income"
			}
		]

		Each object must include:
		- user_id (str): User ID
		- date (date): Date of the transaction
		- amount (int): Amount of the transaction
		- description (str): Description of the transaction
		- category (str): Category of the transaction
		- type (enum: expense, income): Type of the transaction
		"""

	def output_schema(self):
		return "str"


class FindTransactionRawSQLTool(Tool):
	def __init__(self) -> None:
		self.repository = get_transaction_repository()

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
	def __init__(self) -> None:
		self.repository = get_transaction_repository()

	def name(self) -> str:
		return "find_transaction"

	def description(self) -> str:
		return "Find or Get data from the database by natural-language query from user input"

	def run(self, args):
		query = args["query"]

		system_prompt = (
			"You are a precise transaction finder. You must return only string the RAW SQL query."
			"Given RAW SQL query to solve the natural-language query from user input"
			"""
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
            """
			"""
            Example: 
            "SELECT * FROM transaction WHERE user_id = '123' AND date = '2023-01-01'"
            "Select * from transaction where user_id = '123' order by amount desc limit 1"
            "select * from transaction where user_id = '123' and description like '%food%' order by date desc"
            """
			"Return only string the RAW SQL query without any other text or formatting"
		)

		# 2) Call the LLM
		llm_service = get_llm_service()
		resp = llm_service.query_execute(
			messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
		)
		transactions = self.repository.findRaw(resp)
		return f"{transactions}"

	def get_args_schema(self):
		return [{"name": "query", "type": "string", "description": "Natural-language query"}]

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
		return [{"name": "id", "type": "int", "description": "ID of the transaction to delete"}]

	def output_schema(self):
		return "str"
