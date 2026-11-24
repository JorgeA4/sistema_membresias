
from decimal import Decimal

from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_compra,
    mapear_transaccion_cashback,
    mapear_transaccion_puntos,
)

from base_de_datos.consultas.membresias.consultas_membresias import _consulta_membresia
from base_de_datos.consultas.recompensas.consultas_recompensas import _consulta_version_recompensa
from base_de_datos.consultas.usuarios.consultas_usuarios import _obtener_usuario_conexion

# Consulta una compra y su fecha derivada
def _consulta_compra(conexion, num):
    consulta = """
        SELECT
            c.*,
            (
                SELECT MIN(tp.fecha)
                FROM transaccion_puntos AS tp
                WHERE tp.compra = c.num
                AND tp.movimiento > 0
                AND tp.version_recompensa IS NULL
            ) AS fecha
        FROM
            compra c
        WHERE
            c.num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_compra(
        fila, _consulta_membresia(conexion, fila["membresia"]),
        _obtener_usuario_conexion(conexion, fila["usuario"]),
    )

# consulta una compra por su numero
def buscar_compra_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_compra(conexion, num)

#consulta las compras de una membresia
def obtener_compras_de_membresia(num_membresia):
    consulta = """
        SELECT num
        FROM compra
        WHERE membresia = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_membresia,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_compra(conexion, num)
            for num in lista_numeros
        ]

# consulta las compras registradas por un usuario
def obtener_compras_de_usuario(num_usuario):
    consulta = """
        SELECT num
        FROM compra
        WHERE usuario = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_usuario,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_compra(conexion, num)
            for num in lista_numeros
        ]

# Consulta una transaccion de puntos y sus relaciones.
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

# consulta los movimientos de puntos de un miembro
def obtener_transacciones_de_miembro(num_miembro):
    consulta = """
        SELECT
            tp.num
        FROM
            transaccion_puntos tp
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

# consulta el saldo qctual de puntos de un miembro
def obtener_saldo_de_miembro(num_miembro):
    transacciones = obtener_transacciones_de_miembro(num_miembro)
    if not transacciones:
        return 0
    return max(
        transacciones,
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    ).saldo

# consulta una transaccion de cashback y sus relaciones
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

# consulta los movimientos de casback de una membresia
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

# consulta el saldo actual de cashback de una membresia
def obtener_saldo_cashback_de_membresia(num_membresia):
    transacciones = obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        return Decimal("0")
    return max(
        transacciones,
        key=lambda transaccion: (transaccion.fecha, transaccion.num),
    ).saldo
