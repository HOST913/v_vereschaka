from src.main.api.models.base_model import BaseModel


# Данные платежа по кредиту: кредит, счёт списания и сумма.
class CreditUserRepayRequest(BaseModel):
    creditId: int
    accountId: int
    amount: int