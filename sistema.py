import json
import os
from datetime import datetime

from dominio import LARGO_LEGAJO, SIN_AREA, EstadoSolicitud, Prioridad, TipoSolicitud

# areas responsables (hardcodeadas por ahora)
areas = [
    {"id": 1, "nombre": "Bedelia", "responsable": "Laura Gomez"},
    {"id": 2, "nombre": "Secretaria Academica", "responsable": "Martin Ruiz"},
    {"id": 3, "nombre": "Departamento de Alumnos", "responsable": "Sofia Herrera"},
]

ESTADOS_CERRADOS = (EstadoSolicitud.RESUELTA, EstadoSolicitud.RECHAZADA)


class Sistema:

    def __init__(self):
        self.lista = []
        self.est = []
        self.cont = 1
        self.cargar()

    def cargar(self):
        try:
            if os.path.exists("datos.json"):
                f = open("datos.json", "r", encoding="utf-8")
                d = json.load(f)
                f.close()
                self.est = d["estudiantes"]
                self.lista = d["solicitudes"]
                self.cont = d["contador"]
        except:
            pass

    def guardar(self):
        try:
            f = open("datos.json", "w", encoding="utf-8")
            json.dump({"estudiantes": self.est, "solicitudes": self.lista, "contador": self.cont}, f, indent=2, ensure_ascii=False)
            f.close()
        except:
            print("error")

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
        if self._buscar_estudiante(legajo) is not None:
            print("Error: ya existe un estudiante con ese legajo")
            return
        self.est.append({"legajo": legajo, "nombre": nombre, "apellido": apellido, "email": email})
        self.guardar()
        print("Estudiante registrado: " + apellido + ", " + nombre)

    def registrar_solicitud(self):
        legajo = input("Legajo del estudiante: ")
        if not self._legajo_valido(legajo):
            print("Error: legajo invalido (debe tener 5 digitos)")
            return
        e = self._buscar_estudiante(legajo)
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
        p = self._calcular_prioridad(t, desc)
        fecha = datetime.now().strftime("%Y-%m-%d")
        s = self.crear_solicitud(self.cont, e["legajo"], e["nombre"], e["apellido"], e["email"], t.codigo, desc, p.codigo,
                                 EstadoSolicitud.PENDIENTE.codigo, SIN_AREA, fecha)
        self.lista.append(s)
        self.cont = self.cont + 1
        self.guardar()
        print("Solicitud #" + str(s["id"]) + " registrada con prioridad " + p.etiqueta)

    def crear_solicitud(self, id, legajo, nombre, apellido, email, tipo, descripcion, prioridad, estado, area, fecha):
        s = {}
        s["id"] = id
        s["legajo"] = legajo
        s["estudiante"] = apellido + ", " + nombre
        s["email"] = email
        s["tipo"] = tipo
        s["descripcion"] = descripcion
        s["prioridad"] = prioridad
        s["estado"] = estado
        s["area"] = area
        s["fecha"] = fecha
        return s

    def cambiar_estado(self):
        s = self._pedir_solicitud_abierta("Error: la solicitud esta cerrada y no puede modificarse")
        if s is None:
            return
        actual = EstadoSolicitud.desde_codigo(s["estado"])
        print("Estado actual: " + actual.etiqueta)
        for numero, estado in enumerate(EstadoSolicitud, start=1):
            print(str(numero) + ". " + estado.etiqueta)
        nuevo = self._estado_desde_opcion(input("Nuevo estado: "))
        if nuevo is None:
            print("Error: estado invalido")
            return
        if nuevo is actual:
            print("Error: la solicitud ya se encuentra en ese estado")
            return
        if actual is EstadoSolicitud.PENDIENTE and nuevo is EstadoSolicitud.RESUELTA:
            print("Error: una solicitud pendiente no puede resolverse sin pasar por En proceso")
            return
        if nuevo is EstadoSolicitud.EN_PROCESO and s["area"] == SIN_AREA:
            print("Error: debe asignar un responsable antes de pasar a En proceso")
            return
        s["estado"] = nuevo.codigo
        self.guardar()
        print("Estado actualizado")

    def asignar_responsable(self):
        s = self._pedir_solicitud_abierta("Error: no se puede asignar una solicitud cerrada")
        if s is None:
            return
        print("Areas disponibles:")
        for a in areas:
            print(str(a["id"]) + ". " + a["nombre"] + " (" + a["responsable"] + ")")
        area = self._buscar_area(input("Area: "))
        if area is None:
            print("Error: area invalida")
            return
        s["area"] = area["id"]
        self.guardar()
        print("Solicitud #" + str(s["id"]) + " asignada a " + area["nombre"] + " (" + area["responsable"] + ")")

    def listar(self):
        if len(self.lista) == 0:
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
        if len(self.lista) == 0:
            print("No hay solicitudes para reportar")
            return
        total = len(self.lista)
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total: " + str(total))
        print("Por estado:")
        for estado in EstadoSolicitud:
            print("  " + estado.etiqueta + ": " + str(self._contar("estado", estado.codigo)))
        print("Por tipo:")
        for tipo in TipoSolicitud:
            print("  " + tipo.etiqueta + ": " + str(self._contar("tipo", tipo.codigo)))
        print("Por prioridad:")
        for prioridad in reversed(Prioridad):
            print("  " + prioridad.etiqueta + ": " + str(self._contar("prioridad", prioridad.codigo)))
        print("Sin responsable asignado: " + str(self._contar("area", SIN_AREA)))
        resueltas = self._contar("estado", EstadoSolicitud.RESUELTA.codigo)
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

    def _buscar_estudiante(self, legajo):
        for e in self.est:
            if e["legajo"] == legajo:
                return e
        return None

    def _buscar_solicitud(self, numero):
        for s in self.lista:
            if s["id"] == numero:
                return s
        return None

    def _buscar_area(self, texto):
        for a in areas:
            if texto.isdigit() and a["id"] == int(texto):
                return a
        return None

    def _esta_cerrada(self, s):
        return EstadoSolicitud.desde_codigo(s["estado"]) in ESTADOS_CERRADOS

    def _pedir_solicitud_abierta(self, mensaje_si_esta_cerrada):
        i = input("ID de solicitud: ")
        if not i.isdigit():
            print("Error: id invalido")
            return None
        s = self._buscar_solicitud(int(i))
        if s is None:
            print("Error: solicitud no encontrada")
            return None
        if self._esta_cerrada(s):
            print(mensaje_si_esta_cerrada)
            return None
        return s

    def _calcular_prioridad(self, tipo, descripcion):
        if tipo is TipoSolicitud.RECLAMO_DE_NOTA:
            p = Prioridad.ALTA
        elif tipo in (TipoSolicitud.EQUIVALENCIA, TipoSolicitud.CAMBIO_DE_COMISION):
            p = Prioridad.MEDIA
        else:
            p = Prioridad.BAJA
        if "urgente" in descripcion.lower() and p is not Prioridad.ALTA:
            p = Prioridad.desde_codigo(p.codigo + 1)
        return p

    def _pedir_filtro(self, f):
        if f == "1":
            return list(self.lista)
        if f == "2":
            print("  ".join(str(n) + ". " + e.etiqueta for n, e in enumerate(EstadoSolicitud, start=1)))
            e = self._estado_desde_opcion(input("Estado: "))
            if e is None:
                print("Error: estado invalido")
                return None
            return self._filtrar("estado", e.codigo)
        if f == "3":
            print("  ".join(str(t.codigo) + ". " + t.etiqueta for t in TipoSolicitud))
            t = self._tipo_desde_texto(input("Tipo: "))
            if t is None:
                print("Error: tipo invalido")
                return None
            return self._filtrar("tipo", t.codigo)
        if f == "4":
            opciones = ", ".join(str(p.codigo) + "=" + p.etiqueta for p in Prioridad)
            p = self._prioridad_desde_texto(input("Prioridad (" + opciones + "): "))
            if p is None:
                print("Error: prioridad invalida")
                return None
            return self._filtrar("prioridad", p.codigo)
        print("Error: filtro invalido")
        return None

    def _filtrar(self, clave, valor):
        return [s for s in self.lista if s[clave] == valor]

    def _contar(self, clave, valor):
        return len(self._filtrar(clave, valor))

    def _imprimir_solicitud(self, s):
        tipo = TipoSolicitud.desde_codigo(s["tipo"])
        prioridad = Prioridad.desde_codigo(s["prioridad"])
        estado = EstadoSolicitud.desde_codigo(s["estado"])
        print("#" + str(s["id"]) + " | " + tipo.etiqueta + " | " + prioridad.etiqueta + " | " + estado.etiqueta
              + " | " + s["estudiante"] + " (" + s["legajo"] + ") | Area: " + self._nombre_area(s["area"]))
        print("    " + s["descripcion"])

    def _nombre_area(self, id_area):
        for a in areas:
            if a["id"] == id_area:
                return a["nombre"]
        return "Sin asignar"
