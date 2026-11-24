"""Lecturas de membresías y renovaciones desde la base de datos."""
from base_de_datos.consultas import _persistencia as bd

buscar_membresia_por_num = bd.buscar_membresia_por_num
buscar_membresia_de_miembro = bd.buscar_membresia_de_miembro
obtener_membresias_de_miembro = bd.obtener_membresias_de_miembro
obtener_renovaciones_de_membresia = bd.obtener_renovaciones_de_membresia
