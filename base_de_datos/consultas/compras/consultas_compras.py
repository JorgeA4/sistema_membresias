"""Lecturas de compras y movimientos desde la base de datos."""
from base_de_datos.consultas import _persistencia as bd

buscar_compra_por_num = bd.buscar_compra_por_num
obtener_compras_de_membresia = bd.obtener_compras_de_membresia
obtener_compras_de_usuario = bd.obtener_compras_de_usuario
obtener_transacciones_de_miembro = bd.obtener_transacciones_de_miembro
obtener_saldo_de_miembro = bd.obtener_saldo_de_miembro
obtener_transacciones_cashback_de_membresia = bd.obtener_transacciones_cashback_de_membresia
obtener_saldo_cashback_de_membresia = bd.obtener_saldo_cashback_de_membresia
