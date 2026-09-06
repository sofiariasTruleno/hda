"""Query: obtener un trabajo por identificador.

Lado de LECTURA. No muta nada, no abre unidad de trabajo y no emite eventos.
Esa asimetria frente a los comandos es exactamente lo que CQS busca.
"""
from dataclasses import dataclass
from uuid import UUID

from hda.seedwork.aplicacion.queries import Query, QueryResultado, ejecutar_query

from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import QueryTrabajoBaseHandler


@dataclass(frozen=True)
class ObtenerTrabajo(Query):
    id: str


class ObtenerTrabajoHandler(QueryTrabajoBaseHandler):

    def handle(self, query: ObtenerTrabajo) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_repositorio_lectura()
        trabajo = repositorio.obtener_por_id(UUID(query.id))
        if not trabajo:
            raise TrabajoNoExiste(query.id)
        return QueryResultado(resultado=MapeadorTrabajo().entidad_a_dto(trabajo))


@ejecutar_query.register
def _(query: ObtenerTrabajo):
    return ObtenerTrabajoHandler().handle(query)
