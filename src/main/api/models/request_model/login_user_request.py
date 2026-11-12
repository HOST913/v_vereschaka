# Учётные данные для входа и получения токена.
from src.main.api.models.base_model import BaseModel

class LoginUserRequest(BaseModel):
    username: str
    password: str