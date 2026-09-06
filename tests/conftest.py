"""Configuracion de pruebas.

Cada prueba recibe una base de datos limpia y un despachador de eventos
limpio. Sin esto, el orden de ejecucion afectaria los resultados.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ["HDA_DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture
def app():
    from hda.api import crear_app
    from hda.config.db import Session, drop_db, init_db
    from hda.seedwork.aplicacion.handlers import despachador_dominio
    from hda.seedwork.infraestructura.despachadores import despachador_integracion
    from hda.modulos.seguimiento.infraestructura.proyeccion import proyeccion_seguimiento
    from hda.modulos.cumplimiento.aplicacion.handlers import repositorio_cumplimiento

    despachador_dominio.limpiar()
    despachador_integracion.limpiar()
    proyeccion_seguimiento.limpiar()
    repositorio_cumplimiento.limpiar()

    Session.remove()
    drop_db()

    aplicacion = crear_app({"TESTING": True})

    yield aplicacion

    Session.remove()
    drop_db()


@pytest.fixture
def cliente(app):
    return app.test_client()
