"""Modulo interno de Cumplimiento.

Vive DENTRO del microservicio de Orquestacion de Trabajos, no es otro
servicio. Se comunica con el modulo Trabajos exclusivamente por eventos de
dominio: nunca importa la agregacion Trabajo ni consulta su repositorio.

Ese es el punto que sustenta el item de la rubrica sobre comunicacion entre
modulos por eventos de dominio.
"""
from hda.seedwork.dominio.fechas import ahora
from dataclasses import dataclass, field
from datetime import datetime

from hda.seedwork.dominio.entidades import AgregacionRaiz


@dataclass
class RegistroIncumplimiento(AgregacionRaiz):
    trabajo_id: str = None
    horas_comprometidas: int = None
    horas_reales: float = None
    fecha_registro: datetime = field(default_factory=ahora)

    def desviacion_horas(self) -> float:
        return round(self.horas_reales - self.horas_comprometidas, 2)


@dataclass
class AlertaBloqueo(AgregacionRaiz):
    trabajo_id: str = None
    tipo_novedad: str = None
    descripcion: str = None
    fecha_alerta: datetime = field(default_factory=ahora)
