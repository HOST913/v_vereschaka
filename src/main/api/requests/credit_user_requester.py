# Отдельный requester для подачи заявки на кредит.
from http import HTTPStatus

from src.main.api.models.request_model.credit_user_request import CreditUserRequest
from src.main.api.models.response_model.credit_user_response import CreditUserResponse
from src.main.api.requests.requester import Requester
import requests


class CreditUserRequester(Requester):
    def post(self, credit_user_requester: CreditUserRequest):
        url = f"{self.base_url}/credit/request"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url=url,
            json=credit_user_requester.model_dump(),
            headers=self.headers
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        if response.status_code == HTTPStatus.CREATED:
            return CreditUserResponse(**response.json())
        return response
