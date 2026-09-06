"""Suscriptores del modulo Seguimiento.

Construye la vista de seguimiento reaccionando al ciclo de vida del Trabajo.
Igual que Cumplimiento: conoce eventos, no entidades.
"""
import logging

from hda.seedwork.aplicacion.handlers import despachador_dominio
from hda.modulos.trabajos.dominio.eventos import (
    EjecucionIniciada,
    NovedadRegistrada,
    ProveedorAsignado,
    TrabajoRegistrado,
)

from ..infraestructura.proyeccion import proyeccion_seguimiento

logger = logging.getLogger(__name__)


def manejar_trabajo_registrado(evento: TrabajoRegistrado):
    vista = proyeccion_seguimiento.obtener_o_crear(evento.trabajo_id)
    vista.mercado_id = evento.mercado_id
    vista.categoria = evento.categoria
    vista.estado = "REGISTRADO"
    vista.agregar_hito("Solicitud registrada")


def manejar_proveedor_asignado(evento: ProveedorAsignado):
    vista = proyeccion_seguimiento.obtener_o_crear(evento.trabajo_id)
    vista.estado = "ASIGNADO"
    vista.proveedor_id = evento.proveedor_id
    vista.agregar_hito(f"Proveedor {evento.proveedor_id} asignado")


def manejar_ejecucion_iniciada(evento: EjecucionIniciada):
    vista = proyeccion_seguimiento.obtener_o_crear(evento.trabajo_id)
    vista.estado = "EN_EJECUCION"
    vista.agregar_hito("Ejecucion iniciada en sitio")


def manejar_novedad(evento: NovedadRegistrada):
    vista = proyeccion_seguimiento.obtener_o_crear(evento.trabajo_id)
    vista.agregar_hito(f"Novedad {evento.tipo}: {evento.descripcion}")


def registrar_suscriptores():
    despachador_dominio.suscribir(TrabajoRegistrado, manejar_trabajo_registrado)
    despachador_dominio.suscribir(ProveedorAsignado, manejar_proveedor_asignado)
    despachador_dominio.suscribir(EjecucionIniciada, manejar_ejecucion_iniciada)
    despachador_dominio.suscribir(NovedadRegistrada, manejar_novedad)
