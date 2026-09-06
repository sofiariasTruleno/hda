from hda.seedwork.dominio.fechas import ahora
from datetime import datetime


def time_millis() -> int:
    return int(ahora().timestamp() * 1000)


def a_iso(fecha: datetime | None) -> str | None:
    return fecha.isoformat() if fecha else None
