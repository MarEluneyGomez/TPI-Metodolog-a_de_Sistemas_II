# Diagnóstico de deuda técnica y code smells (versión base)

Versión analizada: tag `estado-inicial`.

## Cómo leer las ubicaciones

Todos los problemas detectados están en el archivo `sistema.py`, que contiene la lógica del sistema. Las ubicaciones indican números de línea de ese archivo en la versión `estado-inicial`:

- **"Líneas 46 y 65"** significa la línea 46 y la línea 65, que son dos lugares distintos con el mismo problema.
- **"Líneas 208 a 274"** significa el bloque completo que va desde la línea 208 hasta la 274, por ejemplo un método entero.

Para ver cada ubicación, abrir `sistema.py` en el editor e ir a la línea indicada (en VS Code: `Ctrl+G`).

## Criterio de prioridad

La prioridad combina el impacto del problema (qué tan grave es si causa un error o frena un cambio) con la probabilidad de que esa zona del código tenga que cambiar (nuevos tipos, nuevas reglas, nueva interfaz o nueva persistencia).

- **Alta:** bloquea cambios probables o puede causar defectos.
- **Media:** encarece el mantenimiento.
- **Baja:** afecta la legibilidad, con poco riesgo.

## Resumen

| ID | Code smell / debilidad | Ubicación en `sistema.py` | Prioridad |
|---|---|---|---|
| S01 | God Class | Líneas 13 a 322: la clase `Sistema` completa | Alta |
| S02 | Long Method | Líneas 208 a 274 (método `listar`) y 63 a 112 (método `registrar_solicitud`) | Alta |
| S03 | Lógica de negocio acoplada a la consola | Todos los métodos de la clase `Sistema` que usan `input()` y `print()` | Alta |
| S04 | Duplicated Code | Líneas 46 y 65; 133 a 139 y 181 a 187; 140 y 188; entre otras | Alta |
| S05 | Switch Statements (rompe OCP) | Líneas 89 a 100 (cálculo de prioridad) y 6 lugares más que dependen del tipo | Alta |
| S06 | Magic Numbers / Magic Strings | Valores como `"pend"`, `"res"`, `4`, `5` y `0` repartidos en todo el archivo | Alta |
| S07 | Manejo de errores deficiente | Línea 30 (método `cargar`) y líneas 38 y 39 (método `guardar`) | Alta |
| S08 | Primitive Obsession | Todo el archivo: solicitudes y estudiantes se manejan como diccionarios | Media |
| S09 | Acoplamiento directo a la persistencia (rompe DIP) | Líneas 21 a 39 (métodos `cargar` y `guardar`) | Media |
| S10 | Long Parameter List | Línea 114 (método `crear_solicitud`, 11 parámetros) | Media |
| S11 | Feature Envy / modelo anémico | Líneas 89 a 100, 140 y 188 | Media |
| S12 | Nombres poco expresivos | Líneas 16 a 18 y todo el archivo (`e`, `t`, `p`, `s`, `x`, `procesar2`) | Media |
| S13 | Datos globales mutables | Líneas 6 a 10 (lista `areas`) | Baja |
| S14 | Código muerto | Líneas 318 a 322 (método `procesar2`) | Baja |

## Detalle

### S01. God Class (prioridad Alta)

- **Evidencia:** la clase `Sistema` concentra 11 métodos y 5 responsabilidades distintas: interacción con el usuario (`input`/`print`), validación de datos, reglas de negocio (prioridad y transiciones de estado), persistencia en JSON y generación del reporte.
- **Ubicación:** líneas 13 a 322 de `sistema.py`. Es la clase completa y contiene el 100 % de la lógica del sistema.
- **Impacto:** viola SRP. Cualquier cambio, sea en la interfaz, en una regla o en el formato de archivo, obliga a modificar la misma clase.
- **Riesgo de mantenimiento:** cambios que no tienen relación entre sí terminan en conflicto. Es difícil entender el código y no se puede probar una parte sin las demás.

### S02. Long Method (prioridad Alta)

- **Evidencia:**
  - `listar()`: 67 líneas, complejidad ciclomática 33 (nota E de radon), 35 ramas y 70 sentencias (pylint: `too-many-branches`, `too-many-statements`).
  - `registrar_solicitud()`: 50 líneas, complejidad 19. Pide los datos, valida, busca el estudiante, muestra el menú, calcula la prioridad, crea, guarda e imprime.
  - `cambiar_estado()` tiene complejidad 18 y `reporte()` complejidad 14.
- **Ubicación:**
  - `listar`: líneas 208 a 274.
  - `registrar_solicitud`: líneas 63 a 112.
  - `cambiar_estado`: líneas 128 a 174.
  - `reporte`: líneas 276 a 316.
- **Impacto:** cada método mezcla varios niveles de abstracción. Para cambiar un detalle hay que entender el método completo.
- **Riesgo de mantenimiento:** es alta la probabilidad de introducir errores al modificarlos. Además son imposibles de probar por partes.

### S03. Lógica de negocio acoplada a la consola (prioridad Alta)

