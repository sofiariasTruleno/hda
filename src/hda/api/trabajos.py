"""Adaptador de entrada HTTP.

Es la capa mas delgada del proyecto a proposito: traduce JSON a comandos o
queries y despacha. Cero reglas de negocio aqui.
"""
from datetime import datetime

from flask import Blueprint, jsonify, request

from hda.seedwork.aplicacion.comandos import ejecutar_comando
from hda.seedwork.aplicacion.queries import ejecutar_query
from hda.seedwork.dominio.excepciones import ExcepcionDominio

from hda.modulos.trabajos.aplicacion.comandos import (
    AsignarProveedor,
    CompletarTrabajo,
    CrearTrabajo,
    IniciarEjecucion,
    RegistrarDiagnostico,
    RegistrarNovedad,
)
from hda.modulos.trabajos.aplicacion.queries import ListarTrabajos, ObtenerTrabajo
from hda.modulos.trabajos.aplicacion.mapeadores import MapeadorTrabajoDTOJson
from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste
from hda.modulos.seguimiento.infraestructura.proyeccion import proyeccion_seguimiento

bp = Blueprint("trabajos", __name__, url_prefix="/trabajos")

mapeador_json = MapeadorTrabajoDTOJson()


def _serializar(dto):
    return mapeador_json.dto_a_externo(dto)


# ------------------------------------------------------------------ comandos

@bp.route("", methods=["POST"])
def crear_trabajo():
    datos = request.json or {}
    direccion = datos.get("direccion", {}) or {}
    ventana = datos.get("ventana_atencion", {}) or {}

    comando = CrearTrabajo(
        dueno_de_hogar_id=datos.get("dueno_de_hogar_id"),
        mercado_id=datos.get("mercado_id"),
        categoria=datos.get("categoria"),
        urgencia=datos.get("urgencia", "MEDIA"),
        canal=datos.get("canal", "MARKETPLACE"),
        descripcion=datos.get("descripcion"),
        direccion_linea=direccion.get("linea"),
        direccion_ciudad=direccion.get("ciudad"),
        direccion_pais=direccion.get("pais"),
        ventana_inicio=datetime.fromisoformat(ventana.get("inicio")),
        ventana_fin=datetime.fromisoformat(ventana.get("fin")),
        partner_id=datos.get("partner_id"),
    )
    return jsonify(_serializar(ejecutar_comando(comando))), 201


@bp.route("/<trabajo_id>/proveedor", methods=["PUT"])
def asignar_proveedor(trabajo_id):
    datos = request.json or {}
    comando = AsignarProveedor(
        trabajo_id=trabajo_id,
        proveedor_id=datos.get("proveedor_id"),
        mercado_proveedor=datos.get("mercado_proveedor"),
        cotizacion_id=datos.get("cotizacion_id"),
    )
    return jsonify(_serializar(ejecutar_comando(comando))), 200


@bp.route("/<trabajo_id>/diagnostico", methods=["POST"])
def registrar_diagnostico(trabajo_id):
    datos = request.json or {}
    comando = RegistrarDiagnostico(
        trabajo_id=trabajo_id,
        hallazgo=datos.get("hallazgo"),
        requiere_repuesto=bool(datos.get("requiere_repuesto", False)),
        diagnosticado_por=datos.get("diagnosticado_por"),
    )
    return jsonify(_serializar(ejecutar_comando(comando))), 201


@bp.route("/<trabajo_id>/ejecucion", methods=["POST"])
def iniciar_ejecucion(trabajo_id):
    return jsonify(_serializar(ejecutar_comando(IniciarEjecucion(trabajo_id=trabajo_id)))), 200


@bp.route("/<trabajo_id>/novedades", methods=["POST"])
def registrar_novedad(trabajo_id):
    datos = request.json or {}
    comando = RegistrarNovedad(
        trabajo_id=trabajo_id,
        tipo=datos.get("tipo"),
        descripcion=datos.get("descripcion"),
        bloquea_ejecucion=bool(datos.get("bloquea_ejecucion", False)),
    )
    return jsonify(_serializar(ejecutar_comando(comando))), 201


@bp.route("/<trabajo_id>/completar", methods=["POST"])
def completar_trabajo(trabajo_id):
    return jsonify(_serializar(ejecutar_comando(CompletarTrabajo(trabajo_id=trabajo_id)))), 200


# ------------------------------------------------------------------- queries

@bp.route("/<trabajo_id>", methods=["GET"])
def obtener_trabajo(trabajo_id):
    resultado = ejecutar_query(ObtenerTrabajo(id=trabajo_id))
    return jsonify(_serializar(resultado.resultado)), 200


@bp.route("", methods=["GET"])
def listar_trabajos():
    resultado = ejecutar_query(
        ListarTrabajos(
            estado=request.args.get("estado"),
            mercado_id=request.args.get("mercado_id"),
        )
    )
    return jsonify([_serializar(dto) for dto in resultado.resultado]), 200


@bp.route("/<trabajo_id>/seguimiento", methods=["GET"])
def obtener_seguimiento(trabajo_id):
    """Lee de la proyeccion construida por eventos de dominio, no del
    repositorio de escritura. Es el lado de lectura de CQRS."""
    vista = proyeccion_seguimiento.obtener(trabajo_id)
    if not vista:
        return jsonify({"error": "Sin seguimiento para ese trabajo"}), 404
    return jsonify({
        "trabajo_id": vista.trabajo_id,
        "mercado_id": vista.mercado_id,
        "estado": vista.estado,
        "proveedor_id": vista.proveedor_id,
        "categoria": vista.categoria,
        "hitos": vista.hitos,
        "actualizado": vista.actualizado.isoformat(),
    }), 200


# ----------------------------------------------------------- manejo de error

@bp.errorhandler(TrabajoNoExiste)
def _no_existe(error):
    return jsonify({"error": str(error)}), 404


@bp.errorhandler(ExcepcionDominio)
def _dominio(error):
    """Una invariante violada es 409, no 500: el sistema funciona bien, la
    operacion es la que no procede."""
    return jsonify({"error": str(error)}), 409


@bp.errorhandler(ValueError)
def _valor(error):
    return jsonify({"error": str(error)}), 400
