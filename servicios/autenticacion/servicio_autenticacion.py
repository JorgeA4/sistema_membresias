import base_de_datos.consultas as bd
from clases.miembro import Miembro
from clases.usuario import Usuario
from utilidades.seguridad import verificar_contraseña


def autenticar_miembro(correo: str, contraseña: str) -> Miembro | None:
    if not correo or not contraseña:
        return None

    miembro = bd.buscar_miembro_por_correo(correo)
    if miembro and verificar_contraseña(contraseña, miembro.contraseña):
        return miembro
    return None


def autenticar_usuario(correo: str, contraseña: str) -> Usuario | None:
    if not correo or not contraseña:
        return None

    usuario = bd.buscar_usuario_por_correo(correo)
    if usuario and verificar_contraseña(contraseña, usuario.contraseña):
        return usuario
    return None
