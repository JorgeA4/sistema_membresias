"""Validadores interactivos de miembros."""


def crear_validador_correo(obtener_miembros, identidad: dict):
    def validar(valor, valores):
        if any(
            miembro.correo.casefold() == valor.strip().casefold()
            for miembro in obtener_miembros(identidad)
        ):
            return "El correo ya está registrado."

    return validar
