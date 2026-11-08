from repositorio import RepositorioJson
from sistema import Sistema

ARCHIVO_DATOS = "datos.json"


def menu():
    print("")
    print("===== GESTION DE SOLICITUDES ACADEMICAS =====")
    print("1. Registrar estudiante")
    print("2. Registrar solicitud")
    print("3. Cambiar estado de solicitud")
    print("4. Asignar responsable")
    print("5. Listar / filtrar solicitudes")
    print("6. Reporte")
    print("0. Salir")


repositorio = RepositorioJson(ARCHIVO_DATOS)
s = Sistema(repositorio, repositorio)
while True:
    menu()
    op = input("Opcion: ")
    if op == "1":
        s.registrar_estudiante()
    elif op == "2":
        s.registrar_solicitud()
    elif op == "3":
        s.cambiar_estado()
    elif op == "4":
        s.asignar_responsable()
    elif op == "5":
        s.listar()
    elif op == "6":
        s.reporte()
    elif op == "0":
        print("Hasta luego")
        break
    else:
        print("Opcion invalida")
