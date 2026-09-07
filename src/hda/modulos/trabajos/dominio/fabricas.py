"""Fabrica del modulo Trabajos.

Construir un Trabajo valido implica derivar el acuerdo de servicio, validar
la ventana de atencion y emitir los eventos de registro. Eso es demasiado
para un constructor, y ponerlo en la capa de aplicacion filtraria reglas de
negocio fuera del dominio. De ahi la fabrica.
"""
from datetime import datetime

from hda.seedwork.dominio.objetos_valor import Direccion

from .entidades import Trabajo
from .objetos_valor import (
    Canal,
    CategoriaDeServicio,
    DescripcionDelProblema,
    Urgencia,
    VentanaDeAtencion,
)


class ConstructorTrabajo:
    """Camino de creacion de un agregado nuevo desde datos crudos.

    Tipa los objetos valor, arma la direccion y la ventana, y delega en
    `registrar()` la derivacion del SLA y la emision de los eventos. Aqui no
    se traduce entre representaciones: se construye aplicando reglas de
    negocio.
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
