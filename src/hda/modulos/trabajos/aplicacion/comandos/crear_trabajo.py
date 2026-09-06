"""Comando: registrar un trabajo nuevo.

Nota de diseno para la sustentacion: el handler NO contiene reglas de
negocio. Solo orquesta -- construye via fabrica, persiste, hace commit. Las
invariantes viven en el dominio. Si aqui apareciera un `if urgencia ==
SINIESTRO`, el dominio estaria anemico.
"""
from dataclasses import dataclass
from datetime import datetime

from hda.seedwork.aplicacion.comandos import Comando, ejecutar_comando
from hda.seedwork.infraestructura.uow import UnidadTrabajo

from hda.modulos.trabajos.dominio.fabricas import ConstructorTrabajo
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajo

from .base import ComandoTrabajoBaseHandler


@dataclass(frozen=True)
class CrearTrabajo(Comando):
    dueno_de_hogar_id: str
    mercado_id: str
    categoria: str
    urgencia: str
    canal: str
    descripcion: str
    direccion_linea: str
    direccion_ciudad: str
    direccion_pais: str
    ventana_inicio: datetime
    ventana_fin: datetime
    partner_id: str | None = None


class CrearTrabajoHandler(ComandoTrabajoBaseHandler):

    def handle(self, comando: CrearTrabajo):
        trabajo = ConstructorTrabajo.construir(
            dueno_de_hogar_id=comando.dueno_de_hogar_id,
            mercado_id=comando.mercado_id,
            categoria=comando.categoria,
            urgencia=comando.urgencia,
            canal=comando.canal,
            descripcion=comando.descripcion,
            direccion_linea=comando.direccion_linea,
            direccion_ciudad=comando.direccion_ciudad,
            direccion_pais=comando.direccion_pais,
            ventana_inicio=comando.ventana_inicio,
            ventana_fin=comando.ventana_fin,
            partner_id=comando.partner_id,
        )

        uow: UnidadTrabajo = self.fabrica_repositorio.crear_uow()
        repositorio = self.fabrica_repositorio.crear_repositorio(uow)

        repositorio.agregar(trabajo)
        uow.registrar(trabajo)
        uow.commit()

        return MapeadorTrabajo().entidad_a_dto(trabajo)


@ejecutar_comando.register
def _(comando: CrearTrabajo):
    return CrearTrabajoHandler().handle(comando)
