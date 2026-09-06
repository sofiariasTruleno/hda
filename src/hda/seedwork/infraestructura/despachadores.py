"""Despachador de eventos de INTEGRACION (hacia el bus).

Es un adaptador de salida. La implementacion por defecto escribe en memoria
para que el proyecto corra sin dependencias externas; la de Kafka esta
esbozada para mostrar que cambiar el broker no toca el dominio, que es
justamente el argumento de la arquitectura hexagonal.

La clave de particion es MercadoId, coherente con la decision de
aislamiento por mercado del escenario de escalabilidad SC-ESC-02.
"""
from abc import ABC, abstractmethod
import json
import logging

from hda.seedwork.dominio.eventos import EventoIntegracion

logger = logging.getLogger(__name__)


class DespachadorIntegracion(ABC):
    @abstractmethod
    def publicar(self, evento: EventoIntegracion):
        ...


class DespachadorEnMemoria(DespachadorIntegracion):
    """Adaptador de pruebas: guarda lo publicado para poder afirmarlo en tests."""

    def __init__(self):
        self.publicados: list[EventoIntegracion] = []

    def publicar(self, evento: EventoIntegracion):
        self.publicados.append(evento)
        logger.info(
            "[BUS] topico=%s clave=%s payload=%s",
            self._topico(evento),
            self._clave_particion(evento),
            json.dumps(self._payload(evento), default=str),
        )

    def limpiar(self):
        self.publicados = []

    def _topico(self, evento) -> str:
        return f"hda.trabajos.{evento.nombre}.{evento.version_esquema}"

    def _clave_particion(self, evento) -> str:
        return getattr(evento, "mercado_id", "sin-mercado")

    def _payload(self, evento) -> dict:
        return {
            k: v for k, v in evento.__dict__.items() if not k.startswith("_")
        }


class DespachadorKafka(DespachadorIntegracion):
    """Adaptador de produccion. No se instancia en el proyecto de entrega.

    Se deja para evidenciar que el puerto es el mismo: sustituir este
    adaptador por el de memoria no requiere tocar el dominio ni la
    aplicacion.
    """

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self._productor = None

    def publicar(self, evento: EventoIntegracion):
        raise NotImplementedError(
            "Adaptador de Kafka no habilitado en la entrega. "
            "Requiere un broker en ejecucion."
        )


despachador_integracion: DespachadorIntegracion = DespachadorEnMemoria()
