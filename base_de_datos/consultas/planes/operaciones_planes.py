"""Operaciones de persistencia de planes y sus versiones."""
from base_de_datos.consultas import _persistencia as bd

guardar_plan = bd.guardar_plan
eliminar_plan = bd.eliminar_plan
guardar_version_plan = bd.guardar_version_plan
eliminar_version_plan = bd.eliminar_version_plan
