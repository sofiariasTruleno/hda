"""Fabrica de la aplicacion Flask.

Flask es solo un adaptador de entrada. Toda la logica vive por debajo y no
sabe que existe un servidor HTTP.
"""
import logging
import os

from flask import Flask, jsonify

from hda.seedwork.dominio.excepciones import ExcepcionDominio
from hda.modulos.trabajos.dominio.excepciones import TrabajoNoExiste


def registrar_handlers_dominio():
    """Suscribe los modulos internos a los eventos de dominio.

    Se hace al arrancar. Si esto no corriera, los modulos Cumplimiento y
    Seguimiento quedarian sordos, y ese es justamente el acoplamiento que
    los eventos de dominio evitan: el modulo Trabajos no los conoce.
    """
    from hda.modulos.cumplimiento.aplicacion import handlers as h_cumplimiento
    from hda.modulos.seguimiento.aplicacion import handlers as h_seguimiento

    h_cumplimiento.registrar_suscriptores()
    h_seguimiento.registrar_suscriptores()


def importar_modulos_alchemy():
    from hda.modulos.trabajos.infraestructura import dto  # noqa: F401


def crear_app(configuracion=None):
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("HDA_SECRET_KEY", "dev")

    if configuracion:
        app.config.update(configuracion)

    importar_modulos_alchemy()

    from hda.config.db import init_db, Session
    init_db()

    registrar_handlers_dominio()

    from . import trabajos
    app.register_blueprint(trabajos.bp)

    @app.teardown_appcontext
    def cerrar_sesion(exception=None):
        Session.remove()

    @app.errorhandler(TrabajoNoExiste)
    def _no_existe(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(ExcepcionDominio)
    def _dominio(error):
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(ValueError)
    def _valor(error):
        return jsonify({"error": str(error)}), 400

    @app.route("/salud")
    def salud():
        return jsonify({"estado": "ok", "servicio": "orquestacion-trabajos"}), 200

    return app
