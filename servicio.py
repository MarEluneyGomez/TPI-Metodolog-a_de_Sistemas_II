from collections import Counter
from dataclasses import dataclass
from datetime import date

from dominio import Area, ErrorDeNegocio, EstadoSolicitud, Estudiante, Solicitud, validar_legajo

# areas responsables (hardcodeadas por ahora)
areas = [
    Area(1, "Bedelia", "Laura Gomez"),
    Area(2, "Secretaria Academica", "Martin Ruiz"),
    Area(3, "Departamento de Alumnos", "Sofia Herrera"),
]


@dataclass(frozen=True)
class Reporte:
    total: int
    por_estado: Counter
    por_tipo: Counter
    por_prioridad: Counter
    sin_responsable: int

    @property
    def porcentaje_resueltas(self):
        return round(self.por_estado[EstadoSolicitud.RESUELTA] * 100 / self.total, 1)


def fecha_de_hoy():
    return date.today().isoformat()


class ServicioSolicitudes:

    def __init__(self, estudiantes, solicitudes, obtener_fecha=fecha_de_hoy):
        self._estudiantes = estudiantes
        self._solicitudes = solicitudes
        self._obtener_fecha = obtener_fecha

    def registrar_estudiante(self, legajo, nombre, apellido, email):
        estudiante = Estudiante.nuevo(legajo, nombre, apellido, email)
        if self._estudiantes.buscar_estudiante(legajo) is not None:
            raise ErrorDeNegocio("ya existe un estudiante con ese legajo")
        self._estudiantes.agregar_estudiante(estudiante)
        return estudiante

    def buscar_estudiante(self, legajo):
        validar_legajo(legajo)
        estudiante = self._estudiantes.buscar_estudiante(legajo)
        if estudiante is None:
            raise ErrorDeNegocio("estudiante no encontrado")
        return estudiante

    def registrar_solicitud(self, datos):
        solicitud = Solicitud.crear(self._solicitudes.proximo_numero(), datos, self._obtener_fecha())
        self._solicitudes.agregar_solicitud(solicitud)
        return solicitud

    def solicitud_para_cambiar_estado(self, numero):
        solicitud = self._obtener_solicitud(numero)
        solicitud.verificar_que_admite_cambio_de_estado()
        return solicitud

    def cambiar_estado(self, numero, nuevo_estado):
        solicitud = self._obtener_solicitud(numero)
        solicitud.cambiar_estado(nuevo_estado)
        self._solicitudes.actualizar_solicitud(solicitud)

    def solicitud_para_asignar(self, numero):
        solicitud = self._obtener_solicitud(numero)
        solicitud.verificar_que_admite_asignacion()
        return solicitud

    def areas_disponibles(self):
        return list(areas)

    def asignar_area(self, numero, numero_area):
        area = self.buscar_area(numero_area)
        if area is None:
            raise ErrorDeNegocio("area invalida")
        solicitud = self._obtener_solicitud(numero)
        solicitud.asignar_area(area)
        self._solicitudes.actualizar_solicitud(solicitud)
        return area

    def buscar_area(self, numero_area):
        for area in areas:
            if area.numero == numero_area:
                return area
        return None

    def hay_solicitudes(self):
        return len(self._solicitudes.listar_solicitudes()) > 0

    def listar(self, estado=None, tipo=None, prioridad=None):
        return [
            s for s in self._solicitudes.listar_solicitudes()
            if (estado is None or s.estado is estado)
            and (tipo is None or s.tipo is tipo)
            and (prioridad is None or s.prioridad is prioridad)
        ]

    def generar_reporte(self):
        todas = self._solicitudes.listar_solicitudes()
        if not todas:
            raise ErrorDeNegocio("no hay solicitudes para reportar")
        return Reporte(
            total=len(todas),
            por_estado=Counter(s.estado for s in todas),
            por_tipo=Counter(s.tipo for s in todas),
            por_prioridad=Counter(s.prioridad for s in todas),
            sin_responsable=sum(1 for s in todas if not s.tiene_responsable),
        )

    def _obtener_solicitud(self, numero):
        solicitud = self._solicitudes.buscar_solicitud(numero)
        if solicitud is None:
            raise ErrorDeNegocio("solicitud no encontrada")
        return solicitud
