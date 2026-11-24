"""Conversión centralizada de fechas introducidas por el usuario."""

from datetime import date, datetime, timedelta
import re


_FORMATOS_FECHA = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")


def convertir_fecha(valor, fecha_referencia: date | None = None) -> date:
    """Convierte fechas absolutas o desplazamientos relativos a una fecha."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor

    texto = str(valor).strip()
    if re.fullmatch(r"[+-]?\d+", texto):
        referencia = fecha_referencia or date.today()
        return referencia + timedelta(days=int(texto))

    for formato in _FORMATOS_FECHA:
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue

    raise ValueError(
        "La fecha debe tener formato DD/MM/AAAA o ser un desplazamiento "
        "relativo (0=hoy, -1=ayer, 1=mañana)."
    )
