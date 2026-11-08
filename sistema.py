from collections import Counter
from datetime import datetime

from dominio import (LARGO_LEGAJO, SIN_AREA, Area, DatosSolicitud, ErrorDeNegocio, EstadoSolicitud, Estudiante,
                     Prioridad, Solicitud, TipoSolicitud)

# areas responsables (hardcodeadas por ahora)
areas = [
    Area(1, "Bedelia", "Laura Gomez"),
    Area(2, "Secretaria Academica", "Martin Ruiz"),
    Area(3, "Departamento de Alumnos", "Sofia Herrera"),
]


class Sistema:

    def __init__(self, estudiantes, solicitudes):
        self.estudiantes = estudiantes
        self.solicitudes = solicitudes

    def registrar_estudiante(self):
        legajo = input("Legajo: ")
        nombre = input("Nombre: ")
        apellido = input("Apellido: ")
        email = input("Email: ")
        if not self._legajo_valido(legajo):
            print("Error: legajo invalido (debe tener 5 digitos)")
            return
        if nombre == "" or apellido == "":
            print("Error: nombre y apellido son obligatorios")
            return
        if not self._email_valido(email):
            print("Error: email invalido")
            return
        if self.estudiantes.buscar_estudiante(legajo) is not None:
            print("Error: ya existe un estudiante con ese legajo")
            return
        e = Estudiante(legajo, nombre, apellido, email)
        self.estudiantes.agregar_estudiante(e)
        print("Estudiante registrado: " + e.nombre_completo)

    def registrar_solicitud(self):
        legajo = input("Legajo del estudiante: ")
        if not self._legajo_valido(legajo):
            print("Error: legajo invalido (debe tener 5 digitos)")
            return
        e = self.estudiantes.buscar_estudiante(legajo)
        if e is None:
            print("Error: estudiante no encontrado")
            return
        print("Tipos de solicitud:")
        for tipo in TipoSolicitud:
            print(str(tipo.codigo) + ". " + tipo.etiqueta)
        t = self._tipo_desde_texto(input("Tipo: "))
        if t is None:
            print("Error: tipo invalido")
            return
        desc = input("Descripcion: ")
        if desc.strip() == "":
            print("Error: la descripcion es obligatoria")
            return
        datos = DatosSolicitud(e, t, desc)
        fecha = datetime.now().strftime("%Y-%m-%d")
        s = Solicitud.crear(self.solicitudes.proximo_numero(), datos, fecha)
        self.solicitudes.agregar_solicitud(s)
        print("Solicitud #" + str(s.numero) + " registrada con prioridad " + s.prioridad.etiqueta)

    def cambiar_estado(self):
        s = self._pedir_solicitud_abierta("Error: la solicitud esta cerrada y no puede modificarse")
        if s is None:
            return
        print("Estado actual: " + s.estado.etiqueta)
        for numero, estado in enumerate(EstadoSolicitud, start=1):
            print(str(numero) + ". " + estado.etiqueta)
        nuevo = self._estado_desde_opcion(input("Nuevo estado: "))
        if nuevo is None:
            print("Error: estado invalido")
            return
        try:
            s.cambiar_estado(nuevo)
        except ErrorDeNegocio as error:
            print("Error: " + str(error))
            return
        self.solicitudes.actualizar_solicitud(s)
        print("Estado actualizado")

    def asignar_responsable(self):
        s = self._pedir_solicitud_abierta("Error: no se puede asignar una solicitud cerrada")
        if s is None:
            return
        print("Areas disponibles:")
        for a in areas:
            print(str(a.numero) + ". " + a.nombre + " (" + a.responsable + ")")
        area = self._buscar_area(input("Area: "))
        if area is None:
            print("Error: area invalida")
            return
        s.asignar_area(area)
        self.solicitudes.actualizar_solicitud(s)
        print("Solicitud #" + str(s.numero) + " asignada a " + area.nombre + " (" + area.responsable + ")")

    def listar(self):
        if len(self.solicitudes.listar_solicitudes()) == 0:
            print("No hay solicitudes")
            return
        print("1. Todas")
        print("2. Por estado")
        print("3. Por tipo")
        print("4. Por prioridad")
        res = self._pedir_filtro(input("Filtro: "))
        if res is None:
            return
        if len(res) == 0:
            print("No hay solicitudes que coincidan con el filtro")
            return
        for s in res:
            self._imprimir_solicitud(s)

    def reporte(self):
        todas = self.solicitudes.listar_solicitudes()
        if len(todas) == 0:
            print("No hay solicitudes para reportar")
            return
        total = len(todas)
        por_estado = Counter(s.estado for s in todas)
        por_tipo = Counter(s.tipo for s in todas)
        por_prioridad = Counter(s.prioridad for s in todas)
        sin_responsable = len(self._filtrar(lambda s: s.area == SIN_AREA))
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total: " + str(total))
        print("Por estado:")
        for estado in EstadoSolicitud:
            print("  " + estado.etiqueta + ": " + str(por_estado[estado]))
        print("Por tipo:")
        for tipo in TipoSolicitud:
            print("  " + tipo.etiqueta + ": " + str(por_tipo[tipo]))
        print("Por prioridad:")
        for prioridad in reversed(Prioridad):
            print("  " + prioridad.etiqueta + ": " + str(por_prioridad[prioridad]))
        print("Sin responsable asignado: " + str(sin_responsable))
        resueltas = por_estado[EstadoSolicitud.RESUELTA]
        print("Porcentaje resueltas: " + str(round(resueltas * 100 / total, 1)) + "%")

    def _legajo_valido(self, legajo):
        return legajo.isdigit() and len(legajo) == LARGO_LEGAJO

    def _email_valido(self, email):
        return "@" in email and "." in email.split("@")[-1]

    def _tipo_desde_texto(self, texto):
        if not texto.isdigit():
            return None
        for tipo in TipoSolicitud:
            if tipo.codigo == int(texto):
                return tipo
        return None

    def _estado_desde_opcion(self, opcion):
        for numero, estado in enumerate(EstadoSolicitud, start=1):
            if opcion == str(numero):
                return estado
        return None

    def _prioridad_desde_texto(self, texto):
        for prioridad in Prioridad:
            if texto == str(prioridad.codigo):
                return prioridad
        return None

    def _buscar_area(self, texto):
        for a in areas:
            if texto.isdigit() and a.numero == int(texto):
                return a
        return None

    def _pedir_solicitud_abierta(self, mensaje_si_esta_cerrada):
        i = input("ID de solicitud: ")
        if not i.isdigit():
            print("Error: id invalido")
            return None
        s = self.solicitudes.buscar_solicitud(int(i))
        if s is None:
            print("Error: solicitud no encontrada")
            return None
        if s.esta_cerrada:
            print(mensaje_si_esta_cerrada)
            return None
        return s

    def _pedir_filtro(self, f):
        if f == "1":
            return self.solicitudes.listar_solicitudes()
        if f == "2":
            print("  ".join(str(n) + ". " + e.etiqueta for n, e in enumerate(EstadoSolicitud, start=1)))
            e = self._estado_desde_opcion(input("Estado: "))
            if e is None:
                print("Error: estado invalido")
                return None
            return self._filtrar(lambda s: s.estado is e)
        if f == "3":
            print("  ".join(str(t.codigo) + ". " + t.etiqueta for t in TipoSolicitud))
            t = self._tipo_desde_texto(input("Tipo: "))
            if t is None:
                print("Error: tipo invalido")
                return None
            return self._filtrar(lambda s: s.tipo is t)
        if f == "4":
            opciones = ", ".join(str(p.codigo) + "=" + p.etiqueta for p in Prioridad)
            p = self._prioridad_desde_texto(input("Prioridad (" + opciones + "): "))
            if p is None:
                print("Error: prioridad invalida")
                return None
            return self._filtrar(lambda s: s.prioridad is p)
        print("Error: filtro invalido")
        return None

    def _filtrar(self, condicion):
        return [s for s in self.solicitudes.listar_solicitudes() if condicion(s)]

    def _imprimir_solicitud(self, s):
        print("#" + str(s.numero) + " | " + s.tipo.etiqueta + " | " + s.prioridad.etiqueta + " | " + s.estado.etiqueta
              + " | " + s.estudiante + " (" + s.legajo + ") | Area: " + self._nombre_area(s.area))
        print("    " + s.descripcion)

    def _nombre_area(self, numero_area):
        for a in areas:
            if a.numero == numero_area:
                return a.nombre
        return "Sin asignar"
