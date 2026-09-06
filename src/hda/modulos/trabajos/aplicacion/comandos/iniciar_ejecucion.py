"""Comando: iniciar la ejecucion en sitio."""
from dataclasses import dataclass
from uuid import UUID

from hda.seedwork.aplicacion.comandos import Comando, ejecutar_comando

from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import ComandoTrabajoBaseHandler


@dataclass(frozen=True)
class IniciarEjecucion(Comando):
    trabajo_id: str


class IniciarEjecucionHandler(ComandoTrabajoBaseHandler):

    def handle(self, comando: IniciarEjecucion):
        uow = self.fabrica_repositorio.crear_uow()
        repositorio = self.fabrica_repositorio.crear_repositorio(uow)

        trabajo = repositorio.obtener_por_id(UUID(comando.trabajo_id))
        if not trabajo:
            raise TrabajoNoExiste(comando.trabajo_id)

        trabajo.iniciar_ejecucion()

        repositorio.actualizar(trabajo)
        uow.registrar(trabajo)
        uow.commit()

        return MapeadorTrabajo().entidad_a_dto(trabajo)


@ejecutar_comando.register
def _(comando: IniciarEjecucion):
    return IniciarEjecucionHandler().handle(comando)
