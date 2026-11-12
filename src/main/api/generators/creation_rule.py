# Правило генерации значения поля по регулярному выражению.
from dataclasses import dataclass


@dataclass
class CreationRule:
    regex: str