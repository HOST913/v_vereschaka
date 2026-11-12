# Отдельный requester для погашения кредита.
from http import HTTPStatus

from src.main.api.models.request_model.repay_user_credit_request import CreditUserRepayRequest
from src.main.api.models.response_model.repay_user_credit_response import RepayUserCreditResponse
from src.main.api.requests.requester import Requester
import requests

class RepayCreditUserRequester(Requester):
    def post(self, repay_credit_user_requester: CreditUserRepayRequest):
        url = f"{self.base_url}/credit/repay"
        # Выполняем HTTP-запрос к выбранной операции API.
        response = requests.post(
            url=url,
            json=repay_credit_user_requester.model_dump(),
            headers = self.headers
        )
        # Проверяем HTTP-ответ по переданной спецификации.
        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return RepayUserCreditResponse(**response.json())
        return response
