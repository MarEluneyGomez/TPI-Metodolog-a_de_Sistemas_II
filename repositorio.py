import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

from dominio import Estudiante, Solicitud


class ErrorDePersistencia(Exception):
    pass


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
        # Si el archivo existe pero no se puede leer, no se arranca con las listas
        # vacias: la proxima operacion lo sobrescribiria y se perderian los datos.
        if not self._ruta.exists():
            return
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            estudiantes = [Estudiante.desde_diccionario(e) for e in datos["estudiantes"]]
            solicitudes = [Solicitud.desde_diccionario(s) for s in datos["solicitudes"]]
            proximo_numero = datos["contador"]
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ErrorDePersistencia(
                f"no se pudo leer el archivo de datos {self._ruta.name} ({error}). "
                "El archivo no se modifico: reviselo o restaurelo desde una copia antes de volver a ejecutar."
            ) from error
        self._estudiantes = estudiantes
        self._solicitudes = solicitudes
        self._proximo_numero = proximo_numero

    def _persistir(self):
        # Se escribe en un archivo temporal y despues se reemplaza el original, para
        # que un corte a mitad de la escritura no deje el archivo danado.
        datos = {
            "estudiantes": [e.a_diccionario() for e in self._estudiantes],
            "solicitudes": [s.a_diccionario() for s in self._solicitudes],
            "contador": self._proximo_numero,
        }
        temporal = self._ruta.with_name(self._ruta.name + ".tmp")
        try:
            with open(temporal, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
            os.replace(temporal, self._ruta)
        except OSError as error:
            raise ErrorDePersistencia(f"no se pudo guardar el archivo de datos {self._ruta.name} ({error})") from error
