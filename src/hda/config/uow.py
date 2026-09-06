"""Unidad de trabajo sobre SQLAlchemy.

Implementa el puerto UnidadTrabajo del seedwork. Es un ADAPTADOR: la logica
de orden de publicacion de eventos vive en la clase base del seedwork, aqui
solo se resuelve el commit y el rollback concretos.
"""
from hda.seedwork.infraestructura.uow import UnidadTrabajo

from .db import Session


class UnidadTrabajoSQLAlchemy(UnidadTrabajo):
    def __init__(self, session=None):
        super().__init__()
        self.session = session or Session

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
        self._agregaciones = []
