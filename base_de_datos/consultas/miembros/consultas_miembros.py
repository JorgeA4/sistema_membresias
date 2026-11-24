"""Acceso persistente de miembros."""

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

from base_de_datos.consultas.usuarios.consultas_usuarios import _obtener_usuario_conexion

def _obtener_miembro_conexion(conexion, num):
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM miembro WHERE num = %s", (num,))
        return mapear_miembro(obtener_fila(cursor))

def buscar_miembro_por_correo(correo):
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM miembro WHERE correo = %s", (correo,))
            return mapear_miembro(obtener_fila(cursor))

def buscar_miembro_por_num(num):
    with usar_conexion() as conexion:
        return _obtener_miembro_conexion(conexion, num)

def obtener_todos_los_miembros():
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT num FROM miembro ORDER BY num")
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_obtener_miembro_conexion(conexion, num) for num in numeros]

def buscar_miembros(filtros):
    """Busca miembros usando filtros opcionales y su membresía actual."""
    consulta = """
        SELECT mi.num
        FROM miembro mi
        LEFT JOIN membresia me ON me.num = (
            SELECT m2.num
            FROM membresia m2
            WHERE m2.miembro = mi.num
            ORDER BY (m2.estado = 'CANCELADA'), m2.num DESC
            LIMIT 1
        )
        LEFT JOIN version_plan vp ON vp.num = me.version_plan_actual
        WHERE 1 = 1
    """
    parametros = []
    filtros_texto = (
        ("nombre", "mi.nombre"),
        ("primer_apellido", "mi.primer_apellido"),
        ("correo", "mi.correo"),
        ("telefono", "mi.telefono"),
    )
    for clave, columna in filtros_texto:
        valor = filtros.get(clave)
        if valor:
            consulta += f" AND {columna} LIKE %s"
            parametros.append(f"%{valor}%")

    if filtros.get("estado"):
        consulta += " AND me.estado = %s"
        parametros.append(filtros["estado"])
    if filtros.get("plan"):
        consulta += " AND vp.plan = %s"
        parametros.append(filtros["plan"])
    elif filtros.get("version_plan_actual"):
        consulta += " AND me.version_plan_actual = %s"
        parametros.append(filtros["version_plan_actual"])
    consulta += " ORDER BY mi.num"

    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(consulta, parametros)
            numeros = [fila["num"] for fila in obtener_filas(cursor)]
        return [_obtener_miembro_conexion(conexion, num) for num in numeros]

def tiene_historial_miembro(num):
    """Indica si el miembro tiene al menos una membresía registrada."""
    with usar_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM membresia WHERE miembro=%s) "
                "AS tiene_historial",
                (num,),
            )
            return bool(obtener_fila(cursor)["tiene_historial"])
