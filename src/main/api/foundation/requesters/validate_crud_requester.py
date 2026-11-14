# Преобразование JSON-ответа CrudRequester в модель выбранного endpoint.
from typing import Optional
import allure

from src.main.api.configs.config import Config
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.models.base_model import BaseModel


class ValidateCrudRequester(HttpRequester):
    # Создаём HTTP-requester с теми же настройками и проверкой ответа.
    def __init__(self, request_spec, endpoint, response_spec):
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec = request_spec,
            endpoint = endpoint,
            response_spec = response_spec
        )

    # Преобразуем ответ POST в модель выбранного endpoint.
    def post(self, model: Optional[BaseModel] = None) -> BaseModel:
        response = self.crud_requester.post(model)
        with allure.step(f"POST{Config.fetch("backendUrl")}{self.endpoint.value.url} and Validated Model"):
            allure.attach(f"Validated Model response: {self.endpoint.value.response_model.__name__}")


        self.response_spec(response)
        # Проверяем JSON по структуре модели ответа и возвращаем модель.
        return self.endpoint.value.response_model.model_validate(response.json())

    # Преобразуем ответ DELETE согласно модели ответа endpoint.
    def delete(self, user_id: int):
        response = self.crud_requester.delete(user_id)
        with allure.step(f"DELETE {Config.fetch("backendUrl")}{self.endpoint.value.url} and Validated Model"):
            allure.attach(f"Validated Model response: {self.endpoint.value.response_model.__name__}")


        self.response_spec(response)
        # Проверяем JSON по структуре модели ответа и возвращаем модель.
        return self.endpoint.value.response_model.model_validate(response.json())

    # Преобразуем ответ GET для записи в модель endpoint.
    def get(self, user_id: int) -> BaseModel:
        response = self.crud_requester.get(user_id)
        with allure.step(f"GET {Config.fetch("backendUrl")}{self.endpoint.value.url} and Validated Model"):
            allure.attach(f"Validated Model response: {self.endpoint.value.response_model.__name__}")

        self.response_spec(response)
        # Проверяем JSON по структуре модели ответа и возвращаем модель.
        return self.endpoint.value.response_model.model_validate(response.json())

    # Преобразуем ответ GET по общему пути в модель endpoint.
    def get_all(self) -> BaseModel:
        response = self.crud_requester.get_all()
        with allure.step(f"GETALL {Config.fetch("backendUrl")}{self.endpoint.value.url} and Validated Model"):
            allure.attach(f"Validated Model response: {self.endpoint.value.response_model.__name__}")


        self.response_spec(response)
        # Проверяем JSON по структуре модели ответа и возвращаем модель.
        return self.endpoint.value.response_model.model_validate(response.json())