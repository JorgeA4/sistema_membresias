
from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_recompensa,
    mapear_version_recompensa,
)

# consulta una recompensa usando una conexion existente
def _obtener_recompensa_conexion(conexion, codigo):
    consulta = """
        SELECT *
        FROM recompensa
        WHERE codigo = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (codigo,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_recompensa(fila)

# consulta una versin de recompensa y su recompensa
def _consulta_version_recompensa(conexion, num):
    consulta = """
        SELECT *
        FROM version_recompensa
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_version_recompensa(
        fila, _obtener_recompensa_conexion(conexion, fila["recompensa"])
    )

# consulta una recompensa por su codigo
def buscar_recompensa_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_recompensa_conexion(conexion, codigo)

# Consulta todas las recompensas ordenadas por codigo
def obtener_todas_las_recompensas():
    consulta = """
        SELECT codigo
        FROM recompensa
        ORDER BY codigo
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            filas = obtener_filas(cursor)
            lista_codigos = [fila["codigo"] for fila in filas]
        return [
            _obtener_recompensa_conexion(conexion, codigo)
            for codigo in lista_codigos
        ]

# consulta las versiones de una recompensa.
def obtener_versiones_de_recompensa(codigo_recompensa):
    consulta = """
        SELECT num
        FROM version_recompensa
        WHERE recompensa = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (codigo_recompensa,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_version_recompensa(conexion, num)
            for num in lista_numeros
        ]

# consulta una version de recompensa por su numero
def buscar_version_recompensa_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_version_recompensa(conexion, num)

# consuta la version vigente de una recompensa
def buscar_version_recompensa_vigente(codigo_recompensa):
    consulta = """
        SELECT num
        FROM version_recompensa
        WHERE recompensa = %s
        AND CURDATE() BETWEEN fecha_inicio AND fecha_final
        ORDER BY num DESC
        LIMIT 1
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (codigo_recompensa,))
            fila = obtener_fila(cursor)
        if fila is None:
            return None
        return _consulta_version_recompensa(conexion, fila["num"])
