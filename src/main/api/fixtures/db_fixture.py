# Фикстура сессии БД для проверки сохранённых данных.
import pytest
from src.main.api.db.engine import SessionLocal, engine


# Выдаём тесту сессию БД внутри отдельной транзакции.
@pytest.fixture(scope="function")
def db_session():
    # Открываем соединение и транзакцию для SQL-запросов текущего теста.
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        # Передаём сессию тесту; после его завершения выполняется finally.
        yield session
    finally:
        session.close()
        # Откатываем SQL-изменения этой транзакции; API использует отдельные транзакции.
        transaction.rollback()
        connection.close()