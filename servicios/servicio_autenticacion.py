# servicios/servicio_autenticacion.py
#
# Servicio de autenticación — involucra Miembro + Usuario (dos clases),
# por eso vive aquí en servicios/ y no como método de una sola clase.
#
# CONTRATO CON LA INTERFAZ (Qt):
#   - Las funciones reciben datos simples (str, int, etc.)
#   - Siempre devuelven un valor con `return`
#   - Nunca hacen print(), nunca abren ventanas

from clases.miembro import Miembro
from clases.usuario import Usuario
import base_de_datos.consultas as bd

def autenticar_miembro(correo: str, contraseña: str) -> Miembro | None:
    miembro = bd.buscar_miembro_por_correo(correo)
    if miembro and miembro.contraseña == contraseña:
        return miembro
    else:
        return None

def autenticar_usuario_admin(correo: str, contraseña: str) -> Usuario | None:
    usuario = bd.buscar_usuario_por_correo(correo)
    if usuario and usuario.contraseña == contraseña:
        return usuario
    else:
        return None
