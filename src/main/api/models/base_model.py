# Общая основа Pydantic-моделей запросов и ответов проекта.
from pydantic import BaseModel as BM


class BaseModel(BM):
    ...