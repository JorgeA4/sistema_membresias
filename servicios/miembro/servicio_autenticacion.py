from clases.miembro import Miembro
import base_de_datos.consultas as bd

def autenticar_miembro(correo: str, contraseña: str) -> Miembro | None:
    miembro = bd.buscar_miembro_por_correo(correo)
    if miembro and miembro.contraseña == contraseña:
        return miembro
    else:
        return None