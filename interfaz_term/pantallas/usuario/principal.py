"""Menú operativo de Administrador y Cajero."""

import questionary
from rich.console import Console

from interfaz_term.componentes.banner import mostrar_banner
from interfaz_term.componentes.formulario import pedir_formulario
from interfaz_term.componentes.mensajes import error, exito, pausar
from interfaz_term.componentes.tabla import mostrar_tabla
from interfaz_term.estilos.tema import COLOR_ENCABEZADO
from servicios.caja.servicio_caja import registrar_operacion_caja
from servicios.compra.servicio_compra import (
    obtener_compras_de_membresia,
    obtener_transacciones_de_membresia,
)
from servicios.ajuste.servicio_ajuste import ajustar_cashback, ajustar_puntos
from servicios.membresia.servicio_membresia import (
    cancelar_membresia,
    reactivar_membresia,
    renovar_membresia,
    suspender_membresia,
)
from servicios.miembro.servicio_miembro import (
    modificar_miembro,
    registrar_miembro_con_membresia,
)
from servicios.miembro.servicio_miembro import buscar_miembros, obtener_miembros
from servicios.plan.servicio_plan import (
    crear_promocion,
    crear_version_plan,
    eliminar_condicion_futura_plan,
    finalizar_version_plan,
    modificar_condiciones_plan,
    modificar_plan,
    modificar_plan_con_condiciones,
    obtener_planes,
    obtener_condiciones_regulares,
    obtener_promociones,
    obtener_versiones_plan_para_operacion,
    registrar_plan,
    registrar_plan_con_condiciones,
)
from clases.version_plan import ConfigCashback, ConfigDescuento, ConfigPuntos
from servicios.recompensa.servicio_recompensa import (
    crear_version_recompensa,
    consultar_recompensa,
    eliminar_condicion_futura_recompensa,
    obtener_versiones_de_recompensa,
    reactivar_recompensa,
    registrar_recompensa_con_condiciones,
    modificar_recompensa_con_condiciones,
    modificar_recompensa,
    obtener_recompensas,
    registrar_recompensa,
)
from servicios.usuario.servicio_usuario import (
    consultar_usuario,
    modificar_usuario,
    obtener_actividad_usuario,
    obtener_usuarios,
    registrar_usuario,
)
from servicios.miembro.servicio_miembro import consultar_miembro
from servicios.membresia.servicio_membresia import (
    consultar_membresia,
    consultar_membresia_de_miembro,
)
from interfaz_term.navegacion import (
    ACTIVIDAD_AJUSTES,
    CERRAR_SESION,
    DETALLE_MIEMBRO,
    RESULTADOS_MIEMBROS,
    MIEMBROS_MEMBRESIAS,
    OPERACIONES_TIENDA,
    PLANES,
    RECOMPENSAS,
    USUARIOS_ADMINISTRATIVOS,
    VOLVER,
)
from utilidades.excepciones import EntidadNoEncontrada
from interfaz_term.validaciones.validadores_compra import (
    crear_validador_membresia_compra,
    crear_validador_recompensa,
    crear_mostrador_cashback,
    validar_cashback,
)
from interfaz_term.validaciones.validadores_membresia import (
    crear_validador_membresia,
    crear_validador_membresia_para_renovacion,
)
from interfaz_term.validaciones.validadores_miembro import (
    crear_validador_correo as crear_validador_correo_miembro,
)
from interfaz_term.validaciones.validadores_plan import (
    crear_validador_codigo_plan,
    crear_validador_codigo_plan_nuevo,
    validar_fecha_final as validar_fecha_final_plan,
)
from interfaz_term.validaciones.validadores_recompensa import (
    crear_validador_codigo_nuevo,
    validar_codigo_existente,
    validar_fecha_final as validar_fecha_final_recompensa,
)
from interfaz_term.validaciones.validadores_usuario import (
    crear_validador_correo,
    crear_validador_usuario,
)

_consola = Console()


def _mostrar_encabezado(sesion: dict) -> None:
    identidad = sesion.get("identidad") or {}
    nombre_rol = identidad.get("rol_nombre", "Usuario")
    nombre = identidad.get("nombre", "")
    mostrar_banner(
        f"Usuario: {nombre} | Rol: [{COLOR_ENCABEZADO}]{nombre_rol}[/{COLOR_ENCABEZADO}]"
    )


def _rol(sesion: dict) -> str:
    return (sesion.get("identidad") or {}).get("rol", "").upper()


def _ejecutar_operacion(operacion):
    """Ejecuta una operación administrativa y muestra sus errores de dominio."""
    try:
        return operacion()
    except (ValueError, PermissionError) as exc:
        error(str(exc))
        return None


def mostrar_menu_usuario(sesion: dict) -> tuple:
    opciones = [
        ("Operaciones de tienda", OPERACIONES_TIENDA),
        ("Miembros y membresías", MIEMBROS_MEMBRESIAS),
    ]
    if _rol(sesion) in {"ADM", "GER"}:
        opciones.extend(
            [
                ("Planes", PLANES),
                ("Recompensas", RECOMPENSAS),
                ("Ajustes", ACTIVIDAD_AJUSTES),
            ]
        )
    if _rol(sesion) == "ADM":
        opciones.append(("Usuarios y permisos", USUARIOS_ADMINISTRATIVOS))
    opciones.append(("Cerrar sesión", CERRAR_SESION))
    _mostrar_encabezado(sesion)
    seleccion = questionary.select(
        "¿Qué deseas hacer?",
        choices=[opcion[0] for opcion in opciones],
    ).ask()
    for nombre, pantalla in opciones:
        if seleccion == nombre:
            return None if pantalla == CERRAR_SESION else "usuario", pantalla
    return "usuario", CERRAR_SESION


