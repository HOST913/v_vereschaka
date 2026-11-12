# Проверки пополнения на минимальную сумму и отказа для суммы ниже минимума.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.db.crud.account_crud import AccountCrudDb as Account





@pytest.mark.api
class TestDepositUser:
    # Проверяем успешное пополнение счёта на 1000.
    def test_deposit_user_valid(self,db_session: Session,api_manager: ApiManager, create_user_request: CreateUserRequest):
        # Создаём счёт пользователя
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0
        account_id = response.id

        # Пополняем счёт на минимальную разрешённую сумму 1000
        deposit_user_request = DepositUserRequest(accountId = account_id, amount = 1000)
        response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_user_request, create_user_request=create_user_request)
        assert response.balance == 1000

        # Сверяем сохранённый в БД счёт и баланс после пополнения.
        account_from_db = Account.get_account_by_id(db_session, response.id)
        assert account_from_db.id == response.id, 'Аккаунт не создан id аккаунта нет в бд'
        assert account_from_db.balance == 1000, 'Поле баланса для созданого отсудтвует в бд'


    # Проверяем отказ при пополнении на 999 и сохранность баланса.
    def test_deposit_user_invalid(self,db_session: Session, api_manager: ApiManager, create_user_request: CreateUserRequest):
        # Создаём счёт пользователя
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0
        account_id = response.id

        # Сохраняем баланс счёта до запроса
        balance = api_manager.user_steps.get_account(account_id=account_id,create_user_request=create_user_request)
        account_balance_from = balance.balance

        # Пытаемся пополнить счёт на 999 и ожидаем отказ 400
        deposit_user_request = DepositUserRequest(accountId = account_id, amount = 999)
        response = api_manager.user_steps.account_deposit_invalid(deposit_user_request=deposit_user_request, create_user_request=create_user_request)

        # Повторно читаем баланс счёта после отказа
        balance = api_manager.user_steps.get_account(account_id=account_id,create_user_request=create_user_request)
        account_balance_to = balance.balance

        # Проверяем, что баланс счёта не изменился
        assert account_balance_from == account_balance_to

        # Сверяем баланс счёта в БД с балансом до отклонённого пополнения.
        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.id == account_id, 'Аккаунт не создан id аккаунта нет в бд'
        assert account_from_db.balance == account_balance_from, 'Поле баланса для созданого отсудтвует в бд'






