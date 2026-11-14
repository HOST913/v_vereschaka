# Отдельный requester для создания банковского счёта.
import requests

from src.main.api.models.response_model.create_account_response import CreateAccountResponse
from src.main.api.requests.requester import Requester


class CreateAccountRequester(Requester):
    def post(self, model = None) -> CreateAccountResponse:
        url = f"{self.base_url}/account/create"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url=url,
            headers=self.headers,
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        return CreateAccountResponse(**response.json())