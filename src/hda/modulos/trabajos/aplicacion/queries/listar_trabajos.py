"""Query: listar trabajos, opcionalmente filtrando por estado o mercado.

El filtro por mercado_id no es cosmetico: es la clave de aislamiento del
escenario SC-ESC-02 y de la particion del bus. La lectura respeta la misma
frontera que la escritura.
"""
from dataclasses import dataclass

from hda.seedwork.aplicacion.queries import Query, QueryResultado, ejecutar_query

from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import QueryTrabajoBaseHandler


@dataclass(frozen=True)
class ListarTrabajos(Query):
    estado: str | None = None
    mercado_id: str | None = None


class ListarTrabajosHandler(QueryTrabajoBaseHandler):

    def handle(self, query: ListarTrabajos) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_repositorio_lectura()

        if query.mercado_id:
            trabajos = repositorio.obtener_por_mercado(query.mercado_id)
        elif query.estado:
            trabajos = repositorio.obtener_por_estado(query.estado.upper())
        else:
            trabajos = repositorio.obtener_todos()

        if query.mercado_id and query.estado:
            trabajos = [t for t in trabajos if t.estado.value == query.estado.upper()]

        mapeador = MapeadorTrabajo()
        return QueryResultado(resultado=[mapeador.entidad_a_dto(t) for t in trabajos])


@ejecutar_query.register
def _(query: ListarTrabajos):
    return ListarTrabajosHandler().handle(query)