def mostrar_operaciones_tienda(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    opciones = [
        "Registrar venta",
        "Contratar membresía",
        "Renovar membresía",
        "Cambiar plan",
        "← Volver",
    ]
    accion = questionary.select("Operaciones de tienda", choices=opciones).ask()
    identidad = sesion["identidad"]
    if accion == "Registrar venta":
        _registrar_venta(identidad)
    elif accion == "Contratar membresía":
        _contratar_nuevo_miembro(identidad)
    elif accion == "Renovar membresía":
        _renovar(identidad)
    elif accion == "Cambiar plan":
        _renovar(identidad, titulo="Cambiar plan mediante renovación")
    elif accion == "← Volver":
        return "usuario", VOLVER
    return "usuario", None


def mostrar_miembros_membresias(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    opciones = ["Buscar una membresía", "Filtrar miembros", "← Volver"]
    accion = questionary.select("Miembros y membresías", choices=opciones).ask()
    if accion == "Buscar una membresía":
        return _buscar_membresia(sesion)
    if accion == "Filtrar miembros":
        return _filtrar_miembros(sesion)
    elif accion == "← Volver":
        return "usuario", VOLVER
    return "usuario", None


def _buscar_membresia(sesion: dict) -> tuple:
    identidad = sesion["identidad"]

    datos = pedir_formulario(
        [{
            "clave": "num_membresia",
            "etiqueta": "Número de membresía",
            "validador": crear_validador_membresia(identidad),
        }]
    )
    if datos is None:
        return "usuario", None
    membresia = datos["_membresia"]
    sesion["membresia_seleccionada"] = membresia.num
    sesion["membresias_resultado"] = [membresia.num]
    return "usuario", DETALLE_MIEMBRO


def _filtrar_miembros(sesion: dict) -> tuple:
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre", "requerido": False},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido", "requerido": False},
            {"clave": "correo", "etiqueta": "Correo", "requerido": False},
            {"clave": "telefono", "etiqueta": "Teléfono", "requerido": False},
            {"clave": "estado", "etiqueta": "Estado (ACTIVA, SUSPENDIDA o CANCELADA)", "requerido": False},
            {"clave": "plan", "etiqueta": "Código del plan activo", "requerido": False},
        ],
    )
    if datos is None:
        return "usuario", None
    try:
        identidad = sesion["identidad"]
        if datos["estado"]:
            datos["estado"] = datos["estado"].upper()
        miembros = buscar_miembros(sesion["identidad"], datos)
        if not miembros:
            error("No se encontraron miembros con esos filtros.")
            return "usuario", None
        sesion["membresias_resultado"] = [
            membresia.num
            for miembro in miembros
            if (membresia := consultar_membresia_de_miembro(identidad, miembro.num))
            is not None
        ]
        if not sesion["membresias_resultado"]:
            error("No se encontraron miembros con membresía asociada.")
            return "usuario", None
        return "usuario", RESULTADOS_MIEMBROS
    except (ValueError, PermissionError) as exc:
        error(str(exc))
        return "usuario", None


def mostrar_resultados_miembros(sesion: dict) -> tuple:
    identidad = sesion["identidad"]
    membresias = [
        consultar_membresia(identidad, num)
        for num in sesion.get("membresias_resultado", [])
    ]
    membresias = [membresia for membresia in membresias if membresia is not None]
    if not membresias:
        error("No hay resultados para mostrar.")
        return "usuario", VOLVER

    opciones = []
    referencias = {}
    for membresia in membresias:
        miembro = membresia.miembro
        etiqueta = (
            f"Membresía {membresia.num} | "
            f"{miembro.nombre} {miembro.primer_apellido} | {miembro.correo}"
        )
        opciones.append(etiqueta)
        referencias[etiqueta] = membresia.num
    opciones.append("← Volver")

    _mostrar_encabezado(sesion)
    seleccion = questionary.select("Selecciona un miembro", choices=opciones).ask()
    if seleccion == "← Volver" or seleccion is None:
        return "usuario", VOLVER
    sesion["membresia_seleccionada"] = referencias[seleccion]
    return "usuario", DETALLE_MIEMBRO


def mostrar_detalle_miembro(sesion: dict) -> tuple:
    identidad = sesion["identidad"]
    num_membresia = sesion.get("membresia_seleccionada")
    membresia = consultar_membresia(identidad, num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    miembro = membresia.miembro

    _mostrar_encabezado(sesion)
    mostrar_tabla(
        "Información del miembro",
        ["Nombre", "Correo", "Teléfono"],
        [(
            f"{miembro.nombre} {miembro.primer_apellido}",
            miembro.correo,
            miembro.telefono,
        )],
    )
    if membresia is not None:
        version = membresia.version_plan_actual
        mostrar_tabla(
            "Membresía actual",
            ["Número", "Estado", "Plan", "Condiciones"],
            [(
                membresia.num,
                membresia.estado.value,
                version.plan.nombre if version else "Sin plan",
                version.num if version else "-",
            )],
        )

    opciones = ["Consultar actividad", "← Volver"] if membresia is not None else ["← Volver"]
    if _rol(sesion) in {"ADM", "GER"}:
        opciones = ["Modificar miembro"]
        if membresia is not None:
            opciones.append("Consultar actividad")
            if membresia.estado.value == "ACTIVA":
                opciones.append("Suspender membresía")
                opciones.append("Cancelar membresía")
            elif membresia.estado.value == "SUSPENDIDA":
                opciones.append("Reactivar membresía")
                opciones.append("Cancelar membresía")
        opciones.append("← Volver")
    accion = questionary.select("¿Qué deseas hacer?", choices=opciones).ask()
    if accion == "Modificar miembro":
        _modificar_miembro_seleccionado(identidad, miembro)
        return "usuario", None
    if accion == "Suspender membresía":
        _cambiar_estado_membresia_seleccionada(identidad, num_membresia, suspender_membresia, "suspendida")
        return "usuario", None
    if accion == "Reactivar membresía":
        _cambiar_estado_membresia_seleccionada(identidad, num_membresia, reactivar_membresia, "activa")
        return "usuario", None
    if accion == "Consultar actividad":
        _mostrar_actividad_membresia(identidad, membresia.num)
        return "usuario", None
    if accion == "Cancelar membresía":
        _cambiar_estado_membresia_seleccionada(identidad, num_membresia, cancelar_membresia, "cancelada")
        return "usuario", None
    return "usuario", VOLVER


def _modificar_miembro_seleccionado(identidad: dict, miembro) -> None:
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre actual", "valor_inicial": miembro.nombre},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido actual", "valor_inicial": miembro.primer_apellido},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido actual", "requerido": False,
             "valor_inicial": miembro.segundo_apellido or ""},
            {"clave": "telefono", "etiqueta": "Teléfono actual", "valor_inicial": miembro.telefono},
            {"clave": "correo", "etiqueta": "Correo actual", "valor_inicial": miembro.correo},
        ],
        iniciar_en_resumen=True,
    )
    if datos is None:
        return
    miembro = _ejecutar_operacion(
        lambda: modificar_miembro(identidad, miembro.num, datos)
    )
    if miembro is not None:
        exito("Miembro modificado.")


