"""Reglas de negocio explicitas.

Cada invariante del dominio se modela como un objeto y no como un `if`
suelto dentro de un metodo. Esto permite nombrarla, probarla en aislamiento
y reportarla con un mensaje de negocio y no tecnico.
"""
from abc import ABC, abstractmethod


class ReglaNegocio(ABC):
    __mensaje: str = "La regla de negocio no se cumple"

    def __init__(self, mensaje: str | None = None):
        if mensaje:
            self.__mensaje = mensaje

    def mensaje(self) -> str:
        return self.__mensaje

    @abstractmethod
    def es_valido(self) -> bool:
        ...

    def __str__(self) -> str:
        return f"{self.__class__.__name__} - {self.__mensaje}"


class ReglaCompuesta(ReglaNegocio):
    """Permite componer varias reglas y evaluarlas como una sola."""

    def __init__(self, reglas: list[ReglaNegocio], mensaje: str | None = None):
        self.reglas = reglas
        super().__init__(mensaje or "Al menos una regla compuesta no se cumple")

    def es_valido(self) -> bool:
        return all(regla.es_valido() for regla in self.reglas)
