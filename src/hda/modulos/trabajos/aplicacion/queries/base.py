from hda.seedwork.aplicacion.queries import QueryHandler

from hda.modulos.trabajos.infraestructura.fabricas import FabricaRepositorio


class QueryTrabajoBaseHandler(QueryHandler):
    def __init__(self):
        self._fabrica_repositorio = FabricaRepositorio()

    @property
    def fabrica_repositorio(self) -> FabricaRepositorio:
        return self._fabrica_repositorio
