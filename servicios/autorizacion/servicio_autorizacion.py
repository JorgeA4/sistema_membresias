from clases.membresia import Membresia
from clases.miembro import Miembro
from clases.usuario import Usuario


def requiere_administrador(usuario: Usuario) -> None:
    _verificar_usuario(usuario)
    if not _tiene_rol(usuario, "ADM", "administrador"):
        raise PermissionError("Se requiere el rol Administrador.")


def requiere_operador_compra(usuario: Usuario) -> None:
    _verificar_usuario(usuario)
    if not _tiene_rol(usuario, "ADM", "administrador", "CAJ", "cajero"):
        raise PermissionError("El usuario no puede registrar compras.")


def requiere_administrador_o_propietario(
    actor: Usuario | Miembro,
    membresia: Membresia,
) -> None:
    if isinstance(actor, Usuario):
        requiere_administrador(actor)
        return

    if isinstance(actor, Miembro) and actor.num == membresia.miembro.num:
        return

    raise PermissionError("No tiene permiso para operar sobre esta membresía.")


def _verificar_usuario(usuario: Usuario) -> None:
    if not isinstance(usuario, Usuario):
        raise PermissionError("Se requiere un usuario autenticado.")
    if usuario.rol is None:
        raise PermissionError("El usuario no tiene un rol asignado.")


def _tiene_rol(usuario: Usuario, *roles: str) -> bool:
    valores = {rol.casefold() for rol in roles}
    return (
        usuario.rol.codigo.casefold() in valores
        or usuario.rol.nombre.casefold() in valores
    )
