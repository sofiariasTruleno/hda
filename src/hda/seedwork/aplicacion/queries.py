"""Lado de LECTURA del patron CQS.

Una query no muta estado. Que sea un camino separado del de comandos es lo
que permite, mas adelante, escalar lecturas de forma independiente o
apuntarlas a una proyeccion distinta sin tocar el modelo de escritura.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatch
from typing import Any


@dataclass(frozen=True)
class Query:
    ...


@dataclass
class QueryResultado:
    resultado: Any


class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> QueryResultado:
        ...


@singledispatch
def ejecutar_query(query) -> QueryResultado:
    raise NotImplementedError(
        f"No existe implementacion para la query {type(query).__name__}"
    )
