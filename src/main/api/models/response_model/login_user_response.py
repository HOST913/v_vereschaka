# Модели ответа авторизации: токен и данные вошедшего пользователя.
from src.main.api.models.base_model import BaseModel


class User(BaseModel):
    username: str
    role: str

class LoginUserResponse(BaseModel):
    token: str
    user: User
