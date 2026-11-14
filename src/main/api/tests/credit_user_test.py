# Проверки выдачи кредита разрешённой роли и отказа обычному пользователю.
import pytest
from sqlalchemy.orm import Session

from src.main.api.db.crud.account_crud import AccountCrudDb
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.classes.api_manager import ApiManager


@pytest.mark.api
class TestCreditUser:
    # Выдаём кредит на подготовленный собственный счёт разрешённой роли.
    def test_credit_user_valid(self,db_session: Session,api_manager: ApiManager, credit_setup: dict):
        response = api_manager.user_steps.account_credit(credit_setup["request"], credit_setup["user"])
        assert response.balance == credit_setup["expected_balance"], f'После выдачи кредита API должен вернуть баланс {credit_setup["expected_balance"]}, получен {response.balance}'
        assert response.amount == credit_setup["request"].amount, f'Ожидалась сумма кредита {credit_setup["request"].amount}, получена {response.amount}'
        assert response.id == credit_setup["account"].id, f'Кредит должен быть выдан на счёт {credit_setup["account"].id}, получен {response.id}'
        assert response.termMonths == credit_setup["request"].termMonths, f'Ожидался срок {credit_setup["request"].termMonths} месяцев, получен {response.termMonths}'

        # Сверяем выданный кредит с заявкой и счётом в БД.
        db_session.expire_all()
        credit_from_db = CreditCrudDb.get_credit_by_id(db_session, response.creditId)
        assert credit_from_db is not None, f'Выданный кредит {response.creditId} не найден в БД'
        assert credit_from_db.account_id == credit_setup["account"].id, f'Кредит в БД должен быть связан со счётом {credit_setup["account"].id}, получен {credit_from_db.account_id}'
        assert credit_from_db.amount == credit_setup["request"].amount, f'Сумма кредита в БД должна быть {credit_setup["request"].amount}, получена {credit_from_db.amount}'
        assert credit_from_db.term_months == credit_setup["request"].termMonths, f'Срок кредита в БД должен быть {credit_setup["request"].termMonths}, получен {credit_from_db.term_months}'

        # Проверяем единственное кредитное обязательство и зачисление денег.
        credits_after = CreditCrudDb.get_credits_by_account_id(db_session, credit_setup["account"].id)
        assert len(credits_after) == 1, f'У счёта {credit_setup["account"].id} должен быть один кредит, найдено {len(credits_after)}'
        assert credits_after[0].id == response.creditId, f'Ожидался кредит {response.creditId}, найден {credits_after[0].id}'
        account_from_db = AccountCrudDb.get_account_by_id(db_session, credit_setup["account"].id)
        assert account_from_db is not None, f'Счёт {credit_setup["account"].id} не найден в БД после выдачи кредита'
        assert account_from_db.balance == credit_setup["expected_balance"], f'После выдачи кредита баланс в БД должен быть {credit_setup["expected_balance"]}, получен {account_from_db.balance}'

    # Проверяем отказ обычному пользователю и отсутствие изменений.
    def test_credit_user_invalid(self,db_session: Session,api_manager: ApiManager, forbidden_credit_setup: dict):
        api_manager.user_steps.account_credit_invalid(forbidden_credit_setup["request"], forbidden_credit_setup["user"])

        # Сравниваем балансы после отказа со снимками API и БД из фикстуры.
        account_after = api_manager.user_steps.get_account(account_id=forbidden_credit_setup["account"].id, create_user_request=forbidden_credit_setup["user"])
        assert account_after.balance == forbidden_credit_setup["balance_before"], f'После отказа баланс по API должен остаться {forbidden_credit_setup["balance_before"]}, получен {account_after.balance}'
        db_session.expire_all()
        account_after_db = AccountCrudDb.get_account_by_id(db_session, forbidden_credit_setup["account"].id)
        assert account_after_db is not None, f'Счёт {forbidden_credit_setup["account"].id} не найден в БД после отказа в кредите'
        assert account_after_db.balance == forbidden_credit_setup["balance_before_db"], f'После отказа баланс в БД должен остаться {forbidden_credit_setup["balance_before_db"]}, получен {account_after_db.balance}'
        credits_after = CreditCrudDb.get_credits_by_account_id(db_session, forbidden_credit_setup["account"].id)
        assert credits_after == [], f'После отказа у счёта {forbidden_credit_setup["account"].id} появились кредиты: найдено {len(credits_after)}'
