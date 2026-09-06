"""DTOs de la capa de aplicacion.

Existen para que la API nunca reciba ni devuelva objetos de dominio. Si la
API hablara directamente con el agregado, cualquier cambio en el modelo
romperia el contrato HTTP.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DTO:
    ...
