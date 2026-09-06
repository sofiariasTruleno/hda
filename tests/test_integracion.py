"""Pruebas de integracion: API + persistencia + eventos.

Verifican los cinco items de la rubrica de implementacion de punta a punta.
"""
from datetime import timedelta

from hda.seedwork.dominio.fechas import ahora


def payload_trabajo(**extra):
    inicio = ahora() + timedelta(hours=2)
    fin = ahora() + timedelta(hours=6)
    base = {
        "dueno_de_hogar_id": "dh-001",
        "mercado_id": "CO",
        "categoria": "PLOMERIA",
        "urgencia": "ALTA",
        "canal": "MARKETPLACE",
        "descripcion": "Fuga de agua bajo el lavaplatos de la cocina",
        "direccion": {"linea": "Calle 100 #15-20", "ciudad": "Bogota", "pais": "Colombia"},
        "ventana_atencion": {"inicio": inicio.isoformat(), "fin": fin.isoformat()},
    }
    base.update(extra)
    return base


def test_salud(cliente):
    assert cliente.get("/salud").status_code == 200


def test_crear_y_recuperar_trabajo(cliente):
    respuesta = cliente.post("/trabajos", json=payload_trabajo())
    assert respuesta.status_code == 201
    creado = respuesta.get_json()
    assert creado["estado"] == "REGISTRADO"
    assert creado["horas_sla"] == 8

    recuperado = cliente.get(f"/trabajos/{creado['id']}")
    assert recuperado.status_code == 200
    assert recuperado.get_json()["id"] == creado["id"]


def test_persistencia_sobrevive_a_la_consulta(cliente):
    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    listado = cliente.get("/trabajos").get_json()
    assert any(t["id"] == creado["id"] for t in listado)


def test_flujo_completo_por_api(cliente):
    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    tid = creado["id"]

    r = cliente.put(f"/trabajos/{tid}/proveedor",
                    json={"proveedor_id": "prov-1", "mercado_proveedor": "CO"})
    assert r.status_code == 200 and r.get_json()["estado"] == "ASIGNADO"

    r = cliente.post(f"/trabajos/{tid}/diagnostico",
                     json={"hallazgo": "Sifon roto", "requiere_repuesto": True,
                           "diagnosticado_por": "prov-1"})
    assert r.status_code == 201

    r = cliente.post(f"/trabajos/{tid}/ejecucion")
    assert r.status_code == 200 and r.get_json()["estado"] == "EN_EJECUCION"

    r = cliente.post(f"/trabajos/{tid}/novedades",
                     json={"tipo": "RETRASO", "descripcion": "Trafico en la 100"})
    assert r.status_code == 201

    r = cliente.post(f"/trabajos/{tid}/completar")
    assert r.status_code == 200
    final = r.get_json()
    assert final["estado"] == "COMPLETADO"
    assert final["ejecucion"]["duracion_horas"] is not None
    assert len(final["novedades"]) == 1


def test_invariante_violada_devuelve_409(cliente):
    """Completar sin ejecucion no es un error del sistema, es una operacion
    que el dominio no permite."""
    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    r = cliente.post(f"/trabajos/{creado['id']}/completar")
    assert r.status_code == 409


def test_proveedor_de_otro_mercado_rechazado_por_api(cliente):
    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    r = cliente.put(f"/trabajos/{creado['id']}/proveedor",
                    json={"proveedor_id": "prov-br", "mercado_proveedor": "BR"})
    assert r.status_code == 409


def test_trabajo_inexistente_devuelve_404(cliente):
    import uuid
    r = cliente.get(f"/trabajos/{uuid.uuid4()}")
    assert r.status_code == 404


def test_filtro_por_mercado(cliente):
    cliente.post("/trabajos", json=payload_trabajo(mercado_id="CO"))
    cliente.post("/trabajos", json=payload_trabajo(mercado_id="BR"))
    solo_br = cliente.get("/trabajos?mercado_id=BR").get_json()
    assert len(solo_br) == 1 and solo_br[0]["mercado_id"] == "BR"


# ------------------------------------------------- eventos de dominio

def test_eventos_de_dominio_alimentan_la_proyeccion_de_seguimiento(cliente):
    """El modulo Seguimiento se entera del ciclo de vida SIN consultar el
    repositorio de Trabajos. Solo escucha eventos de dominio."""
    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    tid = creado["id"]

    seguimiento = cliente.get(f"/trabajos/{tid}/seguimiento").get_json()
    assert seguimiento["estado"] == "REGISTRADO"
    assert len(seguimiento["hitos"]) == 1

    cliente.put(f"/trabajos/{tid}/proveedor",
                json={"proveedor_id": "prov-1", "mercado_proveedor": "CO"})
    cliente.post(f"/trabajos/{tid}/ejecucion")

    seguimiento = cliente.get(f"/trabajos/{tid}/seguimiento").get_json()
    assert seguimiento["estado"] == "EN_EJECUCION"
    assert seguimiento["proveedor_id"] == "prov-1"
    assert len(seguimiento["hitos"]) == 3


def test_modulo_cumplimiento_reacciona_a_novedad_bloqueante(cliente):
    from hda.modulos.cumplimiento.aplicacion.handlers import repositorio_cumplimiento
    repositorio_cumplimiento.limpiar()

    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    tid = creado["id"]
    cliente.put(f"/trabajos/{tid}/proveedor",
                json={"proveedor_id": "prov-1", "mercado_proveedor": "CO"})
    cliente.post(f"/trabajos/{tid}/ejecucion")
    cliente.post(f"/trabajos/{tid}/novedades",
                 json={"tipo": "ACCESO_DENEGADO", "descripcion": "Nadie abrio",
                       "bloquea_ejecucion": True})

    assert len(repositorio_cumplimiento.alertas()) == 1


# --------------------------------------------- eventos de integracion

def test_evento_de_integracion_se_publica_al_bus(cliente):
    """TrabajoCompletado sale al bus como published language. Es el disparo
    del recalculo de reputacion del escenario SC-ESC-03."""
    from hda.seedwork.infraestructura.despachadores import despachador_integracion
    despachador_integracion.limpiar()

    creado = cliente.post("/trabajos", json=payload_trabajo()).get_json()
    tid = creado["id"]
    cliente.put(f"/trabajos/{tid}/proveedor",
                json={"proveedor_id": "prov-1", "mercado_proveedor": "CO"})
    cliente.post(f"/trabajos/{tid}/ejecucion")
    cliente.post(f"/trabajos/{tid}/completar")

    nombres = [e.nombre for e in despachador_integracion.publicados]
    assert "TrabajoCompletadoIntegracion" in nombres

    evento = next(e for e in despachador_integracion.publicados
                  if e.nombre == "TrabajoCompletadoIntegracion")
    assert evento.proveedor_id == "prov-1"
    assert evento.mercado_id == "CO"
    assert evento.version_esquema == "v1"


def test_eventos_solo_se_publican_tras_el_commit(cliente):
    """Si la escritura falla, no debe salir ningun evento anunciando un
    hecho que no ocurrio."""
    from hda.seedwork.infraestructura.despachadores import despachador_integracion
    despachador_integracion.limpiar()

    malo = payload_trabajo(categoria="ASTROFISICA")
    respuesta = cliente.post("/trabajos", json=malo)
    assert respuesta.status_code == 400
    assert despachador_integracion.publicados == []
