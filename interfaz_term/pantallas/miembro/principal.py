"""Menú de consulta para miembros."""

from rich.console import Console
from rich.panel import Panel
from rich import box as rich_box

import questionary

from interfaz_term.componentes.mensajes import error, informacion
from interfaz_term.componentes.tabla import mostrar_tabla
from interfaz_term.estilos.tema import COLOR_ENCABEZADO, COLOR_TITULO
from servicios.compra.servicio_compra import (
    obtener_compras_de_membresia,
    obtener_fecha_vencimiento_puntos,
    obtener_saldo_de_miembro,
    obtener_transacciones_de_miembro,
)
from servicios.membresia.servicio_membresia import consultar_membresia_de_miembro
from servicios.miembro.servicio_miembro import consultar_miembro
from servicios.recompensa.servicio_recompensa import (
    obtener_historial_canjes,
    obtener_versiones_recompensa_vigentes,
)

_consola = Console()


def mostrar_miembro(sesion: dict) -> tuple:
    identidad = sesion.get("identidad") or {}
    nombre = identidad.get("nombre", "")
    opciones = [
        "Mi información",
        "Mi membresía",
        "Mis puntos",
        "Recompensas disponibles",
        "Historial de compras",
        "Historial de puntos",
        "Historial de canjes",
        "Solicitar renovación en tienda",
        "Solicitar cancelación en tienda",
        "Solicitar canje en tienda",
        "Cerrar sesión",
    ]

    while True:
        _consola.clear()
        _consola.print(
            Panel(
                f"[{COLOR_TITULO}]NEXUM[/{COLOR_TITULO}] — [dim]Interfaz de Miembro[/dim]\n"
                f"Miembro: [{COLOR_ENCABEZADO}]{nombre}[/{COLOR_ENCABEZADO}]",
                border_style=COLOR_ENCABEZADO,
                box=rich_box.ROUNDED,
                padding=(0, 4),
            )
        )
        accion = questionary.select("¿Qué deseas consultar?", choices=opciones).ask()
        try:
            if accion == "Mi información":
                _mostrar_informacion(identidad)
            elif accion == "Mi membresía":
                _mostrar_membresia(identidad)
            elif accion == "Mis puntos":
                _mostrar_puntos(identidad)
            elif accion == "Recompensas disponibles":
                _mostrar_recompensas()
            elif accion == "Historial de compras":
                _mostrar_compras(identidad)
            elif accion == "Historial de puntos":
                _mostrar_historial_puntos(identidad)
            elif accion == "Historial de canjes":
                _mostrar_historial_canjes(identidad)
            elif accion == "Solicitar renovación en tienda":
                informacion("La renovación debe realizarla un Cajero o Administrador en caja.")
            elif accion == "Solicitar cancelación en tienda":
                informacion("La solicitud será atendida en tienda; la cancelación efectiva la realiza un Administrador.")
            elif accion == "Solicitar canje en tienda":
                informacion("El canje debe realizarlo un Cajero o Administrador en caja.")
            else:
                sesion["identidad"] = None
                return None, 1
        except (ValueError, PermissionError) as exc:
            error(str(exc))


def _mostrar_informacion(identidad: dict) -> None:
    miembro = consultar_miembro(identidad, identidad["num"])
    if miembro is None:
        raise ValueError("El miembro no existe.")
    mostrar_tabla(
        "Información personal",
        ["Número", "Nombre", "Correo", "Teléfono"],
        [(miembro.num, f"{miembro.nombre} {miembro.primer_apellido}", miembro.correo, miembro.telefono)],
    )
    _pausa()


def _mostrar_membresia(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise ValueError("No tienes una membresía registrada.")
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
        ["Número", "Estado", "Plan", "Versión", "Precio", "Plazo", "Puntos", "Descuento", "Cashback"],
        [fila],
    )
    _pausa()


def _mostrar_puntos(identidad: dict) -> None:
    saldo = obtener_saldo_de_miembro(identidad, identidad["num"])
    fecha_vencimiento = obtener_fecha_vencimiento_puntos(identidad, identidad["num"])
    mostrar_tabla(
        "Saldo de puntos",
        ["Miembro", "Saldo", "Válidos hasta"],
        [(identidad["num"], saldo, fecha_vencimiento or "Sin vencimiento")],
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
        raise ValueError("No tienes una membresía registrada.")
    compras = obtener_compras_de_membresia(identidad, membresia.num)
    mostrar_tabla(
        "Historial de compras",
        ["Número", "Monto base", "Descuento", "Monto final"],
        [(c.num, c.monto_base, c.descuento_nominal, c.monto_final) for c in compras],
    )
    _pausa()


def _mostrar_historial_puntos(identidad: dict) -> None:
    transacciones = obtener_transacciones_de_miembro(identidad, identidad["num"])
    mostrar_tabla(
        "Historial de puntos",
        ["Número", "Movimiento", "Saldo", "Concepto"],
        [(t.num, t.movimiento, t.saldo, t.concepto or "") for t in transacciones],
    )
    _pausa()


def _mostrar_historial_canjes(identidad: dict) -> None:
    membresia = consultar_membresia_de_miembro(identidad, identidad["num"])
    if membresia is None:
        raise ValueError("No tienes una membresía registrada.")
    canjes = obtener_historial_canjes(identidad, membresia.num)
    mostrar_tabla(
        "Historial de canjes",
        ["Número", "Movimiento", "Saldo", "Recompensa"],
        [
            (t.num, t.movimiento, t.saldo, t.version_recompensa.recompensa.nombre)
            for t in canjes
        ],
    )
    _pausa()


def _pausa() -> None:
    input("Presiona Enter para continuar.")
