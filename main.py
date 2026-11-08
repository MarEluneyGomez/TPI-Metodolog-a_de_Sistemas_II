import sys

from consola import InterfazConsola
from dominio import AREAS_RESPONSABLES
from repositorio import ErrorDePersistencia, RepositorioJson
from servicio import ServicioSolicitudes

ARCHIVO_DATOS = "datos.json"


def main():
    try:
        repositorio = RepositorioJson(ARCHIVO_DATOS)
    except ErrorDePersistencia as error:
        print("Error: " + str(error))
        return 1
    servicio = ServicioSolicitudes(
        estudiantes=repositorio, solicitudes=repositorio, areas=AREAS_RESPONSABLES)
    InterfazConsola(servicio).ejecutar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
