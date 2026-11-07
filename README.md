# Sistema de Gestión de Solicitudes Académicas

TPI de Metodología de Sistemas II (UTN - TUP a distancia).

Aplicación de consola para registrar estudiantes y sus solicitudes académicas,
clasificarlas por tipo, prioridad y estado, asignar un área responsable,
filtrarlas y generar un reporte.

> Esta es la versión base (`estado-inicial`): funciona correctamente, pero
> su estructura interna tiene problemas de diseño intencionalmente sin resolver,
> que se diagnostican y corrigen en las etapas siguientes del TPI.

## Requisitos

- Python 3.10 o superior
- Para ejecutar los tests: `pip install -r requirements.txt`

## Uso

```bash
python main.py
```

Los datos se guardan en `datos.json`, en la carpeta desde la que se ejecuta el programa.

## Funcionalidades

1. Registrar estudiante (legajo de 5 dígitos, nombre, apellido, email)
2. Registrar solicitud (la prioridad se calcula según el tipo; "urgente" en la descripción la sube un nivel)
3. Cambiar estado: Pendiente → En proceso → Resuelta / Rechazada
4. Asignar área responsable
5. Listar / filtrar por estado, tipo o prioridad
6. Reporte resumen

## Tests

```bash
python -m pytest -v
```

Los tests de caracterización ejecutan la aplicación real con entradas guionadas
y comparan la salida contra archivos grabados sobre la versión base (`tests/golden/`).

## Tecnologías

Python 3 y pytest.
