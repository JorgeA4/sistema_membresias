"""Validadores reutilizables para rangos de fechas."""

from datetime import date


def validar_fecha_final_rango(valor, valores):
    if not valores.get("fecha_inicio"):
        return None
    fecha_inicio = date.fromisoformat(str(valores["fecha_inicio"]))
    fecha_final = date.fromisoformat(str(valor))
    if fecha_final < fecha_inicio:
        return "La fecha final no puede ser anterior a la fecha inicial."


def convertir_a_fecha(valor):
    if hasattr(valor, "date"):
        return valor.date()
    return valor
