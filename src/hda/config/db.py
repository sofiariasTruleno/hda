"""Configuracion del manejador de base de datos.

SQLAlchemy puro, sin Flask-SQLAlchemy, a proposito: la persistencia no debe
depender del framework web. Si manana la entrada deja de ser HTTP y pasa a
ser un consumidor de Kafka, esta capa no cambia.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

Base = declarative_base()

DATABASE_URL = os.getenv("HDA_DATABASE_URL", "sqlite:///hda_trabajos.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Session = scoped_session(SessionFactory)


def init_db():
    """Crea el esquema. Importa los modelos para que queden registrados."""
    from hda.modulos.trabajos.infraestructura import dto  # noqa: F401
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)
