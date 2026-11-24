"""Lecturas de miembros desde la base de datos."""
from base_de_datos.consultas import _persistencia as bd

buscar_miembro_por_correo = bd.buscar_miembro_por_correo
buscar_miembro_por_num = bd.buscar_miembro_por_num
obtener_todos_los_miembros = bd.obtener_todos_los_miembros
buscar_miembros = bd.buscar_miembros
tiene_historial_miembro = bd.tiene_historial_miembro
