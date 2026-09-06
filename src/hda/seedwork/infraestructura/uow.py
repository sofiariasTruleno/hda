"""Unidad de Trabajo.

Coordina la frontera transaccional y el orden de publicacion de eventos.
La secuencia importa y es defendible:

  1. commit a la base de datos
  2. publicar eventos de DOMINIO (en proceso, otros modulos reaccionan)
  3. publicar eventos de INTEGRACION (al bus, otros servicios reaccionan)

Si se publicara antes del commit, un rollback dejaria eventos anunciando
hechos que nunca ocurrieron.
"""
from abc import ABC, abstractmethod

from hda.seedwork.aplicacion.handlers import despachador_dominio
from hda.seedwork.dominio.eventos import EventoIntegracion


class UnidadTrabajo(ABC):
    def __init__(self):
        self._agregaciones = []

    def registrar(self, agregacion):
        if agregacion not in self._agregaciones:
            self._agregaciones.append(agregacion)

    @abstractmethod
    def _commit(self):
        ...

    @abstractmethod
    def rollback(self):
        ...

    def _recolectar_eventos(self) -> list:
        eventos = []
        for agregacion in self._agregaciones:
            eventos.extend(agregacion.obtener_eventos())
            agregacion.limpiar_eventos()
        return eventos

    def commit(self):
        self._commit()
        eventos = self._recolectar_eventos()

        dominio = [e for e in eventos if not isinstance(e, EventoIntegracion)]
        integracion = [e for e in eventos if isinstance(e, EventoIntegracion)]

        despachador_dominio.publicar_lote(dominio)

        from .despachadores import despachador_integracion
        for evento in integracion:
            despachador_integracion.publicar(evento)

        self._agregaciones = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.rollback()
        return False
