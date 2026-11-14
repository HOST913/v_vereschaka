# Проверки ожидаемых HTTP-статусов ответов API.
from requests import Response
from http import HTTPStatus



class ResponseSpecs:
    # Ожидаем HTTP 200: успешное выполнение запроса.
    @staticmethod
    def request_ok():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.OK, f'Ожидался HTTP {HTTPStatus.OK.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm

    # Ожидаем HTTP 201: успешное создание ресурса.
    @staticmethod
    def request_created():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.CREATED, f'Ожидался HTTP {HTTPStatus.CREATED.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm

    # Ожидаем HTTP 400: отказ из-за некорректного запроса.
    @staticmethod
    def request_bad():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, f'Ожидался HTTP {HTTPStatus.BAD_REQUEST.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm

    # Ожидаем HTTP 403: отказ из-за отсутствия прав.
    @staticmethod
    def request_forbidden():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.FORBIDDEN, f'Ожидался HTTP {HTTPStatus.FORBIDDEN.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm

    # Ожидаем HTTP 404: отсутствие запрошенного ресурса.
    @staticmethod
    def request_not_found():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.NOT_FOUND, f'Ожидался HTTP {HTTPStatus.NOT_FOUND.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm

    # Ожидаем HTTP 409: конфликт с текущим состоянием ресурса.
    @staticmethod
    def request_conflict():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.CONFLICT, f'Ожидался HTTP {HTTPStatus.CONFLICT.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm
    
    # Ожидаем HTTP 422: отказ при обработке переданных данных.
    @staticmethod
    def request_unprocessable():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, f'Ожидался HTTP {HTTPStatus.UNPROCESSABLE_ENTITY.value}, получен {response.status_code}. Тело ответа: {response.text}'
        return confirm


