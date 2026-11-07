import argparse
import io
import subprocess
import sys
import tarfile
import tempfile
from importlib.metadata import version
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CARPETAS_EXCLUIDAS = {"tests", "herramientas", "docs", "venv", "__pycache__"}

# --persistent=n: la salida no depende de ejecuciones anteriores de pylint.
OPCIONES_PYLINT = ["--disable=C0114,C0115,C0116", "--persistent=n"]


def archivos_a_medir(base):
    archivos = []
    for ruta in base.rglob("*.py"):
        carpetas = ruta.relative_to(base).parts[:-1]
        if any(c in CARPETAS_EXCLUIDAS or c.startswith(".") for c in carpetas):
            continue
        archivos.append(ruta.relative_to(base).as_posix())
    return sorted(archivos)


def ejecutar(comando, carpeta):
    resultado = subprocess.run(
        [sys.executable, "-m", *comando],
        cwd=carpeta,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return resultado


def ejecutar_radon(subcomando, opciones, archivos, carpeta):
    resultado = ejecutar(["radon", subcomando, *opciones, *archivos], carpeta)
    if resultado.returncode != 0:
        raise RuntimeError(f"radon {subcomando} fallo:\n{resultado.stderr}")
    return resultado.stdout


def ejecutar_pylint(archivos, carpeta):
    resultado = ejecutar(["pylint", *OPCIONES_PYLINT, *archivos], carpeta)
    # pylint sale con codigo distinto de 0 cuando encuentra problemas; solo los
    # bits 1 (fatal) y 32 (error de uso) significan que no pudo analizar.
    if resultado.returncode & (1 | 32):
        raise RuntimeError(f"pylint no pudo analizar el codigo:\n{resultado.stderr}")
    return resultado.stdout


def extraer_version(ref, destino):
    commit = subprocess.run(
        ["git", "rev-parse", "--short", f"{ref}^{{commit}}"],
        cwd=RAIZ, capture_output=True, text=True, check=True,
    ).stdout.strip()
    contenido = subprocess.run(
        ["git", "archive", "--format=tar", ref],
        cwd=RAIZ, capture_output=True, check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(contenido)) as tar:
        tar.extractall(destino, filter="data")
    return commit


def escribir(carpeta, nombre, contenido):
    (carpeta / nombre).write_text(contenido, encoding="utf-8", newline="\n")


def medir(base, salida, descripcion_version):
    archivos = archivos_a_medir(base)
    if not archivos:
        raise RuntimeError(f"No se encontraron archivos .py para medir en {base}")
    salida.mkdir(parents=True, exist_ok=True)

    escribir(salida, "radon-complejidad.txt", ejecutar_radon("cc", ["-s", "-a"], archivos, base))
    escribir(salida, "radon-mantenibilidad.txt", ejecutar_radon("mi", ["-s"], archivos, base))
    escribir(salida, "radon-tamanio.txt", ejecutar_radon("raw", ["-s"], archivos, base))
    escribir(salida, "pylint.txt", ejecutar_pylint(archivos, base))

    escribir(salida, "informacion.txt", "\n".join([
        f"Version medida: {descripcion_version}",
        f"Archivos medidos: {', '.join(archivos)}",
        f"Python {sys.version.split()[0]}",
        f"radon {version('radon')}",
        f"pylint {version('pylint')} (astroid {version('astroid')})",
        "Comandos:",
        "  radon cc -s -a <archivos>",
        "  radon mi -s <archivos>",
        "  radon raw -s <archivos>",
        f"  pylint {' '.join(OPCIONES_PYLINT)} <archivos>",
        "",
    ]))
    print(f"Metricas de {descripcion_version} guardadas en {salida}")


def main():
    parser = argparse.ArgumentParser(description="Mide la calidad del codigo con radon y pylint.")
    parser.add_argument("--salida", required=True, help="carpeta donde guardar los resultados")
    parser.add_argument("--ref", help="tag o commit de git a medir (por defecto, la carpeta actual)")
    argumentos = parser.parse_args()
    salida = (Path.cwd() / argumentos.salida).resolve()

    if argumentos.ref is None:
        medir(RAIZ, salida, "carpeta de trabajo actual")
        return
    with tempfile.TemporaryDirectory() as temporal:
        commit = extraer_version(argumentos.ref, temporal)
        medir(Path(temporal), salida, f"{argumentos.ref} (commit {commit})")


if __name__ == "__main__":
    main()
