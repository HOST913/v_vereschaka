# Формирование заголовков запросов с авторизацией и без неё.
import requests

from src.main.api.configs.config import Config
from src.main.api.models.request_model.login_user_request import LoginUserRequest
from src.main.api.models.response_model.login_user_response import LoginUserResponse


class RequestSpecs:
    # Задаём заголовки обмена данными в формате JSON.
    @staticmethod
    def base_headers():
        return {
            "Content-Type": "application/json",
            "accept": "application/json"
        }

    # Входим под указанным пользователем и формируем заголовок Bearer-токена.
    @staticmethod
    def auth_headers(username: str, password: str):
        # Готовим учётные данные для получения токена.
        request = LoginUserRequest(username=username, password=password)
        response = requests.post(
            url = "http://localhost:4111/api/auth/token/login",
            json=request.model_dump(),
            headers=RequestSpecs.base_headers()
        )
        if response.status_code == 200:
            response_data = LoginUserResponse(**response.json())
            token = response_data.token
            headers = RequestSpecs.base_headers()
            # Передаём полученный токен в заголовке авторизации.
            headers["Authorization"] = f"Bearer {token}"
            return headers

        raise Exception("Failed to login")

    # Возвращаем JSON-заголовки для запроса без токена.
    @staticmethod
    def unauth_headers():
        return RequestSpecs.base_headers()
