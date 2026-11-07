# Calidad externa vs. calidad interna (versión base)

- **Calidad externa:** lo que percibe quien usa el sistema. ¿Hace lo que tiene que hacer, valida bien y no pierde datos?
- **Calidad interna:** lo que percibe quien mantiene el sistema. ¿Se entiende, se puede cambiar sin miedo y se puede probar?

Un sistema puede tener buena calidad externa y mala calidad interna. Así está la versión base de este proyecto (tag `estado-inicial`).

## 1. Calidad externa: lo que funciona bien

Desde el punto de vista del usuario, la versión base cumple todas sus funciones. Lo respaldan 5 tests de caracterización que pasan (`tests/test_caracterizacion.py`):

| Funcionalidad | Comportamiento verificado |
|---|---|
| Registrar estudiante | Valida legajo de 5 dígitos, nombre y apellido obligatorios, formato de email y legajo duplicado |
| Registrar solicitud | Valida estudiante existente, tipo y descripción. Calcula la prioridad según el tipo y la sube un nivel si la descripción dice "urgente" |
| Cambiar estado | Respeta las reglas: no permite modificar solicitudes cerradas, ni pasar de Pendiente a Resuelta, ni pasar a En proceso sin responsable |
| Asignar responsable | Valida el área e impide asignar solicitudes cerradas |
| Listar / filtrar | Por estado, tipo o prioridad, con mensajes claros cuando no hay resultados |
| Reporte | Totales por estado, tipo y prioridad; solicitudes sin responsable; porcentaje de resueltas |
| Persistencia | Los datos se conservan entre ejecuciones y los ids no se repiten |

Los mensajes de error son claros y el flujo por menú es simple. Un usuario que prueba el sistema no ve ningún problema.

**Excepción detectada:** el sistema tiene un defecto externo latente. Si `datos.json` se daña, el sistema pierde todos los datos sin avisar (ver [evidencias/defecto-perdida-de-datos.md](evidencias/defecto-perdida-de-datos.md)). Es un problema de calidad interna (S07) que termina afectando al usuario. En el uso normal no aparece, por eso no se detecta probando el sistema.

## 2. Calidad interna: los problemas de la estructura

Hacia adentro, el sistema es difícil de mantener (detalle en [code-smells.md](code-smells.md)):

- **Toda la lógica está en una sola clase** (`Sistema`, en un archivo de 322 líneas), que mezcla interfaz, reglas, persistencia y reporte (S01, S03).
- **Métodos largos y muy ramificados:** `listar` tiene complejidad ciclomática 33 (S02).
- **Reglas duplicadas** en varios lugares (S04) y valores mágicos como `"pend"`, `4` o `0` (S06).
- **No existen las entidades del dominio** como clases: todo son diccionarios (S08, S11).
- **Los errores se silencian** (S07).

Las métricas lo confirman: el índice de mantenibilidad de `sistema.py` es 8.93, por debajo de 10, que es el umbral de "difícil de mantener", mientras que el de `main.py`, que es simple, es 53.19.

## 3. Por qué importa: costo de los cambios probables

La calidad interna no se ve en la pantalla, pero define cuánto cuesta cambiar el sistema. Estos son cambios realistas para un sistema de solicitudes académicas:

| Cambio probable | Costo en la versión base | Causa |
|---|---|---|
| Agregar un tipo de solicitud ("Baja de materia") | Modificar 7 lugares en 3 métodos, con riesgo de olvidar alguno | S05, S04, S06 |
| Cambiar el formato del legajo (de 5 a 6 dígitos) | Modificar 2 validaciones copiadas | S04, S06 |
| Agregar un estado ("Observada") | Tocar unas 10 comparaciones de texto y 5 conversiones a texto | S06, S04 |
| Guardar en una base de datos en lugar de JSON | Reescribir partes de la clase central; la lógica depende del archivo | S09, S01 |
| Agregar una interfaz web | Reescribir toda la lógica, porque cada regla está mezclada con `input()` y `print()` | S03 |
| Probar una regla aislada (por ejemplo, la prioridad) | Imposible sin ejecutar toda la aplicación por consola | S03, S01 |

## 4. Relación con mantenibilidad, legibilidad y evolución

- **Legibilidad:** los nombres cortos (`e`, `t`, `p`, `s`) y los métodos largos obligan a leer línea por línea para entender la intención (S12, S02).
- **Mantenibilidad:** como las reglas están duplicadas, cada corrección hay que repetirla en varios lugares, con riesgo de inconsistencias (S04).
- **Evolución futura:** cada cambio de los listados arriba es más caro de lo necesario, y ese costo crece a medida que se agregan funcionalidades. Esa es la deuda técnica, un ahorro de tiempo al escribir el código que se paga con intereses en cada cambio posterior.

## 5. Conclusión

La versión base es correcta pero frágil. El objetivo del refactoring no es agregar funcionalidad, sino que los cambios probables de la tabla anterior sean baratos y seguros. Para eso:

- Separar responsabilidades (SRP).
- Hacer extensibles los tipos (OCP).
- Desacoplar la persistencia (DIP).
- Hacer visibles los errores.

Todo esto sin alterar el comportamiento que ve el usuario, verificado con los tests de caracterización, y corrigiendo además el defecto de pérdida de datos.
