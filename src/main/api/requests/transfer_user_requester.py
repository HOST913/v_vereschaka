# Отдельный requester для перевода между банковскими счетами.
from http import HTTPStatus

from src.main.api.models.request_model.transfer_user_request import TransferUserRequest
from src.main.api.models.response_model.transfer_user_response import TransferUserResponse
from src.main.api.requests.requester import Requester
import requests


class TransferUserRequester(Requester):
    def post(self, transfer_user_requester: TransferUserRequest):
        url = f"{self.base_url}/account/transfer"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url=url,
            json = transfer_user_requester.model_dump(),
            headers = self.headers
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return TransferUserResponse(**response.json())
        return response
