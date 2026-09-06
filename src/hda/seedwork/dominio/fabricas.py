"""Fabricas de dominio.

Se usan cuando construir un objeto valido implica mas que asignar campos:
validar varias invariantes a la vez, o traducir entre representaciones sin
que el dominio conozca la infraestructura.
"""
from abc import ABC, abstractmethod


class Fabrica(ABC):
    @abstractmethod
    def crear_objeto(self, obj, mapeador=None):
        ...
