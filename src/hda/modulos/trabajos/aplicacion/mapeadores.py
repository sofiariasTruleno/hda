"""Mapeadores de aplicacion: dominio <-> DTO.

Este mapeador es un ADAPTADOR del hexagono por el lado de entrada/salida
HTTP. El de infraestructura/mapeadores.py adapta el lado de persistencia.
Son dos traducciones distintas y por eso son dos clases distintas.
"""
from datetime import datetime

from hda.seedwork.dominio.objetos_valor import Direccion
from hda.seedwork.dominio.repositorios import Mapeador
from hda.seedwork.infraestructura.utils import a_iso

from hda.modulos.trabajos.dominio.entidades import Trabajo
from hda.modulos.trabajos.dominio.objetos_valor import (
    Canal,
    CategoriaDeServicio,
    DescripcionDelProblema,
    EstadoSolicitud,
    Urgencia,
    VentanaDeAtencion,
)

from .dto import (
    DiagnosticoDTO,
    DireccionDTO,
    EjecucionDTO,
    NovedadDTO,
    TrabajoDTO,
    VentanaDTO,
)


class MapeadorTrabajoDTOJson(Mapeador):
    """Traduce entre JSON crudo de la API y el DTO de aplicacion."""

    def _procesar_ventana(self, ventana: dict) -> VentanaDTO:
        return VentanaDTO(inicio=ventana.get("inicio"), fin=ventana.get("fin"))

    def externo_a_dto(self, externo: dict) -> TrabajoDTO:
        direccion = externo.get("direccion", {}) or {}
        ventana = externo.get("ventana_atencion", {}) or {}
        return TrabajoDTO(
            id=externo.get("id"),
            dueno_de_hogar_id=externo.get("dueno_de_hogar_id"),
            mercado_id=externo.get("mercado_id"),
            partner_id=externo.get("partner_id"),
            categoria=externo.get("categoria"),
            urgencia=externo.get("urgencia"),
            canal=externo.get("canal"),
            descripcion=externo.get("descripcion"),
            direccion=DireccionDTO(
                linea=direccion.get("linea"),
                ciudad=direccion.get("ciudad"),
                pais=direccion.get("pais"),
            ),
            ventana_atencion=self._procesar_ventana(ventana),
        )

    def dto_a_externo(self, dto: TrabajoDTO) -> dict:
        return {
            "id": dto.id,
            "dueno_de_hogar_id": dto.dueno_de_hogar_id,
            "mercado_id": dto.mercado_id,
            "partner_id": dto.partner_id,
            "categoria": dto.categoria,
            "urgencia": dto.urgencia,
            "canal": dto.canal,
            "estado": dto.estado,
            "proveedor_id": dto.proveedor_id,
            "cotizacion_id": dto.cotizacion_id,
            "descripcion": dto.descripcion,
            "direccion": dto.direccion.__dict__ if dto.direccion else None,
            "ventana_atencion": dto.ventana_atencion.__dict__ if dto.ventana_atencion else None,
            "horas_sla": dto.horas_sla,
            "diagnostico": dto.diagnostico.__dict__ if dto.diagnostico else None,
            "ejecucion": dto.ejecucion.__dict__ if dto.ejecucion else None,
            "novedades": [n.__dict__ for n in dto.novedades],
            "fecha_registro": dto.fecha_registro,
            "fecha_completado": dto.fecha_completado,
        }

    def obtener_tipo(self) -> type:
        return TrabajoDTO

    def entidad_a_dto(self, entidad):
        raise NotImplementedError("Use MapeadorTrabajo para traducir el dominio")

    def dto_a_entidad(self, dto):
        raise NotImplementedError("Use MapeadorTrabajo para traducir el dominio")


class MapeadorTrabajo(Mapeador):
    """Traduce entre la agregacion Trabajo y el TrabajoDTO."""

    def obtener_tipo(self) -> type:
        return Trabajo

    def entidad_a_dto(self, entidad: Trabajo) -> TrabajoDTO:
        diagnostico = None
        if entidad.diagnostico:
            diagnostico = DiagnosticoDTO(
                id=str(entidad.diagnostico.id),
                hallazgo=entidad.diagnostico.resultado.hallazgo,
                requiere_repuesto=entidad.diagnostico.resultado.requiere_repuesto,
                diagnosticado_por=entidad.diagnostico.diagnosticado_por,
            )

        ejecucion = None
        if entidad.ejecucion:
            ejecucion = EjecucionDTO(
                id=str(entidad.ejecucion.id),
                proveedor_id=entidad.ejecucion.proveedor_id,
                fecha_inicio=a_iso(entidad.ejecucion.fecha_inicio),
                fecha_fin=a_iso(entidad.ejecucion.fecha_fin),
                duracion_horas=entidad.ejecucion.duracion_horas(),
            )

        return TrabajoDTO(
            id=str(entidad.id),
            dueno_de_hogar_id=entidad.dueno_de_hogar_id,
            mercado_id=entidad.mercado_id,
            partner_id=entidad.partner_id,
            categoria=entidad.categoria.codigo if entidad.categoria else None,
            urgencia=entidad.urgencia.value if entidad.urgencia else None,
            canal=entidad.canal.value if entidad.canal else None,
            estado=entidad.estado.value if entidad.estado else None,
            proveedor_id=entidad.proveedor_id,
            cotizacion_id=entidad.cotizacion_id,
            descripcion=entidad.descripcion.texto if entidad.descripcion else None,
            direccion=DireccionDTO(
                linea=entidad.direccion.linea,
                ciudad=entidad.direccion.ciudad,
                pais=entidad.direccion.pais,
            ) if entidad.direccion else None,
            ventana_atencion=VentanaDTO(
                inicio=a_iso(entidad.ventana_atencion.inicio),
                fin=a_iso(entidad.ventana_atencion.fin),
            ) if entidad.ventana_atencion else None,
            horas_sla=entidad.acuerdo_servicio.horas_respuesta if entidad.acuerdo_servicio else None,
            diagnostico=diagnostico,
            ejecucion=ejecucion,
            novedades=[
                NovedadDTO(
                    id=str(n.id),
                    tipo=n.tipo.value if hasattr(n.tipo, "value") else str(n.tipo),
                    descripcion=n.descripcion,
                    bloquea_ejecucion=n.bloquea_ejecucion,
                    fecha_reporte=a_iso(n.fecha_reporte),
                )
                for n in entidad.novedades
            ],
            fecha_registro=a_iso(entidad.fecha_registro),
            fecha_completado=a_iso(entidad.fecha_completado),
        )

    def dto_a_entidad(self, dto: TrabajoDTO) -> Trabajo:
        return Trabajo(
            dueno_de_hogar_id=dto.dueno_de_hogar_id,
            mercado_id=dto.mercado_id,
            partner_id=dto.partner_id,
            categoria=CategoriaDeServicio.de_codigo(dto.categoria),
            urgencia=Urgencia(dto.urgencia),
            canal=Canal(dto.canal),
            direccion=Direccion(
                linea=dto.direccion.linea,
                ciudad=dto.direccion.ciudad,
                pais=dto.direccion.pais,
            ),
            ventana_atencion=VentanaDeAtencion(
                datetime.fromisoformat(dto.ventana_atencion.inicio),
                datetime.fromisoformat(dto.ventana_atencion.fin),
            ),
            descripcion=DescripcionDelProblema(dto.descripcion),
        )
