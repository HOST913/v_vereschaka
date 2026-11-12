# Подготовка пользователей разных ролей, счетов и выданного кредита.
import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest


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
def issued_credit(api_manager, credit_user):
    account = api_manager.user_steps.create_account(credit_user)
    credit_request = CreditUserRequest(accountId=account.id,amount=5000,termMonths=12)
    credit = api_manager.user_steps.account_credit(credit_user_request=credit_request, create_user_request=credit_user)
    # Передаём тесту пользователя, созданный счёт и ответ выдачи кредита.
    return {
        "user": credit_user,
        "account": account,
        "credit": credit
    }
