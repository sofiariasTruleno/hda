from hda.seedwork.dominio.excepciones import ExcepcionDominio


class TrabajoNoExiste(ExcepcionDominio):
    def __init__(self, trabajo_id):
        super().__init__(f"No existe un trabajo con id {trabajo_id}")


class TipoObjetoNoValido(ExcepcionDominio):
    ...
