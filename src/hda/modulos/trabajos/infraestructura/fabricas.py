"""Fabrica de adaptadores de infraestructura.

Es el punto unico donde se decide que implementacion concreta se inyecta.
Cambiar de SQLAlchemy a otra tecnologia toca solo este archivo, no los
handlers.
"""
from hda.config.uow import UnidadTrabajoSQLAlchemy

from .repositorios import RepositorioTrabajosLectura, RepositorioTrabajosSQLAlchemy


class FabricaRepositorio:

    def crear_uow(self) -> UnidadTrabajoSQLAlchemy:
        return UnidadTrabajoSQLAlchemy()

    def crear_repositorio(self, uow=None) -> RepositorioTrabajosSQLAlchemy:
        session = uow.session if uow else None
        return RepositorioTrabajosSQLAlchemy(session)

    def crear_repositorio_lectura(self) -> RepositorioTrabajosLectura:
        return RepositorioTrabajosLectura()
