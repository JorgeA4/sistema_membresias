"""Menú operativo de Administrador y Cajero."""

from rich.console import Console
from rich.panel import Panel
from rich import box as rich_box

import questionary

from interfaz_term.componentes.formulario import pedir_formulario
from interfaz_term.componentes.mensajes import error, exito
from interfaz_term.componentes.tabla import mostrar_tabla
from interfaz_term.estilos.tema import COLOR_ENCABEZADO, COLOR_TITULO
from servicios.caja.servicio_caja import registrar_operacion_caja
from servicios.compra.servicio_compra import (
    obtener_compras_de_membresia,
    obtener_transacciones_de_miembro,
)
from servicios.ajuste.servicio_ajuste import ajustar_cashback, ajustar_puntos
from servicios.membresia.servicio_membresia import (
    contratar_membresia,
    cancelar_membresia,
    renovar_membresia,
    suspender_membresia,
)
from servicios.miembro.servicio_miembro import modificar_miembro, registrar_miembro
from servicios.plan.servicio_plan import (
    crear_version_plan,
    finalizar_version_plan,
    modificar_plan,
    obtener_planes,
    registrar_plan,
)
from clases.version_plan import ConfigCashback, ConfigDescuento, ConfigPuntos
from servicios.recompensa.servicio_recompensa import (
    crear_version_recompensa,
    modificar_recompensa,
    obtener_recompensas,
    registrar_recompensa,
)
from servicios.usuario.servicio_usuario import (
    modificar_usuario,
    obtener_usuarios,
    registrar_usuario,
)
from servicios.miembro.servicio_miembro import consultar_miembro
from servicios.membresia.servicio_membresia import consultar_membresia

_consola = Console()


def mostrar_usuario(sesion: dict) -> tuple:
    identidad = sesion.get("identidad") or {}
    rol = identidad.get("rol", "")
    nombre_rol = identidad.get("rol_nombre", "Usuario")
    nombre = identidad.get("nombre", "")

    while True:
        _consola.clear()
        _consola.print(
            Panel(
                f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}] — [dim]Interfaz administrativa[/dim]\n"
                f"Usuario: {nombre} | Rol: [{COLOR_ENCABEZADO}]{nombre_rol}[/{COLOR_ENCABEZADO}]",
                border_style=COLOR_ENCABEZADO,
                box=rich_box.ROUNDED,
                padding=(0, 4),
            )
        )

        opciones = [
            "Registrar venta",
            "Registrar miembro",
            "Contratar membresía",
            "Renovar membresía",
            "Cambiar plan",
            "Consultar miembro",
        ]
        if rol == "ADM":
            opciones.extend(
                [
                    "Consultar planes",
                    "Crear plan",
                    "Modificar miembro",
                    "Modificar plan",
                    "Crear versión de plan",
                    "Finalizar versión de plan",
                    "Consultar recompensas",
                    "Crear recompensa",
                    "Modificar recompensa",
                    "Crear versión de recompensa",
                    "Registrar usuario administrativo",
                    "Modificar usuario administrativo",
                    "Consultar usuarios",
                    "Consultar actividad",
                    "Suspender membresía",
                    "Cancelar membresía",
                    "Ajustar puntos",
                    "Ajustar cashback",
                ]
            )
        opciones.append("Cerrar sesión")

        accion = questionary.select("¿Qué deseas hacer?", choices=opciones).ask()
        if accion == "Registrar venta":
            _registrar_venta(identidad)
        elif accion == "Registrar miembro":
            _registrar_nuevo_miembro(identidad)
        elif accion == "Modificar miembro":
            _modificar_miembro(identidad)
        elif accion == "Contratar membresía":
            _contratar(identidad)
        elif accion == "Renovar membresía":
            _renovar(identidad)
        elif accion == "Cambiar plan":
            _renovar(identidad, titulo="Cambiar plan mediante renovación")
        elif accion == "Consultar miembro":
            _consultar_miembro(identidad)
        elif accion == "Consultar planes":
            _consultar_planes(identidad)
        elif accion == "Crear plan":
            _crear_plan(identidad)
        elif accion == "Modificar plan":
            _modificar_plan(identidad)
        elif accion == "Crear versión de plan":
            _crear_version_plan(identidad)
        elif accion == "Finalizar versión de plan":
            _finalizar_version_plan(identidad)
        elif accion == "Consultar recompensas":
            _consultar_recompensas(identidad)
        elif accion == "Crear recompensa":
            _crear_recompensa(identidad)
        elif accion == "Modificar recompensa":
            _modificar_recompensa(identidad)
        elif accion == "Crear versión de recompensa":
            _crear_version_recompensa(identidad)
        elif accion == "Registrar usuario administrativo":
            _registrar_usuario(identidad)
        elif accion == "Modificar usuario administrativo":
            _modificar_usuario(identidad)
        elif accion == "Consultar usuarios":
            _consultar_usuarios(identidad)
        elif accion == "Consultar actividad":
            _consultar_actividad(identidad)
        elif accion == "Suspender membresía":
            _cambiar_estado_membresia(identidad, suspender_membresia, "suspendida")
        elif accion == "Cancelar membresía":
            _cambiar_estado_membresia(identidad, cancelar_membresia, "cancelada")
        elif accion == "Ajustar puntos":
            _ajustar_puntos(identidad)
        elif accion == "Ajustar cashback":
            _ajustar_cashback(identidad)
        else:
            sesion["identidad"] = None
            return None, 1


