"""Menú de consulta para miembros."""

from decimal import Decimal

import questionary

from interfaz_term.componentes.banner import mostrar_banner, mostrar_banner_operacion
from interfaz_term.componentes.formulario import pedir_formulario
from interfaz_term.componentes.mensajes import error, informacion, pausar
from interfaz_term.componentes.tabla import formatear_fecha_hora, mostrar_tabla
from interfaz_term.estilos.tema import COLOR_ENCABEZADO
from interfaz_term.navegacion import (
    BENEFICIOS,
    CERRAR_SESION,
    HISTORIAL,
    MI_CUENTA,
    SOLICITUDES_TIENDA,
    VOLVER,
)
from servicios.compra.servicio_compra import (
    obtener_compras_de_membresia,
    obtener_fecha_vencimiento_puntos,
    obtener_saldo_de_membresia,
    obtener_transacciones_cashback_de_membresia,
    obtener_transacciones_de_membresia,
)
from servicios.membresia.servicio_membresia import consultar_membresia_de_miembro
from servicios.miembro.servicio_miembro import consultar_miembro
from servicios.recompensa.servicio_recompensa import (
    obtener_historial_canjes,
    obtener_versiones_recompensa_vigentes,
)
from utilidades.excepciones import EntidadNoEncontrada
from utilidades.movimientos import obtener_datos_movimiento
from interfaz_term.validaciones.validadores_fecha import validar_fecha_final_rango

def _mostrar_encabezado(sesion: dict) -> None:
    identidad = sesion.get("identidad") or {}
    nombre = identidad.get("nombre", "")
    mostrar_banner(
        f"Miembro: [{COLOR_ENCABEZADO}]{nombre}[/{COLOR_ENCABEZADO}]"
    )


def mostrar_miembro(sesion: dict) -> tuple:
    opciones = [
        ("Mi cuenta", MI_CUENTA),
        ("Beneficios", BENEFICIOS),
        ("Historial", HISTORIAL),
        ("Solicitudes en tienda", SOLICITUDES_TIENDA),
        ("Cerrar sesión", CERRAR_SESION),
    ]
    _mostrar_encabezado(sesion)
    seleccion = questionary.select(
        "¿Qué deseas hacer?",
        choices=[opcion[0] for opcion in opciones],
    ).ask()
    for nombre, pantalla in opciones:
        if seleccion == nombre:
            return None if pantalla == CERRAR_SESION else "miembro", pantalla
    return None, CERRAR_SESION


