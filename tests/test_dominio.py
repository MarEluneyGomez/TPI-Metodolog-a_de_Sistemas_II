import pytest

from dominio import (SIN_AREA, Area, DatosSolicitud, ErrorDeNegocio, EstadoSolicitud, Estudiante,
                     Prioridad, Solicitud, TipoSolicitud)

ANA = Estudiante("10001", "Ana", "Lopez", "ana@mail.com")
BEDELIA = Area(1, "Bedelia", "Laura Gomez")


def nueva_solicitud():
    datos = DatosSolicitud(ANA, TipoSolicitud.EQUIVALENCIA, "Equivalencia de Algebra")
    return Solicitud.crear(1, datos, "2026-11-08")


@pytest.mark.parametrize("tipo, prioridad", [
    (TipoSolicitud.CERTIFICADO_ALUMNO_REGULAR, Prioridad.BAJA),
    (TipoSolicitud.EQUIVALENCIA, Prioridad.MEDIA),
    (TipoSolicitud.CAMBIO_DE_COMISION, Prioridad.MEDIA),
    (TipoSolicitud.RECLAMO_DE_NOTA, Prioridad.ALTA),
])
def test_la_prioridad_depende_del_tipo(tipo, prioridad):
    assert DatosSolicitud(ANA, tipo, "Pedido").calcular_prioridad() is prioridad


@pytest.mark.parametrize("tipo, prioridad", [
    (TipoSolicitud.CERTIFICADO_ALUMNO_REGULAR, Prioridad.MEDIA),
    (TipoSolicitud.RECLAMO_DE_NOTA, Prioridad.ALTA),
])
def test_urgente_sube_la_prioridad_un_nivel_sin_pasar_de_alta(tipo, prioridad):
    assert DatosSolicitud(ANA, tipo, "Pedido URGENTE").calcular_prioridad() is prioridad


@pytest.mark.parametrize("legajo, nombre, email, mensaje", [
    ("123", "Ana", "ana@mail.com", "legajo invalido"),
    ("10001", "", "ana@mail.com", "nombre y apellido son obligatorios"),
    ("10001", "Ana", "ana@mail", "email invalido"),
])
def test_validaciones_del_estudiante(legajo, nombre, email, mensaje):
    with pytest.raises(ErrorDeNegocio, match=mensaje):
        Estudiante.nuevo(legajo, nombre, "Lopez", email)


def test_la_descripcion_es_obligatoria():
    with pytest.raises(ErrorDeNegocio, match="la descripcion es obligatoria"):
        DatosSolicitud(ANA, TipoSolicitud.EQUIVALENCIA, "   ")


def test_una_solicitud_nueva_queda_pendiente_y_sin_area():
    solicitud = nueva_solicitud()

    assert solicitud.estado is EstadoSolicitud.PENDIENTE
    assert solicitud.numero_area == SIN_AREA


@pytest.mark.parametrize("nuevo, mensaje", [
    (EstadoSolicitud.RESUELTA, "sin pasar por En proceso"),
    (EstadoSolicitud.EN_PROCESO, "debe asignar un responsable"),
    (EstadoSolicitud.PENDIENTE, "ya se encuentra en ese estado"),
])
def test_transiciones_invalidas_desde_pendiente(nuevo, mensaje):
    with pytest.raises(ErrorDeNegocio, match=mensaje):
        nueva_solicitud().cambiar_estado(nuevo)


def test_una_solicitud_cerrada_no_se_modifica():
    solicitud = nueva_solicitud()
    solicitud.cambiar_estado(EstadoSolicitud.RECHAZADA)

    with pytest.raises(ErrorDeNegocio, match="esta cerrada"):
        solicitud.cambiar_estado(EstadoSolicitud.PENDIENTE)
    with pytest.raises(ErrorDeNegocio, match="no se puede asignar una solicitud cerrada"):
        solicitud.asignar_area(BEDELIA)


def test_la_solicitud_se_guarda_con_el_formato_de_la_version_base():
    solicitud = nueva_solicitud()
    solicitud.asignar_area(BEDELIA)

    assert solicitud.a_diccionario() == {
        "id": 1,
        "legajo": "10001",
        "estudiante": "Lopez, Ana",
        "email": "ana@mail.com",
        "tipo": 2,
        "descripcion": "Equivalencia de Algebra",
        "prioridad": 2,
        "estado": "pend",
        "area": 1,
        "fecha": "2026-11-08",
    }
