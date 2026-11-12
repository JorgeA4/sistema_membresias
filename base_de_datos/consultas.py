import mariadb
import sys
from datetime import datetime

from base_de_datos.consultas_simuladas import (
    # Miembro
    buscar_miembro_por_correo, #<
    buscar_miembro_por_num, #<
    obtener_todos_los_miembros, #<
    guardar_miembro, #<
    eliminar_miembro, #<
    # Usuario
    buscar_usuario_por_correo, #<
    buscar_usuario_por_num, #<
    obtener_todos_los_usuarios, #<
    guardar_usuario, #<
    eliminar_usuario, #<
    # Plan y VersionPlan
    buscar_plan_por_codigo, #<
    obtener_todos_los_planes, #<
    guardar_plan, #<
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
#Funciones de Miembro:
def buscar_miembro_por_correo(correo, conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM miembro WHERE correo = ?
    cursor.execute(consulta, (correo,))
    
    miembro = cursor.fetchone()
    return miembro

def buscar_miembro_por_num(num, conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM miembro WHERE num = ?
    cursor.execute(consulta, (num,))
    
    miembro = cursor.fetchone()
    return miembro

def obtener_todos_los_miembros(conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM miembro
    cursor.execute(consulta)
    
    miembro = cur.fetchall()
    return miembro

def guardar_miembro(conn, nombre, PrimerApell, telefono, correo, contraseña, rol, SegApell = None):
    cursor = conn.cursor()
    consulta = INSERT INTO usuario (nombre, PrimerApell, SegApell, telefono, correo, contraseña, rol) VALUES (?, ?, ?, ?, ?, ?, ?)
    fechaRegist = datetime.now()
    
    nuevo_miembro = (nombre, PrimerApell, SegApell, telefono, correo, contraseña, rol, fechaRegist)
    cursor = execute(consulta, nuevo_miembro)
    return nuevo_miembro

def eliminar_miembro(conn, num):
    cursor = conn.cursor()
    cursor.execute(DELETE FROM miembro WHERE num = ?, (num,))
    
    miembro = conn.commit()
    return miembro #Esto ultimo solo te muestra la nueva lista actualizada donde tu puedes verificar que en efecto, se elimino dicho miembro
    
#Funciones de Usuario:
def buscar_usuario_por_correo(correo, conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM usuario WHERE correo = ?
    cursor.execute(consulta, (correo,))
    
    usuario = cursor.fetchone()
    return usuario

def buscar_usuario_por_num(num, conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM usuario WHERE num = ?
    cursor.execute(consulta, (num,))
    
    usuario = cursor.fetchone()
    return usuario

def obtener_todos_los_usuarios(conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM usuario
    cursor.execute(consulta)
    
    usuario = cur.fetchall()
    return usuario

def guardar_usuario(conn, nombre, PrimerApell, telefono, correo, contraseña, rol, SegApell = None):
    cursor = conn.cursor()
    consulta = INSERT INTO usuario (nombre, PrimerApell, SegApell, telefono, correo, contraseña, rol) VALUES (?, ?, ?, ?, ?, ?, ?)
    
    nuevo_usuario = (nombre, PrimerApell, SegApell, telefono, correo, contraseña, rol)
    cursor = execute(consulta, nuevo_usuario)
    return nuevo_usuario

def eliminar_usuario(conn, num):
    cursor = conn.cursor()
    cursor.execute(DELETE FROM usuario WHERE num = ?, (num,))
    
    usuario = conn.commit()
    return usuario #Esto ultimo solo te muestra la nueva lista actualizada donde tu puedes verificar que en efecto, se elimino dicho usuario

#Funciones para Plan y VersionPlan
def buscar_plan_por_codigo(conn, num):
    cursor = conn.cursor()
    consulta = 
        SELECT id, codigo, nombre, descripcion, precio, duracion_dias
        FROM plan
        WHERE codigo = ?
        LIMIT 1;

    try:
        cursor.execute(consulta, (num,))
        resultado = cursor.fetchone()
        return resultado
    except mariadb.Error as e:
        return None #Esto es en caso de que no se pueda encontrar el codigo en la base de datos
    finally:
        cursor.close()

def obtener_todos_los_planes(conn):
    cursor = conn.cursor()
    consulta = SELECT * FROM plan
    cursor.execute(consulta)
    
    lista_planes = cur.fetchall()
    return lista_planes
