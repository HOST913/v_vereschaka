import random




class OperationDataGenerator:
    # Сохраняем точные параметры заявки из ТЗ.
    @staticmethod
    def credit_data():
        return {
            "amount": 5000,
            "termMonths": 12
        }

    # Проверяем минимальную сумму пополнения и значение на единицу ниже неё.
    @staticmethod
    def deposit_data():
        return {
            "amount": 1000,
            "invalid_amount": 999
        }

    # Сохраняем начальные балансы и граничные суммы перевода из ТЗ.
    @staticmethod
    def transfer_data():
        return {
            "from_balance": 3000,
            "to_balance": 1000,
            "amount": 500,
            "invalid_amount": 499
        }

    # Для погашения выбираем кредит, сумму которого можно также внести пополнением.
    # Сумма кредита: 5000–9000; допустимый срок: 1–60 месяцев.
    @staticmethod
    def random_credit_data():
        return {
            "amount": random.randint(5000, 9000),
            "termMonths": random.randint(1, 60)
        }
