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


AREAS_RESPONSABLES = (
    Area(1, "Bedelia", "Laura Gomez"),
    Area(2, "Secretaria Academica", "Martin Ruiz"),
    Area(3, "Departamento de Alumnos", "Sofia Herrera"),
)


def validar_legajo(legajo):
    if not (legajo.isdigit() and len(legajo) == LARGO_LEGAJO):
        raise ErrorDeNegocio(f"legajo invalido (debe tener {LARGO_LEGAJO} digitos)")


def email_valido(email):
    return "@" in email and "." in email.split("@")[-1]


@dataclass
class Estudiante:
    legajo: str
    nombre: str
    apellido: str
    email: str

    @classmethod
    def nuevo(cls, legajo, nombre, apellido, email):
        # Mismo orden de validacion que la version base, para mostrar los mismos mensajes.
        validar_legajo(legajo)
        if nombre == "" or apellido == "":
            raise ErrorDeNegocio("nombre y apellido son obligatorios")
        if not email_valido(email):
            raise ErrorDeNegocio("email invalido")
        return cls(legajo, nombre, apellido, email)

    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    def a_diccionario(self):
        return {
            "legajo": self.legajo,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(datos["legajo"], datos["nombre"], datos["apellido"], datos["email"])


@dataclass(frozen=True)
class DatosSolicitud:
    estudiante: Estudiante
    tipo: TipoSolicitud
    descripcion: str

    def __post_init__(self):
        if self.descripcion.strip() == "":
            raise ErrorDeNegocio("la descripcion es obligatoria")

    def calcular_prioridad(self):
        prioridad = self.tipo.prioridad_base
        if PALABRA_URGENTE in self.descripcion.lower():
            prioridad = prioridad.subir()
        return prioridad


@dataclass
class Solicitud:
    # El nombre y el email del estudiante se guardan copiados dentro de la
    # solicitud para mantener el formato de datos.json de la version base.
    numero: int
    legajo: str
    nombre_estudiante: str
    email_estudiante: str
    tipo: TipoSolicitud
    descripcion: str
    prioridad: Prioridad
    estado: EstadoSolicitud
    numero_area: int
    fecha: str

    @classmethod
    def crear(cls, numero, datos, fecha):
        estudiante = datos.estudiante
        return cls(
            numero=numero,
            legajo=estudiante.legajo,
            nombre_estudiante=estudiante.nombre_completo,
            email_estudiante=estudiante.email,
            tipo=datos.tipo,
            descripcion=datos.descripcion,
            prioridad=datos.calcular_prioridad(),
            estado=EstadoSolicitud.PENDIENTE,
            numero_area=SIN_AREA,
            fecha=fecha,
        )

    @property
    def esta_cerrada(self):
        return self.estado.es_final

    @property
    def tiene_responsable(self):
        return self.numero_area != SIN_AREA

    def verificar_que_admite_cambio_de_estado(self):
        if self.esta_cerrada:
            raise ErrorDeNegocio("la solicitud esta cerrada y no puede modificarse")

    def verificar_que_admite_asignacion(self):
        if self.esta_cerrada:
            raise ErrorDeNegocio("no se puede asignar una solicitud cerrada")

    def cambiar_estado(self, nuevo):
        self.verificar_que_admite_cambio_de_estado()
        if nuevo is self.estado:
            raise ErrorDeNegocio("la solicitud ya se encuentra en ese estado")
        if self.estado is EstadoSolicitud.PENDIENTE and nuevo is EstadoSolicitud.RESUELTA:
            raise ErrorDeNegocio(
                "una solicitud pendiente no puede resolverse sin pasar por En proceso")
        if nuevo is EstadoSolicitud.EN_PROCESO and not self.tiene_responsable:
            raise ErrorDeNegocio("debe asignar un responsable antes de pasar a En proceso")
        self.estado = nuevo

    def asignar_area(self, area):
        self.verificar_que_admite_asignacion()
        self.numero_area = area.numero

    def a_diccionario(self):
        return {
            "id": self.numero,
            "legajo": self.legajo,
            "estudiante": self.nombre_estudiante,
            "email": self.email_estudiante,
            "tipo": self.tipo.codigo,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad.codigo,
            "estado": self.estado.codigo,
            "area": self.numero_area,
            "fecha": self.fecha,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(
            numero=datos["id"],
            legajo=datos["legajo"],
            nombre_estudiante=datos["estudiante"],
            email_estudiante=datos["email"],
            tipo=TipoSolicitud.desde_codigo(datos["tipo"]),
            descripcion=datos["descripcion"],
            prioridad=Prioridad.desde_codigo(datos["prioridad"]),
            estado=EstadoSolicitud.desde_codigo(datos["estado"]),
            numero_area=datos["area"],
            fecha=datos["fecha"],
        )
