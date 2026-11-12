# Проверки полного погашения кредита и отказа при повторном платеже.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.models.request_model.repay_user_credit_request import CreditUserRepayRequest



@pytest.mark.api
class TestRepayUserCredit:
    # Полностью погашаем действующий кредит и сверяем счёт и задолженность.
    def test_repay_user_valid(self,db_session: Session,api_manager: ApiManager, credit_user: CreateUserRequest):
        # Создаём счёт кредитного пользователя
        response = api_manager.user_steps.create_account(credit_user)
        assert response.balance == 0
        account_id = response.id

        # Получаем кредит 5000 на 12 месяцев
        user_credit_request = CreditUserRequest(accountId=account_id, amount=5000, termMonths=12)
        response = api_manager.user_steps.account_credit(user_credit_request, credit_user)
        assert response.balance == 5000
        assert response.amount == user_credit_request.amount
        assert response.id == user_credit_request.accountId
        assert response.termMonths == user_credit_request.termMonths
        credit_user_id = response.creditId

        # Сохраняем баланс банковского счёта из БД до погашения.
        account_before = AccountCrudDb.get_account_by_id(db_session, account_id)
        assert account_before is not None, 'Счёт не найден в БД'
        balance_before = account_before.balance
        # Проверяем связь кредита со счётом и наличие задолженности до платежа.
        credit_before = CreditCrudDb.get_credit_by_id(db_session, credit_user_id)
        assert credit_before is not None
        assert credit_before.account_id == account_before.id
        assert credit_before.balance != 0
        assert balance_before == 5000



        # Полностью погашаем кредит суммой 5000
        repay_request = CreditUserRepayRequest(creditId = credit_user_id, accountId = account_id, amount = 5000 )
        response = api_manager.user_steps.account_repay_credit(repay_request, credit_user)
        assert response.creditId == credit_user_id
        assert response.amountDeposited == 5000

        # Проверяем отсутствие долга по погашенному кредиту
        credit_history = api_manager.user_steps.get_credit_history(credit_user)
        found_credit = None
        for credit in credit_history.credits:
            if credit["creditId"] == credit_user_id:
                found_credit = credit
                break

        assert found_credit is not None, (f"Кредит {credit_user_id} не найден в истории")
        assert float(found_credit["balance"]) == 0, (f"После погашения остался долг: {found_credit['balance']}")


        # Обновляем ранее загруженные данные перед повторным чтением БД.
        db_session.expire_all()

        # Читаем состояние банковского счёта и кредита после погашения.
        account_after = AccountCrudDb.get_account_by_id(db_session, account_id)
        credit_after = CreditCrudDb.get_credit_by_id(db_session, credit_user_id)

        assert account_after is not None, 'Счёт не найден в БД'
        assert credit_after is not None, 'Кредит не найден в БД'
        # Проверяем закрытие долга и списание точной суммы платежа.
        assert credit_after.balance == 0, 'После погашения осталась задолженность'
        assert account_after.balance == balance_before - repay_request.amount, 'Со счёта списана неверная сумма'

    # Проверяем отсутствие второго списания после повторного погашения.
    def test_repay_user_invalid(self,db_session: Session, api_manager: ApiManager, credit_user: CreateUserRequest):
        # Создаём счёт и получаем кредит 5000
        account = api_manager.user_steps.create_account(credit_user)
        credit_request = CreditUserRequest(accountId=account.id, amount=5000, termMonths=12)
        credit_response = api_manager.user_steps.account_credit( credit_request, credit_user)
        credit_id = credit_response.creditId

        # Добавляем ещё 5000: на счёте должно стать 10000
        deposit_request = DepositUserRequest(accountId=account.id,amount=5000)
        deposit_response = api_manager.user_steps.account_deposit(deposit_request, credit_user)
        assert deposit_response.balance == 10000

        # Первый раз полностью погашаем кредит
        repay_request = CreditUserRepayRequest(creditId=credit_id,accountId=account.id,amount=5000)
        response = api_manager.user_steps.account_repay_credit(repay_request, credit_user)
        assert response.creditId == credit_id
        assert response.amountDeposited == 5000

        # Перед повторным платежом читаем счёт и уже погашенный кредит из БД.
        account_before_db = AccountCrudDb.get_account_by_id(db_session, account.id)
        credit_before_db = CreditCrudDb.get_credit_by_id(db_session, credit_id)
        assert account_before_db is not None, 'Счёт не найден в БД'
        assert credit_before_db is not None, 'Кредит не найден в БД'
        assert credit_before_db.account_id == account.id
        assert account_before_db.balance == 5000
        assert credit_before_db.balance == 0
        # Сохраняем число баланса для сравнения после отклонённого платежа.
        balance_before_db = account_before_db.balance


        # Подтверждаем, что кредит уже погашен
        history = api_manager.user_steps.get_credit_history(credit_user)
        found_credit = None

        for credit in history.credits:
            if credit["creditId"] == credit_id:
                found_credit = credit
                break

        assert found_credit is not None, "Кредит не найден в истории"
        assert float(found_credit["balance"]) == 0

        # Запоминаем баланс перед повторной оплатой
        account_before = api_manager.user_steps.get_account(account.id, credit_user)
        balance_before = account_before.balance
        assert balance_before == 5000

        # Повторяем тот же платёж: ожидаем отказ 409
        response = api_manager.user_steps.account_repay_credit_again(repay_request, credit_user)
        assert response.status_code == 409

        # Обновляем ранее загруженные данные перед проверкой повторного платежа.
        db_session.expire_all()

        # Проверяем отсутствие второго списания
        account_after = api_manager.user_steps.get_account(account.id, credit_user)
        assert account_after.balance == balance_before

        # Повторно проверяем нулевой долг
        history = api_manager.user_steps.get_credit_history(credit_user)
        found_credit = None

        for credit in history.credits:
            if credit["creditId"] == credit_id:
                found_credit = credit
                break

        assert found_credit is not None, "Кредит исчез из истории"
        assert float(found_credit["balance"]) == 0

        # Повторно читаем банковский счёт и кредит после отказа 409.
        account_after_db = AccountCrudDb.get_account_by_id(db_session, account.id)
        credit_after_db = CreditCrudDb.get_credit_by_id(db_session, credit_id)
        assert account_after_db is not None, 'Счёт не найден в БД'
        assert credit_after_db is not None, 'Кредит не найден в БД'
        # Проверяем отсутствие второго списания и нулевую задолженность.
        assert account_after_db.balance == balance_before_db, 'Произошло повторное списание'
        assert credit_after_db.balance == 0, 'Задолженность изменилась'







