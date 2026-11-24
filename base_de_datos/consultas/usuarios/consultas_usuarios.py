"""Acceso persistente de usuarios."""

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

def _obtener_rol_conexion(conexion, codigo):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM rol WHERE codigo = %s", (codigo,))
        return mapear_rol(obtener_fila(cursor))

def _obtener_usuario_conexion(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM usuario WHERE num = %s", (num,))
        fila = obtener_fila(cursor)
    return mapear_usuario(fila, _obtener_rol_conexion(conexion, fila["rol"])) if fila else None

def buscar_usuario_por_correo(correo):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
            fila = obtener_fila(cursor)
        return mapear_usuario(fila, _obtener_rol_conexion(conexion, fila["rol"])) if fila else None

def buscar_usuario_por_num(num):
    with usar_conexion() as conexion:
        return _obtener_usuario_conexion(conexion, num)

def obtener_todos_los_usuarios():
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT num FROM usuario ORDER BY num")
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_obtener_usuario_conexion(conexion, num) for num in numeros]

def tiene_historial_usuario(num):
    """Indica si el usuario tiene al menos una compra registrada."""
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM compra WHERE usuario=%s) "
                "AS tiene_historial",
                (num,),
            )
            return bool(obtener_fila(cursor)["tiene_historial"])

def buscar_rol_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_rol_conexion(conexion, codigo)

def obtener_todos_los_roles():
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM rol ORDER BY codigo")
            return [mapear_rol(fila) for fila in obtener_filas(cursor)]
