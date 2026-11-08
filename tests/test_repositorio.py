from dominio import AREAS_RESPONSABLES, DatosSolicitud, Estudiante, Solicitud, TipoSolicitud
from repositorio import RepositorioJson

ANA = Estudiante("10001", "Ana", "Lopez", "ana@mail.com")


def test_los_datos_guardados_se_recuperan_en_otra_ejecucion(tmp_path):
    archivo = tmp_path / "datos.json"
    repositorio = RepositorioJson(archivo)
    repositorio.agregar_estudiante(ANA)
    datos = DatosSolicitud(ANA, TipoSolicitud.EQUIVALENCIA, "Pedido")
    solicitud = Solicitud.crear(1, datos, "2026-11-08")
    repositorio.agregar_solicitud(solicitud)
    solicitud.asignar_area(AREAS_RESPONSABLES[0])
    repositorio.actualizar_solicitud(solicitud)

    recuperado = RepositorioJson(archivo)

    assert recuperado.buscar_estudiante("10001") == ANA
    assert recuperado.listar_solicitudes() == [solicitud]
    assert recuperado.proximo_numero() == 2


def test_al_guardar_no_queda_el_archivo_temporal(tmp_path):
    repositorio = RepositorioJson(tmp_path / "datos.json")

    repositorio.agregar_estudiante(ANA)

    assert [archivo.name for archivo in tmp_path.iterdir()] == ["datos.json"]
