from src.main.api.models.base_model import BaseModel

# Данные пополнения: идентификатор банковского счёта и сумма.
class DepositUserRequest(BaseModel):
    accountId: int
    amount: float