def _cambiar_estado_membresia_seleccionada(
    identidad: dict,
    num_membresia: int,
    operacion,
    estado: str,
) -> None:
    membresia = consultar_membresia(identidad, num_membresia)
    if membresia is None:
        error("La membresía no existe.")
        return
    try:
        operacion(identidad, membresia.num)
        exito(f"La membresía quedó {estado}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def mostrar_planes(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    opciones = ["Planes"]
    if _rol(sesion) == "ADM":
        opciones.append("Crear plan")
    opciones.append("← Volver")
    accion = questionary.select("Planes", choices=opciones).ask()
    identidad = sesion["identidad"]
    if accion == "Planes":
        _navegar_planes(identidad, _rol(sesion))
    elif accion == "Crear plan":
        _crear_plan_completo(identidad)
    elif accion == "← Volver":
        return "usuario", VOLVER
    return "usuario", None


def mostrar_recompensas(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    opciones = ["Recompensas"]
    if _rol(sesion) == "ADM":
        opciones.append("Crear recompensa")
    opciones.append("← Volver")
    accion = questionary.select("Recompensas", choices=opciones).ask()
    identidad = sesion["identidad"]
    if accion == "Recompensas":
        _navegar_recompensas(identidad, _rol(sesion))
    elif accion == "Crear recompensa":
        _crear_recompensa_completa(identidad)
    elif accion == "← Volver":
        return "usuario", VOLVER
    return "usuario", None


def mostrar_usuarios_permisos(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    opciones = ["Usuarios", "Registrar usuario", "← Volver"]
    accion = questionary.select("Usuarios y permisos", choices=opciones).ask()
    identidad = sesion["identidad"]
    if accion == "Usuarios":
        _navegar_usuarios(identidad)
    elif accion == "Registrar usuario":
        _registrar_usuario(identidad)
    elif accion == "← Volver":
        return "usuario", VOLVER
    return "usuario", None


def mostrar_usuarios_administrativos(sesion: dict) -> tuple:
    """Compatibilidad para el estado de navegación existente."""
    return mostrar_usuarios_permisos(sesion)


def mostrar_actividad_ajustes(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    opciones = ["Ajustar puntos", "Ajustar cashback", "← Volver"]
    accion = questionary.select("Ajustes", choices=opciones).ask()
    identidad = sesion["identidad"]
    if accion == "Ajustar puntos":
        _ajustar_puntos(identidad)
    elif accion == "Ajustar cashback":
        _ajustar_cashback(identidad)
    elif accion == "← Volver":
        return "usuario", VOLVER
    return "usuario", None


def mostrar_usuario(sesion: dict) -> tuple:
    """Compatibilidad para llamadas existentes al menú administrativo."""
    return mostrar_menu_usuario(sesion)


def _registrar_venta(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "num_membresia",
                "etiqueta": "Número de membresía",
                "validador": crear_validador_membresia_compra(identidad),
            },
            {"clave": "monto_base", "etiqueta": "Monto de la compra"},
            {
                "clave": "cashback_aplicado",
                "etiqueta": "Cashback a utilizar (vacío si no aplica)",
                "requerido": False,
                "antes_de_pedir": crear_mostrador_cashback(identidad),
                "validador": validar_cashback,
            },
            {
                "clave": "codigo_recompensa",
                "etiqueta": "Código de recompensa (vacío si no aplica)",
                "requerido": False,
                "validador": crear_validador_recompensa(identidad),
            },
        ]
    )
    if datos is None:
        return
    try:
        datos["num_membresia"] = _numero(datos["num_membresia"])
        datos["cashback_aplicado"] = datos.get("cashback_aplicado") or 0
        resultado = registrar_operacion_caja(identidad, datos)
        mensaje = f"Compra registrada con número {resultado['compra'].num}."
        if resultado["canje"] is not None:
            mensaje += " El canje también fue registrado."
        exito(mensaje)
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _contratar_nuevo_miembro(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido", "requerido": False},
            {"clave": "telefono", "etiqueta": "Teléfono"},
            {
                "clave": "correo",
                "etiqueta": "Correo electrónico",
                "validador": crear_validador_correo_miembro(obtener_miembros, identidad),
            },
            {
                "clave": "contraseña",
                "etiqueta": "Contraseña",
                "contrasena": True,
                "confirmar": True,
            },
        ]
    )
    if datos is None:
        return
    version = _seleccionar_version_plan(identidad, "CONTRATACION")
    if version is None:
        return
    resultado = _ejecutar_operacion(
        lambda: registrar_miembro_con_membresia(identidad, datos, version.num)
    )
    if resultado is not None:
        miembro, renovacion = resultado
        exito(
            f"Membresía contratada con número {renovacion.membresia.num}. "
            f"Renovación inicial {renovacion.num}."
        )


def _modificar_miembro(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "num", "etiqueta": "Número de membresía"},
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido", "requerido": False},
            {"clave": "telefono", "etiqueta": "Teléfono"},
            {"clave": "correo", "etiqueta": "Correo electrónico"},
        ]
    )
    if datos is None:
        return
    numero_membresia = _ejecutar_operacion(lambda: _numero(datos.pop("num")))
    if numero_membresia is None:
        return
    membresia = _ejecutar_operacion(
        lambda: consultar_membresia(identidad, numero_membresia)
    )
    if membresia is None:
        error("La membresía no existe.")
        return
    miembro = _ejecutar_operacion(
        lambda: modificar_miembro(identidad, membresia.miembro.num, datos)
    )
    if miembro is not None:
        exito("Miembro modificado.")