def mostrar_mi_cuenta(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    accion = questionary.select(
        "Mi cuenta",
        choices=["Mi información", "Mi membresía", "← Volver"],
    ).ask()
    identidad = sesion["identidad"]
    try:
        if accion == "Mi información":
            _mostrar_informacion(identidad)
        elif accion == "Mi membresía":
            _mostrar_membresia(identidad)
        elif accion == "← Volver":
            return "miembro", VOLVER
    except (ValueError, PermissionError) as exc:
        error(str(exc))
    return "miembro", None


def mostrar_beneficios(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    accion = questionary.select(
        "Beneficios",
        choices=["Mis puntos", "Recompensas disponibles", "← Volver"],
    ).ask()
    identidad = sesion["identidad"]
    try:
        if accion == "Mis puntos":
            _mostrar_puntos(identidad)
        elif accion == "Recompensas disponibles":
            _mostrar_recompensas()
        elif accion == "← Volver":
            return "miembro", VOLVER
    except (ValueError, PermissionError) as exc:
        error(str(exc))
    return "miembro", None


def mostrar_historial(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    accion = questionary.select(
        "Historial",
        choices=[
            "Historial de compras",
            "Historial de puntos",
            "Historial de canjes",
            "← Volver",
        ],
    ).ask()
    identidad = sesion["identidad"]
    try:
        if accion == "Historial de compras":
            _mostrar_compras(identidad)
        elif accion == "Historial de puntos":
            _mostrar_historial_puntos(identidad)
        elif accion == "Historial de canjes":
            _mostrar_historial_canjes(identidad)
        elif accion == "← Volver":
            return "miembro", VOLVER
    except (ValueError, PermissionError) as exc:
        error(str(exc))
    return "miembro", None


def mostrar_solicitudes_tienda(sesion: dict) -> tuple:
    _mostrar_encabezado(sesion)
    accion = questionary.select(
        "Solicitudes en tienda",
        choices=[
            "Solicitar renovación",
            "Solicitar cancelación",
            "Solicitar canje",
            "← Volver",
        ],
    ).ask()
    if accion == "Solicitar renovación":
        informacion("La renovación debe realizarla un Cajero o Administrador en caja.")
    elif accion == "Solicitar cancelación":
        informacion(
            "La solicitud será atendida en tienda; la cancelación efectiva la realiza un Administrador."
        )
    elif accion == "Solicitar canje":
        informacion("El canje debe realizarlo un Cajero o Administrador en caja.")
    elif accion == "← Volver":
        return "miembro", VOLVER
    return "miembro", None


def _mostrar_informacion(identidad: dict) -> None:
    miembro = consultar_miembro(identidad, identidad["num"])
    if miembro is None:
        raise EntidadNoEncontrada("El miembro no existe.")
    mostrar_tabla(
        "Información personal",
        ["Nombre", "Correo", "Teléfono"],
        [(f"{miembro.nombre} {miembro.primer_apellido}", miembro.correo, miembro.telefono)],
    )
    _pausa()


def _mostrar_membresia(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise EntidadNoEncontrada("No tienes una membresía registrada.")
    version = membresia.version_plan_actual
    if version is None:
        fila = (membresia.num, membresia.estado.value, "Sin plan", "-", "-", "-", "-", "-", "-")
    else:
        puntos = version.config_puntos
        descuento = version.config_descuento
        cashback = version.config_cashback
        fila = (
            membresia.num,
            membresia.estado.value,
            version.plan.nombre,
            version.num,
            version.precio,
            version.plazo_meses,
            "No configurados" if puntos is None else f"{puntos.porcentaje} (vigencia: {puntos.vigencia_meses or 'sin caducidad'} meses)",
            "No configurado" if descuento is None else descuento.porcentaje,
            "No configurado" if cashback is None else f"{cashback.porcentaje} (umbral: {cashback.limite_min_mensual or 'sin umbral'})",
        )
    mostrar_tabla(
        "Membresía y beneficios",
        ["Número", "Estado", "Plan", "Condiciones", "Precio", "Plazo", "Puntos", "Descuento", "Cashback"],
        [fila],
    )
    _pausa()


def _mostrar_puntos(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise EntidadNoEncontrada("No tienes una membresía registrada.")
    saldo = obtener_saldo_de_membresia(identidad, membresia.num)
    fecha_vencimiento = obtener_fecha_vencimiento_puntos(identidad, membresia.num)
    mostrar_tabla(
        "Saldo de puntos",
        ["Membresía", "Saldo", "Válidos hasta"],
        [(membresia.num, saldo, fecha_vencimiento or "Sin vencimiento")],
    )
    _pausa()


def _mostrar_recompensas() -> None:
    versiones = obtener_versiones_recompensa_vigentes()
    mostrar_tabla(
        "Recompensas disponibles",
        ["Versión", "Código", "Nombre", "Costo", "Límite"],
        [
            (v.num, v.recompensa.codigo, v.recompensa.nombre, v.costo_puntos, v.limite_canjes or "Sin límite")
            for v in versiones
        ],
    )
    _pausa()


def _mostrar_compras(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise EntidadNoEncontrada("No tienes una membresía registrada.")
    rango = _pedir_rango_fechas(identidad, membresia, "Historial de compras")
    if rango is None:
        return
    fecha_inicio, fecha_final = rango
    compras = obtener_compras_de_membresia(
        identidad,
        membresia.num,
        fecha_inicio,
        fecha_final,
    )
    puntos = obtener_transacciones_de_membresia(identidad, membresia.num)
    cashback = obtener_transacciones_cashback_de_membresia(
        identidad, membresia.num
    )
    puntos_por_compra = {
        compra.num: sum(
            transaccion.movimiento
            for transaccion in puntos
            if transaccion.compra is not None
            and transaccion.compra.num == compra.num
            and transaccion.movimiento > 0
        )
        for compra in compras
    }
    cashback_por_compra = {
        compra.num: sum(
            (
                transaccion.monto
                for transaccion in cashback
                if transaccion.compra is not None
                and transaccion.compra.num == compra.num
                and transaccion.monto > 0
            ),
            Decimal("0.00"),
        )
        for compra in compras
    }
    mostrar_tabla(
        "Historial de compras",
        [
            "Número",
            "Fecha y hora",
            "Monto base",
            "Descuento",
            "Cashback aplicado",
            "Cashback generado",
            "Puntos generados",
            "Monto final",
        ],
        [
            (
                c.num,
                formatear_fecha_hora(c.fecha),
                c.monto_base,
                c.descuento_nominal,
                c.cashback_aplicado,
                cashback_por_compra[c.num],
                puntos_por_compra[c.num],
                c.monto_final,
            )
            for c in compras
        ],
    )
    _pausa()


def _mostrar_historial_puntos(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise EntidadNoEncontrada("No tienes una membresía registrada.")
    rango = _pedir_rango_fechas(identidad, membresia, "Historial de puntos")
    if rango is None:
        return
    fecha_inicio, fecha_final = rango
    transacciones = obtener_transacciones_de_membresia(
        identidad,
        membresia.num,
        fecha_inicio,
        fecha_final,
    )
    mostrar_tabla(
        "Historial de puntos",
        [
            "Fecha y hora",
            "Número",
            "Tipo",
            "Movimiento",
            "Saldo anterior",
            "Saldo posterior",
            "Concepto",
        ],
        [
            (
                formatear_fecha_hora(t.fecha),
                t.num,
                *obtener_datos_movimiento(t),
                t.concepto or "",
            )
            for t in transacciones
        ],
    )
    _pausa()


def _pedir_rango_fechas(identidad: dict, membresia, titulo: str):
    datos = pedir_formulario(
        [
            {
                "clave": "fecha_inicio",
                "etiqueta": "Fecha inicial (opcional)",
                "requerido": False,
            },
            {
                "clave": "fecha_final",
                "etiqueta": "Fecha final (opcional)",
                "requerido": False,
                "validador": validar_fecha_final_rango,
            },
        ],
        titulo=titulo,
        mostrar_encabezado=lambda nombre, _valores, contexto: mostrar_banner_operacion(
            nombre,
            {"nombre": identidad.get("nombre", ""), "rol_nombre": "Miembro"},
            contexto,
            limpiar=False,
        ),
        mostrar_contexto=lambda _valores: [
            f"Cliente: {membresia.miembro.nombre} "
            f"{membresia.miembro.primer_apellido}",
            f"Membresía: {membresia.num}",
        ],
    )
    if datos is None:
        return None
    from datetime import date
    return (
        date.fromisoformat(datos["fecha_inicio"])
        if datos["fecha_inicio"] else None,
        date.fromisoformat(datos["fecha_final"])
        if datos["fecha_final"] else None,
    )


def _mostrar_historial_canjes(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise EntidadNoEncontrada("No tienes una membresía registrada.")
    canjes = obtener_historial_canjes(identidad, membresia.num)
    mostrar_tabla(
        "Historial de canjes",
        ["Fecha", "Número", "Movimiento", "Saldo", "Recompensa"],
        [
            (
                formatear_fecha_hora(t.fecha),
                t.num,
                t.movimiento,
                t.saldo,
                t.version_recompensa.recompensa.nombre,
            )
            for t in canjes
        ],
    )
    _pausa()


def _pausa() -> None:
    pausar()
