# ORM-модель банковского счёта из таблицы account.
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from src.main.api.db.base import Base


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Связываем банковский счёт с его владельцем.
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    number = Column(String, unique=True, nullable=False)
    # Храним текущий остаток денег на банковском счёте.
    balance = Column(Float, nullable=False)

# Возвращаем текстовое представление данных объекта для диагностики.
def __repr__(self):
    return f'<Account(id={self.id}, user_id={self.user_id}, balance={self.balance})>'