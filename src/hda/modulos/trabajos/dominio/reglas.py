"""Invariantes de la agregacion Trabajo.

Cada regla es un objeto con nombre. En la sustentacion esto se defiende asi:
la maquina de estados no vive dispersa en `if`s dentro de los metodos, vive
en objetos que se pueden listar, probar y explicar uno por uno.
"""
from hda.seedwork.dominio.fechas import ahora
from datetime import datetime

from hda.seedwork.dominio.reglas import ReglaNegocio

from .objetos_valor import EstadoSolicitud, VentanaDeAtencion


class TransicionDeEstadoValida(ReglaNegocio):
    """Unica fuente de verdad de la maquina de estados del Trabajo."""

    TRANSICIONES = {
        EstadoSolicitud.REGISTRADO: {EstadoSolicitud.ASIGNADO, EstadoSolicitud.CANCELADO},
        EstadoSolicitud.ASIGNADO: {EstadoSolicitud.EN_EJECUCION, EstadoSolicitud.CANCELADO},
        EstadoSolicitud.EN_EJECUCION: {EstadoSolicitud.COMPLETADO, EstadoSolicitud.CANCELADO},
        EstadoSolicitud.COMPLETADO: set(),
        EstadoSolicitud.CANCELADO: set(),
    }

    def __init__(self, actual: EstadoSolicitud, destino: EstadoSolicitud, mensaje=None):
        self.actual = actual
        self.destino = destino
        super().__init__(
            mensaje or f"No se permite pasar de {actual.value} a {destino.value}"
        )

    def es_valido(self) -> bool:
        return self.destino in self.TRANSICIONES.get(self.actual, set())


class TrabajoDebeTenerProveedorAsignado(ReglaNegocio):
    def __init__(self, proveedor_id, mensaje=None):
        self.proveedor_id = proveedor_id
        super().__init__(mensaje or "El trabajo no tiene un proveedor asignado")

    def es_valido(self) -> bool:
        return self.proveedor_id is not None


class VentanaDeAtencionEnFuturo(ReglaNegocio):
    def __init__(self, ventana: VentanaDeAtencion, momento: datetime = None, mensaje=None):
        self.ventana = ventana
        self.momento = momento or ahora()
        super().__init__(mensaje or "La ventana de atencion no puede estar en el pasado")

    def es_valido(self) -> bool:
        return self.ventana.fin > self.momento


class TrabajoNoPuedeEstarEnEstadoTerminal(ReglaNegocio):
    def __init__(self, estado: EstadoSolicitud, mensaje=None):
        self.estado = estado
        super().__init__(
            mensaje or f"El trabajo esta en estado terminal ({estado.value}) y no admite cambios"
        )

    def es_valido(self) -> bool:
        return not self.estado.es_terminal()


class ProveedorDebeOperarEnElMercado(ReglaNegocio):
    """Mantiene la frontera con la agregacion Mercado: el Trabajo no conoce
    las reglas territoriales, solo recibe el veredicto ya resuelto."""

    def __init__(self, mercado_trabajo: str, mercado_proveedor: str, mensaje=None):
        self.mercado_trabajo = mercado_trabajo
        self.mercado_proveedor = mercado_proveedor
        super().__init__(
            mensaje or "El proveedor no opera en el mercado del trabajo"
        )

    def es_valido(self) -> bool:
        return self.mercado_trabajo == self.mercado_proveedor


class EjecucionDebeEstarIniciada(ReglaNegocio):
    def __init__(self, ejecucion, mensaje=None):
        self.ejecucion = ejecucion
        super().__init__(mensaje or "No existe una ejecucion iniciada para este trabajo")

    def es_valido(self) -> bool:
        return self.ejecucion is not None and self.ejecucion.fecha_inicio is not None
