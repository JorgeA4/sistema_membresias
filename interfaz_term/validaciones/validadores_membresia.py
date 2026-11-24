"""Validadores relacionados con membresías."""

from servicios.membresia.servicio_membresia import consultar_membresia


def crear_validador_membresia(identidad: dict, exigir_activa: bool = False):
    """Crea un validador que consulta y conserva una membresía en el contexto."""
    def validar(valor, valores):
        valores.pop("_membresia", None)
        membresia = consultar_membresia(identidad, int(valor))
        if membresia is None:
            return "La membresía no existe."
        if exigir_activa and membresia.estado.value != "ACTIVA":
            return "La membresía no está activa."
        valores["_membresia"] = membresia

    return validar


def crear_validador_membresia_para_renovacion(identidad: dict):
    """Valida una membresía que puede renovarse."""
    def validar(valor, valores):
        valores.pop("_membresia", None)
        membresia = consultar_membresia(identidad, int(valor))
        if membresia is None:
            return "La membresía no existe."
        if membresia.estado.value == "CANCELADA":
            return "La membresía está cancelada y requiere una nueva contratación."
        valores["_membresia"] = membresia

    return validar
