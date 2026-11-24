
from base_de_datos.ejecutor import (
    ejecutar_una,
    obtener_fila,
    obtener_filas,
    usar_conexion,
)
from base_de_datos.mapeadores import (
    mapear_miembro,
)


# consulta un miembro usando una conexipn existente
def _obtener_miembro_conexion(conexion, num):
    consulta = """
        SELECT *
        FROM miembro
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)

    if fila is None:
        return None

    return mapear_miembro(fila)

# consulta un miembro por su correo electronico
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

# consulta un miembro por su numero
def buscar_miembro_por_num(num):
    with usar_conexion() as conexion:
        return _obtener_miembro_conexion(conexion, num)

# consulta todos los miembros ordenados por numero.
def obtener_todos_los_miembros():
    consulta = """
        SELECT num
        FROM miembro
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _obtener_miembro_conexion(conexion, num)
            for num in lista_numeros
        ]

# comprueba si un miembro tiene membresias registradas
def tiene_historial_miembro(num):
    consulta = """
        SELECT EXISTS(
            SELECT 1
            FROM membresia
            WHERE miembro = %s
        ) AS tiene_historial
    """
    fila = ejecutar_una(consulta, (num,))
    return bool(fila["tiene_historial"])
