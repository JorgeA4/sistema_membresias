from clases.usuario import Usuario
import base_de_datos.consultas as bd

def autenticar_usuario(correo: str, contraseña: str) -> Usuario | None:
    usuario = bd.buscar_usuario_por_correo(correo)
    if usuario and usuario.contraseña == contraseña:
        return usuario
    else:
        return None
