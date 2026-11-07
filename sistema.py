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
        if legajo == "" or not legajo.isdigit() or len(legajo) != 5:
            print("Error: legajo invalido (debe tener 5 digitos)")
            return
        if nombre == "" or apellido == "":
            print("Error: nombre y apellido son obligatorios")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            print("Error: email invalido")
            return
        for e in self.est:
            if e["legajo"] == legajo:
                print("Error: ya existe un estudiante con ese legajo")
                return
        self.est.append({"legajo": legajo, "nombre": nombre, "apellido": apellido, "email": email})
        self.guardar()
        print("Estudiante registrado: " + apellido + ", " + nombre)

    def registrar_solicitud(self):
        legajo = input("Legajo del estudiante: ")
        if legajo == "" or not legajo.isdigit() or len(legajo) != 5:
            print("Error: legajo invalido (debe tener 5 digitos)")
            return
        e = None
        for x in self.est:
            if x["legajo"] == legajo:
                e = x
        if e == None:
            print("Error: estudiante no encontrado")
            return
        print("Tipos de solicitud:")
        print("1. Certificado de alumno regular")
        print("2. Equivalencia")
        print("3. Cambio de comision")
        print("4. Reclamo de nota")
        t = input("Tipo: ")
        if not t.isdigit() or int(t) < 1 or int(t) > 4:
            print("Error: tipo invalido")
            return
        t = int(t)
        desc = input("Descripcion: ")
        if desc.strip() == "":
            print("Error: la descripcion es obligatoria")
            return
        p = 1
        if t == 4:
            p = 3
        elif t == 2:
            p = 2
        elif t == 3:
            p = 2
        elif t == 1:
            p = 1
        if "urgente" in desc.lower():
            if p < 3:
                p = p + 1
        fecha = datetime.now().strftime("%Y-%m-%d")
        s = self.crear_solicitud(self.cont, e["legajo"], e["nombre"], e["apellido"], e["email"], t, desc, p, "pend", 0, fecha)
        self.lista.append(s)
        self.cont = self.cont + 1
        self.guardar()
        if p == 3:
            pr = "Alta"
        elif p == 2:
            pr = "Media"
        else:
            pr = "Baja"
        print("Solicitud #" + str(s["id"]) + " registrada con prioridad " + pr)

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
        i = input("ID de solicitud: ")
        if not i.isdigit():
            print("Error: id invalido")
            return
        s = None
        for x in self.lista:
            if x["id"] == int(i):
                s = x
        if s == None:
            print("Error: solicitud no encontrada")
            return
        if s["estado"] == "res" or s["estado"] == "rech":
            print("Error: la solicitud esta cerrada y no puede modificarse")
            return
        if s["estado"] == "pend":
            print("Estado actual: Pendiente")
        elif s["estado"] == "proc":
            print("Estado actual: En proceso")
        print("1. Pendiente")
        print("2. En proceso")
        print("3. Resuelta")
        print("4. Rechazada")
        n = input("Nuevo estado: ")
        if n == "1":
            n = "pend"
        elif n == "2":
            n = "proc"
        elif n == "3":
            n = "res"
        elif n == "4":
            n = "rech"
        else:
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
        i = input("ID de solicitud: ")
        if not i.isdigit():
            print("Error: id invalido")
            return
        s = None
        for x in self.lista:
            if x["id"] == int(i):
                s = x
        if s == None:
            print("Error: solicitud no encontrada")
            return
        if s["estado"] == "res" or s["estado"] == "rech":
            print("Error: no se puede asignar una solicitud cerrada")
            return
        print("Areas disponibles:")
        for a in areas:
            print(str(a["id"]) + ". " + a["nombre"] + " (" + a["responsable"] + ")")
        a = input("Area: ")
        ok = False
        for ar in areas:
            if a.isdigit() and ar["id"] == int(a):
                ok = True
                s["area"] = ar["id"]
                nom = ar["nombre"]
                resp = ar["responsable"]
        if not ok:
            print("Error: area invalida")
            return
        self.guardar()
        print("Solicitud #" + str(s["id"]) + " asignada a " + nom + " (" + resp + ")")

    def listar(self):
        if len(self.lista) == 0:
            print("No hay solicitudes")
            return
        print("1. Todas")
        print("2. Por estado")
        print("3. Por tipo")
        print("4. Por prioridad")
        f = input("Filtro: ")
        res = []
        if f == "1":
            for s in self.lista:
                res.append(s)
        elif f == "2":
            print("1. Pendiente  2. En proceso  3. Resuelta  4. Rechazada")
            e = input("Estado: ")
            if e == "1": e = "pend"
            elif e == "2": e = "proc"
            elif e == "3": e = "res"
            elif e == "4": e = "rech"
            else:
                print("Error: estado invalido")
                return
            for s in self.lista:
                if s["estado"] == e:
                    res.append(s)
        elif f == "3":
            print("1. Certificado de alumno regular  2. Equivalencia  3. Cambio de comision  4. Reclamo de nota")
            t = input("Tipo: ")
            if not t.isdigit() or int(t) < 1 or int(t) > 4:
                print("Error: tipo invalido")
                return
            for s in self.lista:
                if s["tipo"] == int(t):
                    res.append(s)
        elif f == "4":
            p = input("Prioridad (1=Baja, 2=Media, 3=Alta): ")
            if p not in ["1", "2", "3"]:
                print("Error: prioridad invalida")
                return
            for s in self.lista:
                if s["prioridad"] == int(p):
                    res.append(s)
        else:
            print("Error: filtro invalido")
            return
        if len(res) == 0:
            print("No hay solicitudes que coincidan con el filtro")
            return
        for s in res:
            if s["tipo"] == 1: tn = "Certificado de alumno regular"
            elif s["tipo"] == 2: tn = "Equivalencia"
            elif s["tipo"] == 3: tn = "Cambio de comision"
            else: tn = "Reclamo de nota"
            if s["prioridad"] == 3: pn = "Alta"
            elif s["prioridad"] == 2: pn = "Media"
            else: pn = "Baja"
            if s["estado"] == "pend": en = "Pendiente"
            elif s["estado"] == "proc": en = "En proceso"
            elif s["estado"] == "res": en = "Resuelta"
            else: en = "Rechazada"
            an = "Sin asignar"
            for a in areas:
                if a["id"] == s["area"]:
                    an = a["nombre"]
            print("#" + str(s["id"]) + " | " + tn + " | " + pn + " | " + en + " | " + s["estudiante"] + " (" + s["legajo"] + ") | Area: " + an)
            print("    " + s["descripcion"])

    def reporte(self):
        if len(self.lista) == 0:
            print("No hay solicitudes para reportar")
            return
        total = len(self.lista)
        pend = 0; proc = 0; res = 0; rech = 0
        t1 = 0; t2 = 0; t3 = 0; t4 = 0
        alta = 0; media = 0; baja = 0
        sin = 0
        for s in self.lista:
            if s["estado"] == "pend": pend += 1
            elif s["estado"] == "proc": proc += 1
            elif s["estado"] == "res": res += 1
            elif s["estado"] == "rech": rech += 1
            if s["tipo"] == 1: t1 += 1
            elif s["tipo"] == 2: t2 += 1
            elif s["tipo"] == 3: t3 += 1
            elif s["tipo"] == 4: t4 += 1
            if s["prioridad"] == 3: alta += 1
            elif s["prioridad"] == 2: media += 1
            else: baja += 1
            if s["area"] == 0:
                sin += 1
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total: " + str(total))
        print("Por estado:")
        print("  Pendiente: " + str(pend))
        print("  En proceso: " + str(proc))
        print("  Resuelta: " + str(res))
        print("  Rechazada: " + str(rech))
        print("Por tipo:")
        print("  Certificado de alumno regular: " + str(t1))
        print("  Equivalencia: " + str(t2))
        print("  Cambio de comision: " + str(t3))
        print("  Reclamo de nota: " + str(t4))
        print("Por prioridad:")
        print("  Alta: " + str(alta))
        print("  Media: " + str(media))
        print("  Baja: " + str(baja))
        print("Sin responsable asignado: " + str(sin))
        print("Porcentaje resueltas: " + str(round(res * 100 / total, 1)) + "%")

    # version vieja, no borrar por las dudas
    def procesar2(self, s):
        if s["estado"] == "pend":
            s["estado"] = "proc"
        return s
