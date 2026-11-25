"""Validadores interactivos del flujo de compra."""

from decimal import Decimal

from servicios.caja.servicio_caja import validar_canje
from servicios.compra.servicio_compra import (
    obtener_cashback_disponible,
    obtener_saldo_de_membresia,
)
from servicios.membresia.servicio_membresia import consultar_membresia
from interfaz_term.componentes.tabla import mostrar_tabla
from servicios.recompensa.servicio_recompensa import (
    consultar_recompensa,
    obtener_versiones_de_recompensa,
)


def crear_validador_membresia_compra(identidad: dict):
    """Valida una membresía activa con plan para una compra."""
    def validar(valor, valores):
        valores.pop("_membresia", None)
        valores.pop("_cashback_disponible", None)
        membresia = consultar_membresia(identidad, int(valor))
        if membresia is None:
            return "La membresía no existe."
        if membresia.estado.value != "ACTIVA":
            return "La membresía no está activa."
        if membresia.version_plan_actual is None:
            return "La membresía no tiene un plan vigente."
        valores["_membresia"] = membresia

    return validar


def mostrar_cashback_disponible(identidad: dict, valores: dict) -> None:
    """Prepara el saldo disponible antes de solicitar cashback."""
    membresia = valores.get("_membresia")
    if membresia is None:
        return
    saldo = obtener_cashback_disponible(identidad, membresia.num)
    valores["_cashback_disponible"] = saldo


def crear_mostrador_cashback(identidad: dict):
    """Crea la acción que muestra el cashback de la membresía capturada."""
    def mostrar(valores):
        mostrar_cashback_disponible(identidad, valores)

    return mostrar


def mostrar_cliente_compra(valores: dict) -> list[str]:
    """Devuelve el contexto del cliente para el banner de la compra."""
    membresia = valores.get("_membresia")
    if membresia is None:
        return [
            "Cliente:",
            "Cashback disponible:",
            "Puntos disponibles:",
        ]
    miembro = membresia.miembro
    contexto = [f"Cliente: {miembro.nombre} {miembro.primer_apellido}"]
    if "_cashback_disponible" in valores:
        contexto.append(f"Cashback disponible: ${valores['_cashback_disponible']:.2f}")
    else:
        contexto.append("Cashback disponible:")
    contexto.append("Puntos disponibles:")
    return contexto


def crear_mostrador_contexto_compra(identidad: dict):
    """Crea el contexto de compra con los saldos de la membresía."""
    def mostrar(valores: dict) -> list[str]:
        contexto = mostrar_cliente_compra(valores)
        membresia = valores.get("_membresia")
        if membresia is not None:
            contexto[-1] = (
                f"Puntos disponibles: "
                f"{obtener_saldo_de_membresia(identidad, membresia.num):.0f}"
            )
            if "_cashback_disponible" not in valores:
                contexto[-2] = (
                    f"Cashback disponible: "
                    f"${obtener_cashback_disponible(identidad, membresia.num):.2f}"
                )
        return contexto

    return mostrar


def validar_cashback(valor, valores):
    """Valida el cashback contra el saldo y el monto de la compra."""
    if not valor:
        return None
    cashback = Decimal(valor)
    saldo = valores.get("_cashback_disponible", Decimal("0"))
    if cashback > saldo:
        return f"El cashback no puede superar el disponible (${saldo:.2f})."
    if "monto_base" in valores and cashback > Decimal(valores["monto_base"]):
        return "El cashback no puede superar el monto de la compra."


def crear_validador_recompensa(identidad: dict):
    """Valida una recompensa y conserva su versión vigente en el contexto."""
    def validar(valor, valores):
        valores.pop("_version_recompensa", None)
        if not valor:
            return None
        membresia = valores.get("_membresia")
        recompensa = consultar_recompensa(valor.strip())
        if recompensa is None:
            return "La recompensa no existe."
        versiones = [
            version
            for version in obtener_versiones_de_recompensa(recompensa.codigo)
            if version.esta_vigente()
        ]
        if len(versiones) != 1:
            return "La recompensa no tiene una única versión vigente."
        validar_canje(identidad, membresia.num, versiones[0].num)
        valores["_version_recompensa"] = versiones[0]

    return validar


def mostrar_detalle_recompensa(valores: dict) -> None:
    """Muestra el detalle de la recompensa seleccionada en el formulario."""
    version = valores.get("_version_recompensa")
    if version is None:
        return
    mostrar_tabla(
        "Detalle de recompensa",
        ["Código", "Nombre", "Descripción", "Costo", "Límite"],
        [(
            version.recompensa.codigo,
            version.recompensa.nombre,
            version.recompensa.descripcion or "Sin descripción",
            version.costo_puntos,
            version.limite_canjes or "Sin límite",
        )],
    )