- **Evidencia:** todas las operaciones leen con `input()` y responden con `print()` dentro del mismo método que aplica las reglas. Por ejemplo, `cambiar_estado()` pide el id, valida la transición, la aplica e imprime el resultado.
- **Ubicación:** todos los métodos públicos de la clase `Sistema`. Ejemplo: método `cambiar_estado`, líneas 128 a 174.
- **Impacto:** las reglas no se pueden reutilizar desde otra interfaz (web, API) ni probar con tests unitarios. Los únicos tests posibles son de punta a punta, simulando la consola (por eso la red de seguridad actual usa *golden master*).
- **Riesgo de mantenimiento:** agregar otra interfaz implica duplicar o reescribir toda la lógica.

### S04. Duplicated Code (prioridad Alta)

- **Evidencia y ubicación:**
  - Validación del legajo copiada en las líneas 46 y 65.
  - Búsqueda de una solicitud por id, idéntica en las líneas 133 a 139 y 181 a 187.
  - Verificación de "solicitud cerrada" repetida en las líneas 140 y 188.
  - Conversión de código a texto (estado, tipo y prioridad) repetida 7 veces: líneas 106 a 111, 143 a 146, 147 a 162, 224 a 230, 258 a 268, 286 a 296 y 301 a 314.
  - Menú de tipos escrito dos veces (líneas 75 a 79 y línea 235) y validación del tipo también duplicada (líneas 81 y 237).
- **Impacto:** un cambio en una regla, como el formato del legajo o un nuevo estado, hay que hacerlo en varios lugares.
- **Riesgo de mantenimiento:** inconsistencias. Si se actualiza una copia y otra no, el sistema se comporta distinto según la pantalla.

### S05. Switch Statements: cadenas `if/elif` por tipo, rompe OCP (prioridad Alta)

- **Evidencia:** la prioridad se calcula con una cadena `if/elif` por tipo (líneas 89 a 100). Agregar un tipo nuevo, como "Baja de materia", obliga a modificar 7 lugares en 3 métodos:
  1. el menú de tipos (líneas 75 a 79)
  2. la validación `int(t) > 4` (línea 81)
  3. el cálculo de prioridad (líneas 89 a 97)
  4. el menú del filtro (línea 235)
  5. la validación del filtro (línea 237)
  6. la conversión a texto en `listar` (líneas 258 a 261)
  7. el conteo y la impresión en `reporte` (líneas 290 a 293 y 307 a 310)
- **Impacto:** viola el principio Abierto/Cerrado: para extender el sistema hay que modificar código que ya funciona.
- **Riesgo de mantenimiento:** es fácil olvidarse uno de los 7 lugares, y el error no lo detecta nadie hasta que se usa esa pantalla.

### S06. Magic Numbers / Magic Strings (prioridad Alta)

- **Evidencia y ubicación:**
  - Estados codificados como textos sueltos (`"pend"`, `"proc"`, `"res"`, `"rech"`), repartidos en más de 20 comparaciones a lo largo de todo el archivo.
  - Tipos `1` a `4` y prioridades `1` a `3` sin nombre.
  - El valor `0` en el área significa "sin asignar" (líneas 102, 169 y 297).
  - El número `5` como largo del legajo (líneas 46 y 65).
- **Impacto:** el significado de cada valor no se lee en el código, hay que deducirlo.
- **Riesgo de mantenimiento:** un error de tipeo (`"pendiente"` en lugar de `"pend"`) no da error: simplemente nunca coincide.

### S07. Manejo de errores deficiente (prioridad Alta)

- **Evidencia y ubicación:**
  - El método `cargar()` tiene `except: pass` (línea 30), que ignora cualquier error.
  - El método `guardar()` tiene `except: print("error")` (líneas 38 y 39).
  - Los archivos se abren sin `with` (líneas 24 y 35), así que no se cierran si ocurre una excepción.
  - Los errores de negocio se informan con `print` + `return`, sin excepciones.
- **Impacto:** defecto real verificado. Con un `datos.json` dañado, el sistema arranca vacío sin avisar y en la siguiente operación sobrescribe el archivo: se pierden todos los datos (ver [evidencias/defecto-perdida-de-datos.md](evidencias/defecto-perdida-de-datos.md)).
- **Riesgo de mantenimiento:** las fallas quedan ocultas y no hay forma de diagnosticar qué pasó.

### S08. Primitive Obsession (prioridad Media)

- **Evidencia:** solicitudes, estudiantes y áreas son diccionarios con claves de texto (`s["estado"]`, `e["legajo"]`). No existen las clases `Solicitud`, `Estudiante` ni `EstadoSolicitud`.
- **Ubicación:** todo el archivo. Ejemplo: la solicitud se arma como diccionario en las líneas 114 a 126.
- **Impacto:** las reglas propias de cada entidad no tienen dónde vivir. El intérprete no detecta un error de tipeo en una clave hasta que se ejecuta esa línea.
- **Riesgo de mantenimiento:** el código depende de la estructura interna del diccionario en todos lados.

### S09. Acoplamiento directo a la persistencia, rompe DIP (prioridad Media)

