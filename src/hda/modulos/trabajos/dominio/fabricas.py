"""Fabricas del modulo Trabajos.

Construir un Trabajo valido implica derivar el acuerdo de servicio, validar
la ventana de atencion y emitir los eventos de registro. Eso es demasiado
para un constructor, y ponerlo en la capa de aplicacion filtraria reglas de
negocio fuera del dominio. De ahi la fabrica.
"""
from dataclasses import dataclass
from datetime import datetime

from hda.seedwork.dominio.entidades import Entidad
from hda.seedwork.dominio.fabricas import Fabrica
from hda.seedwork.dominio.objetos_valor import Direccion
from hda.seedwork.dominio.repositorios import Mapeador

from .entidades import Trabajo
from .excepciones import TipoObjetoNoValido
from .objetos_valor import (
    AcuerdoDeServicio,
    Canal,
    CategoriaDeServicio,
    DescripcionDelProblema,
    Urgencia,
    VentanaDeAtencion,
)


@dataclass
class _FabricaTrabajo(Fabrica):
    """Traduce en ambos sentidos usando el mapeador que reciba.

    Que la fabrica dependa de un Mapeador abstracto y no de un DTO concreto
    es lo que permite usar la misma fabrica para el adaptador HTTP y para el
    adaptador de base de datos.
    """

    def crear_objeto(self, obj, mapeador: Mapeador = None) -> any:
        if isinstance(obj, Entidad):
            return mapeador.entidad_a_dto(obj)

        trabajo: Trabajo = mapeador.dto_a_entidad(obj)
        return trabajo


@dataclass
class FabricaTrabajos(Fabrica):
    def crear_objeto(self, obj, mapeador: Mapeador = None) -> any:
        if mapeador.obtener_tipo() == Trabajo:
            fabrica = _FabricaTrabajo()
            return fabrica.crear_objeto(obj, mapeador)
        raise TipoObjetoNoValido(
            f"La fabrica no sabe construir objetos de tipo {mapeador.obtener_tipo()}"
        )


class ConstructorTrabajo:
    """Camino de creacion desde datos crudos.

    Se separa de FabricaTrabajos porque resuelve un problema distinto:
    aqui no se traduce entre representaciones, se construye un agregado
    nuevo aplicando reglas de negocio.
    """

    @staticmethod
    def construir(
        dueno_de_hogar_id: str,
        mercado_id: str,
        categoria: str,
        urgencia: str,
        canal: str,
        descripcion: str,
        direccion_linea: str,
        direccion_ciudad: str,
        direccion_pais: str,
        ventana_inicio: datetime,
        ventana_fin: datetime,
        partner_id: str | None = None,
    ) -> Trabajo:
        trabajo = Trabajo(
            dueno_de_hogar_id=dueno_de_hogar_id,
            mercado_id=mercado_id,
            partner_id=partner_id,
            categoria=CategoriaDeServicio.de_codigo(categoria),
            urgencia=Urgencia(urgencia.upper()),
            canal=Canal(canal.upper()),
            direccion=Direccion(
                linea=direccion_linea,
                ciudad=direccion_ciudad,
                pais=direccion_pais,
            ),
            ventana_atencion=VentanaDeAtencion(ventana_inicio, ventana_fin),
            descripcion=DescripcionDelProblema(descripcion),
        )
        trabajo.registrar()
        return trabajo
