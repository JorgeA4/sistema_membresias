"""Validadores interactivos de usuarios administrativos."""


def mostrar_contexto_usuario(valores: dict) -> list[str]:
    """Devuelve el usuario seleccionado para el banner."""
    usuario = valores.get("_usuario")
    if usuario is None:
        return ["Usuario:", "Nombre:"]
    return [
        f"Usuario: {usuario.num}",
        f"Nombre: {usuario.nombre} {usuario.primer_apellido}",
    ]


def crear_validador_usuario(obtener_usuario, identidad: dict):
    def validar(valor, valores):
        usuario = obtener_usuario(identidad, int(valor))
        if usuario is None:
            return "El usuario no existe."
        valores["_usuario"] = usuario

    return validar


def crear_validador_correo(obtener_usuarios, identidad: dict):
    def validar(valor, valores):
        if any(
            usuario.correo.casefold() == valor.strip().casefold()
            for usuario in obtener_usuarios(identidad)
        ):
            return "El correo ya está registrado."

    return validar
