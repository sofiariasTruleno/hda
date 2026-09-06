"""Importar todos los comandos registra sus handlers en el singledispatch."""
from .crear_trabajo import CrearTrabajo, CrearTrabajoHandler
from .asignar_proveedor import AsignarProveedor, AsignarProveedorHandler
from .iniciar_ejecucion import IniciarEjecucion, IniciarEjecucionHandler
from .registrar_novedad import RegistrarNovedad, RegistrarNovedadHandler
from .registrar_diagnostico import RegistrarDiagnostico, RegistrarDiagnosticoHandler
from .completar_trabajo import CompletarTrabajo, CompletarTrabajoHandler
