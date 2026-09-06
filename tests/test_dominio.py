"""Pruebas del dominio puro: sin base de datos, sin Flask.

Que estas pruebas no necesiten infraestructura ES la evidencia de que la
inversion de dependencias funciona.
"""
from hda.seedwork.dominio.fechas import ahora
from datetime import datetime, timedelta
import pytest

from hda.seedwork.dominio.excepciones import ExcepcionReglaDeNegocio
from hda.modulos.trabajos.dominio.fabricas import ConstructorTrabajo
from hda.modulos.trabajos.dominio.objetos_valor import (
    CategoriaDeServicio, EstadoSolicitud, TipoNovedad, VentanaDeAtencion,
)
from hda.modulos.trabajos.dominio.eventos import (
    ProveedorAsignado, TrabajoCompletadoIntegracion, TrabajoRegistrado,
)


def construir_trabajo(urgencia="MEDIA", canal="MARKETPLACE"):
    momento = ahora()
    return ConstructorTrabajo.construir(
        dueno_de_hogar_id="dh-001",
        mercado_id="CO",
        categoria="PLOMERIA",
        urgencia=urgencia,
        canal=canal,
        descripcion="Fuga de agua bajo el lavaplatos de la cocina",
        direccion_linea="Calle 100 #15-20",
        direccion_ciudad="Bogota",
        direccion_pais="Colombia",
        ventana_inicio=momento + timedelta(hours=2),
        ventana_fin=momento + timedelta(hours=6),
    )


def test_registrar_emite_evento_dominio_y_integracion():
    trabajo = construir_trabajo()
    nombres = [e.nombre for e in trabajo.obtener_eventos()]
    assert "TrabajoRegistrado" in nombres
    assert "TrabajoRegistradoIntegracion" in nombres
    assert trabajo.estado == EstadoSolicitud.REGISTRADO


def test_sla_depende_de_urgencia():
    assert construir_trabajo("SINIESTRO").acuerdo_servicio.horas_respuesta == 2
    assert construir_trabajo("BAJA").acuerdo_servicio.horas_respuesta == 72


def test_penalizacion_solo_para_canal_partner():
    assert construir_trabajo(canal="PARTNER_B2B2C").acuerdo_servicio.penalizacion_por_incumplimiento
    assert not construir_trabajo(canal="MARKETPLACE").acuerdo_servicio.penalizacion_por_incumplimiento


def test_no_se_puede_iniciar_ejecucion_sin_proveedor():
    trabajo = construir_trabajo()
    with pytest.raises(ExcepcionReglaDeNegocio):
        trabajo.iniciar_ejecucion()


def test_no_se_puede_completar_sin_ejecucion():
    trabajo = construir_trabajo()
    trabajo.asignar_proveedor("prov-1", "CO")
    with pytest.raises(ExcepcionReglaDeNegocio):
        trabajo.completar()


def test_proveedor_de_otro_mercado_es_rechazado():
    trabajo = construir_trabajo()
    with pytest.raises(ExcepcionReglaDeNegocio):
        trabajo.asignar_proveedor("prov-br", "BR")


def test_ciclo_de_vida_completo():
    trabajo = construir_trabajo()
    trabajo.limpiar_eventos()

    trabajo.asignar_proveedor("prov-1", "CO", cotizacion_id="cot-1")
    assert trabajo.estado == EstadoSolicitud.ASIGNADO

    trabajo.iniciar_ejecucion()
    assert trabajo.estado == EstadoSolicitud.EN_EJECUCION

    trabajo.registrar_novedad(TipoNovedad.RETRASO, "El proveedor llego tarde")
    trabajo.completar()
    assert trabajo.estado == EstadoSolicitud.COMPLETADO

    integracion = [
        e for e in trabajo.obtener_eventos()
        if isinstance(e, TrabajoCompletadoIntegracion)
    ]
    assert len(integracion) == 1
    assert integracion[0].proveedor_id == "prov-1"


def test_estado_terminal_no_admite_cambios():
    trabajo = construir_trabajo()
    trabajo.asignar_proveedor("prov-1", "CO")
    trabajo.iniciar_ejecucion()
    trabajo.completar()
    with pytest.raises(ExcepcionReglaDeNegocio):
        trabajo.asignar_proveedor("prov-2", "CO")


def test_no_se_salta_estados():
    trabajo = construir_trabajo()
    with pytest.raises(ExcepcionReglaDeNegocio):
        trabajo.iniciar_ejecucion()


def test_objetos_valor_rechazan_datos_invalidos():
    momento = ahora()
    with pytest.raises(ValueError):
        VentanaDeAtencion(momento + timedelta(hours=4), momento)
    with pytest.raises(ValueError):
        VentanaDeAtencion(momento, momento + timedelta(hours=20))
    with pytest.raises(ValueError):
        CategoriaDeServicio.de_codigo("ASTROFISICA")


def test_novedad_bloqueante():
    trabajo = construir_trabajo()
    trabajo.asignar_proveedor("prov-1", "CO")
    trabajo.iniciar_ejecucion()
    trabajo.registrar_novedad(TipoNovedad.ACCESO_DENEGADO, "Nadie abrio", True)
    assert trabajo.tiene_novedades_bloqueantes()
