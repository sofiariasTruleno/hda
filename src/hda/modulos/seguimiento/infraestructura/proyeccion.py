"""Proyeccion de lectura del modulo Seguimiento.

Materializa una vista plana del estado del trabajo para el dueno de hogar y
el agente. Se alimenta SOLO de eventos de dominio, nunca consultando el
repositorio de Trabajos.

Este es el lado de lectura de CQRS a escala de modulo: separar esta vista
del modelo de escritura es lo que permite, en el escenario SC-ESC-01,
escalar las 240 lecturas/s sin tocar el camino de escritura.
"""
from hda.seedwork.dominio.fechas import ahora
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VistaSeguimiento:
    trabajo_id: str
    mercado_id: str = None
    estado: str = None
    proveedor_id: str = None
    categoria: str = None
    hitos: list = field(default_factory=list)
    actualizado: datetime = field(default_factory=ahora)

    def agregar_hito(self, descripcion: str):
        self.hitos.append({
            "descripcion": descripcion,
            "momento": ahora().isoformat(),
        })
        self.actualizado = ahora()


class ProyeccionSeguimiento:
    def __init__(self):
        self._vistas: dict[str, VistaSeguimiento] = {}

    def obtener(self, trabajo_id: str) -> VistaSeguimiento | None:
        return self._vistas.get(trabajo_id)

    def obtener_o_crear(self, trabajo_id: str) -> VistaSeguimiento:
        if trabajo_id not in self._vistas:
            self._vistas[trabajo_id] = VistaSeguimiento(trabajo_id=trabajo_id)
        return self._vistas[trabajo_id]

    def todas(self) -> list:
        return list(self._vistas.values())

    def limpiar(self):
        self._vistas = {}


proyeccion_seguimiento = ProyeccionSeguimiento()
