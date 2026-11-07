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

## Tecnologías

Python 3.