- **Evidencia:** el nombre de archivo `"datos.json"` está escrito a mano en las líneas 23, 24 y 35. El formato JSON está mezclado en la clase de negocio, y cada operación llama directamente a `self.guardar()`.
- **Ubicación:** líneas 21 a 39 (métodos `cargar` y `guardar`).
- **Impacto:** la lógica de negocio depende de un detalle concreto (archivo JSON) en lugar de una abstracción. No se puede cambiar a una base de datos, ni probar la lógica en memoria.
- **Riesgo de mantenimiento:** cambiar la forma de guardar implica tocar la clase central.

### S10. Long Parameter List (prioridad Media)

- **Evidencia:** `crear_solicitud(self, id, legajo, nombre, apellido, email, tipo, descripcion, prioridad, estado, area, fecha)` tiene 11 parámetros (pylint: `too-many-arguments 11/5`). La llamada pasa 11 valores por posición.
- **Ubicación:** definición en las líneas 114 a 126; llamada en la línea 102.
- **Impacto:** es fácil invertir dos argumentos del mismo tipo sin que nada lo detecte, por ejemplo `tipo` y `prioridad`, que son enteros.
- **Riesgo de mantenimiento:** agregar un dato a la solicitud obliga a cambiar la firma y todas las llamadas.

### S11. Feature Envy / modelo anémico (prioridad Media)

- **Evidencia:** `Sistema` calcula la prioridad y decide si una solicitud está cerrada usando solo datos de la solicitud. Ese comportamiento le corresponde a `Solicitud`.
- **Ubicación:** cálculo de prioridad en las líneas 89 a 100; verificación de "cerrada" en las líneas 140 y 188.
- **Impacto:** las reglas de la entidad quedan dispersas fuera de ella.
- **Riesgo de mantenimiento:** la misma regla termina reimplementada en varios lugares (ver S04).

### S12. Nombres poco expresivos (prioridad Media)

- **Evidencia y ubicación:**
  - Atributos `self.lista`, `self.est` y `self.cont` (líneas 16 a 18).
  - Variables de una letra en todo el archivo: `e`, `t`, `p`, `s`, `x`, `n`, `i`, `f`, `d`.
  - Abreviaturas `tn`, `pn`, `en`, `an` (líneas 258 a 272) y `pr` (líneas 106 a 111).
  - `procesar2` no dice qué hace (línea 319).
  - El parámetro `id` tapa una función nativa de Python (línea 114, pylint `redefined-builtin`).
- **Impacto:** el código no explica su intención y obliga a leer la implementación.
- **Riesgo de mantenimiento:** sube la curva de aprendizaje y la probabilidad de usar mal una variable.

### S13. Datos globales mutables (prioridad Baja)

- **Evidencia:** la lista `areas` está definida fuera de la clase, a nivel de módulo, escrita a mano y modificable desde cualquier lugar.
- **Ubicación:** líneas 6 a 10.
- **Impacto:** las áreas no se pueden configurar ni persistir, y hay una dependencia oculta en los métodos que la usan.
- **Riesgo de mantenimiento:** bajo hoy, pero crece si las áreas pasan a administrarse.

### S14. Código muerto (prioridad Baja)

- **Evidencia:** el método `procesar2()` no se llama desde ningún lugar del sistema. Su comentario ("version vieja, no borrar por las dudas") indica que quedó de una versión anterior y nadie se animó a borrarlo.
- **Ubicación:** líneas 318 a 322.
- **Impacto:** ruido al leer y dudas sobre qué código está vigente.
- **Riesgo de mantenimiento:** alguien podría usar `procesar2` creyendo que es válido. Además pasa una solicitud de Pendiente a En proceso sin las validaciones de `cambiar_estado` (por ejemplo, sin exigir un responsable asignado), así que usarlo rompería las reglas de negocio.

## Deuda que se mantiene a propósito

- **Datos del estudiante copiados dentro de la solicitud** (campos `estudiante` y `email`, líneas 118 y 119). Es una desnormalización: si cambia el email del estudiante, la solicitud queda desactualizada. No se corrige en este trabajo para mantener la compatibilidad del formato de `datos.json` con los datos existentes, que es parte del comportamiento externo. Queda como mejora futura, con una migración de datos.

## Métricas de la versión base

Salidas completas en [evidencias/metricas-antes/](evidencias/metricas-antes/). Para reproducirlas:

```bash
python herramientas/medir_calidad.py --ref estado-inicial --salida docs/evidencias/metricas-antes
```

| Métrica | Valor |
|---|---|
| Líneas de código (`sistema.py`) | 322 líneas totales, 306 de código |
| Clases | 1 (`Sistema`) |
| Complejidad ciclomática promedio (radon) | 9.77 (B) |
| Método más complejo | `listar`: 33 (E) |
| Índice de mantenibilidad `sistema.py` (radon) | 8.93 (C: por debajo de 10, el umbral de "difícil de mantener") |
| pylint (sin contar docstrings faltantes) | 8.41 / 10, con 2 errores, 3 advertencias y 11 sugerencias de diseño |
