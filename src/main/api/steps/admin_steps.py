# Шаги создания, удаления и авторизации пользователей.
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.login_user_request import LoginUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps



class AdminSteps(BaseSteps):
    # Создаём пользователя и регистрируем его для удаления после теста.
    def create_user(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_ok()
        ).post(create_user_request)

        # Регистрируем созданного пользователя для очистки фикстурой.
        self.created_obj.append(response)
        return response

    # Удаляем пользователя через API с правами администратора.
    def delete_user(self, user_id: int):
        CrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_DELETE_USER,
            ResponseSpecs.request_ok()
        ).delete(user_id)

    # Отправляем некорректные данные пользователя и ожидаем отказ 400.
    def create_invalid_user(self, create_user_request: CreateUserRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_bad()
        ).post(create_user_request)

    # Получаем токен и данные пользователя после успешного входа.
    def login_user(self, login_user_request: LoginUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_ok()
        ).post(login_user_request)
        return response
