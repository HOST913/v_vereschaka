# Генерация моделей со случайными значениями по типам и правилам полей.
import uuid
import random
import rstr
from typing import Any, get_type_hints, Annotated, get_origin, get_args

from src.main.api.generators.creation_rule import CreationRule


class RandomModelGenerator:
    # Генерируем значения полей и создаём экземпляр запрошенной модели.
    @staticmethod
    def generate(cls: type) -> Any:
        # Получаем типы полей вместе с дополнительными правилами Annotated.
        type_hints = get_type_hints(cls, include_extras=True)
        init_data = {}

        for field_name, annotated_type in type_hints.items():
            rule = None
            actual_type = annotated_type

            # Отделяем основной тип поля от метаданных генерации.
            if get_origin(actual_type) is Annotated:
                actual_type, *annotations = get_args(actual_type)

                for ann in annotations:
                    if isinstance(ann, CreationRule):
                        rule = ann

            # Используем шаблон поля либо генерацию по его типу.
            if rule is not None:
                value = RandomModelGenerator._generate_from_regex(
                    rule.regex, actual_type
                )
            else:
                value = RandomModelGenerator._generate_value(actual_type)

            init_data[field_name] = value

        # Собираем модель из сгенерированных значений всех полей.
        return cls(**init_data)

    # Генерируем значение по шаблону и при необходимости преобразуем в число.
    @staticmethod
    def _generate_from_regex(regex: str, field_type: type) -> Any:
        generated = rstr.xeger(regex)
        if field_type is int:
            return int(generated)
        if field_type is float:
            return float(generated)
        return generated

    # Выбираем значение по типу поля или создаём вложенную модель.
    @staticmethod
    def _generate_value(field_type: type) -> Any:
        if field_type is str:
            return str(uuid.uuid4())[:8]
        elif field_type is int:
            return random.randint(1, 9999)
        elif field_type is float:
            return round(random.uniform(0, 100.), 2)
        elif field_type is bool:
            return random.choice([True, False])
        elif field_type is list:
            return [str(uuid.uuid4())[:5]]
        elif isinstance(field_type, type):
            return RandomModelGenerator.generate(field_type)
        return None







