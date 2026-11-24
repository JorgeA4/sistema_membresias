"""Operaciones de persistencia de compras y movimientos."""
from base_de_datos.consultas import _persistencia as bd

guardar_compra = bd.guardar_compra
guardar_transaccion_puntos = bd.guardar_transaccion_puntos
guardar_transaccion_cashback = bd.guardar_transaccion_cashback
