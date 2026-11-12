# HTTP-запросы к API, вложения Allure и проверка ожидаемого ответа.
from typing import Optional
import allure

import requests
from requests import Response

from src.main.api.configs.config import Config
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.models.base_model import BaseModel



class CrudRequester(HttpRequester):
    # Отправляем POST с данными модели и проверяем ожидаемый HTTP-ответ.
    def post(self, model: Optional[BaseModel]) -> Response:
        # Готовим JSON-данные из модели запроса.
        body = model.model_dump() if model is not None else ""

        # Добавляем описание запроса и вложение в отчёт Allure.
        with allure.step(f"POST{Config.fetch("backendUrl")}{self.endpoint.value.url}"):
            allure.attach(str(body), "Request bode", allure.attachment_type.JSON)

        response = requests.post(
            url = f"{Config.fetch("backendUrl")}{self.endpoint.value.url}",
            headers = self.request_spec,
            json = body,
        )

        # Прикрепляем тело полученного HTTP-ответа к отчёту.
        allure.attach(
            response.text,
            "Response body",
            allure.attachment_type.JSON
        )

        # Проверяем HTTP-статус согласно переданной спецификации.
        self.response_spec(response)
        return response


    # Удаляем запись по идентификатору, добавленному к пути endpoint.
    def delete(self, user_id: int) -> Response:
        # Добавляем описание запроса и вложение в отчёт Allure.
        with allure.step(f"DELETE{Config.fetch("backendUrl")}{self.endpoint.value.url}"):
            allure.attach(str(user_id), "Request bode", allure.attachment_type.JSON)

        response = requests.delete(
            url = f"{Config.fetch("backendUrl")}{self.endpoint.value.url}/{user_id}",
            headers = self.request_spec,
        )

        # Прикрепляем тело полученного HTTP-ответа к отчёту.
        allure.attach(
            response.text,
            "Response body",
            allure.attachment_type.JSON
        )
        # Проверяем HTTP-статус согласно переданной спецификации.
        self.response_spec(response)
        return response

    # Читаем запись или её историю по идентификатору в пути запроса.
    def get(self, user_id: int) -> Response:
        # Добавляем описание запроса и вложение в отчёт Allure.
        with allure.step(f"GET{Config.fetch("backendUrl")}{self.endpoint.value.url}"):
            allure.attach(str(user_id), "Request bode", allure.attachment_type.JSON)

        response = requests.get(
            url = f"{Config.fetch("backendUrl")}{self.endpoint.value.url}/{user_id}",
            headers = self.request_spec,
        )

        # Прикрепляем тело полученного HTTP-ответа к отчёту.
        allure.attach(
            response.text,
            "Response body",
            allure.attachment_type.JSON
        )
        # Проверяем HTTP-статус согласно переданной спецификации.
        self.response_spec(response)
        return response

    # Выполняем GET по пути endpoint без дополнительного идентификатора.
    def get_all(self) -> Response:
        # Добавляем описание запроса и вложение в отчёт Allure.
        with allure.step(f"GETALL{Config.fetch("backendUrl")}{self.endpoint.value.url}"):
            allure.attach(str(), "Request bode", allure.attachment_type.JSON)

        response = requests.get(
            url = f"{Config.fetch("backendUrl")}{self.endpoint.value.url}",
            headers = self.request_spec,
        )

        # Прикрепляем тело полученного HTTP-ответа к отчёту.
        allure.attach(
            response.text,
            "Response body",
            allure.attachment_type.JSON
        )
        # Проверяем HTTP-статус согласно переданной спецификации.
        self.response_spec(response)
        return response