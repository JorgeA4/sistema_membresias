"""Acceso persistente de compras."""

from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_compra,
    mapear_configuracion_cashback,
    mapear_configuracion_descuento,
    mapear_configuracion_puntos,
    mapear_membresia,
    mapear_miembro,
    mapear_plan,
    mapear_recompensa,
    mapear_renovacion,
    mapear_rol,
    mapear_transaccion_cashback,
    mapear_transaccion_puntos,
    mapear_usuario,
    mapear_version_plan,
    mapear_version_recompensa,
)

from base_de_datos.consultas.membresias.consultas_membresias import _consulta_membresia
from base_de_datos.consultas.planes.consultas_planes import _consulta_version_plan
from base_de_datos.consultas.recompensas.consultas_recompensas import (
    _consulta_version_recompensa,
)
from base_de_datos.consultas.usuarios.consultas_usuarios import _obtener_usuario_conexion

def _consulta_compra(conexion, num):
    consulta = """
        SELECT c.*,
               (
                   SELECT MIN(tp.fecha)
                   FROM transaccion_puntos tp
                   WHERE tp.compra = c.num
                     AND tp.movimiento > 0
                     AND tp.version_recompensa IS NULL
               ) AS fecha
        FROM compra c WHERE c.num = %s
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

def buscar_compra_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_compra(conexion, num)

def obtener_compras_de_membresia(num_membresia):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT num FROM compra WHERE membresia=%s ORDER BY num", (num_membresia,))
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_compra(conexion, num) for num in numeros]

def obtener_compras_de_usuario(num_usuario):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM compra WHERE usuario=%s ORDER BY num",
                (num_usuario,),
            )
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_compra(conexion, num) for num in numeros]

def _consulta_transaccion_puntos(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM transaccion_puntos WHERE num=%s", (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_transaccion_puntos(
        fila,
        _consulta_compra(conexion, fila["compra"]) if fila["compra"] else None,
        _consulta_version_recompensa(conexion, fila["version_recompensa"])
        if fila["version_recompensa"] else None,
        _consulta_membresia(conexion, fila["membresia"]),
    )

def obtener_transacciones_de_miembro(num_miembro):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT tp.num FROM transaccion_puntos tp "
                "JOIN membresia m ON m.num=tp.membresia WHERE m.miembro=%s "
                "ORDER BY tp.fecha,tp.num", (num_miembro,),
            )
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_transaccion_puntos(conexion, num) for num in numeros]

def obtener_saldo_de_miembro(num_miembro):
    transacciones = obtener_transacciones_de_miembro(num_miembro)
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo if transacciones else 0

def _consulta_transaccion_cashback(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM transaccion_cashback WHERE num=%s", (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_transaccion_cashback(
        fila,
        _consulta_compra(conexion, fila["compra"]) if fila["compra"] else None,
        _consulta_membresia(conexion, fila["membresia"]),
    )

def obtener_transacciones_cashback_de_membresia(num_membresia):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM transaccion_cashback WHERE membresia=%s "
                "ORDER BY fecha,num", (num_membresia,),
            )
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_transaccion_cashback(conexion, num) for num in numeros]

def obtener_saldo_cashback_de_membresia(num_membresia):
    transacciones = obtener_transacciones_cashback_de_membresia(num_membresia)
    if not transacciones:
        from decimal import Decimal
        return Decimal("0")
    return max(transacciones, key=lambda transaccion: (transaccion.fecha, transaccion.num)).saldo
