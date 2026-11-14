# Шаги операций со счетами, переводами и кредитами пользователя.
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.credit_user_request import CreditUserRequest
from src.main.api.models.request_model.repay_user_credit_request import CreditUserRepayRequest
from src.main.api.models.request_model.transfer_user_request import TransferUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.foundation.requesters.crud_requester import CrudRequester


class UserSteps(BaseSteps):
    # Создаём банковский счёт от имени переданного пользователя.
    def create_account(self, create_user_request:CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.request_created()
        ).post()
        return response

    # Пополняем счёт и возвращаем модель успешного ответа.
    def account_deposit(self, deposit_user_request:DepositUserRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_ok()
        ).post(deposit_user_request)
        return response

    # Выполняем перевод от имени владельца счёта отправителя.
    def account_transfer(self, transfer_user_request:TransferUserRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(transfer_user_request)
        return response

    # Запрашиваем кредит от имени переданного пользователя.
    def account_credit(self, credit_user_request:CreditUserRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_USER,
            ResponseSpecs.request_created()
        ).post(credit_user_request)
        return response

    # Отправляем платёж для полного погашения кредита.
    def account_repay_credit(self, credit_user_repay_request : CreditUserRepayRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.REPAY_CREDIT,
            ResponseSpecs.request_ok()
        ).post(credit_user_repay_request)
        return response

    # Проверяем отказ 400 при недопустимом пополнении.
    def account_deposit_invalid(self, deposit_user_request: DepositUserRequest, create_user_request: CreateUserRequest):
        return CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username,password=create_user_request.password),
            Endpoint.ACCOUNT_DEPOSIT,
            ResponseSpecs.request_bad()
        ).post(deposit_user_request)

    # Проверяем отказ 400 при недопустимом переводе.
    def account_transfer_invalid(self, transfer_user_request: TransferUserRequest, create_user_request: CreateUserRequest):
        return CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_bad()
        ).post(transfer_user_request)

    # Проверяем отказ 403 при запросе кредита без нужных прав.
    def account_credit_invalid(self, credit_user_request: CreditUserRequest, create_user_request: CreateUserRequest):
        return CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_USER,
            ResponseSpecs.request_forbidden()
        ).post(credit_user_request)

    # Проверяем отказ 422 для некорректного платежа по кредиту.
    def account_repay_credit_invalid(self, credit_user_repay_request: CreditUserRepayRequest, create_user_request: CreateUserRequest):
        return CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.REPAY_CREDIT,
            ResponseSpecs.request_unprocessable()
        ).post(credit_user_repay_request)

    # Читаем текущий баланс и историю операций собственного счёта.
    def get_account(self, account_id, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.ACCOUNT_TRANSACTIONS,
            ResponseSpecs.request_ok()
        ).get(account_id)
        return response

    # Читаем историю кредитов переданного пользователя.
    def get_credit_history(self, create_user_request):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_HISTORY,
            ResponseSpecs.request_ok()
        ).get_all()
        return response

    # Повторяем платёж по погашенному кредиту и ожидаем отказ 409.
    def account_repay_credit_again(self, credit_user_repay_request: CreditUserRepayRequest, create_user_request: CreateUserRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.REPAY_CREDIT,
            ResponseSpecs.request_conflict()
        ).post(credit_user_repay_request)
        return response
