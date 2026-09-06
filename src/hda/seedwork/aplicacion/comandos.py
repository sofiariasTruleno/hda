"""Lado de ESCRITURA del patron CQS.

Un comando expresa una intencion de cambio ("asigna este proveedor"), se
nombra en imperativo y no retorna datos de negocio. El despacho usa
singledispatch: el tipo del comando resuelve el handler, sin un `if` gigante
ni un registro manual.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatch


@dataclass(frozen=True)
class Comando:
    ...


class ComandoHandler(ABC):
    @abstractmethod
    def handle(self, comando: Comando):
        ...


@singledispatch
def ejecutar_comando(comando):
    raise NotImplementedError(
        f"No existe implementacion para el comando {type(comando).__name__}"
    )
