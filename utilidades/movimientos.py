"""Utilidades comunes para clasificar y presentar movimientos."""


def clasificar_movimiento(movimiento) -> str:
    """Clasifica un movimiento como Ingreso, Egreso o Ajuste."""
    if getattr(movimiento, "version_recompensa", None) is not None:
        return "Egreso"
    if getattr(movimiento, "compra", None) is not None:
        valor = obtener_valor_movimiento(movimiento)
        return "Ingreso" if valor > 0 else "Egreso"
    return "Ajuste"


def obtener_valor_movimiento(movimiento):
    """Obtiene el importe de puntos o cashback del movimiento."""
    if hasattr(movimiento, "movimiento"):
        return movimiento.movimiento
    return movimiento.monto


def obtener_saldo_anterior(movimiento):
    """Calcula el saldo inmediatamente anterior al movimiento."""
    return movimiento.saldo - obtener_valor_movimiento(movimiento)


def obtener_datos_movimiento(movimiento) -> tuple:
    """Devuelve los datos derivados para mostrar un movimiento."""
    return (
        clasificar_movimiento(movimiento),
        obtener_valor_movimiento(movimiento),
        obtener_saldo_anterior(movimiento),
        movimiento.saldo,
    )
