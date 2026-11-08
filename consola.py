from dominio import DatosSolicitud, ErrorDeNegocio, EstadoSolicitud, Prioridad, TipoSolicitud
from repositorio import ErrorDePersistencia


class EntradaInvalida(Exception):
    pass


class InterfazConsola:

    def __init__(self, servicio, leer=input, escribir=print):
        self._servicio = servicio
        self._leer = leer
        self._escribir = escribir
        self._opciones = [
            ("1", "Registrar estudiante", self.registrar_estudiante),
            ("2", "Registrar solicitud", self.registrar_solicitud),
            ("3", "Cambiar estado de solicitud", self.cambiar_estado),
            ("4", "Asignar responsable", self.asignar_responsable),
            ("5", "Listar / filtrar solicitudes", self.listar),
            ("6", "Reporte", self.reporte),
        ]

    def ejecutar(self):
        acciones = {clave: accion for clave, _, accion in self._opciones}
        while True:
            self._mostrar_menu()
            opcion = self._leer("Opcion: ")
            if opcion == "0":
                self._escribir("Hasta luego")
                return
            accion = acciones.get(opcion)
            if accion is None:
                self._escribir("Opcion invalida")
                continue
            try:
                accion()
            except (EntradaInvalida, ErrorDeNegocio, ErrorDePersistencia) as error:
                self._escribir("Error: " + str(error))

    def registrar_estudiante(self):
        legajo = self._leer("Legajo: ")
        nombre = self._leer("Nombre: ")
        apellido = self._leer("Apellido: ")
        email = self._leer("Email: ")
        estudiante = self._servicio.registrar_estudiante(legajo, nombre, apellido, email)
        self._escribir("Estudiante registrado: " + estudiante.nombre_completo)

    def registrar_solicitud(self):
        estudiante = self._servicio.buscar_estudiante(self._leer("Legajo del estudiante: "))
        self._escribir("Tipos de solicitud:")
        for tipo in TipoSolicitud:
            self._escribir(f"{tipo.codigo}. {tipo.etiqueta}")
        tipo = self._leer_tipo()
        descripcion = self._leer("Descripcion: ")
        solicitud = self._servicio.registrar_solicitud(DatosSolicitud(estudiante, tipo, descripcion))
        self._escribir(f"Solicitud #{solicitud.numero} registrada con prioridad {solicitud.prioridad.etiqueta}")

    def cambiar_estado(self):
        solicitud = self._servicio.solicitud_para_cambiar_estado(self._leer_numero_de_solicitud())
        self._escribir("Estado actual: " + solicitud.estado.etiqueta)
        for numero, estado in enumerate(EstadoSolicitud, start=1):
            self._escribir(f"{numero}. {estado.etiqueta}")
        nuevo_estado = self._leer_estado("Nuevo estado: ")
        self._servicio.cambiar_estado(solicitud.numero, nuevo_estado)
        self._escribir("Estado actualizado")

    def asignar_responsable(self):
        solicitud = self._servicio.solicitud_para_asignar(self._leer_numero_de_solicitud())
        self._escribir("Areas disponibles:")
        for area in self._servicio.areas_disponibles():
            self._escribir(f"{area.numero}. {area.nombre} ({area.responsable})")
        texto = self._leer("Area: ")
        if not texto.isdigit():
            raise EntradaInvalida("area invalida")
        area = self._servicio.asignar_area(solicitud.numero, int(texto))
        self._escribir(f"Solicitud #{solicitud.numero} asignada a {area.nombre} ({area.responsable})")

    def listar(self):
        if not self._servicio.hay_solicitudes():
            self._escribir("No hay solicitudes")
            return
        filtros = {
            "1": ("Todas", self._sin_filtro),
            "2": ("Por estado", self._filtro_por_estado),
            "3": ("Por tipo", self._filtro_por_tipo),
            "4": ("Por prioridad", self._filtro_por_prioridad),
        }
        for clave, (texto, _) in filtros.items():
            self._escribir(f"{clave}. {texto}")
        elegido = filtros.get(self._leer("Filtro: "))
        if elegido is None:
            raise EntradaInvalida("filtro invalido")
        _, pedir_filtro = elegido
        solicitudes = self._servicio.listar(**pedir_filtro())
        if not solicitudes:
            self._escribir("No hay solicitudes que coincidan con el filtro")
            return
        for solicitud in solicitudes:
            self._mostrar_solicitud(solicitud)

    def reporte(self):
        if not self._servicio.hay_solicitudes():
            self._escribir("No hay solicitudes para reportar")
            return
        reporte = self._servicio.generar_reporte()
        self._escribir("===== REPORTE DE SOLICITUDES =====")
        self._escribir(f"Total: {reporte.total}")
        self._escribir("Por estado:")
        for estado in EstadoSolicitud:
            self._escribir(f"  {estado.etiqueta}: {reporte.por_estado[estado]}")
        self._escribir("Por tipo:")
        for tipo in TipoSolicitud:
            self._escribir(f"  {tipo.etiqueta}: {reporte.por_tipo[tipo]}")
        self._escribir("Por prioridad:")
        for prioridad in reversed(Prioridad):
            self._escribir(f"  {prioridad.etiqueta}: {reporte.por_prioridad[prioridad]}")
        self._escribir(f"Sin responsable asignado: {reporte.sin_responsable}")
        self._escribir(f"Porcentaje resueltas: {reporte.porcentaje_resueltas}%")

    def _mostrar_menu(self):
        self._escribir("")
        self._escribir("===== GESTION DE SOLICITUDES ACADEMICAS =====")
        for clave, texto, _ in self._opciones:
            self._escribir(f"{clave}. {texto}")
        self._escribir("0. Salir")

    def _mostrar_solicitud(self, solicitud):
        area = self._servicio.buscar_area(solicitud.area)
        nombre_area = area.nombre if area is not None else "Sin asignar"
        self._escribir(
            f"#{solicitud.numero} | {solicitud.tipo.etiqueta} | {solicitud.prioridad.etiqueta}"
            f" | {solicitud.estado.etiqueta} | {solicitud.estudiante} ({solicitud.legajo}) | Area: {nombre_area}"
        )
        self._escribir("    " + solicitud.descripcion)

    def _sin_filtro(self):
        return {}

    def _filtro_por_estado(self):
        self._escribir("  ".join(f"{n}. {e.etiqueta}" for n, e in enumerate(EstadoSolicitud, start=1)))
        return {"estado": self._leer_estado("Estado: ")}

    def _filtro_por_tipo(self):
        self._escribir("  ".join(f"{t.codigo}. {t.etiqueta}" for t in TipoSolicitud))
        return {"tipo": self._leer_tipo()}

    def _filtro_por_prioridad(self):
        opciones = ", ".join(f"{p.codigo}={p.etiqueta}" for p in Prioridad)
        texto = self._leer(f"Prioridad ({opciones}): ")
        for prioridad in Prioridad:
            if texto == str(prioridad.codigo):
                return {"prioridad": prioridad}
        raise EntradaInvalida("prioridad invalida")

    def _leer_numero_de_solicitud(self):
        texto = self._leer("ID de solicitud: ")
        if not texto.isdigit():
            raise EntradaInvalida("id invalido")
        return int(texto)

    def _leer_tipo(self):
        texto = self._leer("Tipo: ")
        if texto.isdigit():
            for tipo in TipoSolicitud:
                if tipo.codigo == int(texto):
                    return tipo
        raise EntradaInvalida("tipo invalido")

    def _leer_estado(self, mensaje):
        texto = self._leer(mensaje)
        for numero, estado in enumerate(EstadoSolicitud, start=1):
            if texto == str(numero):
                return estado
        raise EntradaInvalida("estado invalido")
