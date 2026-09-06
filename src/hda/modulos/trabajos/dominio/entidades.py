"""Agregacion Trabajo.

Frontera transaccional del microservicio de Orquestacion de Trabajos.
Corresponde uno a uno con la agregacion Trabajo de la vista de informacion
HDA-004: entidades internas Diagnostico, Novedad y Ejecucion, y referencias
a otras agregaciones estrictamente por identidad.

Por que Diagnostico, Novedad y Ejecucion son entidades internas y no
agregaciones propias: no tienen ciclo de vida transaccional autonomo fuera
de la orden de servicio. Nadie consulta una Ejecucion sin su Trabajo.
"""
from __future__ import annotations
from hda.seedwork.dominio.fechas import ahora

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from hda.seedwork.dominio.entidades import Entidad, AgregacionRaiz
from hda.seedwork.dominio.objetos_valor import Direccion

from .eventos import (
    DiagnosticoRegistrado,
    EjecucionIniciada,
    NovedadRegistrada,
    ProveedorAsignado,
    SLAIncumplido,
    TrabajoCompletadoIntegracion,
    TrabajoRegistrado,
    TrabajoRegistradoIntegracion,
)
from .objetos_valor import (
    AcuerdoDeServicio,
    Canal,
    CategoriaDeServicio,
    DescripcionDelProblema,
    EstadoSolicitud,
    ResultadoDiagnostico,
    TipoNovedad,
    Urgencia,
    VentanaDeAtencion,
)
from .reglas import (
    EjecucionDebeEstarIniciada,
    ProveedorDebeOperarEnElMercado,
    TrabajoDebeTenerProveedorAsignado,
    TrabajoNoPuedeEstarEnEstadoTerminal,
    TransicionDeEstadoValida,
    VentanaDeAtencionEnFuturo,
)


# ------------------------------------------------------- entidades internas

@dataclass
class Diagnostico(Entidad):
    """Evaluacion tecnica previa a la ejecucion."""
    resultado: ResultadoDiagnostico = None
    diagnosticado_por: str = None
    fecha_diagnostico: datetime = field(default_factory=ahora)


@dataclass
class Novedad(Entidad):
    """Desviacion ocurrida durante la ejecucion."""
    tipo: TipoNovedad = None
    descripcion: str = None
    bloquea_ejecucion: bool = False
    fecha_reporte: datetime = field(default_factory=ahora)


@dataclass
class Ejecucion(Entidad):
    """Realizacion efectiva del trabajo en sitio."""
    proveedor_id: str = None
    fecha_inicio: datetime = None
    fecha_fin: datetime = None

    def iniciar(self, proveedor_id: str, momento: datetime = None):
        self.proveedor_id = proveedor_id
        self.fecha_inicio = momento or ahora()

    def finalizar(self, momento: datetime = None):
        self.fecha_fin = momento or ahora()

    def duracion_horas(self) -> float | None:
        if not self.fecha_inicio or not self.fecha_fin:
            return None
        return (self.fecha_fin - self.fecha_inicio).total_seconds() / 3600


# ------------------------------------------------------------ raiz

