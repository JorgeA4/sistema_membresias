import base_de_datos.consultas as bd
from utilidades.seguridad import verificar_contraseña


def autenticar_miembro(correo: str, contraseña: str) -> dict | None:
    if not correo or not contraseña:
        return None

    miembro = bd.buscar_miembro_por_correo(correo)
    if miembro and verificar_contraseña(contraseña, miembro.contraseña):
        return {
            "tipo": "miembro",
            "num": miembro.num,
            "nombre": miembro.nombre,
        }
    return None


def autenticar_usuario(correo: str, contraseña: str) -> dict | None:
    if not correo or not contraseña:
        return None

    usuario = bd.buscar_usuario_por_correo(correo)
    if usuario and verificar_contraseña(contraseña, usuario.contraseña):
        return {
            "tipo": "usuario",
            "num": usuario.num,
            "nombre": usuario.nombre,
            "rol": usuario.rol.codigo,
            "rol_nombre": usuario.rol.nombre,
        }
    return None
