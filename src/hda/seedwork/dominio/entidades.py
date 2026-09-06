"""Entidades y agregaciones raiz.

Una entidad tiene identidad y ciclo de vida. Una agregacion raiz es la unica
puerta de entrada a su frontera transaccional: nadie modifica una entidad
interna sin pasar por la raiz.
"""
from __future__ import annotations
from hda.seedwork.dominio.fechas import ahora

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .excepciones import ExcepcionReglaDeNegocio
from .reglas import ReglaNegocio


@dataclass
class Entidad:
    id: uuid.UUID = field(hash=True, default_factory=uuid.uuid4)
    _id: uuid.UUID = field(init=False, repr=False, hash=True, default=None)
    fecha_creacion: datetime = field(default_factory=ahora)
    fecha_actualizacion: datetime = field(default_factory=ahora)

    @classmethod
    def siguiente_id(cls) -> uuid.UUID:
        return uuid.uuid4()

    def __post_init__(self):
        self._id = self.id

    def __eq__(self, other) -> bool:
        """Igualdad por identidad, no por atributos. Esta es la diferencia
        estructural entre una entidad y un objeto valor."""
        if not isinstance(other, Entidad):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def validar_regla(self, regla: ReglaNegocio):
        """Punto unico donde el dominio hace cumplir sus invariantes."""
        if not regla.es_valido():
            raise ExcepcionReglaDeNegocio(regla)

    def tocar(self):
        self.fecha_actualizacion = ahora()


@dataclass
class AgregacionRaiz(Entidad):
    """Raiz de una frontera transaccional.

    Acumula eventos en lugar de publicarlos de inmediato. El motivo es
    transaccional: si el commit falla, los eventos nunca deben salir. La
    unidad de trabajo los publica solo despues de persistir.
    """
    eventos: list = field(default_factory=list)

    def agregar_evento(self, evento):
        self.eventos.append(evento)

    def limpiar_eventos(self):
        self.eventos = []

    def obtener_eventos(self) -> list:
        return list(self.eventos)
