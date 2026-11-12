# Ответ с данными счёта, текущим балансом и историей его операций.
from src.main.api.models.base_model import BaseModel


class AccountTransactionsResponse(BaseModel):
    id: int
    number: str
    balance: float
    transactions: list[dict]