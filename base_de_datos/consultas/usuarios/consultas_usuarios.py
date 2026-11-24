
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

# consulta un rol usando una conexion existente
def _obtener_rol_conexion(conexion, codigo):
    consulta = """
        SELECT *
        FROM rol
        WHERE codigo = %s
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (codigo,))
        fila = obtener_fila(cursor)
    if fila is None:
        return None
    return mapear_rol(fila)

# consulta un usuario usando una conexion existente
def _obtener_usuario_conexion(conexion, num):
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

# consulta un usuario por su correo electronico
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

# consulta un usuario por su numero
def buscar_usuario_por_num(num):
    with usar_conexion() as conexion:
        return _obtener_usuario_conexion(conexion, num)

# consulta todos los usuarios ordenados por numero
def obtener_todos_los_usuarios():
    consulta = """
        SELECT num
        FROM usuario
        ORDER BY num
    """
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            filas = obtener_filas(cursor)
            lista_numeros = [fila["num"] for fila in filas]
        return [
            _obtener_usuario_conexion(conexion, num)
            for num in lista_numeros
        ]

# comprueba si un usuario tiene compras registradas
def tiene_historial_usuario(num):
    consulta = """
        SELECT EXISTS(
            SELECT 1
            FROM compra
            WHERE usuario = %s
        ) AS tiene_historial
    """
    fila = ejecutar_una(consulta, (num,))
    return bool(fila["tiene_historial"])

# consulta un rol por su codigo
def buscar_rol_por_codigo(codigo):
    with usar_conexion() as conexion:
        return _obtener_rol_conexion(conexion, codigo)

# consulta todos los roles ordenados por codigo
def obtener_todos_los_roles():
    consulta = """
        SELECT *
        FROM rol
        ORDER BY codigo
    """
    filas = ejecutar_varias(consulta)
    return [mapear_rol(fila) for fila in filas]
