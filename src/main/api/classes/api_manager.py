# Менеджер шагов администратора и пользователя для API-тестов.
from typing import List, Any

from src.main.api.steps.admin_steps import AdminSteps
from src.main.api.steps.user_steps import UserSteps


class ApiManager:
    # Передаём обоим наборам шагов один список созданных объектов.
    def __init__(self, created_obj: List[Any]):
        self.admin_steps = AdminSteps(created_obj)
        self.user_steps = UserSteps(created_obj)