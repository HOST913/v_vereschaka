# Проверки перевода между двумя счетами и отказа для суммы ниже минимума.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.utils.history_utils import find_transaction_in_history


@pytest.mark.api
class TestTransferUser:
    # Выполняем перевод и проверяем оба счёта и записи истории.
    def test_transfer_user_valid(self,db_session: Session,api_manager: ApiManager, transfer_setup: dict):
        response = api_manager.user_steps.account_transfer(transfer_user_request=transfer_setup["request"], create_user_request=transfer_setup["from_user"])
        assert response.fromAccountIdBalance == transfer_setup["expected_from_balance"], f'После перевода ожидался баланс отправителя {transfer_setup["expected_from_balance"]}, получен {response.fromAccountIdBalance}'
        assert response.fromAccountId == transfer_setup["from_account"].id, f'Ожидался счёт отправителя {transfer_setup["from_account"].id}, получен {response.fromAccountId}'
        assert response.toAccountId == transfer_setup["to_account"].id, f'Ожидался счёт получателя {transfer_setup["to_account"].id}, получен {response.toAccountId}'

        # Читаем актуальные балансы и истории от имени владельцев счетов.
        from_after = api_manager.user_steps.get_account(account_id=transfer_setup["from_account"].id, create_user_request=transfer_setup["from_user"])
        to_after = api_manager.user_steps.get_account(account_id=transfer_setup["to_account"].id, create_user_request=transfer_setup["to_user"])
        assert from_after.balance == transfer_setup["expected_from_balance"], f'Баланс отправителя по API должен быть {transfer_setup["expected_from_balance"]}, получен {from_after.balance}'
        assert to_after.balance == transfer_setup["expected_to_balance"], f'Баланс получателя по API должен быть {transfer_setup["expected_to_balance"]}, получен {to_after.balance}'

        # Поиск записей вынесен в utils; здесь проверяем их содержимое.
        transfer_out = find_transaction_in_history(from_after.transactions, "transfer_out")
        assert transfer_out is not None, f'Исходящий перевод не найден в истории счёта {transfer_setup["from_account"].id}'
        assert transfer_out["fromAccountId"] == transfer_setup["from_account"].id, f'В исходящей операции ожидался отправитель {transfer_setup["from_account"].id}, получен {transfer_out["fromAccountId"]}'
        assert transfer_out["toAccountId"] == transfer_setup["to_account"].id, f'В исходящей операции ожидался получатель {transfer_setup["to_account"].id}, получен {transfer_out["toAccountId"]}'
        assert transfer_out["amount"] == -transfer_setup["request"].amount, f'Ожидалась сумма списания {-transfer_setup["request"].amount}, получена {transfer_out["amount"]}'

        transfer_in = find_transaction_in_history(to_after.transactions, "transfer_in")
        assert transfer_in is not None, f'Входящий перевод не найден в истории счёта {transfer_setup["to_account"].id}'
        assert transfer_in["fromAccountId"] == transfer_setup["from_account"].id, f'Во входящей операции ожидался отправитель {transfer_setup["from_account"].id}, получен {transfer_in["fromAccountId"]}'
        assert transfer_in["toAccountId"] == transfer_setup["to_account"].id, f'Во входящей операции ожидался получатель {transfer_setup["to_account"].id}, получен {transfer_in["toAccountId"]}'
        assert transfer_in["amount"] == transfer_setup["request"].amount, f'Ожидалась сумма зачисления {transfer_setup["request"].amount}, получена {transfer_in["amount"]}'
        assert transfer_out["transactionId"] == transfer_in["transactionId"], f'Истории содержат разные ID перевода: исходящий {transfer_out["transactionId"]}, входящий {transfer_in["transactionId"]}'

        # Сверяем фактические остатки банковских счетов в БД.
        db_session.expire_all()
        from_account_db = Account.get_account_by_id(db_session, transfer_setup["from_account"].id)
        to_account_db = Account.get_account_by_id(db_session, transfer_setup["to_account"].id)
        assert from_account_db is not None, f'Счёт отправителя {transfer_setup["from_account"].id} не найден в БД после перевода'
        assert to_account_db is not None, f'Счёт получателя {transfer_setup["to_account"].id} не найден в БД после перевода'
        assert from_account_db.id == transfer_setup["from_account"].id, f'В БД ожидался счёт отправителя {transfer_setup["from_account"].id}, получен {from_account_db.id}'
        assert to_account_db.id == transfer_setup["to_account"].id, f'В БД ожидался счёт получателя {transfer_setup["to_account"].id}, получен {to_account_db.id}'
        assert from_account_db.balance == transfer_setup["expected_from_balance"], f'Баланс отправителя в БД должен быть {transfer_setup["expected_from_balance"]}, получен {from_account_db.balance}'
        assert to_account_db.balance == transfer_setup["expected_to_balance"], f'Баланс получателя в БД должен быть {transfer_setup["expected_to_balance"]}, получен {to_account_db.balance}'

    # Проверяем отказ для суммы ниже минимума и сохранность обоих балансов.
    def test_deposit_user_with_invalid(self,db_session: Session,api_manager: ApiManager, transfer_setup: dict):
        api_manager.user_steps.account_transfer_invalid(transfer_user_request=transfer_setup["invalid_request"], create_user_request=transfer_setup["from_user"])

        # Сравниваем балансы API с фактическим состоянием до запроса.
        from_after = api_manager.user_steps.get_account(account_id=transfer_setup["from_account"].id, create_user_request=transfer_setup["from_user"])
        to_after = api_manager.user_steps.get_account(account_id=transfer_setup["to_account"].id, create_user_request=transfer_setup["to_user"])
        assert from_after.balance == transfer_setup["from_balance_before"], f'После отказа баланс отправителя по API должен остаться {transfer_setup["from_balance_before"]}, получен {from_after.balance}'
        assert to_after.balance == transfer_setup["to_balance_before"], f'После отказа баланс получателя по API должен остаться {transfer_setup["to_balance_before"]}, получен {to_after.balance}'

        # Проверяем сохранность обоих балансов непосредственно в БД.
        db_session.expire_all()
        from_account_db = Account.get_account_by_id(db_session, transfer_setup["from_account"].id)
        to_account_db = Account.get_account_by_id(db_session, transfer_setup["to_account"].id)
        assert from_account_db is not None, f'Счёт отправителя {transfer_setup["from_account"].id} не найден в БД после отказа'
        assert to_account_db is not None, f'Счёт получателя {transfer_setup["to_account"].id} не найден в БД после отказа'
        assert from_account_db.id == transfer_setup["from_account"].id, f'В БД ожидался счёт отправителя {transfer_setup["from_account"].id}, получен {from_account_db.id}'
        assert to_account_db.id == transfer_setup["to_account"].id, f'В БД ожидался счёт получателя {transfer_setup["to_account"].id}, получен {to_account_db.id}'
        assert from_account_db.balance == transfer_setup["from_balance_before_db"], f'После отказа баланс отправителя в БД должен остаться {transfer_setup["from_balance_before_db"]}, получен {from_account_db.balance}'
        assert to_account_db.balance == transfer_setup["to_balance_before_db"], f'После отказа баланс получателя в БД должен остаться {transfer_setup["to_balance_before_db"]}, получен {to_account_db.balance}'
