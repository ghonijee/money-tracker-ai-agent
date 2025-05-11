

from src.database.base import Base

class TransactionType:
    expense = 'expense'
    income = 'income'


class TransactionModel(Base):
    __tablename__ = 'transaction'

    id = Base.Column(Base.Integer, primary_key=True, autoincrement=True)
    user_id = Base.Column(Base.String(255), nullable=False)
    date = Base.Column(Base.DateTime, nullable=False)
    amount = Base.Column(Base.Float, nullable=False)
    description = Base.Column(Base.String(255), nullable=True)
    category = Base.Column(Base.String(100), nullable=True)  # category
    type = Base.Column(Base.Enum('expense', 'income', name='type'), nullable=True)  # type

