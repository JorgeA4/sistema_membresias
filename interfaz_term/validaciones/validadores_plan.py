"""Validadores interactivos de planes y sus versiones."""

from decimal import Decimal, InvalidOperation


def crear_validador_codigo_plan_nuevo(obtener_planes, identidad: dict):
    def validar(valor, valores):
        if any(
            plan.codigo.casefold() == valor.strip().casefold()
            for plan in obtener_planes(identidad)
        ):
            return "El código del plan ya está registrado."

    return validar


def crear_validador_codigo_plan(obtener_planes, identidad: dict):
    def validar(valor, valores):
        if not any(
            plan.codigo.casefold() == valor.strip().casefold()
            for plan in obtener_planes(identidad)
        ):
            return "El plan indicado no existe."

    return validar


def validar_fecha_final(valor, valores):
    from utilidades.fechas import convertir_fecha

    if "fecha_inicio" in valores and convertir_fecha(valor) < convertir_fecha(
        valores["fecha_inicio"]
    ):
        return "La fecha final no puede ser anterior a la fecha inicial."


def validar_decimal_positivo(valor, valores):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return "Este campo debe ser un número decimal válido."
    if numero <= 0:
        return "El valor debe ser mayor que cero."


def validar_decimal_no_negativo(valor, valores):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return "Este campo debe ser un número decimal válido."
    if numero < 0:
        return "El valor no puede ser negativo."


def validar_entero_positivo(valor, valores):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return "Este campo debe ser un número entero."
    if numero <= 0:
        return "El valor debe ser mayor que cero."


def validar_dias_aplicables(valor, valores):
    try:
        dias = [int(dia.strip()) for dia in valor.split(",")]
    except ValueError:
        return "Los días deben ser números separados por comas."
    if any(dia < 1 or dia > 7 for dia in dias):
        return "Los días aplicables deben estar entre 1 y 7."
