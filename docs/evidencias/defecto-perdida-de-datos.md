# Evidencia: pérdida silenciosa de datos con un archivo dañado (versión base)

**Relacionado con:** S07 (manejo de errores deficiente). El problema está en el método `cargar()`, líneas 21 a 31 de `sistema.py`.

## Reproducción

1. Crear un `datos.json` con una estudiante registrada, pero sin la llave de cierre `}` (simula un archivo cortado por un corte de luz o una edición manual):

   ```json
   {"estudiantes": [{"legajo": "10001", "nombre": "Ana", "apellido": "Lopez", "email": "ana@mail.com"}], "solicitudes": [], "contador": 1
   ```

2. Ejecutar `python main.py` y registrar otro estudiante (legajo `10002`, Bruno Diaz).

## Resultado obtenido

```
Opcion: Legajo: Nombre: Apellido: Email: Estudiante registrado: Diaz, Bruno
```

Contenido de `datos.json` después de la operación:

```json
{
  "estudiantes": [
    {
      "legajo": "10002",
      "nombre": "Bruno",
      "apellido": "Diaz",
      "email": "bruno@mail.com"
    }
  ],
  "solicitudes": [],
  "contador": 1
}
```

La estudiante Ana (10001) se perdió y el sistema no mostró ningún aviso.

## Causa

`cargar()` atrapa cualquier excepción con `except: pass`, así que el sistema arranca con las listas vacías como si no hubiera datos. En la siguiente operación, `guardar()` sobrescribe el archivo original.

## Conclusión

Un problema de calidad interna (manejo de errores que silencia fallas) termina siendo un defecto de calidad externa que el usuario no ve hasta que ya perdió los datos. Se corrige en la etapa de refactoring y la corrección se verifica con un test específico.
