"""Acceso persistente de miembros."""

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

from base_de_datos.consultas.usuarios.consultas_usuarios import _obtener_usuario_conexion

def guardar_miembro(miembro):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            valores = (
                miembro.nombre, miembro.primer_apellido,
                miembro.segundo_apellido, miembro.telefono, miembro.correo,
                miembro.contraseña, miembro.fecha_registro,
            )
            if miembro.num is None:
                cursor.execute(
                    "INSERT INTO miembro "
                    "(nombre, primer_apellido, segundo_apellido, telefono, "
                    "correo, `contraseña`, fecha_registro) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)", valores,
                )
                miembro.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE miembro SET nombre=%s, primer_apellido=%s, "
                    "segundo_apellido=%s, telefono=%s, correo=%s, "
                    "`contraseña`=%s, fecha_registro=%s WHERE num=%s",
                    valores + (miembro.num,),
                )

def eliminar_miembro(num):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM miembro WHERE num = %s", (num,))
