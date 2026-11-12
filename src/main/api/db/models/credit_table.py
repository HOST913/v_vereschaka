# ORM-модель кредита и его задолженности из таблицы credit.
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from src.main.api.db.base import Base


class CreditTable(Base):
    __tablename__ = 'credit'
    id = Column(Integer, primary_key=True)
    # Связываем кредит с банковским счётом, на который он выдан.
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    amount = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    # Храним задолженность по кредиту; после полного погашения она равна нулю.
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)
