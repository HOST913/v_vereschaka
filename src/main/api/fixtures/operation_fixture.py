# Подготовка счетов, заявок и исходных балансов для тестов операций.
import pytest

from src.main.api.db.crud.account_crud import AccountCrudDb
from src.main.api.db.crud.credit_crud import CreditCrudDb
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.generators.operation_data_generator import OperationDataGenerator
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.models.request_model.transfer_user_request import TransferUserRequest


def _prepare_account(api_manager, db_session, user):
    # Создаём собственный счёт и сохраняем независимые снимки баланса API и БД.
    account = api_manager.user_steps.create_account(user)
    assert account.balance == 0, f'Баланс нового счёта {account.id} должен быть 0, получен {account.balance}'
    account_before = api_manager.user_steps.get_account(account_id=account.id, create_user_request=user)
    account_from_db = AccountCrudDb.get_account_by_id(db_session, account.id)
    assert account_from_db is not None, f'Созданный счёт {account.id} не найден в БД при подготовке теста'
    assert account_before.balance == account.balance, f'До операции баланс счёта по API должен быть {account.balance}, получен {account_before.balance}'
    assert account_from_db.balance == account_before.balance, f'До операции баланс счёта в БД должен быть {account_before.balance}, получен {account_from_db.balance}'
    return {
        "user": user,
        "account": account,
        "balance_before": account_before.balance,
        "balance_before_db": account_from_db.balance
    }


@pytest.fixture
def deposit_setup(api_manager, db_session, create_user_request):
    # Готовим счёт и обе заявки, само пополнение выполняет тест.
    setup = _prepare_account(api_manager, db_session, create_user_request)
    data = OperationDataGenerator.deposit_data()
    setup["request"] = DepositUserRequest(accountId=setup["account"].id, amount=data["amount"])
    setup["invalid_request"] = DepositUserRequest(accountId=setup["account"].id, amount=data["invalid_amount"])
    setup["expected_balance"] = setup["balance_before"] + setup["request"].amount
    return setup


def _prepare_credit_request(api_manager, db_session, user):
    # Проверяем отсутствие кредитов и готовим заявку без её отправки.
    setup = _prepare_account(api_manager, db_session, user)
    credits_before = CreditCrudDb.get_credits_by_account_id(db_session, setup["account"].id)
    assert credits_before == [], f'До заявки у счёта {setup["account"].id} не должно быть кредитов, найдено {len(credits_before)}'
    data = OperationDataGenerator.credit_data()
    setup["request"] = CreditUserRequest(accountId=setup["account"].id, amount=data["amount"], termMonths=data["termMonths"])
    setup["expected_balance"] = setup["balance_before"] + setup["request"].amount
    return setup


@pytest.fixture
def credit_setup(api_manager, db_session, credit_user):
    # Готовим заявку пользователя с правом на кредит.
    return _prepare_credit_request(api_manager, db_session, credit_user)


@pytest.fixture
def forbidden_credit_setup(api_manager, db_session, create_user_request):
    # Готовим такую же заявку обычного пользователя без права на кредит.
    return _prepare_credit_request(api_manager, db_session, create_user_request)


@pytest.fixture
def transfer_setup(api_manager, db_session, create_user_request):
    # Создаём отдельного получателя; оба пользователя будут удалены общей фикстурой.
    to_user = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(to_user)
    from_account = api_manager.user_steps.create_account(create_user_request)
    to_account = api_manager.user_steps.create_account(to_user)
    assert from_account.balance == 0, f'Начальный баланс отправителя должен быть 0, получен {from_account.balance}'
    assert to_account.balance == 0, f'Начальный баланс получателя должен быть 0, получен {to_account.balance}'

    # Пополняем оба счёта до исходных балансов из ТЗ.
    data = OperationDataGenerator.transfer_data()
    from_deposit = DepositUserRequest(accountId=from_account.id, amount=data["from_balance"])
    from_response = api_manager.user_steps.account_deposit(deposit_user_request=from_deposit, create_user_request=create_user_request)
    assert from_response.balance == data["from_balance"], f'Перед переводом баланс отправителя должен быть {data["from_balance"]}, получен {from_response.balance}'
    to_deposit = DepositUserRequest(accountId=to_account.id, amount=data["to_balance"])
    to_response = api_manager.user_steps.account_deposit(deposit_user_request=to_deposit, create_user_request=to_user)
    assert to_response.balance == data["to_balance"], f'Перед переводом баланс получателя должен быть {data["to_balance"]}, получен {to_response.balance}'

    # Сохраняем фактические балансы до перевода через API и БД.
    from_before = api_manager.user_steps.get_account(account_id=from_account.id, create_user_request=create_user_request)
    to_before = api_manager.user_steps.get_account(account_id=to_account.id, create_user_request=to_user)
    from_before_db = AccountCrudDb.get_account_by_id(db_session, from_account.id)
    to_before_db = AccountCrudDb.get_account_by_id(db_session, to_account.id)
    assert from_before_db is not None, f'Счёт отправителя {from_account.id} не найден в БД перед переводом'
    assert to_before_db is not None, f'Счёт получателя {to_account.id} не найден в БД перед переводом'
    assert from_before.balance == data["from_balance"], f'Перед переводом API должен вернуть баланс отправителя {data["from_balance"]}, получен {from_before.balance}'
    assert to_before.balance == data["to_balance"], f'Перед переводом API должен вернуть баланс получателя {data["to_balance"]}, получен {to_before.balance}'
    assert from_before_db.balance == from_before.balance, f'Баланс отправителя в БД должен быть {from_before.balance}, получен {from_before_db.balance}'
    assert to_before_db.balance == to_before.balance, f'Баланс получателя в БД должен быть {to_before.balance}, получен {to_before_db.balance}'

    transfer_request = TransferUserRequest(fromAccountId=from_account.id, toAccountId=to_account.id, amount=data["amount"])
    invalid_request = TransferUserRequest(fromAccountId=from_account.id, toAccountId=to_account.id, amount=data["invalid_amount"])
    return {
        "from_user": create_user_request,
        "to_user": to_user,
        "from_account": from_account,
        "to_account": to_account,
        "request": transfer_request,
        "invalid_request": invalid_request,
        "from_balance_before": from_before.balance,
        "to_balance_before": to_before.balance,
        "from_balance_before_db": from_before_db.balance,
        "to_balance_before_db": to_before_db.balance,
        "expected_from_balance": from_before.balance - transfer_request.amount,
        "expected_to_balance": to_before.balance + transfer_request.amount
    }
