# Ответ на выдачу кредита с его параметрами и балансом банковского счёта.
from src.main.api.models.base_model import BaseModel


class CreditUserResponse(BaseModel):
    # ID банковского счёта, на который выдан кредит.
    id: int
    amount: int
    termMonths: int
    # Денежный баланс банковского счёта после выдачи кредита.
    balance: int
    # Собственный ID выданного кредита для истории и погашения.
    creditId: int
