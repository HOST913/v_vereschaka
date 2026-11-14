from src.main.api.models.base_model import BaseModel

# Данные перевода: счёт отправителя, счёт получателя и сумма.
class TransferUserRequest(BaseModel):
    fromAccountId: int
    toAccountId: int
    amount: float