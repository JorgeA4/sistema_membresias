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

def guardar_usuario(usuario):
    with usar_conexion() as conexion:
        valores = (
            usuario.nombre, usuario.primer_apellido, usuario.segundo_apellido,
            usuario.telefono, usuario.correo, usuario.contraseña,
            usuario.fecha_registro, usuario.rol.codigo,
        )
        with conexion.cursor() as cursor:
            if usuario.num is None:
                cursor.execute(
                    "INSERT INTO usuario (nombre, primer_apellido, "
                    "segundo_apellido, telefono, correo, `contraseña`, "
                    "fecha_registro, rol) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    valores,
                )
                usuario.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE usuario SET nombre=%s, primer_apellido=%s, "
                    "segundo_apellido=%s, telefono=%s, correo=%s, "
                    "`contraseña`=%s, fecha_registro=%s, rol=%s WHERE num=%s",
                    valores + (usuario.num,),
                )

def eliminar_usuario(num):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM usuario WHERE num = %s", (num,))
