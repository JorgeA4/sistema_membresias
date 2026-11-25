from decimal import Decimal

from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_transaccion_cashback,
    mapear_transaccion_puntos,
)
from base_de_datos.consultas.compras.consultas_compras import _consulta_compra
from base_de_datos.consultas.membresias.consultas_membresias import (
    _consulta_membresia,
)
from base_de_datos.consultas.recompensas.consultas_recompensas import (
    _consulta_version_recompensa,
)


# Consulta una transacción de puntos y sus relaciones.
def _consulta_transaccion_puntos(conexion, num):
    consulta = """
        SELECT *
        FROM transaccion_puntos
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    compra = None
    if fila["compra"]:
        compra = _consulta_compra(conexion, fila["compra"])
    version_recompensa = None
    if fila["version_recompensa"]:
        version_recompensa = _consulta_version_recompensa(
            conexion,
            fila["version_recompensa"],
        )
    return mapear_transaccion_puntos(
        fila,
        compra,
        version_recompensa,
        _consulta_membresia(conexion, fila["membresia"]),
    )


# Consulta los movimientos de puntos de un miembro.
def obtener_transacciones_de_miembro(num_miembro):
    consulta = """
        SELECT tp.num
        FROM transaccion_puntos AS tp
        INNER JOIN
            membresia AS m ON tp.membresia = m.num
        WHERE
            m.miembro = %s
        ORDER BY
            tp.fecha,
            tp.num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_miembro,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_transaccion_puntos(conexion, num)
            for num in lista_numeros
        ]


# Consulta el saldo actual de puntos de un miembro.
def obtener_saldo_de_miembro(num_miembro):
    transacciones = obtener_transacciones_de_miembro(num_miembro)
    if not transacciones:
        return 0
    return max(
        transacciones,
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    ).saldo


# Consulta una transacción de cashback y sus relaciones.
def _consulta_transaccion_cashback(conexion, num):
    consulta = """
        SELECT *
        FROM transaccion_cashback
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    compra = None
    if fila["compra"]:
        compra = _consulta_compra(conexion, fila["compra"])
    return mapear_transaccion_cashback(
        fila,
        compra,
        _consulta_membresia(conexion, fila["membresia"]),
    )


# Consulta los movimientos de cashback de una membresía.
def obtener_transacciones_cashback_de_membresia(num_membresia):
    consulta = """
        SELECT num
        FROM transaccion_cashback
        WHERE membresia = %s
        ORDER BY
            fecha,
            num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_membresia,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_transaccion_cashback(conexion, num)
            for num in lista_numeros
        ]


# Consulta el saldo actual de cashback de una membresía.
def obtener_saldo_cashback_de_membresia(num_membresia):
    transacciones = obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        return Decimal("0")
    return max(
        transacciones,
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    ).saldo
