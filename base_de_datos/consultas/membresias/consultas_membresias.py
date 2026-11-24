
from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import (
    mapear_membresia,
    mapear_renovacion,
)

from base_de_datos.consultas.miembros.consultas_miembros import _obtener_miembro_conexion
from base_de_datos.consultas.planes.consultas_planes import _consulta_version_plan

#consulta una membresia y sus relaciones.
def _consulta_membresia(conexion, num):
    consulta = """
        SELECT *
        FROM membresia
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    version_plan = None
    if fila["version_plan_actual"] is not None:
        version_plan = _consulta_version_plan(
            conexion,
            fila["version_plan_actual"],
        )
    return mapear_membresia(
        fila,
        _obtener_miembro_conexion(conexion, fila["miembro"]),
        version_plan,
    )

# consulta una renovacion y sus relaciones
def _consulta_renovacion(conexion, num):
    consulta = """
        SELECT *
        FROM renovacion
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_renovacion(
        fila, _consulta_membresia(conexion, fila["membresia"]),
        _consulta_version_plan(conexion, fila["version_plan_comprado"]),
    )

# consulta una membresia por su numero.
def buscar_membresia_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_membresia(conexion, num)

# consulta la membresia principal de un miembro
def buscar_membresia_de_miembro(num_miembro):
    consulta = """
        SELECT num
        FROM membresia
        WHERE miembro = %s
        ORDER BY (estado = 'CANCELADA'), num DESC
        LIMIT 1
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_miembro,))
            fila = obtener_fila(cursor)
        if fila is None:
            return None
        return _consulta_membresia(conexion, fila["num"])

# consulta todas las membresias de un mimbro
def obtener_membresias_de_miembro(num_miembro):
    consulta = """
        SELECT num
        FROM membresia
        WHERE miembro = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_miembro,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_membresia(conexion, num)
            for num in lista_numeros
        ]


# consulta las renovaciones de una membresia
def obtener_renovaciones_de_membresia(num_membresia):
    consulta = """
        SELECT num
        FROM renovacion
        WHERE membresia = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_membresia,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_renovacion(conexion, num)
            for num in lista_numeros
        ]
