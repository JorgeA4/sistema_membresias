"""Validadores interactivos de recompensas y sus versiones."""


def crear_validador_codigo_nuevo(obtener_recompensas, identidad: dict):
    def validar(valor, valores):
        if any(
            recompensa.codigo.casefold() == valor.strip().casefold()
            for recompensa in obtener_recompensas(identidad)
        ):
            return "El código de la recompensa ya está registrado."

    return validar


def validar_codigo_existente(consultar_recompensa):
    def validar(valor, valores):
        if consultar_recompensa(valor.strip()) is None:
            return "La recompensa indicada no existe."

    return validar


def validar_fecha_final(valor, valores):
    from datetime import date

    def convertir(fecha):
        if isinstance(fecha, date):
            return fecha
        return date.fromisoformat(fecha)

    if "fecha_inicio" in valores and convertir(valor) < convertir(valores["fecha_inicio"]):
        return "La fecha final no puede ser anterior a la fecha inicial."
