# История кредитов пользователя; отдельные записи представлены словарями.
from src.main.api.models.base_model import BaseModel


class CreditHistoryResponse(BaseModel):
    userId: int
    credits: list[dict]