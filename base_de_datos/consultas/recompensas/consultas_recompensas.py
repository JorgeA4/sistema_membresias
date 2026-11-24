"""Acceso persistente de recompensas."""

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

def _obtener_recompensa_conexion(conexion, codigo):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM recompensa WHERE codigo = %s", (codigo,))
        return mapear_recompensa(obtener_fila(cursor))

def _consulta_version_recompensa(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM version_recompensa WHERE num = %s", (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_version_recompensa(
        fila, _obtener_recompensa_conexion(conexion, fila["recompensa"])
    )

def buscar_recompensa_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_recompensa_conexion(conexion, codigo)

def obtener_todas_las_recompensas():
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT codigo FROM recompensa ORDER BY codigo")
            codigos = [fila["codigo"] for fila in obtener_filas(cursor)]
        return [_obtener_recompensa_conexion(conexion, codigo) for codigo in codigos]

def obtener_versiones_de_recompensa(codigo_recompensa):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM version_recompensa WHERE recompensa=%s ORDER BY num",
                (codigo_recompensa,),
            )
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_version_recompensa(conexion, num) for num in numeros]

def buscar_version_recompensa_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_version_recompensa(conexion, num)

def buscar_version_recompensa_vigente(codigo_recompensa):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT num FROM version_recompensa WHERE recompensa=%s "
                "AND CURDATE() BETWEEN fecha_inicio AND fecha_final "
                "ORDER BY num DESC LIMIT 1", (codigo_recompensa,),
            )
            fila = obtener_fila(cursor)
        return _consulta_version_recompensa(conexion, fila["num"]) if fila else None
