# Проверки пополнения на минимальную сумму и отказа для суммы ниже минимума.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account


@pytest.mark.api
class TestDepositUser:
    # Пополняем подготовленный счёт и сверяем результат с БД.
    def test_deposit_user_valid(self,db_session: Session,api_manager: ApiManager, deposit_setup: dict):
        response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_setup["request"], create_user_request=deposit_setup["user"])
        assert response.id == deposit_setup["account"].id, f'Пополнен другой счёт: ожидался ID {deposit_setup["account"].id}, получен {response.id}'
        assert response.balance == deposit_setup["expected_balance"], f'После пополнения API должен вернуть баланс {deposit_setup["expected_balance"]}, получен {response.balance}'

        # Читаем актуальные данные БД после целевого пополнения.
        db_session.expire_all()
        account_from_db = Account.get_account_by_id(db_session, deposit_setup["account"].id)
        assert account_from_db is not None, f'Пополненный счёт {deposit_setup["account"].id} не найден в БД'
        assert account_from_db.id == response.id, f'ID счёта в БД должен быть {response.id}, получен {account_from_db.id}'
        assert account_from_db.balance == deposit_setup["expected_balance"], f'После пополнения баланс в БД должен быть {deposit_setup["expected_balance"]}, получен {account_from_db.balance}'

    # Проверяем отказ для суммы ниже минимума и сохранность баланса.
    def test_deposit_user_invalid(self,db_session: Session, api_manager: ApiManager, deposit_setup: dict):
        api_manager.user_steps.account_deposit_invalid(deposit_user_request=deposit_setup["invalid_request"], create_user_request=deposit_setup["user"])

        # Сверяем фактические балансы после отказа со снимками из фикстуры.
        account_after = api_manager.user_steps.get_account(account_id=deposit_setup["account"].id, create_user_request=deposit_setup["user"])
        assert account_after.balance == deposit_setup["balance_before"], f'После отказа баланс по API должен остаться {deposit_setup["balance_before"]}, получен {account_after.balance}'
        db_session.expire_all()
        account_from_db = Account.get_account_by_id(db_session, deposit_setup["account"].id)
        assert account_from_db is not None, f'Счёт {deposit_setup["account"].id} не найден в БД после отказа в пополнении'
        assert account_from_db.id == deposit_setup["account"].id, f'Из БД получен другой счёт: ожидался ID {deposit_setup["account"].id}, получен {account_from_db.id}'
        assert account_from_db.balance == deposit_setup["balance_before_db"], f'После отказа баланс в БД должен остаться {deposit_setup["balance_before_db"]}, получен {account_from_db.balance}'
