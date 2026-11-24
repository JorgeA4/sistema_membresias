"""Acceso persistente de planes."""

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

def _guardar_configuracion(conexion, configuracion, tabla, columnas, valores):
    if configuracion is None:
        return None
    with conexion.cursor() as cursor:
        if configuracion.num is None:
            nombres = ", ".join(columnas)
            marcadores = ", ".join(["%s"] * len(valores))
            cursor.execute(
                f"INSERT INTO {tabla} ({nombres}) VALUES ({marcadores})", valores
            )
            configuracion.num = cursor.lastrowid
        else:
            asignaciones = ", ".join(f"{columna}=%s" for columna in columnas)
            cursor.execute(
                f"UPDATE {tabla} SET {asignaciones} WHERE num=%s",
                valores + (configuracion.num,),
            )
    return configuracion.num

def guardar_plan(plan):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO plan (codigo, nombre, descripcion) VALUES "
                "(%s, %s, %s) ON DUPLICATE KEY UPDATE nombre=%s, descripcion=%s",
                (plan.codigo, plan.nombre, plan.descripcion, plan.nombre, plan.descripcion),
            )

def eliminar_plan(codigo):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM plan WHERE codigo = %s", (codigo,))

def guardar_version_plan(version_plan):
    with usar_conexion() as conexion:
        cashback = version_plan.config_cashback
        puntos = version_plan.config_puntos
        descuento = version_plan.config_descuento
        id_cashback = _guardar_configuracion(
            conexion, cashback, "config_cashback",
            ("porcentaje", "limite_min_mensual"),
            (cashback.porcentaje, cashback.limite_min_mensual) if cashback else (),
        )
        id_puntos = _guardar_configuracion(
            conexion, puntos, "config_puntos", ("porcentaje", "vigencia_meses"),
            (puntos.porcentaje, puntos.vigencia_meses) if puntos else (),
        )
        id_descuento = _guardar_configuracion(
            conexion, descuento, "config_descuento",
            ("porcentaje", "monto_minimo"),
            (descuento.porcentaje, descuento.monto_minimo) if descuento else (),
        )
        if descuento is not None:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM dia_aplicable_desc WHERE config_descuento=%s",
                    (id_descuento,),
                )
                for dia in descuento.dias_aplicables:
                    valor = dia.dia_semana if hasattr(dia, "dia_semana") else dia
                    cursor.execute(
                        "INSERT INTO dia_aplicable_desc "
                        "(config_descuento, dia_semana) VALUES (%s, %s)",
                        (id_descuento, valor),
                    )
        base = version_plan.version_base_de_promo
        id_base = base.num if base is not None else None
        valores = (
            version_plan.fecha_inicio, version_plan.fecha_final,
            version_plan.precio, version_plan.plazo_meses,
            version_plan.aplica_en.value, version_plan.plan.codigo,
            id_cashback, id_puntos, id_descuento, id_base,
        )
        with conexion.cursor() as cursor:
            if version_plan.num is None:
                cursor.execute(
                    "INSERT INTO version_plan "
                    "(fecha_inicio, fecha_final, precio, plazo_meses, aplica_en, "
                    "plan, config_cashback, config_puntos, config_descuento, "
                    "version_base_de_promo) VALUES "
                    "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", valores,
                )
                object.__setattr__(version_plan, "num", cursor.lastrowid)
            else:
                cursor.execute(
                    "UPDATE version_plan SET fecha_inicio=%s, fecha_final=%s, "
                    "precio=%s, plazo_meses=%s, aplica_en=%s, plan=%s, "
                    "config_cashback=%s, config_puntos=%s, config_descuento=%s, "
                    "version_base_de_promo=%s WHERE num=%s",
                    valores + (version_plan.num,),
                )

def eliminar_version_plan(num):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM version_plan WHERE num=%s", (num,))
