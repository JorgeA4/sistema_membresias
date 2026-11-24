"""Acceso persistente de membresias."""

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

from base_de_datos.consultas.miembros.consultas_miembros import _obtener_miembro_conexion
from base_de_datos.consultas.planes.consultas_planes import _consulta_version_plan

def _consulta_membresia(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM membresia WHERE num = %s", (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_membresia(
        fila,
        _obtener_miembro_conexion(conexion, fila["miembro"]),
        _consulta_version_plan(conexion, fila["version_plan_actual"])
        if fila["version_plan_actual"] is not None else None,
    )

def _consulta_renovacion(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM renovacion WHERE num=%s", (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_renovacion(
        fila, _consulta_membresia(conexion, fila["membresia"]),
        _consulta_version_plan(conexion, fila["version_plan_comprado"]),
    )

def buscar_membresia_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_membresia(conexion, num)

def buscar_membresia_de_miembro(num_miembro):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM membresia WHERE miembro=%s "
                "ORDER BY (estado = 'CANCELADA'), num DESC LIMIT 1",
                (num_miembro,),
            )
            fila = obtener_fila(cursor)
        return _consulta_membresia(conexion, fila["num"]) if fila else None

def obtener_membresias_de_miembro(num_miembro):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM membresia WHERE miembro=%s ORDER BY num",
                (num_miembro,),
            )
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_membresia(conexion, num) for num in numeros]


def obtener_renovaciones_de_membresia(num_membresia):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM renovacion WHERE membresia=%s ORDER BY num",
                (num_membresia,),
            )
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_renovacion(conexion, num) for num in numeros]
