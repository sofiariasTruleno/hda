"""Suscriptores del modulo Cumplimiento a eventos de dominio del modulo
Trabajos.

Acoplamiento permitido: Cumplimiento conoce el EVENTO, no la ENTIDAD. Si
manana Trabajo cambia su estructura interna, este modulo no se entera
mientras el evento mantenga su forma.
"""
import logging

from hda.seedwork.aplicacion.handlers import despachador_dominio
from hda.modulos.trabajos.dominio.eventos import NovedadRegistrada, SLAIncumplido

from ..dominio.entidades import AlertaBloqueo, RegistroIncumplimiento
from ..infraestructura.repositorios import RepositorioCumplimientoEnMemoria

logger = logging.getLogger(__name__)

repositorio_cumplimiento = RepositorioCumplimientoEnMemoria()


def manejar_sla_incumplido(evento: SLAIncumplido):
    registro = RegistroIncumplimiento(
        trabajo_id=evento.trabajo_id,
        horas_comprometidas=evento.horas_comprometidas,
        horas_reales=evento.horas_reales,
    )
    repositorio_cumplimiento.agregar_incumplimiento(registro)
    logger.warning(
        "[CUMPLIMIENTO] Trabajo %s incumplio SLA: %sh comprometidas, %sh reales",
        evento.trabajo_id, evento.horas_comprometidas, evento.horas_reales,
    )


def manejar_novedad_registrada(evento: NovedadRegistrada):
    if not evento.bloquea_ejecucion:
        return
    alerta = AlertaBloqueo(
        trabajo_id=evento.trabajo_id,
        tipo_novedad=evento.tipo,
        descripcion=evento.descripcion,
    )
    repositorio_cumplimiento.agregar_alerta(alerta)
    logger.warning(
        "[CUMPLIMIENTO] Trabajo %s bloqueado por novedad %s",
        evento.trabajo_id, evento.tipo,
    )


def registrar_suscriptores():
    despachador_dominio.suscribir(SLAIncumplido, manejar_sla_incumplido)
    despachador_dominio.suscribir(NovedadRegistrada, manejar_novedad_registrada)
