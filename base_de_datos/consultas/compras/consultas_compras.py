
from base_de_datos.ejecutor import obtener_fila, obtener_filas, usar_conexion
from base_de_datos.mapeadores import mapear_compra

from base_de_datos.consultas.membresias.consultas_membresias import _consulta_membresia
from base_de_datos.consultas.usuarios.consultas_usuarios import _obtener_usuario_conexion

# Consulta una compra y su fecha derivada
def _consulta_compra(conexion, num):
    consulta = """
        SELECT
            c.*,
            (
                SELECT MIN(tp.fecha)
                FROM transaccion_puntos AS tp
                WHERE tp.compra = c.num
                AND tp.movimiento > 0
                AND tp.version_recompensa IS NULL
            ) AS fecha
        FROM
            compra c
        WHERE
            c.num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_compra(
        fila, _consulta_membresia(conexion, fila["membresia"]),
        _obtener_usuario_conexion(conexion, fila["usuario"]),
    )

# consulta una compra por su numero
def buscar_compra_por_num(num):
    with usar_conexion() as conexion:
        return _consulta_compra(conexion, num)

#consulta las compras de una membresia
def obtener_compras_de_membresia(num_membresia):
    consulta = """
        SELECT num
        FROM compra
        WHERE membresia = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_membresia,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_compra(conexion, num)
            for num in lista_numeros
        ]

# consulta las compras registradas por un usuario
def obtener_compras_de_usuario(num_usuario):
    consulta = """
        SELECT num
        FROM compra
        WHERE usuario = %s
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (num_usuario,))
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _consulta_compra(conexion, num)
            for num in lista_numeros
        ]
