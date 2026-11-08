# Decisiones técnicas

Decisiones tomadas durante la evolución del sistema, con su motivo y su consecuencia. Los identificadores S01 a S14 corresponden a los problemas de [code-smells.md](code-smells.md).

## Proceso

### D01. Tests de caracterización antes de refactorizar

- **Decisión:** antes de cambiar el código se escribieron tests que ejecutan la aplicación real con entradas guionadas y comparan la salida y `datos.json` con archivos grabados sobre la versión base (`tests/golden`).
- **Motivo:** en la versión base la lógica pedía datos con `input()`, así que no se podían escribir tests unitarios (S03). Sin una red de seguridad, no había forma de comprobar que un refactoring no cambiara el comportamiento.
- **Consecuencia:** los archivos golden se graban una sola vez, sobre la versión base, y no se vuelven a grabar. Si un test falla después de un refactoring, el que está mal es el refactoring.

### D02. Métricas reproducibles

- **Decisión:** las métricas se generan con el script `herramientas/medir_calidad.py`, con las versiones de radon y pylint fijadas en `requirements.txt`. El script puede medir una versión guardada en un tag sin tocar la carpeta de trabajo.
- **Motivo:** para que la comparación entre la versión base y la refactorizada sea válida, las dos se tienen que medir con los mismos comandos, las mismas opciones y las mismas versiones de las herramientas.
- **Consecuencia:** cualquiera puede regenerar las carpetas `metricas-antes` y `metricas-despues` y obtener los mismos resultados.

### D03. Un commit por refactoring, en pasos chicos

- **Decisión:** cada refactoring es un commit propio, y los tests de caracterización pasan en todos. Primero se extrajeron métodos (Extract Method) y después se movieron a su lugar definitivo (Move Method, Extract Class).
- **Motivo:** un paso chico es fácil de revisar y, si un test falla, se sabe exactamente qué lo rompió. Extraer antes de mover hace que cada movimiento sea simple, porque el código ya está agrupado en métodos con una sola tarea.
- **Consecuencia:** algunos métodos extraídos en un paso se reemplazan en el siguiente (por ejemplo, la conversión de códigos a texto, que pasa a las enumeraciones). Es esperable: cada paso prepara el siguiente.

### D04. La corrección del defecto va separada de los refactorings

- **Decisión:** la pérdida de datos con un archivo dañado (S07) se corrigió en un commit propio de tipo `fix`, con un test que la reproduce y que fallaba antes de la corrección.
- **Motivo:** un refactoring no cambia el comportamiento y esta corrección sí. Mezclarlos impediría usar los tests de caracterización como prueba de que los refactorings no cambiaron nada.
- **Consecuencia:** en el commit anterior a la corrección, el repositorio JSON todavía tiene el manejo de errores de la versión base, a propósito.

## Compatibilidad

### D05. Se mantienen la salida de la consola y el formato de `datos.json`

- **Decisión:** los mensajes, los menús y el orden en que se piden y se validan los datos son idénticos a los de la versión base. El archivo `datos.json` conserva sus claves y sus códigos (`"pend"`, `4`, etc.).
- **Motivo:** son el comportamiento externo del sistema. Un usuario o un archivo de datos existente no tiene que notar el cambio.
- **Consecuencia:** se mantienen dos debilidades conocidas: la solicitud guarda una copia del nombre y del email del estudiante, y los datos del estudiante se validan recién después de pedir los cuatro campos. Las dos quedan registradas como observaciones en el [checklist de code review](checklist-code-review.md).

## Diseño

### D06. Enumeraciones con código y etiqueta

- **Decisión:** estados, tipos y prioridades son enumeraciones en las que cada valor tiene un código (el que se guarda en `datos.json`) y una etiqueta (el texto que ve el usuario). El tipo de solicitud tiene además su prioridad base.
- **Motivo:** reemplaza los valores sueltos (S06) y las cadenas `if/elif` (S05) por datos en un solo lugar, sin cambiar el formato del archivo.
- **Consecuencia:** agregar un tipo de solicitud es agregar una línea en `TipoSolicitud`. Los menús, la validación, la prioridad, el listado y el reporte se adaptan solos.

### D07. Repositorios detrás de interfaces

- **Decisión:** la persistencia se define con dos interfaces, `RepositorioEstudiantes` y `RepositorioSolicitudes`. `RepositorioEnMemoria` las implementa con listas y `RepositorioJson` hereda de ella y agrega la lectura y escritura del archivo.
- **Motivo:** la lógica depende de una abstracción y no del archivo JSON (S09, inversión de dependencias). Dos interfaces chicas en lugar de una grande respetan la segregación de interfaces.
- **Consecuencia:** el servicio se prueba con el repositorio en memoria, sin archivos. Cambiar a una base de datos implica escribir otra implementación, sin tocar el servicio.

### D08. El servicio recibe todas sus dependencias

- **Decisión:** `ServicioSolicitudes` recibe por parámetro los repositorios, las áreas y la función que da la fecha actual.
- **Motivo:** elimina las dependencias ocultas, como la lista global de áreas (S13) y la fecha tomada del reloj del sistema.
- **Consecuencia:** los tests usan una fecha fija y sus resultados no dependen del día en que se ejecutan. `main.py` es el único lugar donde se arman las piezas.

### D09. Errores con excepciones

- **Decisión:** las reglas de negocio lanzan `ErrorDeNegocio` y los textos que no corresponden a ninguna opción lanzan `EntradaInvalida`. La consola los muestra en un solo lugar, el método `ejecutar` de `InterfazConsola`.
- **Motivo:** en la versión base cada error era un `print` seguido de `return`, repetido en todos los métodos y mezclado con la lógica.
- **Consecuencia:** las reglas se pueden probar verificando la excepción y su mensaje, sin leer la salida de la consola.

### D10. Un archivo dañado detiene el sistema

- **Decisión:** si `datos.json` existe pero no se puede leer, el sistema muestra el error y termina sin modificarlo. Al guardar, escribe primero un archivo temporal y después reemplaza el original.
- **Motivo:** arrancar con las listas vacías, como hacía la versión base, provocaba que la siguiente operación sobrescribiera el archivo y se perdieran todos los datos (S07). La escritura en dos pasos evita que un corte a mitad de camino deje el archivo dañado.
- **Consecuencia:** el usuario tiene que revisar o restaurar el archivo antes de seguir usando el sistema. Es preferible a perder los datos sin aviso.

## Estilo

### D11. Sin docstrings; comentarios solo para decisiones

- **Decisión:** el código no tiene docstrings ni comentarios que repitan lo que ya dice. Solo se comentan decisiones que el código no muestra, como las de D05 y D10.
- **Motivo:** con nombres expresivos, el código se explica solo. Un comentario que repite el código queda desactualizado cuando el código cambia.
- **Consecuencia:** el script de métricas desactiva los avisos de pylint por docstrings faltantes (C0114 a C0116), en las dos versiones medidas.
