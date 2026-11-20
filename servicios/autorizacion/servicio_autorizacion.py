import base_de_datos.consultas as bd
from clases.membresia import Membresia
from clases.usuario import Usuario
from utilidades.excepciones import OperacionNoPermitida


def requiere_administrador(identidad: dict) -> None:
    usuario = _obtener_usuario(identidad)
    _verificar_usuario(usuario)
    if not _tiene_rol(usuario, "ADM", "administrador"):
        raise OperacionNoPermitida("Se requiere el rol Administrador.")


def requiere_operador_compra(identidad: dict) -> Usuario:
    usuario = _obtener_usuario(identidad)
    _verificar_usuario(usuario)
    if not _tiene_rol(usuario, "ADM", "administrador", "CAJ", "cajero"):
        raise OperacionNoPermitida("El usuario no puede registrar compras.")
    return usuario


def requiere_operador_tienda(identidad: dict) -> Usuario:
    """Autoriza operaciones presenciales del administrador o cajero."""
    return requiere_operador_compra(identidad)


def requiere_administrador_o_propietario(
    identidad: dict,
    membresia: Membresia,
) -> None:
    if not isinstance(identidad, dict):
        raise OperacionNoPermitida("Se requiere una identidad autenticada.")
    if identidad.get("tipo") == "usuario":
        requiere_administrador(identidad)
        return

    if identidad.get("tipo") == "miembro":
        miembro = _obtener_miembro(identidad)
        if miembro.num == membresia.miembro.num:
            return

    raise OperacionNoPermitida("No tiene permiso para operar sobre esta membresía.")


def _verificar_usuario(usuario: Usuario) -> None:
    if not isinstance(usuario, Usuario):
        raise OperacionNoPermitida("Se requiere un usuario autenticado.")
    if usuario.rol is None:
        raise OperacionNoPermitida("El usuario no tiene un rol asignado.")


def _tiene_rol(usuario: Usuario, *roles: str) -> bool:
    valores = {rol.casefold() for rol in roles}
    return (
        usuario.rol.codigo.casefold() in valores
        or usuario.rol.nombre.casefold() in valores
    )


def _obtener_usuario(identidad: dict) -> Usuario:
    if not isinstance(identidad, dict):
        raise OperacionNoPermitida("Se requiere una identidad autenticada.")
    if identidad.get("tipo") != "usuario":
        raise OperacionNoPermitida("Se requiere un usuario autenticado.")

    usuario = bd.buscar_usuario_por_num(identidad.get("num"))
    if not isinstance(usuario, Usuario):
        raise OperacionNoPermitida("El usuario autenticado no existe.")
    return usuario


def _obtener_miembro(identidad: dict):
    if not isinstance(identidad, dict):
        raise OperacionNoPermitida("Se requiere una identidad autenticada.")

    miembro = bd.buscar_miembro_por_num(identidad.get("num"))
    if miembro is None:
        raise OperacionNoPermitida("El miembro autenticado no existe.")
    return miembro
