# Операции с банковскими счетами напрямую через сессию БД.
from sqlalchemy.orm import Session

from src.main.api.db.models.account_table import Account


class AccountCrudDb:
    # Ищем банковский счёт по его ID; при отсутствии получаем None.
    @staticmethod
    def get_account_by_id(db: Session, account_id: int) -> Account | None:
        return db.query(Account).filter_by(id=account_id).first()

    # Удаляем найденный счёт и фиксируем изменение в БД.
    @staticmethod
    def delete_account(db: Session, account_id: int) -> None:
        account = db.query(Account).filter_by(id=account_id).first()
        if account:
            db.delete(account)
            db.commit()
