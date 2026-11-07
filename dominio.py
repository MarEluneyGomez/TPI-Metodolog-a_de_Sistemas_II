from enum import Enum

LARGO_LEGAJO = 5
SIN_AREA = 0


class EnumConCodigo(Enum):

    def __init__(self, codigo, etiqueta):
        self.codigo = codigo
        self.etiqueta = etiqueta

    @classmethod
    def desde_codigo(cls, codigo):
        for miembro in cls:
            if miembro.codigo == codigo:
                return miembro
        raise ValueError(f"{cls.__name__}: codigo desconocido {codigo!r}")


class EstadoSolicitud(EnumConCodigo):
    PENDIENTE = ("pend", "Pendiente")
    EN_PROCESO = ("proc", "En proceso")
    RESUELTA = ("res", "Resuelta")
    RECHAZADA = ("rech", "Rechazada")


class TipoSolicitud(EnumConCodigo):
    CERTIFICADO_ALUMNO_REGULAR = (1, "Certificado de alumno regular")
    EQUIVALENCIA = (2, "Equivalencia")
    CAMBIO_DE_COMISION = (3, "Cambio de comision")
    RECLAMO_DE_NOTA = (4, "Reclamo de nota")


class Prioridad(EnumConCodigo):
    BAJA = (1, "Baja")
    MEDIA = (2, "Media")
    ALTA = (3, "Alta")
