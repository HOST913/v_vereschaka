# Проверки создания счёта через API и его сохранения в БД.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.request_model.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateAccount:
    # Создаём новый счёт и сверяем его данные с БД.
    def test_create_account(self, db_session: Session, api_manager: ApiManager, create_user_request: CreateUserRequest):
        # Создаём банковский счёт пользователя.
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0, f'Баланс нового счёта по API должен быть 0, получен {response.balance}'

        # Сверяем созданный счёт с сохранённой записью БД.
        account_from_db = Account.get_account_by_id(db_session, response.id)
        assert account_from_db.id == response.id, f'ID счёта в БД не совпадает с ответом API: ожидался {response.id}, получен {account_from_db.id}'
        assert account_from_db.balance is not None, f'У созданного счёта {response.id} не заполнен баланс в БД'