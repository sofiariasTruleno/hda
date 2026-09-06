"""Comando: cerrar el trabajo.

Es el comando de mayor alcance del servicio: su evento de integracion
dispara reputacion, pago y liquidacion en otros bounded contexts.
"""
from dataclasses import dataclass
from uuid import UUID

from hda.seedwork.aplicacion.comandos import Comando, ejecutar_comando

from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import ComandoTrabajoBaseHandler


@dataclass(frozen=True)
class CompletarTrabajo(Comando):
    trabajo_id: str


class CompletarTrabajoHandler(ComandoTrabajoBaseHandler):

    def handle(self, comando: CompletarTrabajo):
        uow = self.fabrica_repositorio.crear_uow()
        repositorio = self.fabrica_repositorio.crear_repositorio(uow)

        trabajo = repositorio.obtener_por_id(UUID(comando.trabajo_id))
        if not trabajo:
            raise TrabajoNoExiste(comando.trabajo_id)

        trabajo.completar()

        repositorio.actualizar(trabajo)
        uow.registrar(trabajo)
        uow.commit()

        return MapeadorTrabajo().entidad_a_dto(trabajo)


@ejecutar_comando.register
def _(comando: CompletarTrabajo):
    return CompletarTrabajoHandler().handle(comando)
