"""Validadores relacionados con membresías."""

from servicios.membresia.servicio_membresia import consultar_membresia
from servicios.compra.servicio_compra import (
    obtener_cashback_disponible,
    obtener_saldo_de_membresia,
)


def mostrar_contexto_membresia(valores):
    """Devuelve el cliente y estado de la membresía capturada."""
    membresia = valores.get("_membresia")
    if membresia is None:
        return None
    miembro = membresia.miembro
    contexto = [
        f"Cliente: {miembro.nombre} {miembro.primer_apellido}",
        f"Estado: {membresia.estado.value}",
    ]
    if membresia.version_plan_actual is not None:
        contexto.append(f"Plan actual: {membresia.version_plan_actual.plan.nombre}")
    return contexto


def crear_contexto_membresia(identidad: dict, puntos: bool = False, cashback: bool = False):
    """Crea contexto adicional para operaciones sobre una membresía."""
    def mostrar(valores):
        contexto = mostrar_contexto_membresia(valores)
        if contexto is None:
            return None
        membresia = valores["_membresia"]
        if puntos:
            contexto.append(
                f"Saldo de puntos: {obtener_saldo_de_membresia(identidad, membresia.num)}"
            )
        if cashback:
            contexto.append(
                f"Cashback disponible: "
                f"${obtener_cashback_disponible(identidad, membresia.num):.2f}"
            )
        return contexto

    return mostrar


def crear_validador_membresia(identidad: dict, exigir_activa: bool = False):
    """Crea un validador que consulta y conserva una membresía en el contexto."""
    def validar(valor, valores):
        valores.pop("_membresia", None)
        membresia = consultar_membresia(identidad, int(valor))
        if membresia is None:
            return "La membresía no existe."
        if exigir_activa and membresia.estado.value != "ACTIVA":
            return "La membresía no está activa."
        valores["_membresia"] = membresia

    return validar


def crear_validador_membresia_para_renovacion(identidad: dict):
    """Valida una membresía que puede renovarse."""
    def validar(valor, valores):
        valores.pop("_membresia", None)
        membresia = consultar_membresia(identidad, int(valor))
        if membresia is None:
            return "La membresía no existe."
        if membresia.estado.value == "CANCELADA":
            return "La membresía está cancelada y requiere una nueva contratación."
        valores["_membresia"] = membresia

    return validar
