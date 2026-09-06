"""Persistencia del modulo Cumplimiento.

En memoria a proposito: es un modulo de soporte cuyo estado es derivable
reprocesando eventos. Mantenerlo simple evita que absorba responsabilidades
del core, que es uno de los puntos de sensibilidad de la vista funcional.
"""


class RepositorioCumplimientoEnMemoria:
    def __init__(self):
        self._incumplimientos = []
        self._alertas = []

    def agregar_incumplimiento(self, registro):
        self._incumplimientos.append(registro)

    def agregar_alerta(self, alerta):
        self._alertas.append(alerta)

    def incumplimientos(self) -> list:
        return list(self._incumplimientos)

    def alertas(self) -> list:
        return list(self._alertas)

    def limpiar(self):
        self._incumplimientos = []
        self._alertas = []
