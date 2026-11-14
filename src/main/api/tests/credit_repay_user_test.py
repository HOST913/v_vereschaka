# Проверки полного погашения кредита и отказа при повторном платеже.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.utils.history_utils import find_credit_in_history


@pytest.mark.api
class TestRepayUserCredit:
    # Полностью погашаем кредит, выданный фикстурой issued_credit.
    def test_repay_user_valid(self,db_session: Session,api_manager: ApiManager, issued_credit: dict):
        response = api_manager.user_steps.account_repay_credit(issued_credit["repay_request"], issued_credit["user"])
        assert response.creditId == issued_credit["credit"].creditId, f'Ожидался погашенный кредит {issued_credit["credit"].creditId}, получен {response.creditId}'
        assert response.amountDeposited == issued_credit["repay_request"].amount, f'Ожидался платёж {issued_credit["repay_request"].amount}, получен {response.amountDeposited}'

        # Проверяем отсутствие долга по нужному кредиту в истории API.
        history = api_manager.user_steps.get_credit_history(issued_credit["user"])
        found_credit = find_credit_in_history(history.credits, issued_credit["credit"].creditId)
        assert found_credit is not None, f'Погашенный кредит {issued_credit["credit"].creditId} не найден в истории API'
        assert float(found_credit["balance"]) == 0, f'После погашения задолженность по API должна быть 0, получена {found_credit["balance"]}'

        # Сверяем закрытие долга и списание точной суммы со счёта в БД.
        db_session.expire_all()
        account_after = AccountCrudDb.get_account_by_id(db_session, issued_credit["account"].id)
        credit_after = CreditCrudDb.get_credit_by_id(db_session, issued_credit["credit"].creditId)
        assert account_after is not None, f'Счёт {issued_credit["account"].id} не найден в БД после погашения'
        assert credit_after is not None, f'Кредит {issued_credit["credit"].creditId} не найден в БД после погашения'
        assert credit_after.balance == 0, f'После погашения задолженность в БД должна быть 0, получена {credit_after.balance}'
        assert account_after.balance == issued_credit["balance_before_db"] - issued_credit["repay_request"].amount, f'После погашения баланс в БД должен быть {issued_credit["balance_before_db"] - issued_credit["repay_request"].amount}, получен {account_after.balance}'

    # Повторяем платёж по кредиту, полностью погашенному фикстурой paid_credit.
    def test_repay_user_invalid(self,db_session: Session, api_manager: ApiManager, paid_credit: dict):
        response = api_manager.user_steps.account_repay_credit_again(paid_credit["repay_request"], paid_credit["user"])
        assert response.status_code == 409, f'При повторном погашении ожидался HTTP 409, получен {response.status_code}'

        # Проверяем отсутствие второго списания по API и нулевой долг.
        account_after = api_manager.user_steps.get_account(account_id=paid_credit["account"].id, create_user_request=paid_credit["user"])
        assert account_after.balance == paid_credit["balance_before"], f'После повторного запроса баланс по API должен остаться {paid_credit["balance_before"]}, получен {account_after.balance}'
        history = api_manager.user_steps.get_credit_history(paid_credit["user"])
        found_credit = find_credit_in_history(history.credits, paid_credit["credit"].creditId)
        assert found_credit is not None, f'Кредит {paid_credit["credit"].creditId} не найден в истории после повторного запроса'
        assert float(found_credit["balance"]) == 0, f'После повторного запроса задолженность по API должна остаться 0, получена {found_credit["balance"]}'

        # Подтверждаем неизменный баланс счёта и закрытый долг непосредственно в БД.
        db_session.expire_all()
        account_after_db = AccountCrudDb.get_account_by_id(db_session, paid_credit["account"].id)
        credit_after_db = CreditCrudDb.get_credit_by_id(db_session, paid_credit["credit"].creditId)
        assert account_after_db is not None, f'Счёт {paid_credit["account"].id} не найден в БД после повторного запроса'
        assert credit_after_db is not None, f'Кредит {paid_credit["credit"].creditId} не найден в БД после повторного запроса'
        assert account_after_db.balance == paid_credit["balance_before_db"], f'После повторного запроса баланс в БД должен остаться {paid_credit["balance_before_db"]}, получен {account_after_db.balance}'
        assert credit_after_db.balance == 0, f'После повторного запроса задолженность в БД должна остаться 0, получена {credit_after_db.balance}'
