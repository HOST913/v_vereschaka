# Отдельный requester для входа пользователя.
import requests
from requests import Response

from src.main.api.models.request_model.login_user_request import LoginUserRequest
from src.main.api.models.response_model.login_user_response import LoginUserResponse
from src.main.api.requests.requester import Requester


class LoginUserRequester(Requester):
    def post(self, login_user_request: LoginUserRequest) -> LoginUserResponse | Response:

        url = f"{self.base_url}/auth/token/login"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url=url,
            json=login_user_request.model_dump(),
            headers=self.headers
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        return LoginUserResponse(**response.json())


