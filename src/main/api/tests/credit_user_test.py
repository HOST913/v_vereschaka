# Проверки выдачи кредита разрешённой роли и отказа обычному пользователю.
import pytest
from sqlalchemy.orm import Session

from src.main.api.db.crud.account_crud import AccountCrudDb
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest


@pytest.mark.api
class TestCreditUser:
    # Проверяем выдачу кредита на собственный счёт разрешённой роли.
    def test_credit_user_valid(self,db_session: Session,api_manager: ApiManager, credit_user: CreateUserRequest):
        # Создаём собственный счёт пользователя
        response = api_manager.user_steps.create_account(credit_user)
        assert response.balance == 0
        account_id = response.id

        # Проверяем, что у нового банковского счёта ещё нет кредитов.
        credits_before = CreditCrudDb.get_credits_by_account_id(db_session, account_id)
        assert credits_before == []

        # Запрашиваем кредит 5000 на 12 месяцев
        user_credit_request = CreditUserRequest(accountId=account_id, amount=5000, termMonths=12)
        response = api_manager.user_steps.account_credit(user_credit_request, credit_user)
        assert response.balance == 5000
        assert response.amount == user_credit_request.amount
        assert response.id == user_credit_request.accountId
        assert response.termMonths == user_credit_request.termMonths
        # Сохраняем ID выданного кредита для поиска его записи в БД.
        credit_id = response.creditId

        # Сверяем сохранённый кредит со счётом, суммой и сроком заявки.
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, credit_id)
        assert credit_from_db is not None
        assert credit_from_db.account_id == user_credit_request.accountId
        assert credit_from_db.amount == user_credit_request.amount
        assert credit_from_db.term_months == user_credit_request.termMonths


        # Проверяем, что у счёта создан ровно один кредит
        credits_after = CreditCrudDb.get_credits_by_account_id(db_session, account_id)
        assert len(credits_after) == 1, 'У счёта должно быть ровно одно кредитное обязательство'
        assert credits_after[0].id == credit_id, 'Найден другой кредит'

        # Проверяем зачисление кредитных денег на банковский счёт
        account_from_db = AccountCrudDb.get_account_by_id(db_session, account_id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.balance == 5000, 'Кредитные деньги не зачислены на счёт'



    # Проверяем отказ обычному пользователю и отсутствие изменений в БД.
    def test_credit_user_invalid(self,db_session: Session,api_manager: ApiManager, create_user_request: CreateUserRequest):
        # Создаём собственный счёт пользователя
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0
        account_id = response.id

        # Проверяем, что у счёта ещё нет кредитов
        credits_before = CreditCrudDb.get_credits_by_account_id(db_session, account_id)
        assert credits_before == [], 'У счёта уже есть кредит'

        # Сохраняем баланс счёта из БД до заявки
        account_before = AccountCrudDb.get_account_by_id(db_session, account_id)
        assert account_before is not None, 'Счёт не найден в БД'
        balance_before = account_before.balance

        # Сохраняем баланс счёта до заявки
        balance = api_manager.user_steps.get_account(account_id=account_id, create_user_request=create_user_request)
        setup_balance = balance.balance

        # Запрашиваем кредит 5000 и ожидаем отказ 403 для обычного пользователя
        user_credit_request = CreditUserRequest(accountId=account_id, amount=5000, termMonths=12)
        api_manager.user_steps.account_credit_invalid(user_credit_request, create_user_request)


        # Повторно читаем баланс счёта после отказа
        balance = api_manager.user_steps.get_account(account_id=account_id, create_user_request=create_user_request)
        teardown_balance = balance.balance
        assert setup_balance == teardown_balance

        # Обновляем ранее загруженные данные сессии
        db_session.expire_all()

        # Проверяем, что баланс счёта в БД не изменился
        account_after = AccountCrudDb.get_account_by_id(db_session, account_id)
        assert account_after is not None, 'Счёт не найден в БД'
        assert account_after.balance == balance_before, 'После отказа баланс счёта изменился'

        # Проверяем, что кредит не появился в БД
        credits_after = CreditCrudDb.get_credits_by_account_id(db_session, account_id)
        assert credits_after == [], 'Несмотря на отказ, кредит появился в БД'





