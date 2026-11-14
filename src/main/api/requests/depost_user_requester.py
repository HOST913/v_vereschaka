# Отдельный requester для пополнения банковского счёта.
from http import HTTPStatus
import requests
from src.main.api.models.response_model.deposit_user_response import DepositUserResponse
from src.main.api.requests.requester import Requester
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest


class DepostUserRequester(Requester):
    def post(self, deposit_user_requester: DepositUserRequest):
        url = f"{self.base_url}/account/deposit"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url = url,
            json = deposit_user_requester.model_dump(),
            headers = self.headers
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return DepositUserResponse(**response.json())
        return response