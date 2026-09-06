"""Puerto de persistencia del modulo Trabajos.

Interfaz abstracta. Vive en el dominio y la implementa infraestructura.
El dominio declara que necesita guardar y buscar Trabajos; no sabe si detras
hay SQLite, PostgreSQL o un mock de pruebas.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from hda.seedwork.dominio.repositorios import Repositorio


class RepositorioTrabajos(Repositorio, ABC):
    @abstractmethod
    def obtener_por_id(self, id: UUID):
        ...

    @abstractmethod
    def obtener_todos(self) -> list:
        ...

    @abstractmethod
    def obtener_por_estado(self, estado: str) -> list:
        ...

    @abstractmethod
    def obtener_por_mercado(self, mercado_id: str) -> list:
        ...

    @abstractmethod
    def agregar(self, trabajo):
        ...

    @abstractmethod
    def actualizar(self, trabajo):
        ...

    @abstractmethod
    def eliminar(self, id: UUID):
        ...
