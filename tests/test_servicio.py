import pytest

from dominio import (AREAS_RESPONSABLES, DatosSolicitud, ErrorDeNegocio, EstadoSolicitud, Prioridad,
                     TipoSolicitud)
from repositorio import RepositorioEnMemoria
from servicio import ServicioSolicitudes

FECHA = "2026-11-08"


@pytest.fixture
def servicio():
    repositorio = RepositorioEnMemoria()
    return ServicioSolicitudes(repositorio, repositorio, AREAS_RESPONSABLES, lambda: FECHA)


@pytest.fixture
def ana(servicio):
    return servicio.registrar_estudiante("10001", "Ana", "Lopez", "ana@mail.com")


def registrar(servicio, estudiante, tipo, descripcion="Pedido"):
    return servicio.registrar_solicitud(DatosSolicitud(estudiante, tipo, descripcion))


def test_no_se_registran_dos_estudiantes_con_el_mismo_legajo(servicio, ana):
    with pytest.raises(ErrorDeNegocio, match="ya existe un estudiante con ese legajo"):
        servicio.registrar_estudiante("10001", "Otra", "Persona", "otra@mail.com")


def test_las_solicitudes_se_numeran_en_orden_y_llevan_la_fecha(servicio, ana):
    primera = registrar(servicio, ana, TipoSolicitud.EQUIVALENCIA)
    segunda = registrar(servicio, ana, TipoSolicitud.RECLAMO_DE_NOTA)

    assert (primera.numero, segunda.numero) == (1, 2)
    assert primera.fecha == FECHA


def test_listar_combina_los_filtros(servicio, ana):
    certificado = TipoSolicitud.CERTIFICADO_ALUMNO_REGULAR
    normal = registrar(servicio, ana, certificado)
    urgente = registrar(servicio, ana, certificado, "urgente")
    registrar(servicio, ana, TipoSolicitud.RECLAMO_DE_NOTA)

    assert servicio.listar(tipo=certificado) == [normal, urgente]
    assert servicio.listar(tipo=certificado, prioridad=Prioridad.MEDIA) == [urgente]


def test_el_reporte_cuenta_por_estado_tipo_y_prioridad(servicio, ana):
    resuelta = registrar(servicio, ana, TipoSolicitud.RECLAMO_DE_NOTA)
    registrar(servicio, ana, TipoSolicitud.EQUIVALENCIA)
    registrar(servicio, ana, TipoSolicitud.EQUIVALENCIA)
    servicio.asignar_area(resuelta.numero, 1)
    servicio.cambiar_estado(resuelta.numero, EstadoSolicitud.EN_PROCESO)
    servicio.cambiar_estado(resuelta.numero, EstadoSolicitud.RESUELTA)

    reporte = servicio.generar_reporte()

    assert reporte.total == 3
    assert reporte.por_estado[EstadoSolicitud.PENDIENTE] == 2
    assert reporte.por_tipo[TipoSolicitud.EQUIVALENCIA] == 2
    assert reporte.por_prioridad[Prioridad.ALTA] == 1
    assert reporte.sin_responsable == 2
    assert reporte.porcentaje_resueltas == 33.3
