import mariadb
import sys

from base_de_datos.consultas_simuladas import (
    # Miembro
    buscar_miembro_por_correo, #F
    buscar_miembro_por_num, #F
    obtener_todos_los_miembros, #F
    guardar_miembro, #F
    eliminar_miembro, #F
    # Usuario
    buscar_usuario_por_correo,
    buscar_usuario_por_num,
    obtener_todos_los_usuarios,
    guardar_usuario,
    eliminar_usuario,
    # Plan y VersionPlan
    buscar_plan_por_codigo,
    obtener_todos_los_planes,
    guardar_plan,
    obtener_versiones_de_plan,
    buscar_version_plan_vigente,
    guardar_version_plan,
    # Membresia y AplicacionVersionPlan
    buscar_membresia_por_num,
    buscar_membresia_de_miembro,
    guardar_membresia,
    obtener_aplicaciones_de_membresia,
    guardar_aplicacion_version_plan,
    # Recompensa y VersionRecompensa
    buscar_recompensa_por_codigo,
    obtener_todas_las_recompensas,
    guardar_recompensa,
    obtener_versiones_de_recompensa,
    buscar_version_recompensa_vigente,
    guardar_version_recompensa,
    # Compra, Canje, Renovacion y TransaccionPuntos
    guardar_compra,
    guardar_canje,
    guardar_renovacion,
    obtener_renovaciones_de_membresia,
    guardar_transaccion_puntos,
    obtener_transacciones_de_miembro,
    obtener_saldo_de_miembro,
    # Rol
    buscar_rol_por_codigo,
    obtener_todos_los_roles,
)
#Funciones de Miembro
def buscar_miembro_por_correo(correo, conn):
    cursor = conn.cursor()
    consulta = "SELECT * FROM miembro WHERE correo = ?"
    cursor.execute(consulta, (correo,))
    
    miembro = cursor.fetchone()
    return miembro

def buscar_miembro_por_num(num, conn):
    cursor = conn.cursor()
    consulta = "SELECT * FROM miembro WHERE num = ?"
    cursor.execute(consulta, (num,))
    
    miembro = cursor.fetchone()
    return miembro

def obtener_todos_los_miembros(conn):
    cursor = conn.cursor()
    consulta = "SELECT * FROM miembro"
    cursor.execute(consulta)
    
    miembro = cur.fetchall()
    return miembro

def guardar_miembro(conn, nombre, PrimerApell, correo, SegApell = None):
    cursor = conn.cursor()
    consulta = "INSERT INTO miembro (nombre, PrimerApell, SegApell, correo) VALUES (?, ?, ?, ?)"
    
    nuevo_miembro = (nombre, PrimerApell, SegApell, correo)
    cursor = execute(consulta, nuevo_miembro)
    return nuevo_miembro

def eliminar_miembro(conn, num):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM miembro WHERE num = ?", (num,))
    
    miembro = conn.commit()
    return miembro
    