def _renovar(identidad: dict, titulo: str = "Renovar membresía") -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "num_membresia",
                "etiqueta": "Número de membresía",
                "validador": crear_validador_membresia_para_renovacion(identidad),
            },
        ]
    )
    if datos is None:
        return
    try:
        version = _seleccionar_version_plan(identidad, "RENOVACION")
        if version is None:
            return
        renovacion = renovar_membresia(
            identidad,
            _numero(datos["num_membresia"]),
            version.num,
        )
        exito(f"{titulo} registrada con renovación {renovacion.num}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _seleccionar_version_plan(identidad: dict, aplica_en: str | None):
    """Muestra planes y sus condiciones disponibles para la operación."""
    versiones = obtener_versiones_plan_para_operacion(identidad, aplica_en)
    if not versiones:
        error("No hay planes disponibles para esta operación.")
        return None

    opciones = [
        (
            f"{'Promoción' if version.version_base_de_promo else 'Regular'} | "
            f"Plan {version.plan.nombre} | "
            f"${version.precio} | {version.plazo_meses} meses"
        )
        for version in versiones
    ]
    opciones.append("← Cancelar")

    while True:
        seleccion = questionary.select(
            "Selecciona las condiciones del plan:",
            choices=opciones,
        ).ask()
        if seleccion in (None, "← Cancelar"):
            return None

        indice = opciones.index(seleccion)
        version = versiones[indice]
        configuracion_puntos = version.config_puntos
        configuracion_cashback = version.config_cashback
        configuracion_descuento = version.config_descuento
        mostrar_tabla(
            "Detalle del plan",
            ["Campo", "Valor"],
            [
                ("Condiciones", "Promoción" if version.version_base_de_promo else "Regulares"),
                ("Plan", f"{version.plan.codigo} - {version.plan.nombre}"),
                ("Inicio", version.fecha_inicio),
                ("Final", version.fecha_final),
                ("Precio", version.precio),
                ("Plazo", f"{version.plazo_meses} meses"),
                ("Aplicación", version.aplica_en.value),
                (
                    "Puntos",
                    "No configurados"
                    if configuracion_puntos is None
                    else configuracion_puntos.porcentaje,
                ),
                (
                    "Descuento",
                    "No configurado"
                    if configuracion_descuento is None
                    else configuracion_descuento.porcentaje,
                ),
                (
                    "Cashback",
                    "No configurado"
                    if configuracion_cashback is None
                    else configuracion_cashback.porcentaje,
                ),
            ],
        )
        confirmado = questionary.confirm(
            "¿Confirmas estas condiciones del plan?",
            default=True,
        ).ask()
        if confirmado:
            return version


def _consultar_miembro(identidad: dict) -> None:
    datos = pedir_formulario([{
        "clave": "num_membresia",
        "etiqueta": "Número de membresía",
        "validador": crear_validador_membresia(identidad),
    }])
    if datos is None:
        return
    membresia = datos["_membresia"]
    miembro = membresia.miembro
    mostrar_tabla(
        "Membresía",
        ["Membresía", "Nombre", "Correo", "Teléfono"],
        [(membresia.num, f"{miembro.nombre} {miembro.primer_apellido}", miembro.correo, miembro.telefono)],
    )
    pausar()


def _consultar_planes(identidad: dict) -> None:
    planes = obtener_planes(identidad)
    mostrar_tabla(
        "Planes",
        ["Código", "Nombre", "Descripción"],
        [(plan.codigo, plan.nombre, plan.descripcion or "") for plan in planes],
    )
    pausar()


def _consultar_recompensas(identidad: dict) -> None:
    recompensas = obtener_recompensas(identidad)
    mostrar_tabla(
        "Recompensas",
        ["Código", "Nombre", "Descripción"],
        [(recompensa.codigo, recompensa.nombre, recompensa.descripcion or "") for recompensa in recompensas],
    )
    pausar()


def _crear_plan(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "codigo",
                "etiqueta": "Código",
                "validador": crear_validador_codigo_plan_nuevo(obtener_planes, identidad),
            },
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "descripcion", "etiqueta": "Descripción", "requerido": False},
        ]
    )
    if datos is None:
        return
    plan = _ejecutar_operacion(lambda: registrar_plan(identidad, datos))
    if plan is not None:
        exito(f"Plan {plan.codigo} registrado.")


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
    codigo = datos.pop("codigo")
    plan = _ejecutar_operacion(lambda: modificar_plan(identidad, codigo, datos))
    if plan is not None:
        exito(f"Plan {plan.codigo} modificado.")


def _crear_version_plan(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "codigo_plan",
                "etiqueta": "Código del plan",
                "validador": crear_validador_codigo_plan(obtener_planes, identidad),
            },
            {"clave": "fecha_inicio", "etiqueta": "Fecha inicial (AAAA-MM-DD)"},
            {
                "clave": "fecha_final",
                "etiqueta": "Fecha final (AAAA-MM-DD)",
                "validador": validar_fecha_final_plan,
            },
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
        exito(f"Condiciones del plan registradas.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _configurar_beneficios_version(datos: dict, anterior=None) -> None:
    if anterior is not None:
        if anterior.config_puntos is not None:
            datos["config_puntos"] = ConfigPuntos(
                None, anterior.config_puntos.porcentaje, anterior.config_puntos.vigencia_meses
            )
        if anterior.config_descuento is not None:
            datos["config_descuento"] = ConfigDescuento(
                None,
                anterior.config_descuento.porcentaje,
                anterior.config_descuento.monto_minimo,
                [
                    dia.dia_semana if hasattr(dia, "dia_semana") else dia
                    for dia in anterior.config_descuento.dias_aplicables
                ],
            )
        if anterior.config_cashback is not None:
            datos["config_cashback"] = ConfigCashback(
                None,
                anterior.config_cashback.porcentaje,
                anterior.config_cashback.limite_min_mensual,
            )
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
                    {"clave": "porcentaje", "etiqueta": "Porcentaje de puntos (ej. 0.025)",
                     "valor_inicial": getattr(getattr(anterior, "config_puntos", None), "porcentaje", "")},
                    {"clave": "vigencia_meses", "etiqueta": "Vigencia en meses (vacío sin caducidad)",
                     "requerido": False, "valor_inicial": getattr(getattr(anterior, "config_puntos", None), "vigencia_meses", "") or ""},
                ],
                iniciar_en_resumen=anterior is not None,
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
                    {"clave": "porcentaje", "etiqueta": "Porcentaje de descuento (ej. 0.10)",
                     "valor_inicial": getattr(getattr(anterior, "config_descuento", None), "porcentaje", "")},
                    {"clave": "monto_minimo", "etiqueta": "Monto mínimo (vacío sin mínimo)", "requerido": False,
                     "valor_inicial": getattr(getattr(anterior, "config_descuento", None), "monto_minimo", "") or ""},
                    {"clave": "dias_aplicables", "etiqueta": "Días ISO separados por coma (vacío todos)", "requerido": False,
                     "valor_inicial": ",".join(str(dia.dia_semana if hasattr(dia, "dia_semana") else dia) for dia in getattr(getattr(anterior, "config_descuento", None), "dias_aplicables", []))},
                ],
                iniciar_en_resumen=anterior is not None,
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
                    {"clave": "porcentaje", "etiqueta": "Porcentaje de cashback (ej. 0.05)",
                     "valor_inicial": getattr(getattr(anterior, "config_cashback", None), "porcentaje", "")},
                    {"clave": "limite_min_mensual", "etiqueta": "Umbral mensual (vacío sin umbral)", "requerido": False,
                     "valor_inicial": getattr(getattr(anterior, "config_cashback", None), "limite_min_mensual", "") or ""},
                ],
                iniciar_en_resumen=anterior is not None,
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
    try:
        version = _seleccionar_version_plan(identidad, None)
    except (ValueError, PermissionError) as exc:
        error(str(exc))
        return
    if version is None:
        return

    datos = pedir_formulario(
        [
            {"clave": "fecha_final", "etiqueta": "Nueva fecha final (AAAA-MM-DD)"},
        ]
    )
    if datos is None:
        return
    try:
        version = finalizar_version_plan(
            identidad,
            version.num,
            _fecha(datos["fecha_final"]),
        )
        exito("Condiciones del plan actualizadas.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _crear_recompensa(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "codigo",
                "etiqueta": "Código",
                "validador": crear_validador_codigo_nuevo(obtener_recompensas, identidad),
            },
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "descripcion", "etiqueta": "Descripción", "requerido": False},
        ]
    )
    if datos is None:
        return
    recompensa = _ejecutar_operacion(lambda: registrar_recompensa(identidad, datos))
    if recompensa is not None:
        exito(f"Recompensa {recompensa.codigo} registrada.")


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
    codigo = datos.pop("codigo")
    recompensa = _ejecutar_operacion(
        lambda: modificar_recompensa(identidad, codigo, datos)
    )
    if recompensa is not None:
        exito(f"Recompensa {recompensa.codigo} modificada.")


