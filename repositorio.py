import json
from abc import ABC, abstractmethod
from pathlib import Path

from dominio import Estudiante, Solicitud


class RepositorioEstudiantes(ABC):

    @abstractmethod
    def buscar_estudiante(self, legajo):
        pass

    @abstractmethod
    def agregar_estudiante(self, estudiante):
        pass


class RepositorioSolicitudes(ABC):

    @abstractmethod
    def proximo_numero(self):
        pass

    @abstractmethod
    def agregar_solicitud(self, solicitud):
        pass

    @abstractmethod
    def actualizar_solicitud(self, solicitud):
        pass

    @abstractmethod
    def buscar_solicitud(self, numero):
        pass

    @abstractmethod
    def listar_solicitudes(self):
        pass


class RepositorioEnMemoria(RepositorioEstudiantes, RepositorioSolicitudes):

    def __init__(self, estudiantes=None, solicitudes=None, proximo_numero=1):
        self._estudiantes = list(estudiantes or [])
        self._solicitudes = list(solicitudes or [])
        self._proximo_numero = proximo_numero

    def buscar_estudiante(self, legajo):
        for estudiante in self._estudiantes:
            if estudiante.legajo == legajo:
                return estudiante
        return None

    def agregar_estudiante(self, estudiante):
        self._estudiantes.append(estudiante)
        self._persistir()

    def proximo_numero(self):
        return self._proximo_numero

    def agregar_solicitud(self, solicitud):
        self._solicitudes.append(solicitud)
        self._proximo_numero = self._proximo_numero + 1
        self._persistir()

    def actualizar_solicitud(self, solicitud):
        self._persistir()

    def buscar_solicitud(self, numero):
        for solicitud in self._solicitudes:
            if solicitud.numero == numero:
                return solicitud
        return None

    def listar_solicitudes(self):
        return list(self._solicitudes)

    def _persistir(self):
        pass


class RepositorioJson(RepositorioEnMemoria):

    def __init__(self, ruta):
        super().__init__()
        self._ruta = Path(ruta)
        self._cargar()

    def _cargar(self):
        try:
            if self._ruta.exists():
                with open(self._ruta, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                self._estudiantes = [Estudiante.desde_diccionario(e) for e in datos["estudiantes"]]
                self._solicitudes = [Solicitud.desde_diccionario(s) for s in datos["solicitudes"]]
                self._proximo_numero = datos["contador"]
        except Exception:
            pass

    def _persistir(self):
        datos = {
            "estudiantes": [e.a_diccionario() for e in self._estudiantes],
            "solicitudes": [s.a_diccionario() for s in self._solicitudes],
            "contador": self._proximo_numero,
        }
        try:
            with open(self._ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
        except OSError:
            print("error")
