"""Lecturas de recompensas, versiones y canjes desde la base de datos."""
from base_de_datos.consultas import _persistencia as bd

buscar_recompensa_por_codigo = bd.buscar_recompensa_por_codigo
obtener_todas_las_recompensas = bd.obtener_todas_las_recompensas
obtener_versiones_de_recompensa = bd.obtener_versiones_de_recompensa
buscar_version_recompensa_por_num = bd.buscar_version_recompensa_por_num
buscar_version_recompensa_vigente = bd.buscar_version_recompensa_vigente
