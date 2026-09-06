"""Demostracion ejecutable del ciclo de vida completo.

Sirve para la sustentacion: muestra en consola el orden real de las cosas
-- primero el commit, despues los eventos de dominio, despues los de
integracion -- sin necesidad de levantar el servidor.

    python demo.py
"""
import logging
import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ.setdefault("HDA_DATABASE_URL", "sqlite:///:memory:")

logging.basicConfig(level=logging.INFO, format="%(message)s")

from hda.api import crear_app, registrar_handlers_dominio  # noqa: E402
from hda.seedwork.aplicacion.comandos import ejecutar_comando  # noqa: E402
from hda.seedwork.aplicacion.queries import ejecutar_query  # noqa: E402
from hda.seedwork.dominio.fechas import ahora  # noqa: E402
from hda.seedwork.infraestructura.despachadores import despachador_integracion  # noqa: E402
from hda.modulos.trabajos.aplicacion.comandos import (  # noqa: E402
    AsignarProveedor, CompletarTrabajo, CrearTrabajo,
    IniciarEjecucion, RegistrarNovedad,
)
from hda.modulos.trabajos.aplicacion.queries import ObtenerTrabajo  # noqa: E402
from hda.modulos.seguimiento.infraestructura.proyeccion import proyeccion_seguimiento  # noqa: E402
from hda.modulos.cumplimiento.aplicacion.handlers import repositorio_cumplimiento  # noqa: E402


def titulo(texto):
    print(f"\n{'=' * 68}\n  {texto}\n{'=' * 68}")


def main():
    app = crear_app()

    with app.app_context():
        titulo("1. COMANDO CrearTrabajo (lado de escritura)")
        dto = ejecutar_comando(CrearTrabajo(
            dueno_de_hogar_id="dh-001",
            mercado_id="CO",
            categoria="PLOMERIA",
            urgencia="ALTA",
            canal="PARTNER_B2B2C",
            partner_id="seguros-alpes",
            descripcion="Fuga de agua bajo el lavaplatos de la cocina",
            direccion_linea="Calle 100 #15-20",
            direccion_ciudad="Bogota",
            direccion_pais="Colombia",
            ventana_inicio=ahora() + timedelta(hours=2),
            ventana_fin=ahora() + timedelta(hours=6),
        ))
        tid = dto.id
        print(f"  Trabajo {tid}")
        print(f"  Estado: {dto.estado} | SLA derivado de urgencia ALTA: {dto.horas_sla}h")

        titulo("2. COMANDO AsignarProveedor")
        dto = ejecutar_comando(AsignarProveedor(
            trabajo_id=tid, proveedor_id="prov-042",
            mercado_proveedor="CO", cotizacion_id="cot-77",
        ))
        print(f"  Estado: {dto.estado} | Proveedor: {dto.proveedor_id}")

        titulo("3. COMANDO IniciarEjecucion")
        dto = ejecutar_comando(IniciarEjecucion(trabajo_id=tid))
        print(f"  Estado: {dto.estado}")

        titulo("4. COMANDO RegistrarNovedad (bloqueante)")
        ejecutar_comando(RegistrarNovedad(
            trabajo_id=tid, tipo="REPUESTO_FALTANTE",
            descripcion="Falta sifon de 2 pulgadas", bloquea_ejecucion=True,
        ))
        print(f"  Alertas en modulo Cumplimiento: {len(repositorio_cumplimiento.alertas())}")
        print("  <- el modulo Cumplimiento reacciono SIN conocer la agregacion Trabajo")

        titulo("5. COMANDO CompletarTrabajo")
        dto = ejecutar_comando(CompletarTrabajo(trabajo_id=tid))
        print(f"  Estado: {dto.estado} | Duracion: {dto.ejecucion.duracion_horas:.4f}h "
              f"(la demo corre en milisegundos)")

        titulo("6. QUERY ObtenerTrabajo (lado de lectura)")
        resultado = ejecutar_query(ObtenerTrabajo(id=tid))
        print(f"  Leido desde persistencia: estado={resultado.resultado.estado}")

        titulo("7. PROYECCION de Seguimiento (construida por eventos de dominio)")
        vista = proyeccion_seguimiento.obtener(tid)
        for hito in vista.hitos:
            print(f"  - {hito['descripcion']}")

        titulo("8. EVENTOS DE INTEGRACION publicados al bus")
        for evento in despachador_integracion.publicados:
            print(f"  {evento.nombre} ({evento.version_esquema})")
        print("\n  Estos cruzan la frontera del microservicio: los consumen")
        print("  Emparejamiento y Asignacion, Confianza y Reputacion, Pagos.")

        print()


if __name__ == "__main__":
    main()
