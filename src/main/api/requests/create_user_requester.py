# Отдельный requester для создания пользователя администратором.
from http import HTTPStatus
import requests
from requests import Response
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.response_model.create_user_response import CreateUserResponse
from src.main.api.requests.requester import Requester


class CreateUserRequester(Requester):
    def post(self, create_user_request: CreateUserRequest) -> CreateUserResponse | Response:
        url = f"{self.base_url}/admin/create"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url=url,
            json=create_user_request.model_dump(),
            headers = self.headers
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return CreateUserResponse(**response.json())
        return response
