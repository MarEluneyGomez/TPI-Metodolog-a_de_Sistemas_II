# Checklist de code review

Revisión de la versión refactorizada (tag `etapa-refactoring`) comparada con la versión base (tag `estado-inicial`). Cada criterio indica el resultado en las dos versiones y la evidencia que lo respalda.

## Cómo leer la tabla

- **Cumple:** el criterio se verifica en todo el código.
- **Parcial:** se verifica con una excepción justificada, que se explica en la sección de observaciones.
- **No cumple:** el criterio no se verifica.
- **Smell:** identificador del problema en [code-smells.md](code-smells.md), cuando corresponde.

## Legibilidad y Clean Code

| # | Criterio | Base | Refactorizada | Evidencia |
|---|---|---|---|---|
| 1 | Los nombres de clases, métodos y variables expresan su intención | No cumple | Cumple | Smell S12. Commit `refactor: nombres expresivos y areas inmutables recibidas por parametro` |
| 2 | Cada método tiene una sola tarea y complejidad baja (nota A o B de radon) | No cumple | Cumple | Smell S02. Complejidad máxima: 33 (E) antes, 8 (B) después, en [metricas-antes](evidencias/metricas-antes/radon-complejidad.txt) y [metricas-despues](evidencias/metricas-despues/radon-complejidad.txt) |
| 3 | No hay código duplicado | No cumple | Cumple | Smell S04. Commits de Extract Method y de enumeraciones |
| 4 | No hay números ni textos mágicos | No cumple | Cumple | Smell S06. Commit `refactor: reemplazar codigos de estado, tipo y prioridad por enumeraciones` |
| 5 | No hay código muerto | No cumple | Cumple | Smell S14. Commit `refactor: eliminar el metodo procesar2 que no se usaba` |
| 6 | Los comentarios explican solo decisiones que el código no muestra | No cumple | Cumple | La versión base tenía el comentario "version vieja, no borrar por las dudas". La refactorizada tiene cuatro comentarios, todos sobre decisiones |

## Diseño y principios SOLID

| # | Criterio | Base | Refactorizada | Evidencia |
|---|---|---|---|---|
| 7 | Responsabilidad única: interfaz, reglas y persistencia están separadas | No cumple | Cumple | Smells S01 y S03. `consola.py`, `servicio.py`, `dominio.py` y `repositorio.py` |
| 8 | Abierto/cerrado: agregar un tipo de solicitud no obliga a modificar la lógica | No cumple | Cumple | Smell S05. Antes había que cambiar 7 lugares; ahora alcanza con una línea en `TipoSolicitud` (`dominio.py`) |
| 9 | Sustitución de Liskov: las implementaciones de un repositorio son intercambiables | No aplica | Cumple | Los tests del servicio usan `RepositorioEnMemoria` y la aplicación usa `RepositorioJson`, sin cambios en el servicio |
| 10 | Segregación de interfaces: cada cliente depende solo de lo que usa | No aplica | Cumple | Dos interfaces chicas: `RepositorioEstudiantes` y `RepositorioSolicitudes` (`repositorio.py`) |
| 11 | Inversión de dependencias: la lógica recibe sus dependencias por parámetro | No cumple | Cumple | Smell S09. `ServicioSolicitudes` recibe los repositorios, las áreas y la forma de obtener la fecha |
| 12 | Las reglas de negocio están en las entidades a las que pertenecen | No cumple | Cumple | Smells S08 y S11. Commit `refactor: mover prioridad y reglas de estado al modelo de dominio` |
| 13 | Ningún método recibe más de 5 parámetros | No cumple | Cumple | Smell S10. `crear_solicitud` tenía 11; pylint ya no informa `too-many-arguments` |
| 14 | No hay datos globales modificables | No cumple | Cumple | Smell S13. `AREAS_RESPONSABLES` es una tupla de objetos inmutables (`dominio.py`) |
| 15 | Ninguna clase acumula datos que no le corresponden | No cumple | Parcial | Ver observación 1 |

## Manejo de errores

| # | Criterio | Base | Refactorizada | Evidencia |
|---|---|---|---|---|
| 16 | Ningún error se ignora en silencio | No cumple | Cumple | Smell S07. [Evidencia del defecto](evidencias/defecto-perdida-de-datos.md) y `tests/test_archivo_danado.py` |
| 17 | Los archivos se cierran aunque ocurra un error | No cumple | Cumple | La versión base abría los archivos sin `with`; pylint informaba `consider-using-with` |
| 18 | Los errores de negocio se informan con excepciones y se muestran en un solo lugar | No cumple | Cumple | `ErrorDeNegocio` y `EntradaInvalida`, mostrados en el método `ejecutar` de `InterfazConsola` |

## Pruebas

| # | Criterio | Base | Refactorizada | Evidencia |
|---|---|---|---|---|
| 19 | El comportamiento externo no cambió con el refactoring | No aplica | Cumple | Los 5 tests de caracterización pasan en cada commit del refactoring |
| 20 | Las reglas de negocio tienen tests unitarios | No cumple | Cumple | En la versión base no se podían escribir porque la lógica pedía datos por consola. Ahora hay 14 tests en `test_dominio.py`, `test_servicio.py` y `test_repositorio.py` |
| 21 | El defecto corregido tiene un test que lo reproduce | No aplica | Cumple | `tests/test_archivo_danado.py` |
| 22 | El formato de `datos.json` se mantiene | No aplica | Cumple | Archivos `.json` de `tests/golden` y el test `test_la_solicitud_se_guarda_con_el_formato_de_la_version_base` |

## Análisis estático

| # | Criterio | Base | Refactorizada | Evidencia |
|---|---|---|---|---|
| 23 | pylint no informa errores ni advertencias | No cumple | Cumple | Antes: 8.41, con 2 errores y 3 advertencias. Después: 9.98, sin errores ni advertencias ([pylint antes](evidencias/metricas-antes/pylint.txt), [pylint después](evidencias/metricas-despues/pylint.txt)) |
| 24 | Todos los archivos tienen índice de mantenibilidad A | No cumple | Cumple | `sistema.py` tenía 8.93 (C). Después, el más bajo es `consola.py`, con 29.74 (A) |

## Observaciones

1. **Atributos de `Solicitud`:** la clase tiene 10 (pylint: `too-many-instance-attributes`, el único aviso que queda). Incluye una copia del nombre y del email del estudiante para mantener el formato de `datos.json`. Es la deuda que se mantiene a propósito, descripta en [code-smells.md](code-smells.md).
2. **Validación al registrar un estudiante:** los datos se validan después de pedir los cuatro campos. Si el legajo es inválido, el usuario se entera recién después de escribir el email. Se mantiene igual que en la versión base porque cambiarlo modifica la salida de la consola, que los tests de caracterización verifican. Queda como mejora futura de usabilidad.
