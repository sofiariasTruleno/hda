"""Base de los command handlers del modulo Trabajos."""
from hda.seedwork.aplicacion.comandos import ComandoHandler

from hda.modulos.trabajos.infraestructura.fabricas import FabricaRepositorio


class ComandoTrabajoBaseHandler(ComandoHandler):
    def __init__(self):
        self._fabrica_repositorio = FabricaRepositorio()

    @property
    def fabrica_repositorio(self) -> FabricaRepositorio:
        return self._fabrica_repositorio
