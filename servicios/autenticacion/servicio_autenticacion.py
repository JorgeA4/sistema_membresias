import base_de_datos.consultas.miembros.consultas_miembros as consultas_miembros
import base_de_datos.consultas.usuarios.consultas_usuarios as consultas_usuarios
from utilidades.seguridad import verificar_contraseña


def autenticar_miembro(correo: str, contraseña: str) -> dict | None:
    if not correo or not contraseña:
        return None

    miembro = consultas_miembros.buscar_miembro_por_correo(correo)
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

    usuario = consultas_usuarios.buscar_usuario_por_correo(correo)
    if usuario and verificar_contraseña(contraseña, usuario.contraseña):
        return {
            "tipo": "usuario",
            "num": usuario.num,
            "nombre": usuario.nombre,
            "rol": usuario.rol.codigo,
            "rol_nombre": usuario.rol.nombre,
        }
    return None
