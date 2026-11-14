# Чтение сохранённых переводов из таблицы transaction.
from sqlalchemy.orm import Session

from src.main.api.db.models.account_table import Account
from src.main.api.db.models.transfer_table import Transfer


class TransferCrudDb:
    # Получаем записи transfer между указанными счетами.
    @staticmethod
    def get_transfers_by_accounts(db: Session, from_account_id: int, to_account_id: int) -> list[Transfer]:
        return db.query(Transfer).filter_by(from_account_id=from_account_id, to_account_id=to_account_id, transaction_type="transfer").all()