def _registrar_venta(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num_membresia", "etiqueta": "Número de membresía"},
            {"clave": "monto_base", "etiqueta": "Monto de la compra"},
            {
                "clave": "cashback_aplicado",
                "etiqueta": "Cashback a utilizar (0 si no aplica)",
                "requerido": True,
            },
            {
                "clave": "codigo_recompensa",
                "etiqueta": "Código de recompensa (vacío si no aplica)",
                "requerido": False,
            },
        ]
    )
    if datos is None:
        return
    try:
        datos["num_membresia"] = _numero(datos["num_membresia"])
        resultado = registrar_operacion_caja(identidad, datos)
        mensaje = f"Compra registrada con número {resultado['compra'].num}."
        if resultado["canje"] is not None:
            mensaje += " El canje también fue registrado."
        exito(mensaje)
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _registrar_nuevo_miembro(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido", "requerido": False},
            {"clave": "telefono", "etiqueta": "Teléfono"},
            {"clave": "correo", "etiqueta": "Correo electrónico"},
            {"clave": "contraseña", "etiqueta": "Contraseña", "contrasena": True},
        ]
    )
    if datos is None:
        return
    try:
        miembro = registrar_miembro(identidad, datos)
        exito(f"Miembro registrado con número {miembro.num}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _modificar_miembro(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num", "etiqueta": "Número de miembro"},
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido", "requerido": False},
            {"clave": "telefono", "etiqueta": "Teléfono"},
            {"clave": "correo", "etiqueta": "Correo electrónico"},
        ]
    )
    if datos is None:
        return
    try:
        numero = _numero(datos.pop("num"))
        miembro = modificar_miembro(identidad, numero, datos)
        exito(f"Miembro {miembro.num} modificado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _contratar(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num_miembro", "etiqueta": "Número de miembro"},
            {"clave": "num_version", "etiqueta": "Número de versión de contratación"},
        ]
    )
    if datos is None:
        return
    try:
        renovacion = contratar_membresia(
            identidad,
            _numero(datos["num_miembro"]),
            _numero(datos["num_version"]),
        )
        exito(f"Membresía contratada con renovación {renovacion.num}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _renovar(identidad: dict, titulo: str = "Renovar membresía") -> None:
    datos = pedir_formulario(
        [
            {"clave": "num_membresia", "etiqueta": "Número de membresía"},
            {"clave": "num_version", "etiqueta": "Número de versión del nuevo plan"},
        ]
    )
    if datos is None:
        return
    try:
        renovacion = renovar_membresia(
            identidad,
            _numero(datos["num_membresia"]),
            _numero(datos["num_version"]),
        )
        exito(f"{titulo} registrada con renovación {renovacion.num}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _consultar_miembro(identidad: dict) -> None:
    numero = questionary.text("Número de miembro:").ask()
    if numero is None:
        return
    try:
        miembro = consultar_miembro(identidad, _numero(numero))
        if miembro is None:
            raise ValueError("El miembro no existe.")
        mostrar_tabla(
            "Miembro",
            ["Número", "Nombre", "Correo", "Teléfono"],
            [(miembro.num, f"{miembro.nombre} {miembro.primer_apellido}", miembro.correo, miembro.telefono)],
        )
        input("Presiona Enter para continuar.")
    except ValueError as exc:
        error(str(exc))


def _consultar_planes(identidad: dict) -> None:
    planes = obtener_planes(identidad)
    mostrar_tabla(
        "Planes",
        ["Código", "Nombre", "Descripción"],
        [(plan.codigo, plan.nombre, plan.descripcion or "") for plan in planes],
    )
    input("Presiona Enter para continuar.")


def _consultar_recompensas(identidad: dict) -> None:
    recompensas = obtener_recompensas(identidad)
    mostrar_tabla(
        "Recompensas",
        ["Código", "Nombre", "Descripción"],
        [(recompensa.codigo, recompensa.nombre, recompensa.descripcion or "") for recompensa in recompensas],
    )
    input("Presiona Enter para continuar.")


def _crear_plan(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "codigo", "etiqueta": "Código"},
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "descripcion", "etiqueta": "Descripción", "requerido": False},
        ]
    )
    if datos is None:
        return
    try:
        plan = registrar_plan(identidad, datos)
        exito(f"Plan {plan.codigo} registrado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _modificar_plan(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "codigo", "etiqueta": "Código del plan"},
            {"clave": "nombre", "etiqueta": "Nuevo nombre"},
            {"clave": "descripcion", "etiqueta": "Nueva descripción", "requerido": False},
        ]
    )
    if datos is None:
        return
    try:
        codigo = datos.pop("codigo")
        plan = modificar_plan(identidad, codigo, datos)
        exito(f"Plan {plan.codigo} modificado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _crear_version_plan(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "codigo_plan", "etiqueta": "Código del plan"},
            {"clave": "fecha_inicio", "etiqueta": "Fecha inicial (AAAA-MM-DD)"},
            {"clave": "fecha_final", "etiqueta": "Fecha final (AAAA-MM-DD)"},
            {"clave": "precio", "etiqueta": "Precio"},
            {"clave": "plazo_meses", "etiqueta": "Plazo en meses"},
            {"clave": "aplica_en", "etiqueta": "Aplicación (CONTRATACION, RENOVACION o AMBAS)"},
        ]
    )
    if datos is None:
        return
    try:
        datos["fecha_inicio"] = _fecha(datos["fecha_inicio"])
        datos["fecha_final"] = _fecha(datos["fecha_final"])
        datos["plazo_meses"] = _numero(datos["plazo_meses"])
        _configurar_beneficios_version(datos)
        version = crear_version_plan(identidad, datos)
        exito(f"Versión {version.num} registrada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _configurar_beneficios_version(datos: dict) -> None:
    configuradas = set()
    opciones = {
        "Configurar puntos": "puntos",
        "Configurar descuento": "descuento",
        "Configurar cashback": "cashback",
    }
    while True:
        disponibles = [opcion for opcion, clave in opciones.items() if clave not in configuradas]
        disponibles.append("Terminar configuración")
        seleccion = questionary.select(
            "¿Qué beneficio deseas configurar?",
            choices=disponibles,
        ).ask()
        if seleccion == "Terminar configuración" or seleccion is None:
            return

        clave = opciones[seleccion]
        if clave == "puntos":
            configuracion = pedir_formulario(
                [
                    {"clave": "porcentaje", "etiqueta": "Porcentaje de puntos (ej. 0.025)"},
                    {"clave": "vigencia_meses", "etiqueta": "Vigencia en meses (vacío sin caducidad)", "requerido": False},
                ]
            )
            if configuracion is not None:
                vigencia = configuracion["vigencia_meses"]
                datos["config_puntos"] = ConfigPuntos(
                    num=None,
                    porcentaje=configuracion["porcentaje"],
                    vigencia_meses=None if not vigencia else _numero(vigencia),
                )
        elif clave == "descuento":
            configuracion = pedir_formulario(
                [
                    {"clave": "porcentaje", "etiqueta": "Porcentaje de descuento (ej. 0.10)"},
                    {"clave": "monto_minimo", "etiqueta": "Monto mínimo (vacío sin mínimo)", "requerido": False},
                    {"clave": "dias_aplicables", "etiqueta": "Días ISO separados por coma (vacío todos)", "requerido": False},
                ]
            )
            if configuracion is not None:
                minimo = configuracion["monto_minimo"]
                dias = configuracion["dias_aplicables"]
                datos["config_descuento"] = ConfigDescuento(
                    num=None,
                    porcentaje=configuracion["porcentaje"],
                    monto_minimo=None if not minimo else minimo,
                    dias_aplicables=[] if not dias else [_numero(dia.strip()) for dia in dias.split(",")],
                )
        else:
            configuracion = pedir_formulario(
                [
                    {"clave": "porcentaje", "etiqueta": "Porcentaje de cashback (ej. 0.05)"},
                    {"clave": "limite_min_mensual", "etiqueta": "Umbral mensual (vacío sin umbral)", "requerido": False},
                ]
            )
            if configuracion is not None:
                limite = configuracion["limite_min_mensual"]
                datos["config_cashback"] = ConfigCashback(
                    num=None,
                    porcentaje=configuracion["porcentaje"],
                    limite_min_mensual=None if not limite else limite,
                )
        if f"config_{clave}" in datos:
            configuradas.add(clave)


def _finalizar_version_plan(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num", "etiqueta": "Número de versión"},
            {"clave": "fecha_final", "etiqueta": "Nueva fecha final (AAAA-MM-DD)"},
        ]
    )
    if datos is None:
        return
    try:
        version = finalizar_version_plan(
            identidad,
            _numero(datos["num"]),
            _fecha(datos["fecha_final"]),
        )
        exito(f"Versión {version.num} finalizada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _crear_recompensa(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "codigo", "etiqueta": "Código"},
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "descripcion", "etiqueta": "Descripción", "requerido": False},
        ]
    )
    if datos is None:
        return
    try:
        recompensa = registrar_recompensa(identidad, datos)
        exito(f"Recompensa {recompensa.codigo} registrada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _modificar_recompensa(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "codigo", "etiqueta": "Código de recompensa"},
            {"clave": "nombre", "etiqueta": "Nuevo nombre"},
            {"clave": "descripcion", "etiqueta": "Nueva descripción", "requerido": False},
        ]
    )
    if datos is None:
        return
    try:
        codigo = datos.pop("codigo")
        recompensa = modificar_recompensa(identidad, codigo, datos)
        exito(f"Recompensa {recompensa.codigo} modificada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _crear_version_recompensa(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "codigo_recompensa", "etiqueta": "Código de recompensa"},
            {"clave": "fecha_inicio", "etiqueta": "Fecha inicial (AAAA-MM-DD)"},
            {"clave": "fecha_final", "etiqueta": "Fecha final (AAAA-MM-DD)"},
            {"clave": "costo_puntos", "etiqueta": "Costo en puntos"},
            {"clave": "limite_canjes", "etiqueta": "Límite de canjes", "requerido": False},
        ]
    )
    if datos is None:
        return
    try:
        datos["fecha_inicio"] = _fecha(datos["fecha_inicio"])
        datos["fecha_final"] = _fecha(datos["fecha_final"])
        datos["costo_puntos"] = _numero(datos["costo_puntos"])
        if datos["limite_canjes"]:
            datos["limite_canjes"] = _numero(datos["limite_canjes"])
        else:
            datos["limite_canjes"] = None
        version = crear_version_recompensa(identidad, datos)
        exito(f"Versión {version.num} registrada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _registrar_usuario(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "correo", "etiqueta": "Correo electrónico"},
            {"clave": "contraseña", "etiqueta": "Contraseña", "contrasena": True},
            {"clave": "codigo_rol", "etiqueta": "Rol (ADM o CAJ)"},
        ]
    )
    if datos is None:
        return
    try:
        usuario = registrar_usuario(identidad, datos)
        exito(f"Usuario registrado con número {usuario.num}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _modificar_usuario(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num", "etiqueta": "Número de usuario"},
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "correo", "etiqueta": "Correo electrónico"},
            {"clave": "codigo_rol", "etiqueta": "Rol (ADM o CAJ)"},
        ]
    )
    if datos is None:
        return
    try:
        numero = _numero(datos.pop("num"))
        usuario = modificar_usuario(identidad, numero, datos)
        exito(f"Usuario {usuario.num} modificado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _cambiar_estado_membresia(identidad: dict, operacion, estado: str) -> None:
    numero = questionary.text("Número de membresía:").ask()
    if numero is None:
        return
    try:
        operacion(identidad, _numero(numero))
        exito(f"La membresía quedó {estado}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _ajustar_puntos(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num_membresia", "etiqueta": "Número de membresía"},
            {"clave": "movimiento", "etiqueta": "Movimiento de puntos (+/-)"},
            {"clave": "concepto", "etiqueta": "Concepto"},
        ]
    )
    if datos is None:
        return
    try:
        transaccion = ajustar_puntos(
            identidad,
            _numero(datos["num_membresia"]),
            _numero(datos["movimiento"]),
            datos["concepto"],
        )
        exito(f"Ajuste registrado. Nuevo saldo: {transaccion.saldo} puntos.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _ajustar_cashback(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num_membresia", "etiqueta": "Número de membresía"},
            {"clave": "movimiento", "etiqueta": "Movimiento de cashback (+/-)"},
            {"clave": "concepto", "etiqueta": "Concepto"},
        ]
    )
    if datos is None:
        return
    try:
        transaccion = ajustar_cashback(
            identidad,
            _numero(datos["num_membresia"]),
            datos["movimiento"],
            datos["concepto"],
        )
        exito(f"Ajuste registrado. Nuevo saldo: {transaccion.saldo}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _consultar_usuarios(identidad: dict) -> None:
    usuarios = obtener_usuarios(identidad)
    mostrar_tabla(
        "Usuarios administrativos",
        ["Número", "Nombre", "Correo", "Rol"],
        [
            (usuario.num, f"{usuario.nombre} {usuario.primer_apellido}", usuario.correo, usuario.rol.nombre)
            for usuario in usuarios
        ],
    )
    input("Presiona Enter para continuar.")


def _consultar_actividad(identidad: dict) -> None:
    numero = questionary.text("Número de membresía:").ask()
    if numero is None:
        return
    try:
        num_membresia = _numero(numero)
        compras = obtener_compras_de_membresia(identidad, num_membresia)
        membresia = consultar_membresia(identidad, num_membresia)
        transacciones = obtener_transacciones_de_miembro(identidad, membresia.miembro.num)
        mostrar_tabla(
            "Compras",
            ["Número", "Fecha", "Monto base", "Monto final", "Usuario"],
            [
                (compra.num, "-", compra.monto_base, compra.monto_final, compra.usuario.num)
                for compra in compras
            ],
        )
        mostrar_tabla(
            "Movimientos de puntos",
            ["Número", "Movimiento", "Saldo", "Concepto"],
            [(t.num, t.movimiento, t.saldo, t.concepto or "") for t in transacciones],
        )
        input("Presiona Enter para continuar.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _numero(valor: str) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError("El número indicado no es válido.") from None


def _fecha(valor: str):
    from datetime import date

    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from None
