# Чтение кредитных записей по ID кредита или банковского счёта.
from sqlalchemy.orm import Session

from src.main.api.db.models.credit_table import CreditTable


class CreditCrudDb:
    # Ищем кредит по его собственному ID в таблице credit.
    @staticmethod
    def get_credit_by_id(db: Session, credit_id: int) -> CreditTable | None:
       return db.query(CreditTable).filter_by(id=credit_id).first()

    # Получаем список всех кредитов указанного банковского счёта.
    @staticmethod
    def get_credits_by_account_id(db: Session, account_id: int) -> list[CreditTable]:
        return db.query(CreditTable).filter_by(account_id=account_id).all()

