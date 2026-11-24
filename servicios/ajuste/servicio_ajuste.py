from datetime import datetime
from decimal import Decimal, InvalidOperation

import base_de_datos.consultas.compras.consultas_compras as consultas_compras
import base_de_datos.consultas.membresias.consultas_membresias as consultas_membresias
import base_de_datos.consultas.compras.operaciones_compras as operaciones_compras
from clases.transaccion_cashback import TransaccionCashback
from clases.transaccion_puntos import TransaccionPuntos
from servicios.autorizacion.servicio_autorizacion import requiere_administrador_o_gerente
from utilidades.excepciones import (
    DatosInvalidos,
    EntidadNoEncontrada,
    SaldoInsuficiente,
)


def ajustar_puntos(identidad: dict, num_membresia: int, movimiento: int, concepto: str):
    requiere_administrador_o_gerente(identidad)
    membresia = _obtener_membresia(num_membresia)
    if not isinstance(movimiento, int) or isinstance(movimiento, bool) or movimiento == 0:
        raise DatosInvalidos("El ajuste de puntos debe ser un entero distinto de cero.")
    if not concepto or not concepto.strip():
        raise DatosInvalidos("El concepto del ajuste es obligatorio.")
    saldo = _saldo_puntos(membresia.num)
    nuevo_saldo = saldo + movimiento
    if nuevo_saldo < 0:
        raise SaldoInsuficiente("El ajuste dejaría el saldo de puntos en negativo.")
    transaccion = TransaccionPuntos(
        num=None,
        movimiento=movimiento,
        saldo=nuevo_saldo,
        fecha=datetime.now(),
        concepto=concepto.strip(),
        compra=None,
        version_recompensa=None,
        membresia=membresia,
    )
    operaciones_compras.guardar_transaccion_puntos(transaccion)
    return transaccion


def ajustar_cashback(identidad: dict, num_membresia: int, movimiento, concepto: str):
    requiere_administrador_o_gerente(identidad)
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
        fecha=datetime.now(),
        concepto=concepto.strip(),
        compra=None,
        membresia=membresia,
    )
    operaciones_compras.guardar_transaccion_cashback(transaccion)
    return transaccion


def _obtener_membresia(num_membresia: int):
    membresia = consultas_membresias.buscar_membresia_por_num(num_membresia)
    if membresia is None:
        raise EntidadNoEncontrada("La membresía no existe.")
    return membresia


def _saldo_puntos(num_membresia: int) -> int:
    membresia = _obtener_membresia(num_membresia)
    transacciones = [
        transaccion
        for transaccion in consultas_compras.obtener_transacciones_de_miembro(membresia.miembro.num)
        if transaccion.membresia is not None
        and transaccion.membresia.num == num_membresia
    ]
    if not transacciones:
        return 0
    return max(transacciones, key=lambda t: (t.fecha, t.num)).saldo


def _saldo_cashback(num_membresia: int) -> Decimal:
    transacciones = consultas_compras.obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        return Decimal("0.00")
    return max(transacciones, key=lambda t: (t.fecha, t.num)).saldo
