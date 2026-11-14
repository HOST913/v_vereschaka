# Подключаем фикстуру менеджера API-шагов.
from src.main.api.fixtures.api_fixture import *
# Подключаем сбор созданных объектов и очистку пользователей.
from src.main.api.fixtures.object_fixture import *
# Подключаем подготовку обычного и кредитного пользователей.
from src.main.api.fixtures.user_fixture import *
# Подключаем сессию БД для проверок сохранённых данных.
from src.main.api.fixtures.db_fixture import *
# Подключаем подготовку счетов и заявок для тестов операций.
from src.main.api.fixtures.operation_fixture import *
