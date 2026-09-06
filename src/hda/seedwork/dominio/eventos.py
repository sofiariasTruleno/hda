"""Eventos de dominio.

Distincion clave para la sustentacion:

- EventoDominio: hecho de negocio ocurrido DENTRO del servicio. Es el medio
  de comunicacion entre modulos del mismo microservicio. Habla el lenguaje
  ubicuo interno y puede cambiar sin coordinar con otros equipos.
- EventoIntegracion: hecho publicado HACIA AFUERA por el bus. Es published
  language: es contrato, se versiona y romperlo afecta a otros bounded
  contexts.
"""
from hda.seedwork.dominio.fechas import ahora
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class EventoDominio:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_evento: datetime = field(default_factory=ahora)

    @property
    def nombre(self) -> str:
        return self.__class__.__name__


@dataclass
class EventoIntegracion(EventoDominio):
    """Evento que cruza la frontera del microservicio.

    `version_esquema` existe porque el esquema publicado es el unico
    acoplamiento estatico permitido entre bounded contexts; sin version no
    hay forma de evolucionarlo sin romper consumidores.
    """
    version_esquema: str = "v1"
