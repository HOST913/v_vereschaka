# Передача шагам общего списка объектов для последующей очистки.
from typing import List, Any


class BaseSteps:
    # Сохраняем общий список объектов, созданных во время теста.
    def __init__(self, created_obj: List[Any]):
        self.created_obj = created_obj