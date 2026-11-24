"""Lecturas de usuarios y roles desde la base de datos."""
from base_de_datos.consultas import _persistencia as bd

buscar_usuario_por_correo = bd.buscar_usuario_por_correo
buscar_usuario_por_num = bd.buscar_usuario_por_num
obtener_todos_los_usuarios = bd.obtener_todos_los_usuarios
tiene_historial_usuario = bd.tiene_historial_usuario
buscar_rol_por_codigo = bd.buscar_rol_por_codigo
obtener_todos_los_roles = bd.obtener_todos_los_roles
