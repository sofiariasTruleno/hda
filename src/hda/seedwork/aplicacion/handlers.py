"""Despachador de eventos de DOMINIO (intra-servicio).

Este es el mecanismo que la rubrica pide para comunicar los modulos del
servicio entre si. Es sincrono y en proceso: un evento de dominio no sale
por la red.

No confundir con el despachador de eventos de INTEGRACION, que si publica
al bus y vive en infraestructura.
"""
from collections import defaultdict
from typing import Callable

from hda.seedwork.dominio.eventos import EventoDominio


class DespachadorEventosDominio:
    def __init__(self):
        self._suscriptores: dict[type, list[Callable]] = defaultdict(list)

    def suscribir(self, tipo_evento: type, handler: Callable):
        self._suscriptores[tipo_evento].append(handler)

    def publicar(self, evento: EventoDominio):
        for handler in self._suscriptores[type(evento)]:
            handler(evento)

    def publicar_lote(self, eventos: list[EventoDominio]):
        for evento in eventos:
            self.publicar(evento)

    def limpiar(self):
        self._suscriptores.clear()


despachador_dominio = DespachadorEventosDominio()
