# ORM-модель банковской операции из общей таблицы transaction.
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from src.main.api.db.base import Base


class Transfer(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    # Ссылки на счета заполняются в зависимости от типа банковской операции.
    to_account_id = Column(Integer, ForeignKey('account.id'))
    from_account_id = Column(Integer, ForeignKey('account.id'))
    # Указываем связанный кредит для операций, которые его сохраняют.
    credit_id = Column(Integer, ForeignKey('credit.id'))
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)