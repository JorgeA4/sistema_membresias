
from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_configuracion_cashback,
    mapear_configuracion_descuento,
    mapear_configuracion_puntos,
    mapear_plan,
    mapear_version_plan,
)

# consulta un plan usando una conexion existente
def _obtener_plan_conexion(conexion, codigo):
    consulta = """
        SELECT *
        FROM plan
        WHERE codigo = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (codigo,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_plan(fila)

# consulta una versipn de plan y sus configuraciones
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
        filas = obtener_filas(cursor)
        lista_dias = [fila["dia_semana"] for fila in filas]
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
        mapear_configuracion_descuento(fila, lista_dias),
        version_base,
    )

# consuta un plan por su codigo
def buscar_plan_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_plan_conexion(conexion, codigo)

# consulta todos los planes ordenados por codigos
def obtener_todos_los_planes():
    consulta = """
        SELECT codigo
        FROM plan
        ORDER BY codigo
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            filas = obtener_filas(cursor)
            lista_codigos = [fila["codigo"] for fila in filas]
        return [
            _obtener_plan_conexion(conexion, codigo)
            for codigo in lista_codigos
        ]

# consulta las versiones de un plan
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
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_version_plan(conexion, num)
            for num in lista_numeros
        ]

#  consulta una version de plan por su numero
def buscar_version_plan_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_version_plan(conexion, num)

# consulta la version vigente de un plan.
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
