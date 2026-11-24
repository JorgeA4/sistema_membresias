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

def guardar_recompensa(recompensa):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO recompensa (codigo,nombre,descripcion) VALUES "
                "(%s,%s,%s) ON DUPLICATE KEY UPDATE nombre=%s, descripcion=%s",
                (recompensa.codigo, recompensa.nombre, recompensa.descripcion,
                 recompensa.nombre, recompensa.descripcion),
            )

def eliminar_recompensa(codigo):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM recompensa WHERE codigo=%s", (codigo,))

def guardar_version_recompensa(version_recompensa):
    with usar_conexion() as conexion:
        valores = (
            version_recompensa.fecha_inicio, version_recompensa.fecha_final,
            version_recompensa.costo_puntos, version_recompensa.limite_canjes,
            version_recompensa.recompensa.codigo,
        )
        with conexion.cursor() as cursor:
            if version_recompensa.num is None:
                cursor.execute(
                    "INSERT INTO version_recompensa "
                    "(fecha_inicio,fecha_final,costo_puntos,limite_canjes,recompensa) "
                    "VALUES (%s,%s,%s,%s,%s)", valores,
                )
                object.__setattr__(version_recompensa, "num", cursor.lastrowid)
            else:
                cursor.execute(
                    "UPDATE version_recompensa SET fecha_inicio=%s, "
                    "fecha_final=%s, costo_puntos=%s, limite_canjes=%s, "
                    "recompensa=%s WHERE num=%s", valores + (version_recompensa.num,),
                )

def eliminar_version_recompensa(num):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM version_recompensa WHERE num=%s", (num,))
