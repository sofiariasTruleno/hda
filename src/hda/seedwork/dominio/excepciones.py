"""Excepciones base del seedwork.

Aisla al dominio de excepciones de infraestructura: ninguna capa externa
debe filtrar sus errores hacia adentro del hexagono.
"""
from dataclasses import dataclass


class ExcepcionDominio(Exception):
    """Raiz de toda excepcion originada en la capa de dominio."""
    ...


class ExcepcionReglaDeNegocio(ExcepcionDominio):
    """Se lanza cuando una regla de negocio no se cumple."""

    def __init__(self, regla):
        self.regla = regla
        super().__init__(str(regla))


class ExcepcionFabrica(ExcepcionDominio):
    """Se lanza cuando una fabrica recibe un objeto que no sabe construir."""
    ...


class ExcepcionTipoObjetoNoExiste(ExcepcionFabrica):
    def __init__(self, mensaje="No existe una implementacion para el tipo solicitado"):
        self.__mensaje = mensaje
        super().__init__(mensaje)

    def __str__(self):
        return self.__mensaje
