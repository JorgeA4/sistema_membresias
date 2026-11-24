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

def guardar_membresia(membresia):
    with usar_conexion() as conexion:
        valores = (
            membresia.fecha_contratacion, membresia.estado.value,
            membresia.miembro.num,
            membresia.version_plan_actual.num
            if membresia.version_plan_actual is not None else None,
        )
        with conexion.cursor() as cursor:
            if membresia.num is None:
                cursor.execute(
                    "INSERT INTO membresia "
                    "(fecha_contratacion, estado, miembro, version_plan_actual) "
                    "VALUES (%s,%s,%s,%s)", valores,
                )
                membresia.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE membresia SET fecha_contratacion=%s, estado=%s, "
                    "miembro=%s, version_plan_actual=%s WHERE num=%s",
                    valores + (membresia.num,),
                )

def guardar_renovacion(renovacion):
    with usar_conexion() as conexion:
        valores = (
            renovacion.fecha_pago, renovacion.monto_pagado,
            renovacion.fecha_inicio_periodo, renovacion.fecha_fin_periodo,
            renovacion.membresia.num, renovacion.version_plan_comprado.num,
        )
        with conexion.cursor() as cursor:
            if renovacion.num is None:
                cursor.execute(
                    "INSERT INTO renovacion (fecha_pago,monto_pagado,"
                    "fecha_inicio_periodo,fecha_fin_periodo,membresia,version_plan_comprado) "
                    "VALUES (%s,%s,%s,%s,%s,%s)", valores,
                )
                renovacion.num = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE renovacion SET fecha_pago=%s,monto_pagado=%s,"
                    "fecha_inicio_periodo=%s,fecha_fin_periodo=%s,membresia=%s,"
                    "version_plan_comprado=%s WHERE num=%s",
                    valores + (renovacion.num,),
                )
