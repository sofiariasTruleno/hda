"""Eventos del modulo Trabajos.

Dos familias, y la diferencia se sustenta:

EVENTOS DE DOMINIO (intra-servicio). Comunican los modulos internos del
microservicio. Cambiarlos no rompe a nadie fuera.

EVENTOS DE INTEGRACION (inter-servicio). Salen por el bus como published
language. TrabajoCompletadoIntegracion es el que dispara el recalculo en
Confianza y Reputacion, que es exactamente el escenario SC-ESC-03.
"""
from hda.seedwork.dominio.fechas import ahora
from dataclasses import dataclass, field
from datetime import datetime

from hda.seedwork.dominio.eventos import EventoDominio, EventoIntegracion


# ---------------------------------------------------------------- dominio

@dataclass
class TrabajoRegistrado(EventoDominio):
    trabajo_id: str = None
    dueno_de_hogar_id: str = None
    mercado_id: str = None
    partner_id: str | None = None
    categoria: str = None
    urgencia: str = None
    canal: str = None
    horas_sla: int = None


@dataclass
class ProveedorAsignado(EventoDominio):
    trabajo_id: str = None
    proveedor_id: str = None
    cotizacion_id: str | None = None
    mercado_id: str = None


@dataclass
class EjecucionIniciada(EventoDominio):
    trabajo_id: str = None
    proveedor_id: str = None
    fecha_inicio: datetime = None


@dataclass
class NovedadRegistrada(EventoDominio):
    trabajo_id: str = None
    tipo: str = None
    descripcion: str = None
    bloquea_ejecucion: bool = False


@dataclass
class DiagnosticoRegistrado(EventoDominio):
    trabajo_id: str = None
    hallazgo: str = None
    requiere_repuesto: bool = False


@dataclass
class SLAIncumplido(EventoDominio):
    """Emitido al completar fuera del acuerdo. Lo consume el modulo interno
    de cumplimiento sin salir del servicio."""
    trabajo_id: str = None
    horas_comprometidas: int = None
    horas_reales: float = None


# ------------------------------------------------------------ integracion

@dataclass
class TrabajoCompletadoIntegracion(EventoIntegracion):
    """Published language. Consumido por Confianza y Reputacion, Pagos y
    Custodia y Liquidacion. Su esquema es contrato: se versiona, no se
    rompe."""
    trabajo_id: str = None
    proveedor_id: str = None
    dueno_de_hogar_id: str = None
    mercado_id: str = None
    categoria: str = None
    duracion_horas: float = None
    cumplio_sla: bool = None
    fecha_completado: datetime = field(default_factory=ahora)


@dataclass
class TrabajoRegistradoIntegracion(EventoIntegracion):
    """Consumido por Emparejamiento y Asignacion para iniciar la busqueda
    de candidatos."""
    trabajo_id: str = None
    mercado_id: str = None
    categoria: str = None
    urgencia: str = None
    ciudad: str = None
