from dataclasses import dataclass
from enum import Enum

LARGO_LEGAJO = 5
SIN_AREA = 0
PALABRA_URGENTE = "urgente"


class ErrorDeNegocio(Exception):
    pass


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

    @property
    def es_final(self):
        return self in (EstadoSolicitud.RESUELTA, EstadoSolicitud.RECHAZADA)


class Prioridad(EnumConCodigo):
    BAJA = (1, "Baja")
    MEDIA = (2, "Media")
    ALTA = (3, "Alta")

    def subir(self):
        prioridades = list(Prioridad)
        posicion = prioridades.index(self)
        return prioridades[min(posicion + 1, len(prioridades) - 1)]


class TipoSolicitud(EnumConCodigo):
    CERTIFICADO_ALUMNO_REGULAR = (1, "Certificado de alumno regular", Prioridad.BAJA)
    EQUIVALENCIA = (2, "Equivalencia", Prioridad.MEDIA)
    CAMBIO_DE_COMISION = (3, "Cambio de comision", Prioridad.MEDIA)
    RECLAMO_DE_NOTA = (4, "Reclamo de nota", Prioridad.ALTA)

    def __init__(self, codigo, etiqueta, prioridad_base):
        super().__init__(codigo, etiqueta)
        self.prioridad_base = prioridad_base


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


@dataclass(frozen=True)
class DatosSolicitud:
    estudiante: Estudiante
    tipo: TipoSolicitud
    descripcion: str

    def calcular_prioridad(self):
        prioridad = self.tipo.prioridad_base
        if PALABRA_URGENTE in self.descripcion.lower():
            prioridad = prioridad.subir()
        return prioridad


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

    @classmethod
    def crear(cls, numero, datos, fecha):
        estudiante = datos.estudiante
        return cls(numero, estudiante.legajo, estudiante.nombre_completo, estudiante.email, datos.tipo,
                   datos.descripcion, datos.calcular_prioridad(), EstadoSolicitud.PENDIENTE, SIN_AREA, fecha)

    @property
    def esta_cerrada(self):
        return self.estado.es_final

    @property
    def tiene_responsable(self):
        return self.area != SIN_AREA

    def cambiar_estado(self, nuevo):
        if self.esta_cerrada:
            raise ErrorDeNegocio("la solicitud esta cerrada y no puede modificarse")
        if nuevo is self.estado:
            raise ErrorDeNegocio("la solicitud ya se encuentra en ese estado")
        if self.estado is EstadoSolicitud.PENDIENTE and nuevo is EstadoSolicitud.RESUELTA:
            raise ErrorDeNegocio("una solicitud pendiente no puede resolverse sin pasar por En proceso")
        if nuevo is EstadoSolicitud.EN_PROCESO and not self.tiene_responsable:
            raise ErrorDeNegocio("debe asignar un responsable antes de pasar a En proceso")
        self.estado = nuevo

    def asignar_area(self, area):
        if self.esta_cerrada:
            raise ErrorDeNegocio("no se puede asignar una solicitud cerrada")
        self.area = area.numero

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
