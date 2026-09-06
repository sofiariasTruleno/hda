"""Esquemas versionados de los eventos de integracion.

Es el published language del servicio. Vive aparte de los eventos de dominio
justamente porque tiene otro ciclo de vida: los eventos de dominio cambian
cuando cambia el modelo interno, estos solo cambian negociando con los
consumidores.
"""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TrabajoCompletadoV1:
    trabajo_id: str
    proveedor_id: str
    dueno_de_hogar_id: str
    mercado_id: str
    categoria: str
    duracion_horas: float
    cumplio_sla: bool
    fecha_completado: str

    ESPECIFICACION = "hda.trabajos.TrabajoCompletado.v1"

    def a_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TrabajoRegistradoV1:
    trabajo_id: str
    mercado_id: str
    categoria: str
    urgencia: str
    ciudad: str

    ESPECIFICACION = "hda.trabajos.TrabajoRegistrado.v1"

    def a_dict(self) -> dict:
        return asdict(self)