def _crear_version_recompensa(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "codigo_recompensa",
                "etiqueta": "Código de recompensa",
                "validador": validar_codigo_existente(consultar_recompensa),
            },
            {"clave": "fecha_inicio", "etiqueta": "Fecha inicial (AAAA-MM-DD)"},
            {
                "clave": "fecha_final",
                "etiqueta": "Fecha final (AAAA-MM-DD)",
                "validador": validar_fecha_final_recompensa,
            },
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
        exito("Condiciones de recompensa registradas.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _registrar_usuario(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre"},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido"},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido", "requerido": False},
            {"clave": "telefono", "etiqueta": "Teléfono", "requerido": False},
            {
                "clave": "correo",
                "etiqueta": "Correo electrónico",
                "validador": crear_validador_correo(obtener_usuarios, identidad),
            },
            {
                "clave": "contraseña",
                "etiqueta": "Contraseña",
                "contrasena": True,
                "confirmar": True,
            },
            {"clave": "codigo_rol", "etiqueta": "Rol (ADM, CAJ o GER)"},
        ]
    )
    if datos is None:
        return
    usuario = _ejecutar_operacion(lambda: registrar_usuario(identidad, datos))
    if usuario is not None:
        exito(f"Usuario registrado con número {usuario.num}.")


def _navegar_usuarios(identidad: dict) -> None:
    usuarios = obtener_usuarios(identidad)
    if not usuarios:
        error("No hay usuarios registrados.")
        return
    opciones = [
        f"{usuario.num} | {usuario.nombre} {usuario.primer_apellido} | {usuario.rol.nombre}"
        for usuario in usuarios
    ] + ["← Volver"]
    seleccion = questionary.select("Usuarios", choices=opciones).ask()
    if seleccion in (None, "← Volver"):
        return
    usuario = usuarios[opciones.index(seleccion)]
    _mostrar_detalle_usuario(identidad, usuario)


def _mostrar_detalle_usuario(identidad: dict, usuario) -> None:
    while True:
        _mostrar_encabezado({"identidad": {
            "nombre": usuario.nombre,
            "rol_nombre": usuario.rol.nombre,
        }})
        _mostrar_informacion_usuario(usuario)
        accion = questionary.select(
            f"Usuario {usuario.num} - {usuario.nombre} {usuario.primer_apellido}",
            choices=["Modificar", "Consultar actividad", "← Volver"],
        ).ask()
        if accion in (None, "← Volver"):
            return
        if accion == "Modificar":
            _modificar_usuario(identidad, usuario)
            actualizado = consultar_usuario(identidad, usuario.num)
            if actualizado is not None:
                usuario = actualizado
        elif accion == "Consultar actividad":
            _mostrar_actividad_usuario(identidad, usuario)


def _mostrar_informacion_usuario(usuario) -> None:
    mostrar_tabla(
        "Información del usuario",
        ["Número", "Nombre", "Teléfono", "Correo", "Rol", "Fecha de registro"],
        [(
            usuario.num,
            " ".join(filter(None, [usuario.nombre, usuario.primer_apellido, usuario.segundo_apellido])),
            usuario.telefono or "",
            usuario.correo,
            usuario.rol.nombre,
            usuario.fecha_registro,
        )],
    )


def _mostrar_actividad_usuario(identidad: dict, usuario) -> None:
    compras = obtener_actividad_usuario(identidad, usuario.num)
    mostrar_tabla(
        "Actividad del usuario",
        ["Compra", "Fecha", "Membresía", "Miembro", "Monto base", "Descuento", "Cashback", "Monto final"],
        [(
            compra.num,
            compra.fecha or "Sin fecha",
            compra.membresia.num,
            f"{compra.membresia.miembro.nombre} {compra.membresia.miembro.primer_apellido}",
            compra.monto_base,
            compra.descuento_nominal,
            compra.cashback_aplicado,
            compra.monto_final,
        ) for compra in compras],
    )
    if not compras:
        _consola.print("[dim]No hay ventas asociadas a este usuario.[/dim]")
    pausar()


