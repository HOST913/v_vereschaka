# Фикстура менеджера API-шагов для текущего теста.
import pytest

from src.main.api.classes.api_manager import ApiManager


# Создаём менеджер API-шагов со списком объектов для очистки.
@pytest.fixture
def api_manager(created_obj):
    return ApiManager(created_obj)