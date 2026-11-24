"""Acceso persistente de planes."""

from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_configuracion_cashback,
    mapear_configuracion_descuento,
    mapear_configuracion_puntos,
    mapear_plan,
    mapear_version_plan,
)

# Consulta un plan usando una conexión existente.
# Consulta un plan usando una conexión existente.
def _obtener_plan_conexion(conexion, codigo):
    consulta = """
        SELECT *
        FROM plan
        WHERE codigo = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (codigo,))
        return mapear_plan(obtener_fila(cursor))

# Consulta una versión de plan y sus configuraciones.
# Consulta una versión de plan y sus configuraciones.
def _consulta_version_plan(conexion, num):
    consulta = """
        SELECT
            vp.num,
            vp.fecha_inicio,
            vp.fecha_final,
            vp.precio,
            vp.plazo_meses,
            vp.aplica_en,
            vp.plan,
            vp.config_cashback,
            vp.config_puntos,
            vp.config_descuento,
            vp.version_base_de_promo,
            cc.num AS config_cashback_num,
            cc.porcentaje AS config_cashback_porcentaje,
            cc.limite_min_mensual AS config_cashback_limite,
            cp.num AS config_puntos_num,
            cp.porcentaje AS config_puntos_porcentaje,
            cp.vigencia_meses AS config_puntos_vigencia,
            cd.num AS config_descuento_num,
            cd.porcentaje AS config_descuento_porcentaje,
            cd.monto_minimo AS config_descuento_minimo
        FROM
            version_plan vp
        JOIN plan p ON p.codigo = vp.plan
        LEFT JOIN config_cashback cc ON cc.num = vp.config_cashback
        LEFT JOIN config_puntos cp ON cp.num = vp.config_puntos
        LEFT JOIN config_descuento cd ON cd.num = vp.config_descuento
        WHERE
            vp.num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    plan = _obtener_plan_conexion(conexion, fila["plan"])
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT dia_semana
            FROM dia_aplicable_desc
            WHERE config_descuento = %s
            ORDER BY dia_semana
            """,
            (fila["config_descuento_num"],),
        )
        dias = [registro["dia_semana"] for registro in obtener_filas(cursor)]
    version_base = None
    if fila["version_base_de_promo"] is not None:
        version_base = _consulta_version_plan(
            conexion,
            fila["version_base_de_promo"],
        )
    return mapear_version_plan(
        fila,
        plan,
        mapear_configuracion_cashback(fila),
        mapear_configuracion_puntos(fila),
        mapear_configuracion_descuento(fila, dias),
        version_base,
    )

# Consulta un plan por su código.
def buscar_plan_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_plan_conexion(conexion, codigo)

# Consulta todos los planes ordenados por código.
def obtener_todos_los_planes():
    consulta = """
        SELECT codigo
        FROM plan
        ORDER BY codigo
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            codigos = [fila["codigo"] for fila in obtener_filas(cursor)]
        return [_obtener_plan_conexion(conexion, codigo) for codigo in codigos]

# Consulta las versiones de un plan.
def obtener_versiones_de_plan(codigo_plan):
    consulta = """
        SELECT num
        FROM version_plan
        WHERE plan = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (codigo_plan,))
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_consulta_version_plan(conexion, num) for num in numeros]

# Consulta una versión de plan por su número.
def buscar_version_plan_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_version_plan(conexion, num)

# Consulta la versión vigente de un plan.
def buscar_version_plan_vigente(codigo_plan):
    consulta = """
        SELECT num
        FROM version_plan
        WHERE plan = %s
        AND CURDATE() BETWEEN fecha_inicio AND fecha_final
        ORDER BY num DESC
        LIMIT 1
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (codigo_plan,))
            fila = obtener_fila(cursor)
        if fila is None:
            return None
        return _consulta_version_plan(conexion, fila["num"])
