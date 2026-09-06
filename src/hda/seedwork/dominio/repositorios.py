"""Puertos de persistencia y unidad de trabajo.

Estas son INTERFACES y viven en el dominio. Las implementaciones viven en
infraestructura. Esa inversion de dependencias es el nucleo de la
arquitectura hexagonal: el dominio declara lo que necesita, la
infraestructura se adapta.
"""
from abc import ABC, abstractmethod
from uuid import UUID


class Repositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID):
        ...

    @abstractmethod
    def obtener_todos(self) -> list:
        ...

    @abstractmethod
    def agregar(self, entidad):
        ...

    @abstractmethod
    def actualizar(self, entidad):
        ...

    @abstractmethod
    def eliminar(self, id: UUID):
        ...


class Mapeador(ABC):
    """Traduce entre el modelo de dominio y una representacion externa."""

    @abstractmethod
    def obtener_tipo(self) -> type:
        ...

    @abstractmethod
    def entidad_a_dto(self, entidad):
        ...

    @abstractmethod
    def dto_a_entidad(self, dto):
        ...
