from sqlalchemy import Column, DateTime, Integer, String, Enum

from src.database.base import Base


class TransactionType:
	expense = "expense"
	income = "income"


class TransactionModel(Base):
	__tablename__ = "transaction"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(String(255), nullable=False)
	date = Column(DateTime, nullable=False)
	amount = Column(Integer, nullable=False)
	description = Column(String(255), nullable=True)
	category = Column(String(100), nullable=True)  # category
	type = Column(Enum("expense", "income", name="type"), nullable=True)  # type
