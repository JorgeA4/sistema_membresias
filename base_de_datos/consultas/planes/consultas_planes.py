"""Lecturas de planes y sus versiones desde la base de datos."""
from base_de_datos.consultas import _persistencia as bd

buscar_plan_por_codigo = bd.buscar_plan_por_codigo
obtener_todos_los_planes = bd.obtener_todos_los_planes
obtener_versiones_de_plan = bd.obtener_versiones_de_plan
buscar_version_plan_por_num = bd.buscar_version_plan_por_num
buscar_version_plan_vigente = bd.buscar_version_plan_vigente
