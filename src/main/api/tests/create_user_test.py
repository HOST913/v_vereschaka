# Проверки создания пользователя и отказа для некорректных данных.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.db.crud.user_crud import UserCrudDb as User



@pytest.mark.api
class TestCreateUser():
    # Проверяем успешное создание пользователя и его наличие в БД.
    @pytest.mark.parametrize(
        "create_user_request",
        [
            (RandomModelGenerator.generate(CreateUserRequest))
        ]
    )
    def test_create_user_valid(self, api_manager: ApiManager, create_user_request: CreateUserRequest, db_session: Session):
        # Создаём пользователя через административный API.
        response = api_manager.admin_steps.create_user(create_user_request)


        # Сверяем имя и роль созданного пользователя с запросом.
        assert create_user_request.username == response.username
        assert create_user_request.role == response.role

        # Проверяем, что пользователь сохранён в БД.
        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db.username == create_user_request.username, 'Созданного пользователя нет в бд'

    # Проверяем отказ в создании пользователя с некорректными данными.
    @pytest.mark.parametrize(
        "username,password",
        [
            ("абв", "Pas!sw0rd"),
            ("ab", "Pas!sw0rd"),
            ("abv!", "Pas!sw0rd"),
            ("Maxx1", "Pas!sw0rд"),
            ("Maxx2", "Pas!sw0"),
            ("Maxx3", "pas!sw0rd"),
            ("Maxx4", "PAS!SW0RD"),
            ("Maxx5", "Passw0rd"),
            ("Maxx6", "Pas!sword"),
        ]
    )
    def test_create_user_invalid(self,db_session: Session, username: str, password: str, api_manager: ApiManager):
        # Готовим некорректные данные из текущего набора параметров.
        create_user_request = CreateUserRequest(username = username, password=password, role = "ROLE_USER")
        api_manager.admin_steps.create_invalid_user(create_user_request)

        # Проверяем отсутствие пользователя после отклонённого запроса.
        user_from_db = User.get_user_by_username(db_session, create_user_request.username)

        assert user_from_db is None, 'Пользователь создан Ошибка'






