"""Objetos valor de la agregacion Trabajo.

Tomados textualmente de la vista de informacion HDA-004. Se modelan como
objetos valor y no como primitivos para desplazar la validacion desde la
capa de aplicacion hacia el nucleo del dominio: un Trabajo no puede existir
con una ventana de atencion invalida porque el objeto valor no se deja
construir.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from hda.seedwork.dominio.objetos_valor import ObjetoValor, Direccion  # noqa: F401


class EstadoSolicitud(str, Enum):
    """Ciclo de vida del Trabajo.

    Transiciones permitidas:
        REGISTRADO   -> ASIGNADO | CANCELADO
        ASIGNADO     -> EN_EJECUCION | CANCELADO
        EN_EJECUCION -> COMPLETADO | CANCELADO
        COMPLETADO   -> (terminal)
        CANCELADO    -> (terminal)
    """
    REGISTRADO = "REGISTRADO"
    ASIGNADO = "ASIGNADO"
    EN_EJECUCION = "EN_EJECUCION"
    COMPLETADO = "COMPLETADO"
    CANCELADO = "CANCELADO"

    def es_terminal(self) -> bool:
        return self in (EstadoSolicitud.COMPLETADO, EstadoSolicitud.CANCELADO)


class Urgencia(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    SINIESTRO = "SINIESTRO"

    def horas_sla(self) -> int:
        """Un siniestro de aseguradora no espera lo mismo que un cambio de
        grifo. El SLA depende de la urgencia, no del canal."""
        return {"BAJA": 72, "MEDIA": 24, "ALTA": 8, "SINIESTRO": 2}[self.value]


class Canal(str, Enum):
    """Por donde entro la solicitud. Relevante para el modelo B2B2C:
    un trabajo originado por un partner tiene reglas distintas."""
    MARKETPLACE = "MARKETPLACE"
    PARTNER_B2B2C = "PARTNER_B2B2C"
    AGENTE = "AGENTE"
    SUSCRIPCION = "SUSCRIPCION"


@dataclass(frozen=True)
class CategoriaDeServicio(ObjetoValor):
    codigo: str
    nombre: str

    CATALOGO = {
        "PLOMERIA": "Plomeria",
        "ELECTRICIDAD": "Electricidad",
        "CERRAJERIA": "Cerrajeria",
        "REMODELACION": "Remodelacion",
        "ASEO": "Aseo",
        "JARDINERIA": "Jardineria",
    }

    def __post_init__(self):
        if self.codigo not in self.CATALOGO:
            raise ValueError(f"Categoria de servicio no soportada: {self.codigo}")

    @classmethod
    def de_codigo(cls, codigo: str) -> "CategoriaDeServicio":
        codigo = (codigo or "").upper()
        if codigo not in cls.CATALOGO:
            raise ValueError(f"Categoria de servicio no soportada: {codigo}")
        return cls(codigo, cls.CATALOGO[codigo])


@dataclass(frozen=True)
class VentanaDeAtencion(ObjetoValor):
    """Franja acordada con el dueno de hogar."""
    inicio: datetime
    fin: datetime

    def __post_init__(self):
        if self.fin <= self.inicio:
            raise ValueError("La ventana de atencion debe terminar despues de iniciar")
        if (self.fin - self.inicio) > timedelta(hours=12):
            raise ValueError("La ventana de atencion no puede superar 12 horas")

    def contiene(self, momento: datetime) -> bool:
        return self.inicio <= momento <= self.fin

    def duracion_horas(self) -> float:
        return (self.fin - self.inicio).total_seconds() / 3600


@dataclass(frozen=True)
class DescripcionDelProblema(ObjetoValor):
    texto: str

    def __post_init__(self):
        limpio = (self.texto or "").strip()
        if len(limpio) < 10:
            raise ValueError("La descripcion del problema requiere al menos 10 caracteres")
        if len(limpio) > 2000:
            raise ValueError("La descripcion del problema no puede superar 2000 caracteres")


@dataclass(frozen=True)
class AcuerdoDeServicio(ObjetoValor):
    """SLA comprometido. Se calcula en el momento de registrar el trabajo y
    queda congelado: cambiar la politica no debe alterar acuerdos vigentes."""
    horas_respuesta: int
    penalizacion_por_incumplimiento: bool = False

    def __post_init__(self):
        if self.horas_respuesta <= 0:
            raise ValueError("El acuerdo de servicio requiere horas de respuesta positivas")

    @classmethod
    def desde_urgencia(cls, urgencia: Urgencia, canal: Canal) -> "AcuerdoDeServicio":
        penaliza = canal == Canal.PARTNER_B2B2C
        return cls(horas_respuesta=urgencia.horas_sla(), penalizacion_por_incumplimiento=penaliza)


@dataclass(frozen=True)
class ResultadoDiagnostico(ObjetoValor):
    hallazgo: str
    requiere_repuesto: bool = False


class TipoNovedad(str, Enum):
    """Motivo por el que la ejecucion se desvia de lo planeado."""
    RETRASO = "RETRASO"
    ACCESO_DENEGADO = "ACCESO_DENEGADO"
    REPUESTO_FALTANTE = "REPUESTO_FALTANTE"
    ALCANCE_MAYOR = "ALCANCE_MAYOR"
    CLIENTE_AUSENTE = "CLIENTE_AUSENTE"
