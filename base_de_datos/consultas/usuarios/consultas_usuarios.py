"""Acceso persistente de usuarios."""

from base_de_datos.ejecutor import (
    ejecutar_una,
    ejecutar_varias,
    obtener_fila,
    obtener_filas,
    usar_conexion,
)
from base_de_datos.mapeadores import (
    mapear_rol,
    mapear_usuario,
)

# Consulta un rol usando una conexión existente.
# Consulta un rol usando una conexión existente.
def _obtener_rol_conexion(conexion, codigo):
    # Consulta un rol usando una conexión existente.
    consulta = """
        SELECT *
        FROM rol
        WHERE codigo = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (codigo,))
        return mapear_rol(obtener_fila(cursor))

# Consulta un usuario usando una conexión existente.
# Consulta un usuario usando una conexión existente.
def _obtener_usuario_conexion(conexion, num):
    # Consulta un usuario usando una conexión existente.
    consulta = """
        SELECT *
        FROM usuario
        WHERE num = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (num,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    rol = _obtener_rol_conexion(conexion, fila["rol"])
    return mapear_usuario(fila, rol)

# Consulta un usuario por su correo electrónico.
def buscar_usuario_por_correo(correo):
    consulta = """
        SELECT *
        FROM usuario
        WHERE correo = %s
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, (correo,))
            fila = obtener_fila(cursor)
        if fila is None:
            return None
        rol = _obtener_rol_conexion(conexion, fila["rol"])
        return mapear_usuario(fila, rol)

# Consulta un usuario por su número.
def buscar_usuario_por_num(num):
    with usar_conexion() as conexion:
        return _obtener_usuario_conexion(conexion, num)

# Consulta todos los usuarios ordenados por número.
def obtener_todos_los_usuarios():
    consulta = """
        SELECT num
        FROM usuario
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_obtener_usuario_conexion(conexion, num) for num in numeros]

# Comprueba si un usuario tiene compras registradas.
# Comprueba si un usuario tiene compras registradas.
def tiene_historial_usuario(num):
    """Indica si el usuario tiene al menos una compra registrada."""
    consulta = """
        SELECT EXISTS(
            SELECT 1
            FROM compra
            WHERE usuario = %s
        ) AS tiene_historial
    """
    fila = ejecutar_una(consulta, (num,))
    return bool(fila["tiene_historial"])

# Consulta un rol por su código.
def buscar_rol_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_rol_conexion(conexion, codigo)

# Consulta todos los roles ordenados por código.
def obtener_todos_los_roles():
    consulta = """
        SELECT *
        FROM rol
        ORDER BY codigo
    """
    filas = ejecutar_varias(consulta)
    return [mapear_rol(fila) for fila in filas]
