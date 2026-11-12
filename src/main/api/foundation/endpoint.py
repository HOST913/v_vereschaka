# Пути API-операций и соответствующие модели запросов и ответов.
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type
from src.main.api.models.base_model import BaseModel
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.models.request_model.login_user_request import LoginUserRequest
from src.main.api.models.request_model.repay_user_credit_request import CreditUserRepayRequest
from src.main.api.models.request_model.transfer_user_request import TransferUserRequest
from src.main.api.models.response_model.account_transactions_response import AccountTransactionsResponse
from src.main.api.models.response_model.create_account_response import CreateAccountResponse
from src.main.api.models.response_model.create_user_response import CreateUserResponse
from src.main.api.models.response_model.credit_history_response import CreditHistoryResponse
from src.main.api.models.response_model.credit_user_response import CreditUserResponse
from src.main.api.models.response_model.deposit_user_response import DepositUserResponse
from src.main.api.models.response_model.login_user_response import LoginUserResponse
from src.main.api.models.response_model.repay_user_credit_response import RepayUserCreditResponse
from src.main.api.models.response_model.transfer_user_response import TransferUserResponse


@dataclass
class EndpointConfiguration:
    url: str
    request_model: Optional[Type[BaseModel]]
    response_model: Optional[Type[BaseModel]]


class Endpoint(Enum):
    # Создание пользователя администратором.
    ADMIN_CREATE_USER = EndpointConfiguration(
        request_model = CreateUserRequest,
        response_model = CreateUserResponse,
        url = "/admin/create"
    )

    # Удаление пользователя по ID, который requester добавляет к пути.
    ADMIN_DELETE_USER = EndpointConfiguration(
        request_model = None,
        url = "/admin/users",
        response_model = None
    )

    # Вход пользователя и получение токена.
    LOGIN_USER = EndpointConfiguration(
        request_model = LoginUserRequest,
        url = "/auth/token/login",
        response_model = LoginUserResponse
    )

    # Создание банковского счёта для авторизованного пользователя.
    CREATE_ACCOUNT = EndpointConfiguration(
        request_model = None,
        url = "/account/create",
        response_model = CreateAccountResponse
    )

    # Пополнение банковского счёта.
    ACCOUNT_DEPOSIT = EndpointConfiguration(
        request_model = DepositUserRequest,
        url = "/account/deposit",
        response_model = DepositUserResponse
    )

    # Перевод между счетами отправителя и получателя.
    TRANSFER_ACCOUNT = EndpointConfiguration(
        request_model = TransferUserRequest,
        url = "/account/transfer",
        response_model = TransferUserResponse
    )

    # Подача заявки на выдачу кредита.
    CREDIT_USER = EndpointConfiguration(
        request_model = CreditUserRequest,
        url = "/credit/request",
        response_model = CreditUserResponse
    )

    # Погашение задолженности по кредиту.
    REPAY_CREDIT = EndpointConfiguration(
        request_model = CreditUserRepayRequest,
        url = "/credit/repay",
        response_model = RepayUserCreditResponse
    )

    # Чтение баланса и истории конкретного банковского счёта.
    ACCOUNT_TRANSACTIONS = EndpointConfiguration(
        request_model = None,
        url = "/account/transactions",
        response_model = AccountTransactionsResponse
    )

    # Чтение истории кредитов авторизованного пользователя.
    CREDIT_HISTORY = EndpointConfiguration(
        request_model = None,
        url = "/credit/history",
        response_model = CreditHistoryResponse
    )