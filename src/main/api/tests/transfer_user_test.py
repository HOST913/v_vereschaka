# Проверки перевода между двумя счетами и отказа для суммы ниже минимума.
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.request_model.create_user_request import CreateUserRequest
from src.main.api.models.request_model.deposit_user_request import DepositUserRequest
from src.main.api.models.request_model.transfer_user_request import TransferUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.mark.api
class TestTransferUser:
    # Переводим 500 и проверяем оба счёта и записи в истории API.
    def test_transfer_user_valid(self,db_session: Session,api_manager: ApiManager, create_user_request: CreateUserRequest):
        # Используем отправителя, созданного фикстурой
        from_user_request = create_user_request

        # Создаём отдельного пользователя для получения перевода
        to_user_request = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(to_user_request)

        # Создаём счёт отправителя
        from_account = api_manager.user_steps.create_account(from_user_request)
        from_account_id = from_account.id

        # Создаём счёт получателя
        to_account = api_manager.user_steps.create_account(to_user_request)
        to_account_id = to_account.id



        # Пополняем счёт отправителя на 3000
        deposit_request = DepositUserRequest(accountId=from_account.id,amount=3000)
        deposit_response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_request, create_user_request=from_user_request)
        assert deposit_response.balance == 3000

        # Пополняем счёт получателя на 1000
        deposit_request = DepositUserRequest(accountId=to_account.id,amount=1000)
        deposit_response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_request, create_user_request=to_user_request)
        assert deposit_response.balance == 1000

        # Переводим 500 со счёта отправителя получателю
        transfer_request = TransferUserRequest(fromAccountId=from_account.id, toAccountId=to_account.id, amount=500)
        transfer_response = api_manager.user_steps.account_transfer(transfer_user_request=transfer_request, create_user_request=from_user_request)
        assert transfer_response.fromAccountIdBalance == 2500
        assert transfer_response.fromAccountId == from_account.id
        assert transfer_response.toAccountId == to_account.id




        # Читаем актуальный баланс отправителя после перевода
        from_balance = api_manager.user_steps.get_account(account_id=from_account_id,create_user_request=create_user_request)
        account_balance_from = from_balance.balance


        # Получаем историю и баланс получателя
        to_balance = api_manager.user_steps.get_account(account_id=to_account_id,create_user_request=to_user_request)
        account_balance_to = to_balance.balance

        # Проверяем ожидаемые остатки на обоих счетах после перевода.
        assert account_balance_from == 2500
        assert account_balance_to == 1500

        # Ищем исходящий перевод в истории отправителя
        transfer_out = None
        for transaction in from_balance.transactions:
            if transaction["type"] == "transfer_out":
                transfer_out = transaction
                break

        # Проверяем счета перевода и отрицательную сумму списания в истории отправителя.
        assert transfer_out is not None, 'Исходящий перевод не найден в истории'
        assert transfer_out["fromAccountId"] == from_account_id
        assert transfer_out["toAccountId"] == to_account_id
        assert transfer_out["amount"] == -transfer_request.amount


        # Ищем входящий перевод в истории получателя
        transfer_to = None
        for transaction in to_balance.transactions:
            if transaction["type"] == "transfer_in":
                transfer_to = transaction
                break

        # Проверяем счета перевода и положительную сумму зачисления в истории получателя.
        assert transfer_to is not None, 'Входящий перевод не найден в истории'
        assert transfer_to["fromAccountId"] == from_account_id
        assert transfer_to["toAccountId"] == to_account_id
        assert transfer_to["amount"] == transfer_request.amount

        # Убеждаемся, что в обеих историях показана одна и та же операция.
        assert transfer_out["transactionId"] == transfer_to["transactionId"], 'В историях найдены разные переводы'



        # Сверяем ID и остаток счёта отправителя в БД после успешного перевода.
        account_from_db = Account.get_account_by_id(db_session, from_account_id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.id == from_account_id, 'Аккаунт не создан id аккаунта нет в бд'
        assert account_from_db.balance == 2500, 'Поле баланса для созданого отсудтвует в бд'

        # Сверяем ID и остаток счёта получателя в БД после успешного перевода.
        account_from_db = Account.get_account_by_id(db_session, to_account_id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.id == to_account_id, 'Аккаунт не создан id аккаунта нет в бд'
        assert account_from_db.balance == 1500, 'Поле баланса для созданого отсудтвует в бд'




    # Проверяем отказ при переводе 499 и сохранность денег на обоих счетах.
    def test_deposit_user_with_invalid(self,db_session: Session,api_manager: ApiManager, create_user_request: CreateUserRequest):
        # Используем отправителя, созданного фикстурой
        from_user_request = create_user_request

        # Создаём отдельного пользователя для получения перевода
        to_user_request = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(to_user_request)

        # Создаём счёт отправителя
        from_account = api_manager.user_steps.create_account(from_user_request)
        from_account_id = from_account.id

        # Создаём счёт получателя
        to_account = api_manager.user_steps.create_account(to_user_request)
        to_account_id = to_account.id



        # Пополняем счёт отправителя на 3000
        deposit_request = DepositUserRequest(accountId=from_account.id,amount=3000)
        deposit_response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_request, create_user_request=from_user_request)
        assert deposit_response.balance == 3000

        # Пополняем счёт получателя на 1000
        deposit_request = DepositUserRequest(accountId=to_account.id,amount=1000)
        deposit_response = api_manager.user_steps.account_deposit(deposit_user_request=deposit_request, create_user_request=to_user_request)
        assert deposit_response.balance == 1000


        # Пытаемся перевести 499 и ожидаем отказ 400
        transfer_request = TransferUserRequest(fromAccountId=from_account.id, toAccountId=to_account.id, amount=499)
        transfer_response = api_manager.user_steps.account_transfer_invalid(transfer_user_request=transfer_request, create_user_request=from_user_request)

        # Читаем актуальный баланс отправителя после отказа
        from_balance = api_manager.user_steps.get_account(account_id=from_account_id,create_user_request=create_user_request)
        account_balance_from = from_balance.balance

        # Читаем актуальный баланс получателя после отказа
        from_balance = api_manager.user_steps.get_account(account_id=to_account_id,create_user_request=to_user_request)
        account_balance_to = from_balance.balance

        # Проверяем сохранность обоих балансов после отклонённого перевода.
        assert account_balance_from == 3000
        assert account_balance_to == 1000

        # Сверяем ID и неизменный остаток отправителя в БД после отказа.
        account_from_db = Account.get_account_by_id(db_session, from_account_id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.id == from_account_id, 'Аккаунт не создан id аккаунта нет в бд'
        assert account_from_db.balance == 3000, 'Поле баланса для созданого отсудтвует в бд'

        # Сверяем ID и неизменный остаток получателя в БД после отказа.
        account_from_db = Account.get_account_by_id(db_session, to_account_id)
        assert account_from_db is not None, 'Счёт не найден в БД'
        assert account_from_db.id == to_account_id, 'Аккаунт не создан id аккаунта нет в бд'
        assert account_from_db.balance == 1000, 'Поле баланса для созданого отсудтвует в бд'

