from dataclasses import dataclass
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


@dataclass(frozen=True)
class Area:
    numero: int
    nombre: str
    responsable: str


@dataclass
class Estudiante:
    legajo: str
    nombre: str
    apellido: str
    email: str

    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    def a_diccionario(self):
        return {"legajo": self.legajo, "nombre": self.nombre, "apellido": self.apellido, "email": self.email}

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(datos["legajo"], datos["nombre"], datos["apellido"], datos["email"])


@dataclass
class Solicitud:
    numero: int
    legajo: str
    estudiante: str
    email: str
    tipo: TipoSolicitud
    descripcion: str
    prioridad: Prioridad
    estado: EstadoSolicitud
    area: int
    fecha: str

    def a_diccionario(self):
        return {
            "id": self.numero,
            "legajo": self.legajo,
            "estudiante": self.estudiante,
            "email": self.email,
            "tipo": self.tipo.codigo,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad.codigo,
            "estado": self.estado.codigo,
            "area": self.area,
            "fecha": self.fecha,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(
            numero=datos["id"],
            legajo=datos["legajo"],
            estudiante=datos["estudiante"],
            email=datos["email"],
            tipo=TipoSolicitud.desde_codigo(datos["tipo"]),
            descripcion=datos["descripcion"],
            prioridad=Prioridad.desde_codigo(datos["prioridad"]),
            estado=EstadoSolicitud.desde_codigo(datos["estado"]),
            area=datos["area"],
            fecha=datos["fecha"],
        )
