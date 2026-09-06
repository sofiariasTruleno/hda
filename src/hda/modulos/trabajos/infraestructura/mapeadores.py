"""Mapeador de persistencia: agregacion Trabajo <-> TrabajoDBO.

Adaptador del hexagono por el lado de salida. Reconstruye el agregado
completo, incluidas sus entidades internas, porque la agregacion es la
unidad de carga: no se lee media agregacion.
"""
import uuid

from hda.seedwork.dominio.objetos_valor import Direccion
from hda.seedwork.dominio.repositorios import Mapeador

from hda.modulos.trabajos.dominio.entidades import (
    Diagnostico, Ejecucion, Novedad, Trabajo,
)
from hda.modulos.trabajos.dominio.objetos_valor import (
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

from .dto import DiagnosticoDBO, EjecucionDBO, NovedadDBO, TrabajoDBO


class MapeadorTrabajoDBO(Mapeador):

    def obtener_tipo(self) -> type:
        return Trabajo

    # ------------------------------------------------------ dominio -> tabla

    def entidad_a_dto(self, entidad: Trabajo) -> TrabajoDBO:
        dbo = TrabajoDBO(
            id=str(entidad.id),
            dueno_de_hogar_id=entidad.dueno_de_hogar_id,
            mercado_id=entidad.mercado_id,
            partner_id=entidad.partner_id,
            categoria=entidad.categoria.codigo,
            urgencia=entidad.urgencia.value,
            canal=entidad.canal.value,
            estado=entidad.estado.value,
            proveedor_id=entidad.proveedor_id,
            cotizacion_id=entidad.cotizacion_id,
            descripcion=entidad.descripcion.texto,
            direccion_linea=entidad.direccion.linea,
            direccion_ciudad=entidad.direccion.ciudad,
            direccion_pais=entidad.direccion.pais,
            ventana_inicio=entidad.ventana_atencion.inicio,
            ventana_fin=entidad.ventana_atencion.fin,
            horas_sla=entidad.acuerdo_servicio.horas_respuesta,
            penaliza_incumplimiento=entidad.acuerdo_servicio.penalizacion_por_incumplimiento,
            fecha_registro=entidad.fecha_registro,
            fecha_completado=entidad.fecha_completado,
            fecha_actualizacion=entidad.fecha_actualizacion,
        )
        self.sincronizar_internas(entidad, dbo)
        return dbo

    def sincronizar_internas(self, entidad: Trabajo, dbo: TrabajoDBO):
        """Refleja el estado de las entidades internas sobre el DBO."""
        if entidad.diagnostico:
            dbo.diagnostico = DiagnosticoDBO(
                id=str(entidad.diagnostico.id),
                trabajo_id=str(entidad.id),
                hallazgo=entidad.diagnostico.resultado.hallazgo,
                requiere_repuesto=entidad.diagnostico.resultado.requiere_repuesto,
                diagnosticado_por=entidad.diagnostico.diagnosticado_por,
                fecha_diagnostico=entidad.diagnostico.fecha_diagnostico,
            )

        if entidad.ejecucion:
            dbo.ejecucion = EjecucionDBO(
                id=str(entidad.ejecucion.id),
                trabajo_id=str(entidad.id),
                proveedor_id=entidad.ejecucion.proveedor_id,
                fecha_inicio=entidad.ejecucion.fecha_inicio,
                fecha_fin=entidad.ejecucion.fecha_fin,
            )

        existentes = {n.id for n in dbo.novedades}
        for novedad in entidad.novedades:
            if str(novedad.id) in existentes:
                continue
            dbo.novedades.append(
                NovedadDBO(
                    id=str(novedad.id),
                    trabajo_id=str(entidad.id),
                    tipo=novedad.tipo.value if hasattr(novedad.tipo, "value") else str(novedad.tipo),
                    descripcion=novedad.descripcion,
                    bloquea_ejecucion=novedad.bloquea_ejecucion,
                    fecha_reporte=novedad.fecha_reporte,
                )
            )

    def actualizar_dto(self, entidad: Trabajo, dbo: TrabajoDBO) -> TrabajoDBO:
        """Actualiza un DBO ya adjunto a la sesion, sin reemplazarlo.

        Reemplazarlo romperia el control de concurrencia optimista, porque
        SQLAlchemy perderia la version cargada.
        """
        dbo.estado = entidad.estado.value
        dbo.proveedor_id = entidad.proveedor_id
        dbo.cotizacion_id = entidad.cotizacion_id
        dbo.fecha_completado = entidad.fecha_completado
        dbo.fecha_actualizacion = entidad.fecha_actualizacion
        self.sincronizar_internas(entidad, dbo)
        return dbo

    # ------------------------------------------------------ tabla -> dominio

    def dto_a_entidad(self, dto: TrabajoDBO) -> Trabajo:
        trabajo = Trabajo(
            id=uuid.UUID(dto.id),
            dueno_de_hogar_id=dto.dueno_de_hogar_id,
            mercado_id=dto.mercado_id,
            partner_id=dto.partner_id,
            categoria=CategoriaDeServicio.de_codigo(dto.categoria),
            urgencia=Urgencia(dto.urgencia),
            canal=Canal(dto.canal),
            direccion=Direccion(
                linea=dto.direccion_linea,
                ciudad=dto.direccion_ciudad,
                pais=dto.direccion_pais,
            ),
            ventana_atencion=VentanaDeAtencion(dto.ventana_inicio, dto.ventana_fin),
            descripcion=DescripcionDelProblema(dto.descripcion),
            acuerdo_servicio=AcuerdoDeServicio(
                horas_respuesta=dto.horas_sla,
                penalizacion_por_incumplimiento=bool(dto.penaliza_incumplimiento),
            ),
            estado=EstadoSolicitud(dto.estado),
            proveedor_id=dto.proveedor_id,
            cotizacion_id=dto.cotizacion_id,
            fecha_registro=dto.fecha_registro,
            fecha_completado=dto.fecha_completado,
        )

        # El agregado se rehidrata sin eventos: reconstruir no es un hecho
        # de negocio nuevo.
        trabajo.limpiar_eventos()

        if dto.diagnostico:
            trabajo.diagnostico = Diagnostico(
                id=uuid.UUID(dto.diagnostico.id),
                resultado=ResultadoDiagnostico(
                    dto.diagnostico.hallazgo,
                    bool(dto.diagnostico.requiere_repuesto),
                ),
                diagnosticado_por=dto.diagnostico.diagnosticado_por,
                fecha_diagnostico=dto.diagnostico.fecha_diagnostico,
            )

        if dto.ejecucion:
            ejecucion = Ejecucion(id=uuid.UUID(dto.ejecucion.id))
            ejecucion.proveedor_id = dto.ejecucion.proveedor_id
            ejecucion.fecha_inicio = dto.ejecucion.fecha_inicio
            ejecucion.fecha_fin = dto.ejecucion.fecha_fin
            trabajo.ejecucion = ejecucion

        trabajo.novedades = [
            Novedad(
                id=uuid.UUID(n.id),
                tipo=TipoNovedad(n.tipo) if n.tipo in TipoNovedad.__members__ else n.tipo,
                descripcion=n.descripcion,
                bloquea_ejecucion=bool(n.bloquea_ejecucion),
                fecha_reporte=n.fecha_reporte,
            )
            for n in dto.novedades
        ]

        return trabajo
