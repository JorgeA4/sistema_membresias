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
from base_de_datos.consultas.usuarios.consultas_usuarios import _obtener_usuario_conexion

def guardar_compra(compra):
    with usar_conexion() as conexion:
        valores = (
            compra.monto_base, compra.porcentaje_descuento,
            compra.descuento_nominal, compra.cashback_aplicado,
            compra.monto_final, compra.membresia.num, compra.usuario.num,
        )
        with conexion.cursor() as cursor:
            if compra.num is None:
                cursor.execute(
                    "INSERT INTO compra (monto_base,porcentaje_descuento,"
                    "descuento_nominal,cashback_aplicado,monto_final,membresia,usuario) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", valores,
                )
                compra.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE compra SET monto_base=%s, porcentaje_descuento=%s, "
                    "descuento_nominal=%s, cashback_aplicado=%s, monto_final=%s, "
                    "membresia=%s, usuario=%s WHERE num=%s",
                    valores + (compra.num,),
                )

def guardar_transaccion_puntos(transaccion):
    with usar_conexion() as conexion:
        valores = (
            transaccion.movimiento, transaccion.saldo, transaccion.fecha,
            transaccion.concepto, transaccion.compra.num
            if transaccion.compra else None,
            transaccion.version_recompensa.num
            if transaccion.version_recompensa else None,
            transaccion.membresia.num,
        )
        with conexion.cursor() as cursor:
            if transaccion.num is None:
                cursor.execute(
                    "INSERT INTO transaccion_puntos "
                    "(movimiento,saldo,fecha,concepto,compra,version_recompensa,membresia) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)", valores,
                )
                transaccion.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE transaccion_puntos SET movimiento=%s,saldo=%s,fecha=%s,"
                    "concepto=%s,compra=%s,version_recompensa=%s,membresia=%s WHERE num=%s",
                    valores + (transaccion.num,),
                )

def guardar_transaccion_cashback(transaccion):
    with usar_conexion() as conexion:
        valores = (
            transaccion.monto, transaccion.saldo, transaccion.fecha,
            transaccion.concepto, transaccion.compra.num
            if transaccion.compra else None, transaccion.membresia.num,
        )
        with conexion.cursor() as cursor:
            if transaccion.num is None:
                cursor.execute(
                    "INSERT INTO transaccion_cashback "
                    "(monto,saldo,fecha,concepto,compra,membresia) "
                    "VALUES (%s,%s,%s,%s,%s,%s)", valores,
                )
                transaccion.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE transaccion_cashback SET monto=%s,saldo=%s,fecha=%s,"
                    "concepto=%s,compra=%s,membresia=%s WHERE num=%s",
                    valores + (transaccion.num,),
                )
