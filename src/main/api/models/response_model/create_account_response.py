# Модель ответа на создание банковского счёта.
from src.main.api.models.base_model import BaseModel


class CreateAccountResponse(BaseModel):
    id: int
    number: int
    balance: float