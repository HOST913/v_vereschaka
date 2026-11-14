# Ответ с ID кредита и суммой принятого платежа.
from src.main.api.models.base_model import BaseModel


class RepayUserCreditResponse(BaseModel):
    creditId: int
    amountDeposited: int