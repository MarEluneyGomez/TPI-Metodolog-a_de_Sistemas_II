import json
import os
from datetime import datetime

# areas responsables (hardcodeadas por ahora)
areas = [
    {"id": 1, "nombre": "Bedelia", "responsable": "Laura Gomez"},
    {"id": 2, "nombre": "Secretaria Academica", "responsable": "Martin Ruiz"},
    {"id": 3, "nombre": "Departamento de Alumnos", "responsable": "Sofia Herrera"},
]


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
        print("1. Certificado de alumno regular")
        print("2. Equivalencia")
        print("3. Cambio de comision")
        print("4. Reclamo de nota")
        t = input("Tipo: ")
        if not self._tipo_valido(t):
            print("Error: tipo invalido")
            return
        t = int(t)
        desc = input("Descripcion: ")
        if desc.strip() == "":
            print("Error: la descripcion es obligatoria")
            return
        p = self._calcular_prioridad(t, desc)
        fecha = datetime.now().strftime("%Y-%m-%d")
        s = self.crear_solicitud(self.cont, e["legajo"], e["nombre"], e["apellido"], e["email"], t, desc, p, "pend", 0, fecha)
        self.lista.append(s)
        self.cont = self.cont + 1
        self.guardar()
        print("Solicitud #" + str(s["id"]) + " registrada con prioridad " + self._nombre_prioridad(p))

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
        print("Estado actual: " + self._nombre_estado(s["estado"]))
        print("1. Pendiente")
        print("2. En proceso")
        print("3. Resuelta")
        print("4. Rechazada")
        n = self._codigo_estado(input("Nuevo estado: "))
        if n is None:
            print("Error: estado invalido")
            return
        if n == s["estado"]:
            print("Error: la solicitud ya se encuentra en ese estado")
            return
        if s["estado"] == "pend" and n == "res":
            print("Error: una solicitud pendiente no puede resolverse sin pasar por En proceso")
            return
        if n == "proc" and s["area"] == 0:
            print("Error: debe asignar un responsable antes de pasar a En proceso")
            return
        s["estado"] = n
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
        for codigo in ["pend", "proc", "res", "rech"]:
            print("  " + self._nombre_estado(codigo) + ": " + str(self._contar("estado", codigo)))
        print("Por tipo:")
        for tipo in [1, 2, 3, 4]:
            print("  " + self._nombre_tipo(tipo) + ": " + str(self._contar("tipo", tipo)))
        print("Por prioridad:")
        for prioridad in [3, 2, 1]:
            print("  " + self._nombre_prioridad(prioridad) + ": " + str(self._contar("prioridad", prioridad)))
        print("Sin responsable asignado: " + str(self._contar("area", 0)))
        resueltas = self._contar("estado", "res")
        print("Porcentaje resueltas: " + str(round(resueltas * 100 / total, 1)) + "%")

    def _legajo_valido(self, legajo):
        return legajo.isdigit() and len(legajo) == 5

    def _email_valido(self, email):
        return "@" in email and "." in email.split("@")[-1]

    def _tipo_valido(self, texto):
        return texto.isdigit() and 1 <= int(texto) <= 4

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
        return s["estado"] == "res" or s["estado"] == "rech"

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
        if tipo == 4:
            p = 3
        elif tipo == 2 or tipo == 3:
            p = 2
        else:
            p = 1
        if "urgente" in descripcion.lower() and p < 3:
            p = p + 1
        return p

    def _codigo_estado(self, opcion):
        if opcion == "1":
            return "pend"
        if opcion == "2":
            return "proc"
        if opcion == "3":
            return "res"
        if opcion == "4":
            return "rech"
        return None

    def _pedir_filtro(self, f):
        if f == "1":
            return list(self.lista)
        if f == "2":
            print("1. Pendiente  2. En proceso  3. Resuelta  4. Rechazada")
            e = self._codigo_estado(input("Estado: "))
            if e is None:
                print("Error: estado invalido")
                return None
            return self._filtrar("estado", e)
        if f == "3":
            print("1. Certificado de alumno regular  2. Equivalencia  3. Cambio de comision  4. Reclamo de nota")
            t = input("Tipo: ")
            if not self._tipo_valido(t):
                print("Error: tipo invalido")
                return None
            return self._filtrar("tipo", int(t))
        if f == "4":
            p = input("Prioridad (1=Baja, 2=Media, 3=Alta): ")
            if p not in ["1", "2", "3"]:
                print("Error: prioridad invalida")
                return None
            return self._filtrar("prioridad", int(p))
        print("Error: filtro invalido")
        return None

    def _filtrar(self, clave, valor):
        return [s for s in self.lista if s[clave] == valor]

    def _contar(self, clave, valor):
        return len(self._filtrar(clave, valor))

    def _imprimir_solicitud(self, s):
        print("#" + str(s["id"]) + " | " + self._nombre_tipo(s["tipo"]) + " | " + self._nombre_prioridad(s["prioridad"])
              + " | " + self._nombre_estado(s["estado"]) + " | " + s["estudiante"] + " (" + s["legajo"] + ") | Area: "
              + self._nombre_area(s["area"]))
        print("    " + s["descripcion"])

    def _nombre_tipo(self, tipo):
        if tipo == 1:
            return "Certificado de alumno regular"
        if tipo == 2:
            return "Equivalencia"
        if tipo == 3:
            return "Cambio de comision"
        return "Reclamo de nota"

    def _nombre_prioridad(self, prioridad):
        if prioridad == 3:
            return "Alta"
        if prioridad == 2:
            return "Media"
        return "Baja"

    def _nombre_estado(self, estado):
        if estado == "pend":
            return "Pendiente"
        if estado == "proc":
            return "En proceso"
        if estado == "res":
            return "Resuelta"
        return "Rechazada"

    def _nombre_area(self, id_area):
        for a in areas:
            if a["id"] == id_area:
                return a["nombre"]
        return "Sin asignar"
