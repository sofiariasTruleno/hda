"""DTOs de aplicacion del modulo Trabajos.

Frontera entre el mundo exterior y el dominio. La API nunca ve un objeto
Trabajo; ve un TrabajoDTO plano.
"""
from dataclasses import dataclass, field

from hda.seedwork.aplicacion.dto import DTO


@dataclass(frozen=True)
class DireccionDTO(DTO):
    linea: str = None
    ciudad: str = None
    pais: str = None


@dataclass(frozen=True)
class VentanaDTO(DTO):
    inicio: str = None
    fin: str = None


@dataclass(frozen=True)
class NovedadDTO(DTO):
    id: str = None
    tipo: str = None
    descripcion: str = None
    bloquea_ejecucion: bool = False
    fecha_reporte: str = None


@dataclass(frozen=True)
class DiagnosticoDTO(DTO):
    id: str = None
    hallazgo: str = None
    requiere_repuesto: bool = False
    diagnosticado_por: str = None


@dataclass(frozen=True)
class EjecucionDTO(DTO):
    id: str = None
    proveedor_id: str = None
    fecha_inicio: str = None
    fecha_fin: str = None
    duracion_horas: float = None


@dataclass(frozen=True)
class TrabajoDTO(DTO):
    id: str = None
    dueno_de_hogar_id: str = None
    mercado_id: str = None
    partner_id: str = None
    categoria: str = None
    urgencia: str = None
    canal: str = None
    estado: str = None
    proveedor_id: str = None
    cotizacion_id: str = None
    descripcion: str = None
    direccion: DireccionDTO = None
    ventana_atencion: VentanaDTO = None
    horas_sla: int = None
    diagnostico: DiagnosticoDTO = None
    ejecucion: EjecucionDTO = None
    novedades: list = field(default_factory=list)
    fecha_registro: str = None
    fecha_completado: str = None
