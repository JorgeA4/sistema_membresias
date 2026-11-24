"""Validadores reutilizables para rangos de fechas."""

from utilidades.fechas import convertir_fecha


def validar_fecha_final_rango(valor, valores):
    if not valores.get("fecha_inicio"):
        return None
    fecha_inicio = convertir_fecha(valores["fecha_inicio"])
    fecha_final = convertir_fecha(valor)
    if fecha_final < fecha_inicio:
        return "La fecha final no puede ser anterior a la fecha inicial."


def convertir_a_fecha(valor):
    return convertir_fecha(valor)
