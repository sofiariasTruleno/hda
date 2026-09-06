"""Comando: reportar una novedad durante la ejecucion."""
from dataclasses import dataclass
from uuid import UUID

from hda.seedwork.aplicacion.comandos import Comando, ejecutar_comando

from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.trabajos.dominio.objetos_valor import TipoNovedad
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import ComandoTrabajoBaseHandler


@dataclass(frozen=True)
class RegistrarNovedad(Comando):
    trabajo_id: str
    tipo: str
    descripcion: str
    bloquea_ejecucion: bool = False


class RegistrarNovedadHandler(ComandoTrabajoBaseHandler):

    def handle(self, comando: RegistrarNovedad):
        uow = self.fabrica_repositorio.crear_uow()
        repositorio = self.fabrica_repositorio.crear_repositorio(uow)

        trabajo = repositorio.obtener_por_id(UUID(comando.trabajo_id))
        if not trabajo:
            raise TrabajoNoExiste(comando.trabajo_id)

        trabajo.registrar_novedad(
            tipo=TipoNovedad(comando.tipo.upper()),
            descripcion=comando.descripcion,
            bloquea_ejecucion=comando.bloquea_ejecucion,
        )

        repositorio.actualizar(trabajo)
        uow.registrar(trabajo)
        uow.commit()

        return MapeadorTrabajo().entidad_a_dto(trabajo)


@ejecutar_comando.register
def _(comando: RegistrarNovedad):
    return RegistrarNovedadHandler().handle(comando)
