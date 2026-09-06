"""Adaptadores de persistencia del modulo Trabajos.

Implementan el puerto RepositorioTrabajos declarado en el dominio.

Hay DOS implementaciones sobre la misma base de datos y eso es deliberado:
- RepositorioTrabajosSQLAlchemy: camino de ESCRITURA, devuelve agregados.
- RepositorioTrabajosLectura: camino de LECTURA, no participa de la unidad
  de trabajo ni emite eventos.

Separarlos es lo que deja abierta la puerta a apuntar las lecturas a una
replica o a una proyeccion sin tocar el modelo de escritura, que es la
decision del escenario SC-ESC-01.
"""
from uuid import UUID

from hda.config.db import Session
from hda.modulos.trabajos.dominio.entidades import Trabajo
from hda.modulos.trabajos.dominio.repositorios import RepositorioTrabajos

from .dto import TrabajoDBO
from .mapeadores import MapeadorTrabajoDBO


class RepositorioTrabajosSQLAlchemy(RepositorioTrabajos):

    def __init__(self, session=None):
        self.session = session or Session
        self._mapeador = MapeadorTrabajoDBO()

    def obtener_por_id(self, id: UUID) -> Trabajo | None:
        dbo = self.session.query(TrabajoDBO).filter_by(id=str(id)).one_or_none()
        if not dbo:
            return None
        return self._mapeador.dto_a_entidad(dbo)

    def obtener_todos(self) -> list[Trabajo]:
        return [
            self._mapeador.dto_a_entidad(d)
            for d in self.session.query(TrabajoDBO).all()
        ]

    def obtener_por_estado(self, estado: str) -> list[Trabajo]:
        return [
            self._mapeador.dto_a_entidad(d)
            for d in self.session.query(TrabajoDBO).filter_by(estado=estado).all()
        ]

    def obtener_por_mercado(self, mercado_id: str) -> list[Trabajo]:
        return [
            self._mapeador.dto_a_entidad(d)
            for d in self.session.query(TrabajoDBO).filter_by(mercado_id=mercado_id).all()
        ]

    def agregar(self, trabajo: Trabajo):
        self.session.add(self._mapeador.entidad_a_dto(trabajo))

    def actualizar(self, trabajo: Trabajo):
        dbo = self.session.query(TrabajoDBO).filter_by(id=str(trabajo.id)).one_or_none()
        if not dbo:
            self.agregar(trabajo)
            return
        self._mapeador.actualizar_dto(trabajo, dbo)

    def eliminar(self, id: UUID):
        dbo = self.session.query(TrabajoDBO).filter_by(id=str(id)).one_or_none()
        if dbo:
            self.session.delete(dbo)


class RepositorioTrabajosLectura(RepositorioTrabajosSQLAlchemy):
    """Camino de lectura. Hoy comparte la conexion; el punto es que el
    contrato ya esta separado para poder apuntarlo a otra fuente."""

    def agregar(self, trabajo: Trabajo):
        raise NotImplementedError("El repositorio de lectura no escribe")

    def actualizar(self, trabajo: Trabajo):
        raise NotImplementedError("El repositorio de lectura no escribe")

    def eliminar(self, id: UUID):
        raise NotImplementedError("El repositorio de lectura no escribe")