@dataclass
class Trabajo(AgregacionRaiz):
    """Raiz de la agregacion. Unico punto de entrada a la frontera.

    Todos los metodos publicos siguen la misma estructura, y esa regularidad
    es intencional:

        1. validar invariantes con `validar_regla`
        2. mutar el estado interno
        3. emitir el evento correspondiente

    Nunca al reves. Si se mutara antes de validar, el agregado podria quedar
    en un estado invalido cuando la regla falle.
    """

    # --- datos propios
    dueno_de_hogar_id: str = None
    mercado_id: str = None
    partner_id: str | None = None

    categoria: CategoriaDeServicio = None
    urgencia: Urgencia = Urgencia.MEDIA
    canal: Canal = Canal.MARKETPLACE
    direccion: Direccion = None
    ventana_atencion: VentanaDeAtencion = None
    descripcion: DescripcionDelProblema = None
    acuerdo_servicio: AcuerdoDeServicio = None

    estado: EstadoSolicitud = EstadoSolicitud.REGISTRADO

    # --- referencias a otras agregaciones, por identidad
    proveedor_id: str | None = None
    cotizacion_id: str | None = None

    # --- entidades internas
    diagnostico: Diagnostico | None = None
    ejecucion: Ejecucion | None = None
    novedades: list[Novedad] = field(default_factory=list)

    fecha_registro: datetime = field(default_factory=ahora)
    fecha_completado: datetime | None = None

    # ------------------------------------------------------- ciclo de vida

    def registrar(self):
        """Publica el trabajo. Se invoca desde la fabrica, no desde la API."""
        self.validar_regla(VentanaDeAtencionEnFuturo(self.ventana_atencion))

        if not self.acuerdo_servicio:
            self.acuerdo_servicio = AcuerdoDeServicio.desde_urgencia(
                self.urgencia, self.canal
            )

        self.estado = EstadoSolicitud.REGISTRADO

        # Evento de dominio: lo consumen modulos internos del servicio.
        self.agregar_evento(
            TrabajoRegistrado(
                trabajo_id=str(self.id),
                dueno_de_hogar_id=self.dueno_de_hogar_id,
                mercado_id=self.mercado_id,
                partner_id=self.partner_id,
                categoria=self.categoria.codigo,
                urgencia=self.urgencia.value,
                canal=self.canal.value,
                horas_sla=self.acuerdo_servicio.horas_respuesta,
            )
        )

        # Evento de integracion: lo consume Emparejamiento y Asignacion.
        self.agregar_evento(
            TrabajoRegistradoIntegracion(
                trabajo_id=str(self.id),
                mercado_id=self.mercado_id,
                categoria=self.categoria.codigo,
                urgencia=self.urgencia.value,
                ciudad=self.direccion.ciudad,
            )
        )

    def asignar_proveedor(self, proveedor_id: str, mercado_proveedor: str,
                          cotizacion_id: str | None = None):
        self.validar_regla(TrabajoNoPuedeEstarEnEstadoTerminal(self.estado))
        self.validar_regla(
            TransicionDeEstadoValida(self.estado, EstadoSolicitud.ASIGNADO)
        )
        self.validar_regla(
            ProveedorDebeOperarEnElMercado(self.mercado_id, mercado_proveedor)
        )

        self.proveedor_id = proveedor_id
        self.cotizacion_id = cotizacion_id
        self.estado = EstadoSolicitud.ASIGNADO
        self.tocar()

        self.agregar_evento(
            ProveedorAsignado(
                trabajo_id=str(self.id),
                proveedor_id=proveedor_id,
                cotizacion_id=cotizacion_id,
                mercado_id=self.mercado_id,
            )
        )

    def registrar_diagnostico(self, hallazgo: str, requiere_repuesto: bool,
                              diagnosticado_por: str):
        self.validar_regla(TrabajoNoPuedeEstarEnEstadoTerminal(self.estado))
        self.validar_regla(TrabajoDebeTenerProveedorAsignado(self.proveedor_id))

        self.diagnostico = Diagnostico(
            resultado=ResultadoDiagnostico(hallazgo, requiere_repuesto),
            diagnosticado_por=diagnosticado_por,
        )
        self.tocar()

        self.agregar_evento(
            DiagnosticoRegistrado(
                trabajo_id=str(self.id),
                hallazgo=hallazgo,
                requiere_repuesto=requiere_repuesto,
            )
        )

    def iniciar_ejecucion(self, momento: datetime = None):
        self.validar_regla(TrabajoNoPuedeEstarEnEstadoTerminal(self.estado))
        self.validar_regla(TrabajoDebeTenerProveedorAsignado(self.proveedor_id))
        self.validar_regla(
            TransicionDeEstadoValida(self.estado, EstadoSolicitud.EN_EJECUCION)
        )

        self.ejecucion = Ejecucion()
        self.ejecucion.iniciar(self.proveedor_id, momento)
        self.estado = EstadoSolicitud.EN_EJECUCION
        self.tocar()

        self.agregar_evento(
            EjecucionIniciada(
                trabajo_id=str(self.id),
                proveedor_id=self.proveedor_id,
                fecha_inicio=self.ejecucion.fecha_inicio,
            )
        )

    def registrar_novedad(self, tipo: TipoNovedad, descripcion: str,
                          bloquea_ejecucion: bool = False):
        self.validar_regla(TrabajoNoPuedeEstarEnEstadoTerminal(self.estado))
        self.validar_regla(EjecucionDebeEstarIniciada(self.ejecucion))

        novedad = Novedad(
            tipo=tipo,
            descripcion=descripcion,
            bloquea_ejecucion=bloquea_ejecucion,
        )
        self.novedades.append(novedad)
        self.tocar()

        self.agregar_evento(
            NovedadRegistrada(
                trabajo_id=str(self.id),
                tipo=tipo.value,
                descripcion=descripcion,
                bloquea_ejecucion=bloquea_ejecucion,
            )
        )

    def completar(self, momento: datetime = None):
        """Cierre del ciclo. Emite el evento de integracion que dispara el
        recalculo de reputacion (escenario SC-ESC-03), el pago y la
        liquidacion."""
        self.validar_regla(TrabajoNoPuedeEstarEnEstadoTerminal(self.estado))
        self.validar_regla(
            TransicionDeEstadoValida(self.estado, EstadoSolicitud.COMPLETADO)
        )
        self.validar_regla(EjecucionDebeEstarIniciada(self.ejecucion))

        momento = momento or ahora()
        self.ejecucion.finalizar(momento)
        self.estado = EstadoSolicitud.COMPLETADO
        self.fecha_completado = momento
        self.tocar()

        duracion = self.ejecucion.duracion_horas() or 0.0
        horas_totales = (momento - self.fecha_registro).total_seconds() / 3600
        cumplio = horas_totales <= self.acuerdo_servicio.horas_respuesta

        if not cumplio:
            # Evento de dominio: se queda dentro del servicio.
            self.agregar_evento(
                SLAIncumplido(
                    trabajo_id=str(self.id),
                    horas_comprometidas=self.acuerdo_servicio.horas_respuesta,
                    horas_reales=round(horas_totales, 2),
                )
            )

        # Evento de integracion: cruza la frontera del microservicio.
        self.agregar_evento(
            TrabajoCompletadoIntegracion(
                trabajo_id=str(self.id),
                proveedor_id=self.proveedor_id,
                dueno_de_hogar_id=self.dueno_de_hogar_id,
                mercado_id=self.mercado_id,
                categoria=self.categoria.codigo,
                duracion_horas=round(duracion, 2),
                cumplio_sla=cumplio,
                fecha_completado=momento,
            )
        )

    def cancelar(self, motivo: str):
        self.validar_regla(TrabajoNoPuedeEstarEnEstadoTerminal(self.estado))
        self.validar_regla(
            TransicionDeEstadoValida(self.estado, EstadoSolicitud.CANCELADO)
        )
        self.estado = EstadoSolicitud.CANCELADO
        self.tocar()
        self.agregar_evento(
            NovedadRegistrada(
                trabajo_id=str(self.id),
                tipo="CANCELACION",
                descripcion=motivo,
                bloquea_ejecucion=True,
            )
        )

    # -------------------------------------------------------------- consultas

    def tiene_novedades_bloqueantes(self) -> bool:
        return any(n.bloquea_ejecucion for n in self.novedades)
