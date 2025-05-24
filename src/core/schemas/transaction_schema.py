from src.core.models.transaction_model import TransactionType


class CreateTransactionSchema:
	user_id: str
	date: str
	amount: float
	description: str
	category: str
	type: TransactionType

	def __init__(self, user_id, date, amount, description, category, type):
		self.user_id = user_id
		self.date = date
		self.amount = amount
		self.description = description
		self.category = category
		self.type = type

	def to_dict(self):
		return {"user_id": self.user_id, "date": self.date, "amount": self.amount, "description": self.description, "category": self.category, "type": self.type}


class UpdateTransactionSchema:
	id: int
	user_id: str
	date: str
	amount: float
	description: str
	category: str
	type: TransactionType

	def __init__(self, id, user_id, date, amount, description, category, type):
		self.id = id
		self.user_id = user_id
		self.date = date
		self.amount = amount
		self.description = description
		self.category = category
		self.type = type
