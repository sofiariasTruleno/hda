"""Reloj del dominio.

Un unico punto que devuelve la hora. Dos motivos: evitar `ahora()`,
que esta deprecado en Python 3.12, y poder sustituir el reloj en pruebas sin
parchear la libreria estandar.
"""
from datetime import datetime, timezone


def ahora() -> datetime:
    """UTC sin tzinfo, para que sea comparable con lo que devuelve la base
    de datos en columnas DateTime naive."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
