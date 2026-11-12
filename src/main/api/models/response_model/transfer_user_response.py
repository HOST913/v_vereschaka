# Ответ с ID обоих счетов и балансом отправителя после перевода.
from src.main.api.models.base_model import BaseModel


class TransferUserResponse(BaseModel):
    fromAccountId: int
    toAccountId: int
    fromAccountIdBalance: float