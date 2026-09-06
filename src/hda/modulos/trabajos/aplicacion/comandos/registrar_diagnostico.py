"""Comando: registrar el diagnostico tecnico."""
from dataclasses import dataclass
from uuid import UUID

from hda.seedwork.aplicacion.comandos import Comando, ejecutar_comando

from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import ComandoTrabajoBaseHandler


@dataclass(frozen=True)
class RegistrarDiagnostico(Comando):
    trabajo_id: str
    hallazgo: str
    requiere_repuesto: bool
    diagnosticado_por: str


class RegistrarDiagnosticoHandler(ComandoTrabajoBaseHandler):

    def handle(self, comando: RegistrarDiagnostico):
        uow = self.fabrica_repositorio.crear_uow()
        repositorio = self.fabrica_repositorio.crear_repositorio(uow)

        trabajo = repositorio.obtener_por_id(UUID(comando.trabajo_id))
        if not trabajo:
            raise TrabajoNoExiste(comando.trabajo_id)

        trabajo.registrar_diagnostico(
            hallazgo=comando.hallazgo,
            requiere_repuesto=comando.requiere_repuesto,
            diagnosticado_por=comando.diagnosticado_por,
        )

        repositorio.actualizar(trabajo)
        uow.registrar(trabajo)
        uow.commit()

        return MapeadorTrabajo().entidad_a_dto(trabajo)


@ejecutar_comando.register
def _(comando: RegistrarDiagnostico):
    return RegistrarDiagnosticoHandler().handle(comando)
