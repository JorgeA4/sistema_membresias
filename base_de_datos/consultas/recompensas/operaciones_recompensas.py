"""Operaciones de persistencia de recompensas, versiones y canjes."""
from base_de_datos.consultas import _persistencia as bd

guardar_recompensa = bd.guardar_recompensa
eliminar_recompensa = bd.eliminar_recompensa
guardar_version_recompensa = bd.guardar_version_recompensa
eliminar_version_recompensa = bd.eliminar_version_recompensa
