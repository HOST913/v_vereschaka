# Проверки входа администратора и обычного пользователя.
import pytest
from src.main.api.models.request_model.login_user_request import LoginUserRequest




@pytest.mark.api
class TestUserLogin:
    # Проверяем вход администратора и его роль в ответе.
    def test_login_admin(self, api_manager):
        # Готовим данные администратора для входа.
        login_user_request = LoginUserRequest(username="admin", password="123456")
        # Выполняем вход и получаем данные пользователя.
        response = api_manager.admin_steps.login_user(login_user_request)

        # Проверяем имя вошедшего пользователя и административную роль.
        assert login_user_request.username == response.user.username
        assert response.user.role == "ROLE_ADMIN"

    # Проверяем вход созданного пользователя и его обычную роль.
    def test_login_user(self, api_manager, create_user_request):
        # Выполняем вход пользователем, созданным фикстурой.
        response = api_manager.admin_steps.login_user(create_user_request)

        # Проверяем имя вошедшего пользователя и роль ROLE_USER.
        assert create_user_request.username == response.user.username
        assert response.user.role == "ROLE_USER"

