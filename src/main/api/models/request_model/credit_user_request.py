from src.main.api.models.base_model import BaseModel

# Данные заявки на кредит: счёт, сумма и срок в месяцах.
class CreditUserRequest(BaseModel):
    accountId: int
    amount: int
    termMonths: int

