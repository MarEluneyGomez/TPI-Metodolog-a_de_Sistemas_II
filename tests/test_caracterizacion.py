import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MAIN = RAIZ / "main.py"
GOLDEN = Path(__file__).resolve().parent / "golden"
# Los golden files se graban una sola vez, sobre la version base (tag estado-inicial).
ACTUALIZAR = os.environ.get("ACTUALIZAR_GOLDEN") == "1"


def ejecutar_app(entradas, carpeta):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    resultado = subprocess.run(
        [sys.executable, str(MAIN)],
        input="\n".join(entradas) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=carpeta,
        env=env,
        timeout=30,
    )
    assert resultado.returncode == 0, resultado.stderr
    return resultado.stdout


def leer_datos_sin_fecha(carpeta):
    datos = json.loads((Path(carpeta) / "datos.json").read_text(encoding="utf-8"))
    for solicitud in datos["solicitudes"]:
        solicitud.pop("fecha", None)
    return json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True)


def comparar_con_golden(nombre_archivo, contenido_actual):
    archivo = GOLDEN / nombre_archivo
    if ACTUALIZAR:
        GOLDEN.mkdir(exist_ok=True)
        archivo.write_text(contenido_actual, encoding="utf-8")
        return
    assert archivo.exists(), f"Falta el golden file {archivo}"
    assert contenido_actual == archivo.read_text(encoding="utf-8")


# Escenarios: entradas que se escriben en la consola, una por linea

FLUJO_COMPLETO = [
    "1", "10001", "Ana", "Lopez", "ana.lopez@mail.com",
    "1", "10002", "Bruno", "Diaz", "bruno.diaz@mail.com",
    "2", "10001", "4", "Reclamo por nota del parcial de Algebra",
    "2", "10002", "1", "Certificado para presentar en el trabajo",
    "2", "10002", "2", "Equivalencia de Programacion I urgente",
    "4", "1", "1",
    "3", "1", "2",
    "3", "1", "3",
    "4", "2", "3",
    "3", "2", "4",
    "5", "1",
    "6",
    "0",
]

VALIDACIONES = [
    "1", "123", "Xavier", "Ybarra", "x@mail.com",          # legajo invalido
    "1", "10003", "Carla", "Sosa", "carla-mail",           # email invalido
    "1", "10003", "", "Sosa", "carla@mail.com",            # nombre vacio
    "1", "10003", "Carla", "Sosa", "carla@mail.com",       # ok
    "1", "10003", "Carla", "Sosa", "carla@mail.com",       # legajo duplicado
    "2", "1234",                                           # legajo mal formado
    "2", "99999",                                          # estudiante inexistente
    "2", "10003", "7",                                     # tipo invalido
    "2", "10003", "3", "",                                 # descripcion vacia
    "2", "10003", "3", "Cambio a comision noche",          # ok -> #1
    "3", "abc",                                            # id invalido
    "3", "50",                                             # id inexistente
    "3", "1", "9",                                         # estado invalido
    "3", "1", "2",                                         # En proceso sin responsable
    "3", "1", "3",                                         # Pendiente -> Resuelta
    "4", "1", "8",                                         # area invalida
    "4", "1", "2",                                         # ok
    "3", "1", "1",                                         # mismo estado
    "3", "1", "4",                                         # Pendiente -> Rechazada ok
    "4", "1",                                              # asignar cerrada
    "3", "1",                                              # modificar cerrada
    "6",
    "9",                                                   # opcion invalida
    "0",
]

FILTROS = [
    "5",                                                   # sin solicitudes
    "6",                                                   # reporte vacio
    "1", "20001", "Diego", "Ramos", "diego.ramos@mail.com",
    "1", "20002", "Elena", "Vega", "elena.vega@mail.com",
    "2", "20001", "4", "Reclamo de nota final",            # Alta
    "2", "20001", "1", "Certificado urgente para beca",    # Media (urgente)
    "2", "20002", "3", "Cambio de comision por trabajo",   # Media
    "2", "20002", "1", "Certificado para obra social",     # Baja
    "4", "3", "3",
    "3", "3", "2",
    "5", "2", "1",                                         # pendientes
    "5", "2", "2",                                         # en proceso
    "5", "2", "3",                                         # resueltas (ninguna)
    "5", "3", "1",                                         # certificados
    "5", "3", "5",                                         # tipo invalido
    "5", "4", "3",                                         # alta
    "5", "4", "2",                                         # media
    "5", "4", "0",                                         # prioridad invalida
    "5", "2", "9",                                         # estado invalido
    "5", "7",                                              # filtro invalido
    "6",
    "0",
]

PERSISTENCIA_PRIMERA_EJECUCION = [
    "1", "30001", "Franco", "Medina", "franco.medina@mail.com",
    "2", "30001", "2", "Equivalencia de Matematica",
    "0",
]

PERSISTENCIA_SEGUNDA_EJECUCION = [
    "5", "1",
    "2", "30001", "4", "Reclamo de nota de Fisica",
    "1", "30001", "Franco", "Medina", "franco.medina@mail.com",  # ya existe
    "6",
    "0",
]


# Tests

def test_flujo_completo(tmp_path):
    salida = ejecutar_app(FLUJO_COMPLETO, tmp_path)
    comparar_con_golden("flujo_completo.txt", salida)
    comparar_con_golden("flujo_completo.json", leer_datos_sin_fecha(tmp_path))


def test_validaciones_y_reglas_de_negocio(tmp_path):
    salida = ejecutar_app(VALIDACIONES, tmp_path)
    comparar_con_golden("validaciones.txt", salida)
    comparar_con_golden("validaciones.json", leer_datos_sin_fecha(tmp_path))


def test_filtros_y_reporte(tmp_path):
    salida = ejecutar_app(FILTROS, tmp_path)
    comparar_con_golden("filtros.txt", salida)
    comparar_con_golden("filtros.json", leer_datos_sin_fecha(tmp_path))


def test_persistencia_entre_ejecuciones(tmp_path):
    ejecutar_app(PERSISTENCIA_PRIMERA_EJECUCION, tmp_path)
    salida = ejecutar_app(PERSISTENCIA_SEGUNDA_EJECUCION, tmp_path)
    comparar_con_golden("persistencia.txt", salida)
    comparar_con_golden("persistencia.json", leer_datos_sin_fecha(tmp_path))


def test_la_fecha_se_guarda_en_formato_iso(tmp_path):
    ejecutar_app(PERSISTENCIA_PRIMERA_EJECUCION, tmp_path)
    datos = json.loads((tmp_path / "datos.json").read_text(encoding="utf-8"))
    fecha = datos["solicitudes"][0]["fecha"]
    assert len(fecha) == 10 and fecha[4] == "-" and fecha[7] == "-"
