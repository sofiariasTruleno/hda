"""Comando: asignar un proveedor a un trabajo registrado."""
from dataclasses import dataclass
from uuid import UUID

from hda.seedwork.aplicacion.comandos import Comando, ejecutar_comando

from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import ComandoTrabajoBaseHandler


@dataclass(frozen=True)
class AsignarProveedor(Comando):
    trabajo_id: str
    proveedor_id: str
    mercado_proveedor: str
    cotizacion_id: str | None = None


class AsignarProveedorHandler(ComandoTrabajoBaseHandler):

    def handle(self, comando: AsignarProveedor):
        uow = self.fabrica_repositorio.crear_uow()
        repositorio = self.fabrica_repositorio.crear_repositorio(uow)

        trabajo = repositorio.obtener_por_id(UUID(comando.trabajo_id))
        if not trabajo:
            raise TrabajoNoExiste(comando.trabajo_id)

        trabajo.asignar_proveedor(
            proveedor_id=comando.proveedor_id,
            mercado_proveedor=comando.mercado_proveedor,
            cotizacion_id=comando.cotizacion_id,
        )

        repositorio.actualizar(trabajo)
        uow.registrar(trabajo)
        uow.commit()

        return MapeadorTrabajo().entidad_a_dto(trabajo)


@ejecutar_comando.register
def _(comando: AsignarProveedor):
    return AsignarProveedorHandler().handle(comando)
