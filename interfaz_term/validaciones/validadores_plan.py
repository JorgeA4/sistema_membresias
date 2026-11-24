"""Validadores interactivos de planes y sus versiones."""


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
    from datetime import date

    def convertir(fecha):
        if isinstance(fecha, date):
            return fecha
        return date.fromisoformat(fecha)

    if "fecha_inicio" in valores and convertir(valor) < convertir(valores["fecha_inicio"]):
        return "La fecha final no puede ser anterior a la fecha inicial."
