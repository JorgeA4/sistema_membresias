"""Acceso persistente de miembros."""

from base_de_datos.ejecutor import (
    ejecutar_una,
    obtener_fila,
    obtener_filas,
    usar_conexion,
)
from base_de_datos.mapeadores import (
    mapear_miembro,
)


# Consulta un miembro usando una conexión existente.
def _obtener_miembro_conexion(conexion, num):
    # Consulta un miembro usando una conexión existente.
    consulta = """
        SELECT *
        FROM miembro
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        return mapear_miembro(obtener_fila(cursor))

# Consulta un miembro por su correo electrónico.
def buscar_miembro_por_correo(correo):
    consulta = """
        SELECT *
        FROM miembro
        WHERE correo = %s
    """
    fila = ejecutar_una(consulta, (correo,))
    if fila is None:
        return None
    return mapear_miembro(fila)

# Consulta un miembro por su número.
def buscar_miembro_por_num(num):
    with usar_conexion() as conexion:
        return _obtener_miembro_conexion(conexion, num)

# Consulta todos los miembros ordenados por número.
def obtener_todos_los_miembros():
    consulta = """
        SELECT num
        FROM miembro
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_obtener_miembro_conexion(conexion, num) for num in numeros]

# Comprueba si un miembro tiene membresías registradas.
# Comprueba si un miembro tiene membresías registradas.
def tiene_historial_miembro(num):
    """Indica si el miembro tiene al menos una membresía registrada."""
    consulta = """
        SELECT EXISTS(
            SELECT 1
            FROM membresia
            WHERE miembro = %s
        ) AS tiene_historial
    """
    fila = ejecutar_una(consulta, (num,))
    return bool(fila["tiene_historial"])
