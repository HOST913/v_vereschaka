# Чтение общих настроек проекта из файла urls.properties.
from pathlib import Path
from typing import Any


class Config:
    _isinstance = None
    _dictionary = {}

    # При первом обращении читаем файл, затем используем сохранённый экземпляр.
    def __new__(cls):
        if cls._isinstance is None:
            cls._isinstance = super(Config, cls).__new__(cls)

            # Находим файл настроек относительно расположения config.py.
            config_path = Path(__file__).parents[4] / 'resources' / 'urls.properties'

            if not config_path.exists():
                raise FileNotFoundError(f"Config path not found: {config_path}")
            # Читаем строки настроек и сохраняем пары ключей и значений.
            with open(config_path, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.split("=")
                        cls._dictionary[key] = value.strip()

        return cls._isinstance

    # Возвращаем настройку по ключу или переданное значение по умолчанию.
    @staticmethod
    def fetch(key: str, default_value: Any = None) -> Any:
        return Config()._dictionary.get(key, default_value)

