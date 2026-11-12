# Учёт созданных объектов и очистка пользователей после теста.
import logging
from typing import Any, List
import pytest
from pygments.lexers import clean
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.response_model.create_user_response import CreateUserResponse


# Собираем созданные объекты и запускаем очистку после теста.
@pytest.fixture
def created_obj():
    # Создаём отдельный список объектов для очистки после текущего теста.
    objects: List[Any] = []
    yield objects
    # После теста удаляем зарегистрированных пользователей через API.
    clean_user(objects)

# Удаляем пользователей, зарегистрированных в списке созданных объектов.
def clean_user(object: List[Any]):
    api_manager = ApiManager(object)
    for u in object:
        if isinstance(u, CreateUserResponse):
            api_manager.admin_steps.delete_user(u.id)
        else:
            logging.warning(f"Error in deleting user_id: {u.id}")