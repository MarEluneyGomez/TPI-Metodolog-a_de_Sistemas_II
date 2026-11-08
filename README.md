# Sistema de Gestión de Solicitudes Académicas

TPI de Metodología de Sistemas II (UTN, TUP a distancia).

Aplicación de consola para registrar estudiantes y sus solicitudes académicas,
clasificarlas por tipo, prioridad y estado, asignar un área responsable,
filtrarlas y generar un reporte.

El repositorio muestra la evolución del sistema: una versión base que funciona
pero tiene problemas de diseño, su diagnóstico, el refactoring y las pruebas.

## Requisitos

- Python 3.10 o superior
- Para tests y métricas: `pip install -r requirements.txt`

## Uso

```bash
python main.py
```

Los datos se guardan en `datos.json`, en la carpeta desde la que se ejecuta el programa.
Si el archivo existe pero está dañado, el sistema informa el error y termina sin modificarlo.

## Funcionalidades

1. Registrar estudiante (legajo de 5 dígitos, nombre, apellido, email)
2. Registrar solicitud (la prioridad se calcula según el tipo; "urgente" en la descripción la sube un nivel)
3. Cambiar estado: Pendiente → En proceso → Resuelta / Rechazada
4. Asignar área responsable
5. Listar y filtrar por estado, tipo o prioridad
6. Reporte resumen

## Estructura

| Archivo | Contenido |
|---|---|
| `main.py` | Punto de entrada: arma las dependencias y ejecuta la consola |
| `consola.py` | Interfaz de consola: pide los datos y muestra los resultados |
| `servicio.py` | Casos de uso del sistema, sin entrada ni salida por consola |
| `dominio.py` | Entidades, enumeraciones y reglas de negocio |
| `repositorio.py` | Persistencia: interfaces, repositorio en memoria y repositorio JSON |
| `herramientas/medir_calidad.py` | Script que genera las métricas de calidad |

## Tests

```bash
python -m pytest -v
```

- **Caracterización** (`test_caracterizacion.py`): ejecutan la aplicación real con entradas
  guionadas y comparan la salida y `datos.json` con archivos grabados sobre la versión base
  (`tests/golden/`). Garantizan que el refactoring no cambió el comportamiento.
- **Archivo dañado** (`test_archivo_danado.py`): reproducen el defecto de pérdida de datos
  de la versión base y verifican su corrección.
- **Unitarios** (`test_dominio.py`, `test_servicio.py`, `test_repositorio.py`): prueban las
  reglas de negocio, los casos de uso y la persistencia sin ejecutar la aplicación.

## Métricas de calidad

Las métricas se generan con radon y pylint, en las versiones fijadas en
`requirements.txt` (las mediciones del trabajo se hicieron con Python 3.13).
El script mide la versión guardada en un tag, sin tocar la carpeta de trabajo, y
siempre usa los mismos comandos y opciones para que las mediciones sean comparables:

```bash
python herramientas/medir_calidad.py --ref estado-inicial --salida docs/evidencias/metricas-antes
python herramientas/medir_calidad.py --ref etapa-refactoring --salida docs/evidencias/metricas-despues
```

Sin `--ref`, mide el código tal como está en la carpeta de trabajo. Cada carpeta de
resultados incluye `informacion.txt`, con la versión medida, los archivos analizados,
las versiones de las herramientas y los comandos usados.

## Documentación

| Documento | Contenido |
|---|---|
| [Calidad externa e interna](docs/calidad-externa-interna.md) | Análisis de la versión base |
| [Code smells](docs/code-smells.md) | Diagnóstico de deuda técnica, prioridades y métricas de la versión base |
| [Checklist de code review](docs/checklist-code-review.md) | Comparación de la versión base y la refactorizada |
| [Decisiones técnicas](docs/decisiones-tecnicas.md) | Decisiones tomadas durante la evolución, con su motivo |
| [Evidencias](docs/evidencias/) | Defecto de pérdida de datos y métricas de antes y después |

## Etapas

Cada etapa del trabajo está marcada con un tag:

| Tag | Contenido |
|---|---|
| `estado-inicial` | Versión base con sus tests de caracterización |
| `etapa-diagnostico` | Diagnóstico de calidad, code smells y métricas de la versión base |
| `etapa-refactoring` | Refactorings (un commit por refactoring) y corrección del defecto |
| `etapa-pruebas` | Tests unitarios y métricas de la versión refactorizada |
| `etapa-docs` | Checklist de code review, decisiones técnicas y README |
| `estado-refactorizado` | Versión final |

## Tecnologías

Python 3, pytest, radon y pylint (métricas).
