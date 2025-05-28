from sqlalchemy import insert, text
from src.core.models.transaction_model import TransactionModel
from src.core.schemas.transaction_schema import CreateTransactionSchema, UpdateTransactionSchema
from src.database.connection import SessionLocal


def get_transaction_repository():
	return TransactionRepository(SessionLocal())


class TransactionRepository:
	def __init__(self, session):
		self.session = session

	def create(self, data: CreateTransactionSchema | list[CreateTransactionSchema]) -> list[TransactionModel]:
		transactions = []
		if isinstance(data, list):
			for item in data:
				transactions.append(TransactionModel(user_id=item.user_id, date=item.date, amount=item.amount, description=item.description, category=item.category, type=item.type))
		else:
			# check if data is instance of CreateTransactionSchema
			if not isinstance(data, CreateTransactionSchema):
				raise TypeError("data should be an instance of CreateTransactionSchema")
			# check if data has all required keys
			transactions.append(TransactionModel(user_id=data.user_id, date=data.date, amount=data.amount, description=data.description, category=data.category, type=data.type))
		# self.session.add_all(transactions)
		# self.session.commit()
		# stmt = insert(TransactionModel).values(transactions)
		# self.session.execute(stmt)
		self.session.add_all(transactions)
		self.session.commit()
		return transactions

	def get_all(self):
		return self.session.query(TransactionModel).all()

	def update(self, data: UpdateTransactionSchema) -> TransactionModel:
		transaction = self.session.query(TransactionModel).filter_by(id=data.id).first()
		if transaction:
			transaction.user_id = data.user_id
			transaction.date = data.date
			transaction.amount = data.amount
			transaction.description = data.description
			transaction.category = data.category
			transaction.type = data.type
			self.session.commit()
			self.session.refresh(transaction)
			return transaction
		else:
			raise Exception("Transaction not found")

	def delete(self, id, user_id):
		transaction = self.session.query(TransactionModel).filter_by(id=id, user_id=user_id).first()
		if transaction:
			self.session.delete(transaction)
			self.session.commit()
			return transaction
		else:
			raise Exception("Transaction not found")

	def findRaw(self, query):
		try:
			stmt = text(query)
			return self.session.execute(stmt).all()
		except Exception as e:
			self.session.rollback()
			print(f"Error executing raw SQL query: {e}")
			raise e
