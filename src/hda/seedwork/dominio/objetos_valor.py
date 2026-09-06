"""Objetos valor base.

Un objeto valor no tiene identidad: dos instancias con los mismos atributos
son la misma cosa. Se modelan con dataclasses congeladas para garantizar
inmutabilidad, que es la propiedad que los hace seguros de compartir.
"""
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class ObjetoValor(ABC):
    ...


@dataclass(frozen=True)
class Identidad(ObjetoValor):
    """Identificador de agregacion. Envuelve un UUID para que las referencias
    entre agregaciones sean tipadas y no strings sueltos."""
    id: str

    @classmethod
    def nuevo(cls):
        return cls(str(uuid.uuid4()))

    @classmethod
    def de(cls, valor: str):
        try:
            uuid.UUID(str(valor))
        except (ValueError, AttributeError, TypeError):
            raise ValueError(f"El identificador '{valor}' no es un UUID valido")
        return cls(str(valor))

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class Dinero(ObjetoValor):
    """Monto y moneda viajan acoplados a proposito.

    HDA-004 lo justifica por la expansion a Mexico, Brasil y Argentina: un
    monto sin moneda es ambiguo en cuanto hay mas de un mercado activo.
    """
    monto: float
    moneda: str

    def __post_init__(self):
        if self.monto < 0:
            raise ValueError("El monto no puede ser negativo")
        if not self.moneda or len(self.moneda) != 3:
            raise ValueError("La moneda debe ser un codigo ISO-4217 de 3 letras")

    def sumar(self, otro: "Dinero") -> "Dinero":
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden sumar montos de monedas distintas")
        return Dinero(self.monto + otro.monto, self.moneda)


@dataclass(frozen=True)
class Direccion(ObjetoValor):
    linea: str
    ciudad: str
    pais: str
    codigo_postal: str = ""

    def __post_init__(self):
        if not self.linea or not self.ciudad or not self.pais:
            raise ValueError("La direccion requiere linea, ciudad y pais")


@dataclass(frozen=True)
class Periodo(ObjetoValor):
    inicio: datetime
    fin: datetime

    def __post_init__(self):
        if self.fin <= self.inicio:
            raise ValueError("El fin del periodo debe ser posterior al inicio")

    def duracion_horas(self) -> float:
        return (self.fin - self.inicio).total_seconds() / 3600
