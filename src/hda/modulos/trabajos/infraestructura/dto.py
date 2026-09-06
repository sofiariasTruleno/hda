"""Modelos de persistencia (DTOs de infraestructura).

Estas clases NO son el dominio. Son tablas. Existen separadas de las
entidades por una razon concreta: si el agregado Trabajo heredara de Base,
SQLAlchemy dictaria como se modela el negocio, y el dominio quedaria
acoplado al ORM.

Las entidades internas se guardan en tablas propias con llave foranea al
trabajo, y se cargan siempre juntas: la agregacion se lee y se escribe
completa porque esa es su frontera transaccional.
"""
from hda.seedwork.dominio.fechas import ahora
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from hda.config.db import Base


class TrabajoDBO(Base):
    __tablename__ = "trabajos"

    id = Column(String(64), primary_key=True)

    dueno_de_hogar_id = Column(String(64), nullable=False, index=True)
    mercado_id = Column(String(32), nullable=False, index=True)
    partner_id = Column(String(64), nullable=True, index=True)

    categoria = Column(String(32), nullable=False)
    urgencia = Column(String(16), nullable=False)
    canal = Column(String(32), nullable=False)
    estado = Column(String(16), nullable=False, index=True)

    proveedor_id = Column(String(64), nullable=True, index=True)
    cotizacion_id = Column(String(64), nullable=True)

    descripcion = Column(Text, nullable=False)

    direccion_linea = Column(String(255), nullable=False)
    direccion_ciudad = Column(String(120), nullable=False)
    direccion_pais = Column(String(120), nullable=False)

    ventana_inicio = Column(DateTime, nullable=False)
    ventana_fin = Column(DateTime, nullable=False)

    horas_sla = Column(Integer, nullable=False)
    penaliza_incumplimiento = Column(Boolean, default=False)

    fecha_registro = Column(DateTime, default=ahora)
    fecha_completado = Column(DateTime, nullable=True)
    fecha_actualizacion = Column(DateTime, default=ahora)

    # Control de concurrencia optimista. Protege contra escrituras
    # simultaneas sobre el mismo trabajo durante los picos del SC-ESC-01.
    version = Column(Integer, nullable=False, default=1)

    diagnostico = relationship(
        "DiagnosticoDBO", uselist=False, back_populates="trabajo",
        cascade="all, delete-orphan",
    )
    ejecucion = relationship(
        "EjecucionDBO", uselist=False, back_populates="trabajo",
        cascade="all, delete-orphan",
    )
    novedades = relationship(
        "NovedadDBO", back_populates="trabajo",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {"version_id_col": version}


class DiagnosticoDBO(Base):
    __tablename__ = "trabajo_diagnosticos"

    id = Column(String(64), primary_key=True)
    trabajo_id = Column(String(64), ForeignKey("trabajos.id"), nullable=False)
    hallazgo = Column(Text, nullable=False)
    requiere_repuesto = Column(Boolean, default=False)
    diagnosticado_por = Column(String(64), nullable=False)
    fecha_diagnostico = Column(DateTime, default=ahora)

    trabajo = relationship("TrabajoDBO", back_populates="diagnostico")


class EjecucionDBO(Base):
    __tablename__ = "trabajo_ejecuciones"

    id = Column(String(64), primary_key=True)
    trabajo_id = Column(String(64), ForeignKey("trabajos.id"), nullable=False)
    proveedor_id = Column(String(64), nullable=False)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    trabajo = relationship("TrabajoDBO", back_populates="ejecucion")


class NovedadDBO(Base):
    __tablename__ = "trabajo_novedades"

    id = Column(String(64), primary_key=True)
    trabajo_id = Column(String(64), ForeignKey("trabajos.id"), nullable=False)
    tipo = Column(String(32), nullable=False)
    descripcion = Column(Text, nullable=False)
    bloquea_ejecucion = Column(Boolean, default=False)
    fecha_reporte = Column(DateTime, default=ahora)

    trabajo = relationship("TrabajoDBO", back_populates="novedades")
