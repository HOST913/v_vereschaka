# Подготовка пользователей разных ролей, счетов и выданного кредита.
import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest
from src.main.api.generators.operation_data_generator import OperationDataGenerator
from src.main.api.db.crud.account_crud import AccountCrudDb
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.models.request_model.repay_user_credit_request import CreditUserRepayRequest
from src.main.api.utils.history_utils import find_credit_in_history


# Создаём обычного пользователя со случайными данными для текущего теста.
@pytest.fixture
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request

# Создаём пользователя с ролью, разрешающей получение кредита.
@pytest.fixture
def credit_user(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    # Назначаем роль, которой разрешено запрашивать кредит.
    user_request.role = "ROLE_CREDIT_SECRET"
    api_manager.admin_steps.create_user(user_request)
    return user_request

# Подготавливаем пользователя, банковский счёт и выданный кредит.
@pytest.fixture
def issued_credit(api_manager, db_session, credit_user):
    account = api_manager.user_steps.create_account(credit_user)
    assert account.balance == 0, f'Баланс нового счёта перед получением кредита должен быть 0, получен {account.balance}'
    credits_before = CreditCrudDb.get_credits_by_account_id(db_session, account.id)
    assert credits_before == [], f'У нового счёта {account.id} не должно быть кредитов, найдено {len(credits_before)}'
    data = OperationDataGenerator.random_credit_data()
    credit_request = CreditUserRequest(accountId=account.id,amount=data["amount"],termMonths=data["termMonths"])
    credit = api_manager.user_steps.account_credit(credit_user_request=credit_request, create_user_request=credit_user)
    assert credit.balance == credit_request.amount, f'После выдачи кредита баланс должен быть {credit_request.amount}, получен {credit.balance}'
    assert credit.amount == credit_request.amount, f'Сумма подготовленного кредита должна быть {credit_request.amount}, получена {credit.amount}'
    assert credit.id == account.id, f'Кредит должен быть выдан на счёт {account.id}, получен счёт {credit.id}'
    assert credit.termMonths == credit_request.termMonths, f'Срок подготовленного кредита должен быть {credit_request.termMonths}, получен {credit.termMonths}'

    # Подтверждаем действующий долг и сохраняем балансы до целевого погашения.
    account_before = api_manager.user_steps.get_account(account_id=account.id, create_user_request=credit_user)
    account_before_db = AccountCrudDb.get_account_by_id(db_session, account.id)
    credit_before_db = CreditCrudDb.get_credit_by_id(db_session, credit.creditId)
    assert account_before_db is not None, f'Счёт {account.id} не найден в БД перед погашением'
    assert credit_before_db is not None, f'Кредит {credit.creditId} не найден в БД перед погашением'
    assert credit_before_db.account_id == account.id, f'Кредит должен быть связан со счётом {account.id}, получен {credit_before_db.account_id}'
    assert credit_before_db.balance == -credit_request.amount, f'До погашения баланс кредитного обязательства должен быть {-credit_request.amount}, получен {credit_before_db.balance}'
    assert account_before.balance == credit_request.amount, f'До погашения баланс по API должен быть {credit_request.amount}, получен {account_before.balance}'
    assert account_before_db.balance == account_before.balance, f'До погашения баланс в БД должен быть {account_before.balance}, получен {account_before_db.balance}'
    repay_request = CreditUserRepayRequest(creditId=credit.creditId,accountId=account.id,amount=credit_request.amount)

    # Передаём готовый кредит, платёж и числовые снимки балансов.
    return {
        "user": credit_user,
        "account": account,
        "credit": credit,
        "credit_request": credit_request,
        "repay_request": repay_request,
        "balance_before": account_before.balance,
        "balance_before_db": account_before_db.balance
    }


# Подготавливаем уже закрытый кредит и деньги для проверки повторного списания.
@pytest.fixture
def paid_credit(api_manager, db_session, issued_credit):
    setup = issued_credit.copy()
    deposit_request = DepositUserRequest(accountId=setup["account"].id,amount=setup["repay_request"].amount)
    deposit_response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_request, create_user_request=setup["user"])
    expected_before_repay = setup["balance_before"] + deposit_request.amount
    assert deposit_response.balance == expected_before_repay, f'Перед первым погашением баланс должен быть {expected_before_repay}, получен {deposit_response.balance}'

    # Первое погашение является предусловием негативного теста.
    response = api_manager.user_steps.account_repay_credit(setup["repay_request"], setup["user"])
    assert response.creditId == setup["credit"].creditId, f'Первый платёж должен погасить кредит {setup["credit"].creditId}, получен {response.creditId}'
    assert response.amountDeposited == setup["repay_request"].amount, f'Ожидался первый платёж {setup["repay_request"].amount}, получен {response.amountDeposited}'
    expected_after_repay = expected_before_repay - setup["repay_request"].amount
    history = api_manager.user_steps.get_credit_history(setup["user"])
    found_credit = find_credit_in_history(history.credits, setup["credit"].creditId)
    assert found_credit is not None, f'Кредит {setup["credit"].creditId} не найден в истории после первого погашения'
    assert float(found_credit["balance"]) == 0, f'До повторного запроса долг должен быть 0, получен {found_credit["balance"]}'

    # Обновляем БД и сохраняем состояние после первого платежа.
    db_session.expire_all()
    account_before = api_manager.user_steps.get_account(account_id=setup["account"].id, create_user_request=setup["user"])
    account_before_db = AccountCrudDb.get_account_by_id(db_session, setup["account"].id)
    credit_before_db = CreditCrudDb.get_credit_by_id(db_session, setup["credit"].creditId)
    assert account_before_db is not None, f'Счёт {setup["account"].id} не найден в БД после первого погашения'
    assert credit_before_db is not None, f'Кредит {setup["credit"].creditId} не найден в БД после первого погашения'
    assert credit_before_db.account_id == setup["account"].id, f'Кредит должен быть связан со счётом {setup["account"].id}, получен {credit_before_db.account_id}'
    assert credit_before_db.balance == 0, f'До повторного платежа задолженность в БД должна быть 0, получена {credit_before_db.balance}'
    assert account_before.balance == expected_after_repay, f'Перед повторным запросом баланс по API должен быть {expected_after_repay}, получен {account_before.balance}'
    assert account_before_db.balance == expected_after_repay, f'Перед повторным запросом баланс в БД должен быть {expected_after_repay}, получен {account_before_db.balance}'
    assert account_before.balance >= setup["repay_request"].amount, f'Для проверки повторного погашения нужно не меньше {setup["repay_request"].amount}, доступно {account_before.balance}'
    setup["balance_before"] = account_before.balance
    setup["balance_before_db"] = account_before_db.balance
    return setup
