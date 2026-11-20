from datetime import date
from decimal import Decimal, InvalidOperation

import base_de_datos.consultas as bd
from clases.transaccion_cashback import TransaccionCashback
from clases.transaccion_puntos import TransaccionPuntos
from servicios.autorizacion.servicio_autorizacion import requiere_administrador
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    SaldoInsuficiente,
)


def ajustar_puntos(identidad: dict, num_membresia: int, movimiento: int, concepto: str):
    requiere_administrador(identidad)
    membresia = _obtener_membresia(num_membresia)
    if not isinstance(movimiento, int) or isinstance(movimiento, bool) or movimiento == 0:
        raise DatosInvalidos("El ajuste de puntos debe ser un entero distinto de cero.")
    if not concepto or not concepto.strip():
        raise DatosInvalidos("El concepto del ajuste es obligatorio.")
    saldo = _saldo_puntos(membresia.miembro.num)
    nuevo_saldo = saldo + movimiento
    if nuevo_saldo < 0:
        raise SaldoInsuficiente("El ajuste dejaría el saldo de puntos en negativo.")
    transaccion = TransaccionPuntos(
        num=None,
        movimiento=movimiento,
        saldo=nuevo_saldo,
        fecha=date.today(),
        concepto=concepto.strip(),
        compra=None,
        version_recompensa=None,
        membresia=membresia,
    )
    bd.guardar_transaccion_puntos(transaccion)
    return transaccion


def ajustar_cashback(identidad: dict, num_membresia: int, movimiento, concepto: str):
    requiere_administrador(identidad)
    membresia = _obtener_membresia(num_membresia)
    try:
        movimiento_decimal = Decimal(str(movimiento)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        raise DatosInvalidos("El ajuste de cashback no es válido.") from None
    if movimiento_decimal == 0:
        raise DatosInvalidos("El ajuste de cashback debe ser distinto de cero.")
    if not concepto or not concepto.strip():
        raise DatosInvalidos("El concepto del ajuste es obligatorio.")
    saldo = _saldo_cashback(membresia.num)
    nuevo_saldo = saldo + movimiento_decimal
    if nuevo_saldo < 0:
        raise SaldoInsuficiente("El ajuste dejaría el saldo de cashback en negativo.")
    transaccion = TransaccionCashback(
        num=None,
        monto=movimiento_decimal,
        saldo=nuevo_saldo,
        fecha=date.today(),
        concepto=concepto.strip(),
        compra=None,
        membresia=membresia,
    )
    bd.guardar_transaccion_cashback(transaccion)
    return transaccion


def _obtener_membresia(num_membresia: int):
    membresia = bd.buscar_membresia_por_num(num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    return membresia


def _saldo_puntos(num_miembro: int) -> int:
    transacciones = bd.obtener_transacciones_de_miembro(num_miembro)
    if not transacciones:
        return 0
    return max(transacciones, key=lambda t: (t.fecha, t.num)).saldo


def _saldo_cashback(num_membresia: int) -> Decimal:
    transacciones = bd.obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        return Decimal("0.00")
    return max(transacciones, key=lambda t: (t.fecha, t.num)).saldo