def _modificar_usuario(identidad: dict, usuario=None) -> None:
    if usuario is None:
        datos_usuario = pedir_formulario([{
            "clave": "num_usuario",
            "etiqueta": "Número de usuario",
            "validador": crear_validador_usuario(consultar_usuario, identidad),
        }])
        if datos_usuario is None:
            return
        usuario = datos_usuario["_usuario"]
    datos = pedir_formulario(
        [
            {"clave": "nombre", "etiqueta": "Nombre actual", "valor_inicial": usuario.nombre},
            {"clave": "primer_apellido", "etiqueta": "Primer apellido actual", "valor_inicial": usuario.primer_apellido},
            {"clave": "segundo_apellido", "etiqueta": "Segundo apellido actual", "requerido": False,
             "valor_inicial": usuario.segundo_apellido or ""},
            {"clave": "telefono", "etiqueta": "Teléfono actual", "requerido": False,
             "valor_inicial": usuario.telefono or ""},
            {"clave": "correo", "etiqueta": "Correo actual", "valor_inicial": usuario.correo},
            {"clave": "contraseña", "etiqueta": "Nueva contraseña (vacío para conservarla)",
             "requerido": False, "contrasena": True, "confirmar": True},
            {"clave": "codigo_rol", "etiqueta": "Rol actual (ADM, CAJ o GER)",
             "valor_inicial": usuario.rol.codigo},
        ],
        iniciar_en_resumen=True,
    )
    if datos is None:
        return
    try:
        if not datos.get("contraseña"):
            datos.pop("contraseña", None)
        usuario = modificar_usuario(identidad, usuario.num, datos)
        exito(f"Usuario {usuario.num} modificado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _cambiar_estado_membresia(identidad: dict, operacion, estado: str) -> None:
    datos = pedir_formulario([{
        "clave": "num_membresia",
        "etiqueta": "Número de membresía",
        "validador": crear_validador_membresia(identidad),
    }])
    if datos is None:
        return
    try:
        operacion(identidad, datos["_membresia"].num)
        exito(f"La membresía quedó {estado}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _ajustar_puntos(identidad: dict) -> None:
    datos = pedir_formulario(
        [
            {
                "clave": "num_membresia",
                "etiqueta": "Número de membresía",
                "validador": crear_validador_membresia(identidad),
            },
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
            {
                "clave": "num_membresia",
                "etiqueta": "Número de membresía",
                "validador": crear_validador_membresia(identidad),
            },
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
        "Usuarios",
        ["Número", "Nombre", "Correo", "Rol"],
        [
            (usuario.num, f"{usuario.nombre} {usuario.primer_apellido}", usuario.correo, usuario.rol.nombre)
            for usuario in usuarios
        ],
    )
    pausar()


def _consultar_actividad(identidad: dict) -> None:
    datos = pedir_formulario([{
        "clave": "num_membresia",
        "etiqueta": "Número de membresía",
        "validador": crear_validador_membresia(identidad),
    }])
    if datos is None:
        return
    _mostrar_actividad_membresia(identidad, datos["_membresia"].num)


def _mostrar_actividad_membresia(identidad: dict, num_membresia: int) -> None:
    compras = obtener_compras_de_membresia(identidad, num_membresia)
    transacciones = obtener_transacciones_de_membresia(identidad, num_membresia)
    mostrar_tabla(
        "Compras de la membresía",
        ["Número", "Fecha", "Monto base", "Descuento", "Cashback", "Monto final", "Usuario"],
        [
            (
                compra.num,
                compra.fecha or "Sin fecha",
                compra.monto_base,
                compra.descuento_nominal,
                compra.cashback_aplicado,
                compra.monto_final,
                compra.usuario.num,
            )
            for compra in compras
        ],
    )
    mostrar_tabla(
        "Movimientos de puntos de la membresía",
        ["Fecha", "Número", "Movimiento", "Saldo", "Concepto"],
        [
            (transaccion.fecha, transaccion.num, transaccion.movimiento,
             transaccion.saldo, transaccion.concepto or "")
            for transaccion in transacciones
        ],
    )
    pausar()


def _numero(valor: str) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError("El número indicado no es válido.") from None


def _fecha(valor: str):
    from datetime import date

    if isinstance(valor, date):
        return valor
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from None


def _navegar_planes(identidad: dict, rol: str) -> None:
    planes = obtener_planes(identidad)
    if not planes:
        error("No hay planes registrados.")
        return
    opciones = [f"{plan.codigo} | {plan.nombre}" for plan in planes]
    opciones.append("← Volver")
    seleccion = questionary.select("Planes", choices=opciones).ask()
    if seleccion in (None, "← Volver"):
        return
    plan = planes[opciones.index(seleccion)]
    _mostrar_detalle_plan(identidad, plan, rol)


def _mostrar_detalle_plan(identidad: dict, plan, rol: str) -> None:
    while True:
        _mostrar_encabezado({"identidad": identidad})
        _mostrar_condiciones_plan(plan.codigo)
        opciones = ["Historial de condiciones", "Promociones"]
        if rol == "ADM":
            opciones.insert(0, "Modificar plan")
        opciones.append("← Volver")
        seleccion = questionary.select(
            f"Plan {plan.codigo} - {plan.nombre}", choices=opciones
        ).ask()
        if seleccion in (None, "← Volver"):
            return
        if seleccion == "Modificar plan":
            _modificar_plan_completo(identidad, plan)
            plan = obtener_planes(identidad)[
                next(i for i, otro in enumerate(obtener_planes(identidad)) if otro.codigo == plan.codigo)
            ]
        elif seleccion == "Historial de condiciones":
            _mostrar_historial_condiciones(identidad, plan.codigo, rol)
        elif seleccion == "Promociones":
            _mostrar_promociones(identidad, plan, rol)


def _mostrar_condiciones_plan(codigo_plan: str) -> None:
    regulares = obtener_condiciones_regulares(codigo_plan)
    vigentes = [condicion for condicion in regulares if condicion.esta_vigente()]
    regular = max(
        vigentes or regulares,
        key=lambda condicion: (condicion.fecha_inicio, condicion.num),
        default=None,
    )
    if regular is None:
        return
    mostrar_tabla(
        "Condiciones actuales del plan",
        ["Plan", "Inicio", "Final", "Precio", "Plazo", "Disponible para", "Puntos", "Descuento", "Cashback"],
        [(
            regular.plan.nombre,
            regular.fecha_inicio,
            regular.fecha_final,
            regular.precio,
            f"{regular.plazo_meses} meses",
            "Contratación y renovación",
            _valor_configuracion(regular.config_puntos, "porcentaje"),
            _valor_configuracion(regular.config_descuento, "porcentaje"),
            _valor_configuracion(regular.config_cashback, "porcentaje"),
        )],
    )


def _mostrar_historial_condiciones(identidad: dict, codigo_plan: str, rol: str) -> None:
    from datetime import date, timedelta

    condiciones = obtener_condiciones_regulares(codigo_plan) + obtener_promociones(codigo_plan)
    condiciones.sort(key=lambda condicion: (condicion.fecha_inicio, condicion.num), reverse=True)
    mostrar_tabla(
        "Historial de condiciones",
        ["Tipo", "Inicio", "Final", "Precio", "Plazo", "Disponible para"],
        [(
            "Promoción" if condicion.version_base_de_promo is not None else "Regular",
            condicion.fecha_inicio,
            condicion.fecha_final,
            condicion.precio,
            f"{condicion.plazo_meses} meses",
            _texto_aplica(condicion),
        ) for condicion in condiciones],
    )
    futuras = [
        condicion for condicion in condiciones
        if condicion.fecha_inicio >= date.today() + timedelta(days=1)
    ]
    if rol != "ADM" or not futuras:
        pausar()
        return
    opciones = [
        f"Borrar {condicion.fecha_inicio} a {condicion.fecha_final} | "
        f"{'Promoción' if condicion.version_base_de_promo else 'Regular'}"
        for condicion in futuras
    ] + ["← Volver"]
    seleccion = questionary.select("Condiciones futuras", choices=opciones).ask()
    if seleccion in (None, "← Volver"):
        return
    condicion = futuras[opciones.index(seleccion)]
    if not questionary.confirm("¿Borrar esta condición futura? Esta acción no se puede deshacer.", default=False).ask():
        return
    try:
        eliminar_condicion_futura_plan(identidad, condicion.num)
        exito("Condición futura eliminada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _mostrar_promociones(identidad: dict, plan, rol: str) -> None:
    from datetime import date

    while True:
        promociones = [
            promocion for promocion in obtener_promociones(plan.codigo)
            if promocion.fecha_final >= date.today()
        ]
        opciones = [
            f"{promocion.fecha_inicio} a {promocion.fecha_final} | {_texto_aplica(promocion)}"
            for promocion in promociones
        ]
        if rol == "ADM":
            opciones.append("Crear nueva promoción")
        opciones.append("← Volver")
        seleccion = questionary.select("Promociones", choices=opciones).ask()
        if seleccion in (None, "← Volver"):
            return
        if seleccion == "Crear nueva promoción":
            _crear_promocion(identidad, plan.codigo)
            continue
        promocion = promociones[opciones.index(seleccion)]
        if rol == "ADM":
            _editar_fecha_promocion(identidad, promocion)


def _crear_plan_completo(identidad: dict) -> None:
    datos_plan = pedir_formulario([
        {
            "clave": "codigo",
            "etiqueta": "Código",
            "validador": crear_validador_codigo_plan_nuevo(obtener_planes, identidad),
        },
        {"clave": "nombre", "etiqueta": "Nombre"},
        {"clave": "descripcion", "etiqueta": "Descripción", "requerido": False},
    ])
    if datos_plan is None:
        return
    datos_condiciones = _pedir_condiciones("Condiciones iniciales del plan", incluye_aplica=False)
    if datos_condiciones is None:
        return
    try:
        plan = registrar_plan_con_condiciones(identidad, datos_plan, datos_condiciones)
        exito(f"Plan {plan.codigo} registrado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _modificar_plan_completo(identidad: dict, plan) -> None:
    datos_plan = pedir_formulario([
        {"clave": "nombre", "etiqueta": f"Nombre (actual: {plan.nombre})", "valor_inicial": plan.nombre},
        {"clave": "descripcion", "etiqueta": "Descripción actual", "requerido": False,
         "valor_inicial": plan.descripcion or ""},
    ], iniciar_en_resumen=True)
    if datos_plan is None:
        return
    actuales = obtener_condiciones_regulares(plan.codigo)
    vigentes = [condicion for condicion in actuales if condicion.esta_vigente()]
    actual = max(
        vigentes or actuales,
        key=lambda condicion: (condicion.fecha_inicio, condicion.num),
        default=None,
    )
    datos_condiciones = _pedir_condiciones(
        "Nuevas condiciones del plan", incluye_aplica=False, anterior=actual
    )
    if datos_condiciones is None:
        return
    try:
        modificar_plan_con_condiciones(identidad, plan.codigo, datos_plan, datos_condiciones)
        exito(f"Plan {plan.codigo} modificado.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _crear_promocion(identidad: dict, codigo_plan: str) -> None:
    datos = _pedir_condiciones("Nueva promoción", incluye_aplica=True)
    if datos is None:
        return
    try:
        promocion = crear_promocion(identidad, codigo_plan, datos)
        exito(f"Promoción creada del {promocion.fecha_inicio} al {promocion.fecha_final}.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _editar_fecha_promocion(identidad: dict, promocion) -> None:
    datos = pedir_formulario([
        {"clave": "fecha_final", "etiqueta": "Nueva fecha final (AAAA-MM-DD)",
         "valor_inicial": promocion.fecha_final},
    ], iniciar_en_resumen=True)
    if datos is None:
        return
    try:
        finalizar_version_plan(identidad, promocion.num, _fecha(datos["fecha_final"]))
        exito("Fecha de finalización de la promoción actualizada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _pedir_condiciones(titulo: str, incluye_aplica: bool, anterior=None) -> dict | None:
    from datetime import date, timedelta

    def valor(nombre, defecto=""):
        if anterior is not None and nombre == "fecha_inicio":
            return max(date.today(), anterior.fecha_inicio + timedelta(days=1))
        if anterior is not None and nombre == "fecha_final":
            inicio = max(date.today(), anterior.fecha_inicio + timedelta(days=1))
            return max(anterior.fecha_final, inicio)
        return getattr(anterior, nombre, defecto) if anterior is not None else defecto

    campos = [
        {"clave": "fecha_inicio", "etiqueta": "Fecha inicial (AAAA-MM-DD)", "valor_inicial": valor("fecha_inicio")},
        {
            "clave": "fecha_final",
            "etiqueta": "Fecha final (AAAA-MM-DD)",
            "valor_inicial": valor("fecha_final"),
            "validador": validar_fecha_final_plan,
        },
        {"clave": "precio", "etiqueta": "Precio", "valor_inicial": valor("precio")},
        {"clave": "plazo_meses", "etiqueta": "Plazo en meses", "valor_inicial": valor("plazo_meses")},
    ]
    if incluye_aplica:
        campos.append({"clave": "aplica_en", "etiqueta": "Disponible para (CONTRATACION, RENOVACION o AMBAS)"})
    datos = pedir_formulario(campos, iniciar_en_resumen=anterior is not None)
    if datos is None:
        return None
    try:
        datos["fecha_inicio"] = _fecha(datos["fecha_inicio"])
        datos["fecha_final"] = _fecha(datos["fecha_final"])
        datos["plazo_meses"] = _numero(datos["plazo_meses"])
        _configurar_beneficios_version(datos, anterior)
        return datos
    except ValueError as exc:
        error(str(exc))
        return None


def _texto_aplica(condicion) -> str:
    return {
        "CONTRATACION": "Solo contratación",
        "RENOVACION": "Solo renovación",
        "AMBAS": "Contratación y renovación",
    }[condicion.aplica_en.value]


def _valor_configuracion(configuracion, atributo: str):
    if configuracion is None:
        return "No configurado"
    return getattr(configuracion, atributo)


def _navegar_recompensas(identidad: dict, rol: str) -> None:
    recompensas = obtener_recompensas(identidad)
    if not recompensas:
        error("No hay recompensas registradas.")
        return
    opciones = [f"{recompensa.codigo} | {recompensa.nombre}" for recompensa in recompensas]
    opciones.append("← Volver")
    seleccion = questionary.select("Recompensas", choices=opciones).ask()
    if seleccion in (None, "← Volver"):
        return
    recompensa = recompensas[opciones.index(seleccion)]
    _mostrar_detalle_recompensa(identidad, recompensa, rol)


def _mostrar_detalle_recompensa(identidad: dict, recompensa, rol: str) -> None:
    while True:
        _mostrar_encabezado({"identidad": identidad})
        condiciones = obtener_versiones_de_recompensa(recompensa.codigo)
        vigentes = [condicion for condicion in condiciones if condicion.esta_vigente()]
        actual = max(vigentes, key=lambda condicion: (condicion.fecha_inicio, condicion.num), default=None)
        if actual is not None:
            mostrar_tabla(
                "Recompensa",
                ["Código", "Nombre", "Costo", "Límite", "Inicio", "Final"],
                [(recompensa.codigo, recompensa.nombre, actual.costo_puntos,
                  actual.limite_canjes or "Sin límite", actual.fecha_inicio, actual.fecha_final)],
            )
        else:
            mostrar_tabla(
                "Recompensa",
                ["Código", "Nombre", "Estado"],
                [(recompensa.codigo, recompensa.nombre, "Sin condiciones vigentes")],
            )
        opciones = ["Historial de condiciones"]
        if rol == "ADM" and actual is not None:
            opciones.insert(0, "Modificar recompensa")
        if rol == "ADM":
            if actual is None:
                opciones.insert(1, "Reactivar recompensa")
        opciones.append("← Volver")
        seleccion = questionary.select(
            f"Recompensa {recompensa.codigo} - {recompensa.nombre}", choices=opciones
        ).ask()
        if seleccion in (None, "← Volver"):
            return
        if seleccion == "Modificar recompensa":
            _modificar_recompensa_desde_detalle(identidad, recompensa, actual)
        elif seleccion == "Reactivar recompensa":
            _reactivar_recompensa(identidad, recompensa, condiciones)
        elif seleccion == "Historial de condiciones":
            _mostrar_historial_recompensa(identidad, recompensa, rol)


def _mostrar_historial_recompensa(identidad: dict, recompensa, rol: str) -> None:
    from datetime import date, timedelta

    condiciones = sorted(
        obtener_versiones_de_recompensa(recompensa.codigo),
        key=lambda condicion: (condicion.fecha_inicio, condicion.num),
        reverse=True,
    )
    mostrar_tabla(
        "Historial de condiciones",
        ["Inicio", "Final", "Costo", "Límite", "Estado"],
        [(
            condicion.fecha_inicio,
            condicion.fecha_final,
            condicion.costo_puntos,
            condicion.limite_canjes or "Sin límite",
            "Vigente" if condicion.esta_vigente() else
            "Futura" if condicion.fecha_inicio > date.today() else "Vencida",
        ) for condicion in condiciones],
    )
    futuras = [
        condicion for condicion in condiciones
        if condicion.fecha_inicio >= date.today() + timedelta(days=1)
    ]
    if rol != "ADM" or not futuras:
        pausar()
        return
    opciones = [
        f"Borrar {condicion.fecha_inicio} a {condicion.fecha_final}"
        for condicion in futuras
    ] + ["← Volver"]
    seleccion = questionary.select("Condiciones futuras", choices=opciones).ask()
    if seleccion in (None, "← Volver"):
        return
    condicion = futuras[opciones.index(seleccion)]
    confirmar = questionary.confirm(
        "¿Borrar esta condición futura? Esta acción no se puede deshacer.", default=False
    ).ask()
    if not confirmar:
        return
    try:
        eliminar_condicion_futura_recompensa(identidad, condicion.num)
        exito("Condición futura eliminada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _crear_recompensa_completa(identidad: dict) -> None:
    datos_recompensa = pedir_formulario([
        {
            "clave": "codigo",
            "etiqueta": "Código",
            "validador": crear_validador_codigo_nuevo(obtener_recompensas, identidad),
        },
        {"clave": "nombre", "etiqueta": "Nombre"},
        {"clave": "descripcion", "etiqueta": "Descripción", "requerido": False},
    ])
    if datos_recompensa is None:
        return
    datos_condiciones = _pedir_condiciones_recompensa()
    if datos_condiciones is None:
        return
    try:
        recompensa = registrar_recompensa_con_condiciones(
            identidad, datos_recompensa, datos_condiciones
        )
        exito(f"Recompensa {recompensa.codigo} registrada.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _modificar_recompensa_desde_detalle(identidad: dict, recompensa, actual) -> None:
    datos_recompensa = pedir_formulario([
        {"clave": "nombre", "etiqueta": f"Nombre (actual: {recompensa.nombre})", "valor_inicial": recompensa.nombre},
        {"clave": "descripcion", "etiqueta": "Descripción actual", "requerido": False,
         "valor_inicial": recompensa.descripcion or ""},
    ], iniciar_en_resumen=True)
    if datos_recompensa is None or actual is None:
        if actual is None:
            error("La recompensa no tiene condiciones vigentes; utiliza Reactivar recompensa.")
        return
    datos_condiciones = _pedir_condiciones_recompensa(actual)
    if datos_condiciones is None:
        return
    try:
        modificar_recompensa_con_condiciones(
            identidad, recompensa.codigo, datos_recompensa, datos_condiciones
        )
        exito("Recompensa y nuevas condiciones guardadas.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _reactivar_recompensa(identidad: dict, recompensa, condiciones) -> None:
    from datetime import date

    anterior = max(condiciones, key=lambda condicion: (condicion.fecha_inicio, condicion.num), default=None)
    datos = _pedir_condiciones_recompensa(anterior, reactivacion=True)
    if datos is None:
        return
    try:
        reactivar_recompensa(identidad, recompensa.codigo, datos)
        exito("Recompensa reactivada con nuevas condiciones.")
    except (ValueError, PermissionError) as exc:
        error(str(exc))


def _pedir_condiciones_recompensa(anterior=None, reactivacion=False) -> dict | None:
    from datetime import date

    if reactivacion:
        inicio = date.today()
    elif anterior is not None:
        from datetime import timedelta
        inicio = max(date.today(), anterior.fecha_inicio + timedelta(days=1))
    else:
        inicio = ""
    final = max(getattr(anterior, "fecha_final", date.today()), inicio or date.today()) if anterior is not None else ""
    campos = [
        {"clave": "fecha_inicio", "etiqueta": "Fecha inicial (AAAA-MM-DD)", "valor_inicial": inicio},
        {
            "clave": "fecha_final",
            "etiqueta": "Fecha final (AAAA-MM-DD)",
            "valor_inicial": final,
            "validador": validar_fecha_final_recompensa,
        },
        {"clave": "costo_puntos", "etiqueta": "Costo en puntos",
         "valor_inicial": getattr(anterior, "costo_puntos", "")},
        {"clave": "limite_canjes", "etiqueta": "Límite de canjes (vacío sin límite)",
         "requerido": False, "valor_inicial": getattr(anterior, "limite_canjes", "") or ""},
    ]
    datos = pedir_formulario(campos, iniciar_en_resumen=anterior is not None)
    if datos is None:
        return None
    try:
        datos["fecha_inicio"] = _fecha(datos["fecha_inicio"])
        datos["fecha_final"] = _fecha(datos["fecha_final"])
        datos["costo_puntos"] = _numero(datos["costo_puntos"])
        datos["limite_canjes"] = _numero(datos["limite_canjes"]) if datos["limite_canjes"] else None
        return datos
    except ValueError as exc:
        error(str(exc))
        return None
