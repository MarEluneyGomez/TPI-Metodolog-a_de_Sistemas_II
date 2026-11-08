import os
import subprocess
import sys
from pathlib import Path

import pytest

from repositorio import ErrorDePersistencia, RepositorioJson

MAIN = Path(__file__).resolve().parent.parent / "main.py"

# Mismo archivo que en docs/evidencias/defecto-perdida-de-datos.md
ARCHIVO_DANADO = (
    '{"estudiantes": [{"legajo": "10001", "nombre": "Ana", "apellido": "Lopez", '
    '"email": "ana@mail.com"}], "solicitudes": [], "contador": 1'
)

REGISTRAR_OTRO_ESTUDIANTE = ["1", "10002", "Bruno", "Diaz", "bruno@mail.com", "0"]


def test_con_archivo_danado_no_se_pierden_los_datos(tmp_path):
    archivo = tmp_path / "datos.json"
    archivo.write_text(ARCHIVO_DANADO, encoding="utf-8")

    resultado = subprocess.run(
        [sys.executable, str(MAIN)],
        input="\n".join(REGISTRAR_OTRO_ESTUDIANTE) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"),
        timeout=30,
    )

    assert archivo.read_text(encoding="utf-8") == ARCHIVO_DANADO
    assert "no se pudo leer" in resultado.stdout
    assert resultado.returncode != 0


@pytest.mark.parametrize("contenido", [
    ARCHIVO_DANADO,
    '{"estudiantes": []}',
    "[]",
    "",
])
def test_el_repositorio_rechaza_un_archivo_invalido(tmp_path, contenido):
    archivo = tmp_path / "datos.json"
    archivo.write_text(contenido, encoding="utf-8")

    with pytest.raises(ErrorDePersistencia):
        RepositorioJson(archivo)
